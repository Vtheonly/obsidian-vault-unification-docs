"""Command-line interface for the vault_unification framework.

Exit codes:
- 0: success (no actionable problems found);
- 1: actionable failure (invalid inputs, unreadable files, broken links,
     invalid registry records, failing tests);
- 2: usage error (from argparse).

Commands that report problems (check-links, validate-registry, verify-manifest)
exit 1 when problems are found so CI-style gating works; the human summary and
the JSON report always state counts with their denominators.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from . import FRAMEWORK_NAME, __version__
from . import capabilities as capabilities_mod
from . import inventory as inventory_mod
from . import kuregistry as kuregistry_mod
from . import linkcheck as linkcheck_mod
from . import mdextract as mdextract_mod
from . import registry as registry_mod
from . import search as search_mod
from . import selftest as selftest_mod
from . import vaultstats as vaultstats_mod
from .kuregistry import RegistryError
from .pathsafety import PathSafetyError, ensure_dest_safe, validate_roots
from .reporting import write_json_report

REPO_ROOT = Path(__file__).resolve().parents[2]


def _emit_summary(summary: dict) -> None:
    print(json.dumps(summary, indent=2, sort_keys=False))


def _write_report_safe(args, command: str, payload: dict) -> Path | None:
    """Write a report after enforcing destination path safety."""
    report_path = getattr(args, "report", None)
    if not report_path:
        return None
    protected = []
    src = getattr(args, "root", None) or getattr(args, "source", None)
    if src:
        protected.append(Path(src))
    try:
        dest = ensure_dest_safe(report_path, protected)
    except PathSafetyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
    write_json_report(dest, command, payload, args=vars(args) | {"report": str(dest)}, repo_root=REPO_ROOT)
    return dest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vu",
        description=(
            "Deterministic tooling framework for the Obsidian Vault Unification project "
            f"(vault_unification {__version__}). Every command reports scope, denominators "
            "and exclusions. Source roots are never written to."
        ),
    )
    parser.add_argument("--version", action="version", version=f"{FRAMEWORK_NAME} {__version__}")
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    # ---- selftest ----
    p = sub.add_parser("selftest", help="environment diagnostics and dependency check")
    p.add_argument("--report", help="optional JSON report path")

    # ---- check-paths ----
    p = sub.add_parser("check-paths", help="validate source/output roots for overlap and symlink hazards")
    p.add_argument("--source", required=True, help="source vault root (read-only)")
    p.add_argument("--output", required=True, help="planned output root")
    p.add_argument("--report", help="optional JSON report path")

    # ---- inventory ----
    p = sub.add_parser("inventory", help="recursive inventory with SHA-256 hashes")
    p.add_argument("--root", required=True, help="directory to inventory")
    p.add_argument("--manifest", required=True, help="JSONL manifest output path (explicit destination)")
    p.add_argument("--report", help="optional JSON summary report path")
    p.add_argument("--follow-symlinks", action="store_true", help="hash symlink targets instead of recording them")

    # ---- verify-manifest ----
    p = sub.add_parser("verify-manifest", help="compare a stored manifest against current files")
    p.add_argument("--root", required=True, help="directory to re-inventory")
    p.add_argument("--manifest", required=True, help="stored JSONL manifest to compare against")
    p.add_argument("--report", help="optional JSON report path")

    # ---- structure ----
    p = sub.add_parser("structure", help="extract markdown structure (headings, links, fences, math)")
    p.add_argument("--file", required=True, help="markdown file to parse")
    p.add_argument("--report", help="optional JSON report path")

    # ---- check-links ----
    p = sub.add_parser("check-links", help="validate wikilinks, embeds, anchors and markdown links")
    p.add_argument("--root", required=True, help="vault root to check")
    p.add_argument("--report", help="optional JSON report path")

    # ---- search ----
    p = sub.add_parser("search", help="exact / case-insensitive / normalized term search")
    p.add_argument("--root", required=True, help="directory to search")
    p.add_argument("--term", required=True, help="non-empty search term")
    p.add_argument(
        "--mode",
        choices=["exact", "case-insensitive", "normalized"],
        default="exact",
        help="matching mode (default: exact)",
    )
    p.add_argument("--json", action="store_true", help="print full JSON result to stdout")
    p.add_argument("--report", help="optional JSON report path")

    # ---- term-stats ----
    p = sub.add_parser("term-stats", help="term frequency statistics with file distribution")
    p.add_argument("--root", required=True, help="directory to scan")
    p.add_argument("--terms-file", required=True, help="UTF-8 file, one term or 'term|alias|alias' per line")
    p.add_argument("--report", help="optional JSON report path")

    # ---- stats ----
    p = sub.add_parser("stats", help="content statistics: words, headings, tokens, structures")
    p.add_argument("--root", required=True, help="vault root to analyze")
    p.add_argument("--follow-symlinks", action="store_true", help="follow symlinks (off by default)")
    p.add_argument(
        "--per-file",
        help="optional JSONL path for per-file statistics records (kept out of the aggregate report)",
    )
    p.add_argument("--report", help="optional JSON report path (aggregate statistics)")

    # ---- validate-registry ----
    p = sub.add_parser("validate-registry", help="validate task-queue/KU JSONL records against schemas")
    p.add_argument("--tasks", help="task queue JSONL path")
    p.add_argument("--tasks-schema", default=str(REPO_ROOT / "schemas" / "task.schema.json"))
    p.add_argument("--kus", help="knowledge-unit JSONL path")
    p.add_argument("--kus-schema", default=str(REPO_ROOT / "schemas" / "knowledge-unit.schema.json"))
    p.add_argument("--report", help="optional JSON report path")

    # ---- run-tests ----
    p = sub.add_parser("run-tests", help="run the pytest suite with machine-readable results")
    p.add_argument("--tests-dir", default="tests", help="test directory or file (default: tests)")
    p.add_argument("--json-report", required=True, help="path for the pytest-json-report output")
    p.add_argument("--pytest-arg", action="append", default=[], help="extra pytest args (repeatable)")

    # ---- capabilities ----
    p = sub.add_parser("capabilities", help="emit capability inventory (optionally test-verified)")
    p.add_argument("--verify", action="store_true", help="run referenced tests before reporting statuses")
    p.add_argument("--report", help="optional JSON report path")

    # ---- kureg-init ----
    p = sub.add_parser(
        "kureg-init",
        help="create an empty knowledge-unit registry database (derived SQLite index)",
    )
    p.add_argument("--db", required=True, help="registry database path to create (explicit destination)")
    p.add_argument("--force", action="store_true", help="delete and re-create an existing registry (rebuilds start here)")
    p.add_argument(
        "--protected-root",
        action="append",
        default=None,
        help="path the database must not be written under (repeatable); default: <repo>/source-vaults when present",
    )
    p.add_argument("--report", help="optional JSON report path")

    # ---- kureg-load ----
    p = sub.add_parser(
        "kureg-load",
        help="validate a KU JSONL batch and load it atomically into the registry",
    )
    p.add_argument("--db", required=True, help="registry database path (must exist; run kureg-init first)")
    p.add_argument("--kus", required=True, help="KU batch JSONL file (schema-validated before insert)")
    p.add_argument(
        "--mint-ids",
        action="store_true",
        help="mint deterministic knowledge_unit_ids for records that lack one (content-fingerprint based)",
    )
    p.add_argument(
        "--kus-schema",
        default=str(REPO_ROOT / "schemas" / "knowledge-unit.schema.json"),
        help="knowledge-unit JSON Schema path",
    )
    p.add_argument(
        "--protected-root",
        action="append",
        default=None,
        help="path the database must not be written under (repeatable); default: <repo>/source-vaults when present",
    )
    p.add_argument("--report", help="optional JSON report path")

    # ---- kureg-query ----
    p = sub.add_parser(
        "kureg-query",
        help="query the registry and reconstruct schema-shaped KU records",
    )
    p.add_argument("--db", required=True, help="registry database path")
    p.add_argument("--ku", help="exact knowledge_unit_id")
    p.add_argument(
        "--disposition",
        choices=list(kuregistry_mod.DISPOSITIONS),
        help="filter by disposition",
    )
    p.add_argument("--source-path", help="filter by exact source path")
    p.add_argument("--source-id", help="filter by exact source id")
    p.add_argument("--concept", help="filter by concept id")
    p.add_argument("--finding", help="filter by linked finding id")
    p.add_argument("--unit-type", help="filter by unit type")
    p.add_argument(
        "--format",
        choices=["json", "jsonl"],
        default="json",
        help="json: summary with counts; jsonl: one reconstructed record per line",
    )
    p.add_argument("--report", help="optional JSON report path (full query result)")

    # ---- kureg-validate ----
    p = sub.add_parser(
        "kureg-validate",
        help="integrity + accounting-invariant report for a registry database",
    )
    p.add_argument("--db", required=True, help="registry database path")
    p.add_argument("--report", help="optional JSON report path")

    return parser


def cmd_selftest(args) -> int:
    result = selftest_mod.run_selftest()
    payload = {"command": "selftest", "result": result}
    _write_report_safe(args, "selftest", payload)
    _emit_summary({"ok": result["ok"], "mandatory_checks_passed": result["mandatory_checks_passed"], "optional_missing": result["optional_missing"]})
    return 0 if result["ok"] else 1


def cmd_check_paths(args) -> int:
    validation = validate_roots(args.source, args.output)
    payload = {"command": "check-paths", "validation": validation.as_dict()}
    _write_report_safe(args, "check-paths", payload)
    _emit_summary(validation.as_dict())
    return 0 if validation.ok else 1


def cmd_inventory(args) -> int:
    scan = inventory_mod.scan_root(args.root, follow_symlinks=args.follow_symlinks)
    # manifest destination must not be inside the scanned source root
    dest = ensure_dest_safe(args.manifest, [Path(args.root)])
    manifest_path = Path(dest)
    count = inventory_mod.write_manifest(manifest_path, inventory_mod.manifest_records(scan))
    payload = {
        "command": "inventory",
        "root": scan["root"],
        "counts": scan["counts"],
        "total_files": scan["total_files"],
        "manifest_path": str(manifest_path),
        "manifest_records": count,
        "unreadable_files": scan["errors"],
    }
    report = _write_report_safe(args, "inventory", payload)
    _emit_summary(
        {
            "root": scan["root"],
            "total_files": scan["total_files"],
            "counts": scan["counts"],
            "manifest_path": str(manifest_path),
            "report": str(report) if report else None,
        }
    )
    # unreadable files make the run incomplete: actionable failure
    return 1 if scan["errors"] else 0


def cmd_verify_manifest(args) -> int:
    stored = inventory_mod.load_manifest(args.manifest)
    scan = inventory_mod.scan_root(args.root)
    current = inventory_mod.manifest_records(scan)
    diff = inventory_mod.diff_manifests(stored, current)
    payload = {
        "command": "verify-manifest",
        "root": scan["root"],
        "manifest": args.manifest,
        "diff": diff,
        "unreadable_files": scan["errors"],
    }
    _write_report_safe(args, "verify-manifest", payload)
    _emit_summary({"root": scan["root"], "diff_counts": diff["counts"], "added": diff["added"], "removed": diff["removed"], "changed": diff["changed"]})
    if scan["errors"]:
        return 1
    return 0 if diff["counts"]["added"] == diff["counts"]["removed"] == diff["counts"]["changed"] == 0 else 1


def cmd_structure(args) -> int:
    if not Path(args.file).is_file():
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 1
    result = mdextract_mod.extract_structure(args.file)
    payload = {"command": "structure", "result": result}
    _write_report_safe(args, "structure", payload)
    _emit_summary(
        {
            "path": result["path"],
            "line_count": result["line_count"],
            "headings": len(result["headings"]),
            "wikilinks": len(result["wikilinks"]),
            "embeds": len(result["embeds"]),
            "md_links": len(result["md_links"]),
            "code_fences": len(result["code_fences"]),
            "math_blocks": len(result["math_blocks"]),
            "errors": result["errors"],
            "warnings": result["warnings"],
        }
    )
    return 1 if result["errors"] else 0


def cmd_check_links(args) -> int:
    result = linkcheck_mod.check_links(args.root)
    payload = {"command": "check-links", "result": result}
    _write_report_safe(args, "check-links", payload)
    _emit_summary(
        {
            "root": result["root"],
            "markdown_files_checked": result["markdown_files_checked"],
            "links_checked": result["links_checked"],
            "problem_counts": result["problem_counts"],
            "external_links": len(result["external_links"]),
        }
    )
    return 1 if result["problems"] else 0


def cmd_search(args) -> int:
    result = search_mod.search_term(args.root, args.term, args.mode)
    payload = {"command": "search", "result": result}
    _write_report_safe(args, "search", payload)
    if args.json:
        _emit_summary(result)
    else:
        _emit_summary(
            {
                "term": result["term"],
                "mode": result["mode"],
                "match_count": result["match_count"],
                "files_with_matches_count": result["files_with_matches_count"],
                "scope": result["scope"],
            }
        )
    return 0


def cmd_term_stats(args) -> int:
    terms_file = Path(args.terms_file)
    if not terms_file.is_file():
        print(f"error: terms file not found: {terms_file}", file=sys.stderr)
        return 1
    terms: list[str] = []
    aliases: dict[str, list[str]] = {}
    for line in terms_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [piece.strip() for piece in line.split("|")]
        term = parts[0]
        if not term:
            continue
        terms.append(term)
        alias_list = [a for a in parts[1:] if a]
        if alias_list:
            aliases[term] = alias_list
    result = search_mod.term_stats(args.root, terms, aliases=aliases)
    payload = {"command": "term-stats", "result": result}
    _write_report_safe(args, "term-stats", payload)
    _emit_summary(
        {
            "root": result["root"],
            "terms": {term: stat["total_count"] for term, stat in result["stats"].items()},
            "files_scanned": result["denominator"]["files_scanned"],
            "exclusions": result["exclusions"],
        }
    )
    return 0


def cmd_stats(args) -> int:
    result = vaultstats_mod.stats_root(args.root, follow_symlinks=args.follow_symlinks)
    per_file = result.pop("per_file")
    payload = {"command": "stats", **result}
    _write_report_safe(args, "stats", payload)

    per_file_path = getattr(args, "per_file", None)
    if per_file_path:
        dest = ensure_dest_safe(per_file_path, [Path(args.root)])
        Path(dest).parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "w", encoding="utf-8") as handle:
            for rec in per_file:
                handle.write(json.dumps(rec, sort_keys=True) + "\n")

    totals = result["totals"]
    _emit_summary(
        {
            "root": result["root"],
            "files_discovered": totals["files_discovered"],
            "text_files_analyzed": totals["text_files_analyzed"],
            "files_with_errors": totals["text_files_with_errors"],
            "skipped_nontext": totals["files_skipped_nontext"],
            "words_total": totals["words_total"],
            "words_outside_fences": totals["words_outside_fences"],
            "tokens_estimate": totals["tokens_estimate"],
            "headings_total": totals["headings_total"],
            "per_file_records": len(per_file),
            "per_file_path": str(per_file_path) if per_file_path else None,
        }
    )
    return 1 if totals["text_files_with_errors"] else 0


def cmd_validate_registry(args) -> int:
    payload: dict = {"command": "validate-registry", "validations": {}}
    problems = 0
    if args.tasks:
        result = registry_mod.validate_task_queue(args.tasks, args.tasks_schema)
        payload["validations"]["tasks"] = result
        problems += len(result["errors"])
    if args.kus:
        result = registry_mod.validate_ku_file(args.kus, args.kus_schema)
        payload["validations"]["knowledge_units"] = result
        problems += len(result["errors"])
    if not args.tasks and not args.kus:
        print("error: provide --tasks and/or --kus", file=sys.stderr)
        return 1
    payload["problems_total"] = problems
    payload["valid"] = problems == 0
    _write_report_safe(args, "validate-registry", payload)
    _emit_summary({"valid": payload["valid"], "problems_total": problems})
    return 0 if problems == 0 else 1


def cmd_run_tests(args) -> int:
    json_report = Path(args.json_report)
    json_report.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(args.tests_dir),
        "-v",
        "--json-report",
        f"--json-report-file={json_report}",
        *args.pytest_arg,
    ]
    proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, timeout=3600)
    try:
        with open(json_report, encoding="utf-8") as handle:
            pytest_report = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: pytest json report unreadable: {exc}", file=sys.stderr)
        print(proc.stdout[-4000:])
        print(proc.stderr[-2000:], file=sys.stderr)
        return 1
    summary = pytest_report.get("summary", {})
    skipped = [
        {"nodeid": t.get("nodeid"), "reason": (t.get("call") or {}).get("crash", {}).get("message", "")}
        for t in pytest_report.get("tests", [])
        if t.get("outcome") == "skipped"
    ]
    outcomes: dict[str, int] = {}
    for test in pytest_report.get("tests", []):
        outcome = test.get("outcome", "unknown")
        outcomes[outcome] = outcomes.get(outcome, 0) + 1
    _emit_summary(
        {
            "command": " ".join(cmd),
            "returncode": proc.returncode,
            "summary": summary,
            "outcomes": outcomes,
            "json_report": str(json_report),
            "skipped_tests": skipped,
        }
    )
    return proc.returncode


def cmd_capabilities(args) -> int:
    if args.verify:
        result = capabilities_mod.verify_capabilities(REPO_ROOT)
        if not result.get("verified"):
            print(f"error: capability verification failed: {result.get('error')}", file=sys.stderr)
            return 1
        ok = all(
            cap.get("status_verified") in ("implemented-and-tested", "planned", "blocked")
            or not cap.get("module")
            for cap in result["capabilities"]
        )
    else:
        result = capabilities_mod.declared_inventory()
        ok = True
    _write_report_safe(args, "capabilities", result)
    statuses = (
        {
            cap["id"]: cap.get("status_verified", cap.get("status_declared"))
            for cap in result["capabilities"]
        }
        if "capabilities" in result
        else {}
    )
    _emit_summary(
        {
            "framework_version": result.get("framework_version"),
            "verified": bool(args.verify),
            "statuses": statuses,
        }
    )
    if args.verify:
        return 0 if result.get("pytest_returncode", 1) == 0 else 1
    return 0


def _kureg_protected_roots(args) -> list[Path]:
    """Protected roots for registry writes: explicit --protected-root or the
    repository's source-vaults directory when it exists."""
    explicit = getattr(args, "protected_root", None) or []
    if explicit:
        return [Path(p) for p in explicit]
    default = REPO_ROOT / "source-vaults"
    return [default] if default.is_dir() else []


