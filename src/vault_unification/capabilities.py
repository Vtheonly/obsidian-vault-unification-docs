"""Capability inventory, verified against actual test runs.

The declared inventory maps each capability to its owning module, CLI
command, referenced test files and documented limitations. ``--verify`` runs
the referenced tests for real (via pytest) and only upgrades a capability to
``implemented-and-tested`` when every referenced test passed in that run.

Statuses: planned | partial | implemented | implemented-and-tested | blocked.
A capability not listed here does not exist.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from . import __version__

REPO_ROOT = Path(__file__).resolve().parents[2]

CAPABILITIES: list[dict] = [
    {
        "id": "CAP-000",
        "name": "environment self-test",
        "module": "vault_unification.selftest",
        "command": "vu selftest",
        "status_declared": "implemented-and-tested",
        "tests": ["tests/test_selftest.py"],
        "limitations": [
            "checks importability only; does not validate corpus data"
        ],
    },
    {
        "id": "CAP-001",
        "name": "path safety and source immutability",
        "module": "vault_unification.pathsafety",
        "command": "vu check-paths",
        "status_declared": "implemented-and-tested",
        "tests": ["tests/test_pathsafety.py"],
        "limitations": [
            "trailing-space directory names are legal but hazardous; validation reports them as-is",
            "race conditions between check and write are not prevented (no locking)",
        ],
    },
    {
        "id": "CAP-002",
        "name": "recursive inventory and SHA-256 manifests",
        "module": "vault_unification.inventory",
        "command": "vu inventory / vu verify-manifest",
        "status_declared": "implemented-and-tested",
        "tests": ["tests/test_inventory.py"],
        "limitations": [
            "symlinks are recorded, not followed, unless --follow-symlinks is passed",
            "counts measure files, never semantic coverage",
        ],
    },
    {
        "id": "CAP-003",
        "name": "markdown structure extraction",
        "module": "vault_unification.mdextract",
        "command": "vu structure",
        "status_declared": "implemented-and-tested",
        "tests": ["tests/test_mdextract.py"],
        "limitations": [
            "inline $...$ math detection is delimiter-based; currency symbols can yield false positives",
            "no LaTeX syntax validation",
            "nested fences inside fences are treated as fence content",
        ],
    },
    {
        "id": "CAP-004",
        "name": "obsidian link/embed/anchor integrity",
        "module": "vault_unification.linkcheck",
        "command": "vu check-links",
        "status_declared": "implemented-and-tested",
        "tests": ["tests/test_linkcheck.py"],
        "limitations": [
            "heading anchor matching is normalized text equality; exotic anchors may be flagged",
            "percent-encoded markdown links are matched literally",
        ],
    },
    {
        "id": "CAP-005",
        "name": "exact/case-insensitive/normalized search and term stats",
        "module": "vault_unification.search",
        "command": "vu search / vu term-stats",
        "status_declared": "implemented-and-tested",
        "tests": ["tests/test_search.py"],
        "limitations": [
            "normalized mode collapses whitespace per line; multi-line phrase matches are not supported",
            "binary detection is heuristic (null-byte sniff)",
            "counts are lexical evidence only, never proof of semantic preservation",
        ],
    },
    {
        "id": "CAP-006",
        "name": "registry and task-queue schema validation",
        "module": "vault_unification.registry",
        "command": "vu validate-registry",
        "status_declared": "implemented-and-tested",
        "tests": ["tests/test_registry.py"],
        "limitations": [
            "cross-checks only task dependency references and id uniqueness",
            "requires jsonschema package",
        ],
    },
    {
        "id": "CAP-007",
        "name": "machine-readable report generation",
        "module": "vault_unification.reporting",
        "command": "(library; used by all commands)",
        "status_declared": "implemented-and-tested",
        "tests": ["tests/test_reporting.py"],
        "limitations": ["reports include timestamps; not byte-stable across runs (by design)"],
    },
    {
        "id": "CAP-008",
        "name": "test orchestration with machine-readable results",
        "module": "vault_unification.cli (run-tests)",
        "command": "vu run-tests",
        "status_declared": "implemented-and-tested",
        "tests": ["tests/test_cli.py"],
        "limitations": [
            "depends on pytest and pytest-json-report; missing plugins are reported, not hidden",
        ],
    },
    {
        "id": "CAP-009",
        "name": "capability inventory with test verification",
        "module": "vault_unification.capabilities",
        "command": "vu capabilities [--verify]",
        "status_declared": "implemented-and-tested",
        "tests": ["tests/test_cli.py"],
        "limitations": [
            "verification runs the referenced test files; runtime is proportional to suite size",
            "tests/test_capabilities.py verifies the verification logic itself using bounded "
            "subsets and is therefore not referenced here (avoids recursive test execution)",
        ],
    },
    {
        "id": "CAP-010",
        "name": "stable CLI entry point with help and exit codes",
        "module": "vault_unification.cli",
        "command": "vu --help (python -m vault_unification)",
        "status_declared": "implemented-and-tested",
        "tests": ["tests/test_cli.py"],
        "limitations": ["exit code 2 comes from argparse for usage errors"],
    },
    {
        "id": "CAP-011",
        "name": "knowledge-unit registry persistence (derived SQLite index over canonical JSONL)",
        "module": "vault_unification.kuregistry",
        "command": "vu kureg-init / kureg-load / kureg-query / kureg-validate",
        "status_declared": "implemented-and-tested",
        "tests": ["tests/test_kuregistry.py", "tests/test_cli.py"],
        "limitations": [
            "the SQLite database is a derived index; the committed JSONL batches under state/knowledge-units/ are the canonical record (ADR-0007) - rebuild the DB instead of repairing it",
            "all writes flow through kureg-load; no direct-to-database record creation in v1",
            "the conditional Superseded-rationale rule and overlap/disposition separation are enforced by cross-checks, not by JSON Schema",
            "mint_ku_id requires an excerpt, excerpt hash or line range; records without any locator must carry an explicit id",
            "single-writer assumption: no concurrency control on the database file",
            "query reconstruction issues O(n) grouped queries; acceptable at project scale, not benchmarked for millions of rows",
        ],
    },
    {
        "id": "CAP-015",
        "name": "content statistics: words, headings, token estimates",
        "module": "vault_unification.vaultstats",
        "command": "vu stats",
        "status_declared": "implemented-and-tested",
        "tests": ["tests/test_vaultstats.py", "tests/test_cli.py"],
        "limitations": [
            "word/token counts are lexical measurements with documented methods, never proof of semantic coverage",
            "tokens_estimate is chars//4, a rough BPE-style approximation, not an exact tokenizer count",
            "words_outside_fences treats unclosed fences/math blocks as extending to end-of-file",
            "non-markdown text files get lexical counts only (structure is Markdown-specific)",
        ],
    },
    {
        "id": "CAP-012",
        "name": "omission-detection pilot and reusable output auditor",
        "module": "vault_unification.omission",
        "command": "vu omission-pilot / vu audit-output",
        "status_declared": "implemented-and-tested",
        "tests": ["tests/test_omission.py", "tests/test_cli.py"],
        "limitations": [
            "term markers are frequency-based (rare in the source corpus): claims carried only by common vocabulary are not covered by term markers",
            "no stemming or grammar-level matching: reworded claims are caught only through shared distinctive vocabulary; semantic verification remains a separate evidence class",
            "equation/code matching compares normalized source strings; equivalent reformatting counts as different markers",
            "heading-convention check detects mixed schemes per note, not numbering sequences or cross-note ordering",
            "prose-quality is a word-count heuristic for bullet-only degradation, not an argument-quality judge",
            "drift detection requires an accepted manifest; pre-acceptance changes rely on content checks",
            "link findings attribute KU ownership by destination note plus wikilink presence in the excerpt",
            "the pilot fixture is small by design; corpus-scale noise must be re-measured on real extraction batches (CAP-014)",
        ],
    },
    {
        "id": "CAP-013",
        "name": "duplicate/near-duplicate candidate discovery",
        "module": None,
        "command": None,
        "status_declared": "planned",
        "tests": [],
        "limitations": ["planned; deterministic similarity is candidate generation only"],
    },
    {
        "id": "CAP-014",
        "name": "source-to-output coverage and frequency regression reports",
        "module": None,
        "command": None,
        "status_declared": "planned",
        "tests": [],
        "limitations": ["planned; required before synthesis batches are accepted"],
    },
]


def declared_inventory() -> dict:
    """Declared inventory (statuses are claims, not evidence)."""
    return {
        "framework_version": __version__,
        "note": "declared statuses are NOT evidence; run with --verify for test-backed statuses",
        "capabilities": CAPABILITIES,
    }


def verify_capabilities(
    repo_root: Path | None = None,
    test_files: list[str] | None = None,
) -> dict:
    """Run the referenced tests of every code-backed capability.

    A capability is marked ``implemented-and-tested`` only when every test in
    its referenced files passed in this run; otherwise the status is the
    declared one with failure details attached.

    ``test_files`` optionally restricts the pytest invocation to a subset
    (used by the framework's own tests to verify this logic without recursion).
    When pytest cannot run at all (missing files, broken environment) the
    result reports ``verified: false`` with the captured output.
    """
    root = Path(repo_root) if repo_root else REPO_ROOT
    with tempfile.NamedTemporaryFile(
        suffix=".json", prefix="vu-pytest-", delete=False
    ) as tmp:
        report_path = tmp.name

    if test_files is None:
        test_files = sorted(
            {t for cap in CAPABILITIES for t in cap.get("tests", []) if cap.get("module")}
        )
    if not test_files:
        return {
            "framework_version": __version__,
            "verified": False,
            "error": "no test files referenced by any capability",
        }
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "--json-report",
        f"--json-report-file={report_path}",
        *test_files,
    ]
    try:
        proc = subprocess.run(cmd, cwd=root, capture_output=True, text=True, timeout=1200)
    except subprocess.TimeoutExpired:
        return {
            "framework_version": __version__,
            "verified": False,
            "error": "pytest invocation timed out",
            "pytest_command": " ".join(cmd),
        }

    try:
        with open(report_path, encoding="utf-8") as handle:
            pytest_report = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "framework_version": __version__,
            "verified": False,
            "error": f"could not read pytest json report: {exc}",
            "pytest_returncode": proc.returncode,
            "pytest_stdout_tail": proc.stdout[-2000:],
        }

    tests_by_file: dict[str, list[dict]] = {}
    for test in pytest_report.get("tests", []):
        nodeid: str = test.get("nodeid", "")
        file_part = nodeid.split("::", 1)[0]
        tests_by_file.setdefault(file_part, []).append(test)

    capabilities_out: list[dict] = []
    for cap in CAPABILITIES:
        entry = dict(cap)
        if not cap.get("module"):
            entry["status_verified"] = cap["status_declared"]
            capabilities_out.append(entry)
            continue
        relevant: list[dict] = []
        for tf in cap.get("tests", []):
            relevant.extend(tests_by_file.get(tf, []))
        if not relevant:
            entry["status_verified"] = "blocked"
            entry["verify_detail"] = f"no tests collected for referenced files {cap.get('tests')}"
            capabilities_out.append(entry)
            continue
        outcomes = [t.get("outcome") for t in relevant]
        if all(outcome == "passed" for outcome in outcomes):
            entry["status_verified"] = "implemented-and-tested"
        else:
            entry["status_verified"] = cap["status_declared"].replace(
                "implemented-and-tested", "implemented"
            )
            entry["verify_detail"] = {
                "outcomes": {
                    outcome: outcomes.count(outcome) for outcome in sorted(set(outcomes))
                },
                "failed": [t["nodeid"] for t in relevant if t.get("outcome") == "failed"],
                "errors": [t["nodeid"] for t in relevant if t.get("outcome") == "error"],
                "skipped": [t["nodeid"] for t in relevant if t.get("outcome") == "skipped"],
            }
        capabilities_out.append(entry)

    passed = sum(1 for t in pytest_report.get("tests", []) if t.get("outcome") == "passed")
    return {
        "framework_version": __version__,
        "verified": True,
        "pytest_command": " ".join(cmd),
        "pytest_returncode": proc.returncode,
        "tests_total": len(pytest_report.get("tests", [])),
        "tests_passed": passed,
        "capabilities": capabilities_out,
    }