def _kureg_write_report(args, command: str, payload: dict, roots: list[Path]) -> Path | None:
    """Write a kureg report after enforcing destination path safety."""
    report_path = getattr(args, "report", None)
    if not report_path:
        return None
    dest = ensure_dest_safe(report_path, roots)
    write_json_report(dest, command, payload, args=vars(args) | {"report": str(dest)}, repo_root=REPO_ROOT)
    return dest


def cmd_kureg_init(args) -> int:
    roots = _kureg_protected_roots(args)
    db = ensure_dest_safe(args.db, roots)
    result = kuregistry_mod.init_registry(db, force=args.force)
    payload = {"command": "kureg-init", "result": result}
    _kureg_write_report(args, "kureg-init", payload, roots)
    _emit_summary(
        {
            "db_path": result["db_path"],
            "registry_schema_version": result["registry_schema_version"],
            "id_namespace": result["id_namespace"],
            "force_used": result["force_used"],
        }
    )
    return 0


def cmd_kureg_load(args) -> int:
    roots = _kureg_protected_roots(args)
    db = ensure_dest_safe(args.db, roots)
    result = kuregistry_mod.load_jsonl(
        db, args.kus, schema_path=args.kus_schema, mint_ids=args.mint_ids
    )
    payload = {"command": "kureg-load", **result}
    _kureg_write_report(args, "kureg-load", payload, roots)
    _emit_summary(
        {
            "valid": result.get("valid"),
            "records_file": result.get("records_file"),
            "records_in_batch": result.get("records_in_batch"),
            "inserted": result.get("inserted"),
            "skipped_identical": result.get("skipped_identical"),
            "errors_total": len(result.get("errors", [])),
            "counts_after_load": result.get("counts_after_load"),
        }
    )
    return 0 if result.get("valid") else 1


def cmd_kureg_query(args) -> int:
    result = kuregistry_mod.query_registry(
        args.db,
        ku_id=args.ku,
        disposition=args.disposition,
        source_path=args.source_path,
        source_id=args.source_id,
        concept=args.concept,
        finding=args.finding,
        unit_type=args.unit_type,
    )
    payload = {"command": "kureg-query", **result}
    _kureg_write_report(args, "kureg-query", payload, [])
    if args.format == "jsonl":
        for record in result["records"]:
            print(json.dumps(record, sort_keys=True))
    else:
        _emit_summary(
            {
                "filters": result["filters"],
                "count": result["count"],
                "total_kus": result["total_kus"],
            }
        )
    return 0


def cmd_kureg_validate(args) -> int:
    result = kuregistry_mod.validate_registry_db(args.db)
    payload = {"command": "kureg-validate", **result}
    _kureg_write_report(args, "kureg-validate", payload, [])
    _emit_summary(
        {
            "valid": result["valid"],
            "errors_total": len(result["errors"]),
            "warnings_total": len(result["warnings"]),
            "counts": result["counts"],
            "unaccounted_count": result["unaccounted_count"],
            "needs_review_count": result["needs_review_count"],
        }
    )
    return 0 if result["valid"] else 1


HANDLERS = {
    "selftest": cmd_selftest,
    "check-paths": cmd_check_paths,
    "inventory": cmd_inventory,
    "verify-manifest": cmd_verify_manifest,
    "structure": cmd_structure,
    "check-links": cmd_check_links,
    "search": cmd_search,
    "term-stats": cmd_term_stats,
    "stats": cmd_stats,
    "validate-registry": cmd_validate_registry,
    "run-tests": cmd_run_tests,
    "capabilities": cmd_capabilities,
    "kureg-init": cmd_kureg_init,
    "kureg-load": cmd_kureg_load,
    "kureg-query": cmd_kureg_query,
    "kureg-validate": cmd_kureg_validate,
}


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return 2
    handler = HANDLERS[args.command]
    try:
        return handler(args)
    except (PathSafetyError, NotADirectoryError, ValueError, RegistryError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
