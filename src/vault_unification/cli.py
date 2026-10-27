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
from . import artifactlint as artifactlint_mod
from . import capabilities as capabilities_mod
from . import discovery as discovery_mod
from . import notequality as notequality_mod
from . import promptspec as promptspec_mod
from . import repair as repair_mod
from . import inventory as inventory_mod
from . import kuregistry as kuregistry_mod
from . import kuextract as kuextract_mod
from . import kufidelity as kufidelity_mod
from . import linkcheck as linkcheck_mod
from . import mdextract as mdextract_mod
from . import omission as omission_mod
from . import overlap as overlap_mod
from . import registry as registry_mod
from . import search as search_mod
from . import selftest as selftest_mod
from . import vaultstats as vaultstats_mod
from .kuregistry import RegistryError
from .kufidelity import FidelityError
from .omission import AuditError
from .overlap import OverlapError
from .artifactlint import ArtifactLintError
from .discovery import DiscoveryError
from .notequality import QualityError
from .pathsafety import PathSafetyError, ensure_dest_safe, validate_roots
from .promptspec import PromptSpecError
from .repair import RepairError
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
    p = sub.add_parser("search", help="exact / case-insensitive / normalized / multi-line phrase search")
    p.add_argument("--root", required=True, help="directory to search")
    p.add_argument("--term", required=True, help="non-empty search term or (phrase mode) multi-line phrase")
    p.add_argument(
        "--mode",
        choices=["exact", "case-insensitive", "normalized", "phrase"],
        default="exact",
        help=(
            "matching mode (default: exact); 'phrase' = whole-file normalized "
            "matching that finds phrases spanning line breaks (L-01) with "
            "(line_start, line_end) span locators"
        ),
    )
    p.add_argument("--json", action="store_true", help="print full JSON result to stdout")
    p.add_argument("--report", help="optional JSON report path")

    # ---- term-stats ----
    p = sub.add_parser("term-stats", help="term frequency statistics with file distribution")
    p.add_argument("--root", required=True, help="directory to scan")
    p.add_argument("--terms-file", required=True, help="UTF-8 file, one term or 'term|alias|alias' per line")
    p.add_argument(
        "--match-mode",
        choices=["substring", "word-boundary"],
        default="substring",
        help=(
            "counting semantics (L-07): 'substring' = casefolded substring "
            "(backward compatible, 'ridge' counts inside 'bridge'); "
            "'word-boundary' = CAP-013 semantics via the shared pattern authority"
        ),
    )
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
    p = sub.add_parser("validate-registry", help="validate task-queue/KU/classification JSONL records against schemas")
    p.add_argument("--tasks", help="task queue JSONL path")
    p.add_argument("--tasks-schema", default=str(REPO_ROOT / "schemas" / "task.schema.json"))
    p.add_argument("--kus", help="knowledge-unit JSONL path")
    p.add_argument("--kus-schema", default=str(REPO_ROOT / "schemas" / "knowledge-unit.schema.json"))
    p.add_argument("--classifications", help="overlap-classification JSONL path")
    p.add_argument(
        "--classifications-schema",
        default=str(REPO_ROOT / "schemas" / "overlap-classification.schema.json"),
    )
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

    # ---- audit-output ----
    p = sub.add_parser(
        "audit-output",
        help="run the omission/corruption audit pipeline over a candidate output vault",
    )
    p.add_argument("--source-root", required=True, help="source vault root (read-only; term-frequency corpus)")
    p.add_argument("--output-root", required=True, help="candidate output vault root to audit")
    p.add_argument("--ku-batch", required=True, help="KU JSONL batch with source units and destinations")
    p.add_argument(
        "--accepted-manifest",
        help="optional accepted-output manifest (JSONL) enabling drift regression checks",
    )
    p.add_argument(
        "--ku-schema",
        default=str(REPO_ROOT / "schemas" / "knowledge-unit.schema.json"),
        help="knowledge-unit JSON Schema path",
    )
    p.add_argument("--report", help="optional JSON report path")

    # ---- extract-kus ----
    p = sub.add_parser(
        "extract-kus",
        help="deterministically segment source notes into schema-valid KU records",
    )
    p.add_argument("--root", required=True, help="source vault root (read-only)")
    p.add_argument(
        "--scope",
        required=True,
        help="root-relative directory (or single file) to extract; '.' = whole vault",
    )
    p.add_argument(
        "--vault-id",
        required=True,
        help="stable vault identifier used in source_id (e.g. ai-course); keep constant across sessions",
    )
    p.add_argument(
        "--manifest",
        required=True,
        help="baseline manifest JSONL (root-relative relpaths + sha256) the scope is verified against",
    )
    p.add_argument("--out", required=True, help="KU batch JSONL destination (explicit; never under --root)")
    p.add_argument(
        "--kus-schema",
        default=str(REPO_ROOT / "schemas" / "knowledge-unit.schema.json"),
        help="knowledge-unit JSON Schema path",
    )
    p.add_argument(
        "--unclosed-fence-finding",
        default=None,
        help="finding id to attach to units from unclosed fences/math blocks (e.g. F-0002)",
    )
    p.add_argument("--report", help="optional JSON coverage report path")

    # ---- ku-fidelity (CAP-022) ----
    p = sub.add_parser(
        "ku-fidelity",
        help="verify KU batches are byte-faithful to their sources (excerpt slices, hashes, ids)",
    )
    p.add_argument(
        "--batch",
        required=True,
        action="append",
        dest="batches",
        help="KU batch JSONL file to check (repeatable; all must belong to one vault)",
    )
    p.add_argument(
        "--vault-id",
        required=True,
        help="stable vault identifier the batches were extracted with (e.g. ai-course)",
    )
    p.add_argument("--vault-root", required=True, help="source vault root (read-only)")
    p.add_argument(
        "--manifest",
        required=True,
        help="baseline manifest JSONL (root-relative relpaths + sha256) to verify against",
    )
    p.add_argument(
        "--kus-schema",
        default=str(REPO_ROOT / "schemas" / "knowledge-unit.schema.json"),
        help="knowledge-unit JSON Schema path (schema validation included in the check)",
    )
    p.add_argument(
        "--allow-processed",
        action="store_true",
        help="relax the fresh-batch structural-purity check (for post-disposition re-verification)",
    )
    p.add_argument(
        "--cross-check-glob",
        default=None,
        help="glob of additional batches to preload for id-collision checks "
        "(default: every sibling *.jsonl of the checked batches)",
    )
    p.add_argument("--report", help="optional JSON report path")

    # ---- omission-pilot ----
    p = sub.add_parser(
        "omission-pilot",
        help="build the synthetic omission-detection fixture and verify the auditor (hard gate)",
    )
    p.add_argument("--dest", required=True, help="explicit working directory for the pilot fixture (must not be inside a protected root)")
    p.add_argument(
        "--protected-root",
        action="append",
        default=None,
        help="path the pilot must not write under (repeatable); default: <repo>/source-vaults when present",
    )
    p.add_argument(
        "--keep-mutations",
        action="store_true",
        help="keep the mutated copies under <dest>/mutated for inspection (temporary by default)",
    )
    p.add_argument(
        "--ku-schema",
        default=str(REPO_ROOT / "schemas" / "knowledge-unit.schema.json"),
        help="knowledge-unit JSON Schema path",
    )
    p.add_argument("--report", help="optional JSON report path")

    # ---- overlap-candidates ----
    p = sub.add_parser(
        "overlap-candidates",
        help="discover cross-vault overlap candidates (word-boundary term/alias evidence; CAP-013)",
    )
    p.add_argument(
        "--batch",
        required=True,
        action="append",
        dest="batches",
        help="KU batch JSONL path (repeatable; >= 2 batches from distinct vaults)",
    )
    p.add_argument(
        "--terms",
        required=True,
        help="terms JSON file: {term: [aliases]} or [term, ...]",
    )
    p.add_argument(
        "--out",
        required=True,
        help="candidate-pairs JSONL destination (explicit; never under a protected root)",
    )
    p.add_argument(
        "--kus-schema",
        default=str(REPO_ROOT / "schemas" / "knowledge-unit.schema.json"),
        help="knowledge-unit JSON Schema path",
    )
    p.add_argument(
        "--max-pairs-per-topic",
        type=int,
        default=250,
        help="cap on the cross-product pair count per topic (default 250; "
        "excess topics are flagged and their per-KU evidence stays complete)",
    )
    p.add_argument(
        "--protected-root",
        action="append",
        default=None,
        help="path the outputs must not be written under (repeatable); default: <repo>/source-vaults when present",
    )
    p.add_argument("--report", help="optional JSON report path")

    # ---- discover-gaps (CAP-017) ----
    p = sub.add_parser(
        "discover-gaps",
        help="emergent concept & knowledge-gap discovery over KU batches (deterministic evidence; CAP-017)",
    )
    p.add_argument(
        "--batch",
        required=True,
        action="append",
        dest="batches",
        help="KU batch JSONL path (repeatable)",
    )
    p.add_argument(
        "--manifest",
        required=True,
        action="append",
        dest="manifests",
        help="coverage manifest as VAULT=manifest.jsonl (repeatable; every vault in the batches must be declared)",
    )
    p.add_argument(
        "--out",
        required=True,
        help="candidates JSONL destination (explicit; never under a protected root)",
    )
    p.add_argument(
        "--kus-schema",
        default=str(REPO_ROOT / "schemas" / "knowledge-unit.schema.json"),
        help="knowledge-unit JSON Schema path",
    )
    p.add_argument(
        "--max-evidence",
        type=int,
        default=12,
        help="cap on evidence entries per candidate (default 12; counts stay complete in the report)",
    )
    p.add_argument(
        "--protected-root",
        action="append",
        default=None,
        help="path the outputs must not be written under (repeatable); default: <repo>/source-vaults when present",
    )
    p.add_argument("--report", help="optional JSON report path")

    # ---- discovery-decide (CAP-017) ----
    p = sub.add_parser(
        "discovery-decide",
        help="apply reviewed decisions (confirm/accept/reject/defer/merge/split/revise/cover) with append-only history",
    )
    p.add_argument("--candidates", required=True, help="candidates JSONL produced by discover-gaps")
    p.add_argument("--decisions", required=True, help="decisions JSONL (candidate_id, decision_id, action, rationale, reviewer; merge->merge_into; split->split_into/new_candidates)")
    p.add_argument("--out", required=True, help="updated candidates JSONL destination")
    p.add_argument(
        "--candidate-schema",
        default=str(REPO_ROOT / "schemas" / "concept-candidate.schema.json"),
        help="concept-candidate JSON Schema path",
    )
    p.add_argument(
        "--decided-utc",
        default=None,
        help="ISO-8601 UTC timestamp for the decision history entries (default: now, recorded in the report)",
    )
    p.add_argument(
        "--protected-root",
        action="append",
        default=None,
        help="path the outputs must not be written under (repeatable)",
    )
    p.add_argument("--report", help="optional JSON report path")

    # ---- discovery-validate (CAP-017) ----
    p = sub.add_parser(
        "discovery-validate",
        help="validate candidate records against the schema + cross-checks (coverage gate, history integrity)",
    )
    p.add_argument("--candidates", required=True, help="candidates JSONL to validate")
    p.add_argument(
        "--candidate-schema",
        default=str(REPO_ROOT / "schemas" / "concept-candidate.schema.json"),
        help="concept-candidate JSON Schema path",
    )
    p.add_argument(
        "--batch",
        action="append",
        dest="batches",
        default=None,
        help="optional KU batch to cross-check evidence ku_ids (repeatable)",
    )
    p.add_argument(
        "--kus-schema",
        default=str(REPO_ROOT / "schemas" / "knowledge-unit.schema.json"),
        help="knowledge-unit JSON Schema path",
    )
    p.add_argument("--report", help="optional JSON report path")

    # ---- lint-artifacts (CAP-018) ----
    p = sub.add_parser(
        "lint-artifacts",
        help="structural/syntactic artifact validation of generated notes (fences, math, tables, mermaid, links, truncation)",
    )
    p.add_argument("path", help="Markdown file or directory to lint")
    p.add_argument(
        "--no-links",
        action="store_true",
        help="skip internal-link resolution (pure structural lint)",
    )
    p.add_argument(
        "--skip-dir",
        action="append",
        dest="skip_dirs",
        default=[".git", ".obsidian"],
        help="directory name to skip when linting a tree (repeatable)",
    )
    p.add_argument("--report", help="optional JSON report path")

    # ---- assess-quality (CAP-019) ----
    p = sub.add_parser(
        "assess-quality",
        help="note-type-aware deterministic quality assessment of every note under a root",
    )
    p.add_argument("root", help="directory containing generated notes")
    p.add_argument(
        "--provenance",
        help="note->ku_ids mapping JSONL (enables the source_coverage dimension)",
    )
    p.add_argument(
        "--ku-batch",
        action="append",
        dest="ku_batches",
        default=None,
        help="KU batch JSONL for source-coverage term extraction (repeatable)",
    )
    p.add_argument("--out", help="optional assessments JSONL destination")
    p.add_argument("--report", help="optional JSON report path")

    # ---- quality-drift (CAP-019) ----
    p = sub.add_parser(
        "quality-drift",
        help="detect systematic quality drift between early and late notes (per type, per dimension)",
    )
    p.add_argument("--assessments", required=True, help="assessments JSONL produced by assess-quality")
    p.add_argument("--rel-drop", type=float, default=0.15, help="relative drop threshold (default 0.15)")
    p.add_argument("--abs-drop", type=float, default=0.10, help="absolute drop threshold (default 0.10)")
    p.add_argument("--report", help="optional JSON report path")

    # ---- quality-gate (CAP-019) ----
    p = sub.add_parser(
        "quality-gate",
        help="batch acceptance gate: expected notes, lint cleanliness, dimension bands, drift explanation",
    )
    p.add_argument("--assessments", required=True, help="assessments JSONL produced by assess-quality")
    p.add_argument(
        "--expected",
        help="optional text file listing expected note paths (one per line)",
    )
    p.add_argument(
        "--drift-report",
        help="optional quality-drift JSON report (drift explanation criterion)",
    )
    p.add_argument(
        "--waiver",
        action="append",
        dest="waivers",
        default=None,
        help="explicit waiver 'note::dimension=reason' or 'drift::type=reason' (repeatable)",
    )
    p.add_argument("--report", help="optional JSON report path")

    # ---- repair-create (CAP-020) ----
    p = sub.add_parser(
        "repair-create",
        help="convert an artifact-lint report into targeted repair tasks (idempotent, content-addressed)",
    )
    p.add_argument("--lint-report", required=True, help="lint-artifacts JSON report (tree or single file)")
    p.add_argument("--store", required=True, help="repair-task JSONL store (merged when it exists)")
    p.add_argument("--max-attempts", type=int, default=3, help="bounded retries per task (default 3)")
    p.add_argument("--report", help="optional JSON report path")

    # ---- repair-record (CAP-020) ----
    p = sub.add_parser(
        "repair-record",
        help="record a repair attempt (outcome fixed/failed/skipped) on a task",
    )
    p.add_argument("--store", required=True, help="repair-task JSONL store")
    p.add_argument("--id", required=True, help="repair task id (RT-...)")
    p.add_argument("--outcome", required=True, choices=["fixed", "failed", "skipped"], help="attempt outcome")
    p.add_argument("--diff-file", help="optional file containing the unified diff of the change")
    p.add_argument("--note", help="optional free-text note about the attempt")
    p.add_argument("--report", help="optional JSON report path")

    # ---- repair-verify (CAP-020) ----
    p = sub.add_parser(
        "repair-verify",
        help="verify a claimed repair: originating check passes, no new defects, scope local",
    )
    p.add_argument("--store", required=True, help="repair-task JSONL store")
    p.add_argument("--id", required=True, help="repair task id (RT-...)")
    p.add_argument("--note-file", required=True, help="current (repaired) note file")
    p.add_argument("--original-file", help="optional pre-repair copy of the note (enables scope discipline)")
    p.add_argument("--report", help="optional JSON report path")

    # ---- repair-list (CAP-020) ----
    p = sub.add_parser(
        "repair-list",
        help="list repair tasks with status counts (optionally filtered by status)",
    )
    p.add_argument("--store", required=True, help="repair-task JSONL store")
    p.add_argument("--status", help="filter by status (open/awaiting_verification/verified_fixed/escalated_review)")
    p.add_argument("--report", help="optional JSON report path")

    # ---- repair-prompt (CAP-020/021) ----
    p = sub.add_parser(
        "repair-prompt",
        help="build a targeted repair prompt spec from a repair task (smallest sufficient context)",
    )
    p.add_argument("--store", required=True, help="repair-task JSONL store")
    p.add_argument("--id", required=True, help="repair task id (RT-...)")
    p.add_argument("--out", required=True, help="generation-prompt JSON destination")
    p.add_argument("--report", help="optional JSON report path")

    # ---- check-prompt (CAP-021) ----
    p = sub.add_parser(
        "check-prompt",
        help="validate a generation-prompt spec (precision, evidence resolvability, testable criteria, boundedness)",
    )
    p.add_argument("spec", help="generation-prompt spec JSON file")
    p.add_argument(
        "--ku-batch",
        action="append",
        dest="ku_batches",
        default=None,
        help="KU batch JSONL to resolve ku_ids against (repeatable)",
    )
    p.add_argument("--context-budget", type=int, default=4000, help="context budget in words (default 4000)")
    p.add_argument("--max-requirements", type=int, default=25, help="requirements cap (default 25)")
    p.add_argument("--report", help="optional JSON report path")

    # ---- kureg-apply-overlap ----
    p = sub.add_parser(
        "kureg-apply-overlap",
        help="apply append-only overlap classification records to the registry (ADR-0009)",
    )
    p.add_argument("--db", required=True, help="registry database path (must exist; run kureg-init first)")
    p.add_argument(
        "--classifications",
        required=True,
        help="overlap-classification JSONL path (schema-validated before insert)",
    )
    p.add_argument(
        "--classifications-schema",
        default=str(REPO_ROOT / "schemas" / "overlap-classification.schema.json"),
        help="overlap-classification JSON Schema path",
    )
    p.add_argument(
        "--protected-root",
        action="append",
        default=None,
        help="path the database must not be written under (repeatable); default: <repo>/source-vaults when present",
    )
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
    if args.mode == "phrase":
        result = search_mod.search_phrase(args.root, args.term)
    else:
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
    result = search_mod.term_stats(
        args.root, terms, aliases=aliases, match_mode=args.match_mode
    )
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
    if getattr(args, "classifications", None):
        result = registry_mod.validate_classification_file(
            args.classifications, args.classifications_schema
        )
        payload["validations"]["overlap_classifications"] = result
        problems += len(result["errors"])
    if not args.tasks and not args.kus and not getattr(args, "classifications", None):
        print("error: provide --tasks and/or --kus and/or --classifications", file=sys.stderr)
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
            "overlap_classification_counts": result["overlap_classification_counts"],
            "unaccounted_count": result["unaccounted_count"],
            "needs_review_count": result["needs_review_count"],
        }
    )
    return 0 if result["valid"] else 1


def cmd_audit_output(args) -> int:
    validation = validate_roots(args.source_root, args.output_root)
    if not validation.ok:
        _emit_summary({"error": "root validation failed", "problems": validation.problems})
        return 1
    try:
        result = omission_mod.audit_output(
            args.source_root,
            args.output_root,
            args.ku_batch,
            accepted_manifest_path=args.accepted_manifest,
            ku_schema_path=args.ku_schema,
        )
    except omission_mod.AuditError as exc:
        _emit_summary({"error": str(exc)})
        return 1
    payload = {"command": "audit-output", "result": result}
    report_path = getattr(args, "report", None)
    if report_path:
        try:
            dest = ensure_dest_safe(report_path, [Path(args.source_root), Path(args.output_root)])
        except PathSafetyError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        write_json_report(dest, "audit-output", payload, args=vars(args) | {"report": str(dest)}, repo_root=REPO_ROOT)
    _emit_summary(
        {
            "valid": result["valid"],
            "checks_run": result["checks_run"],
            "findings_total": result["stats"].get("findings_total", 0),
            "findings_by_severity": result["stats"].get("findings_by_severity", {}),
            "kus_total": result["stats"].get("kus_total", 0),
            "categories": sorted({f["category"] for f in result["findings"]}),
        }
    )
    return 0 if result["valid"] else 1


def cmd_extract_kus(args) -> int:
    root = Path(args.root)
    if not root.is_dir():
        print(f"error: source root is not a directory: {root}", file=sys.stderr)
        return 1
    # the batch destination must never live inside the read-only source root
    try:
        out_dest = ensure_dest_safe(args.out, [root])
    except PathSafetyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    try:
        result = kuextract_mod.extract_scope(
            root,
            args.scope,
            args.vault_id,
            args.manifest,
            out_dest,
            kus_schema=args.kus_schema,
            unclosed_finding=args.unclosed_fence_finding,
        )
    except kuextract_mod.ExtractionError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    payload = {"command": "extract-kus", "result": result}
    report_path = getattr(args, "report", None)
    if report_path:
        try:
            dest = ensure_dest_safe(report_path, [root])
        except PathSafetyError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        write_json_report(dest, "extract-kus", payload, args=vars(args) | {"report": str(dest)}, repo_root=REPO_ROOT)
    _emit_summary(
        {
            "ok": result["ok"],
            "vault_id": result["vault_id"],
            "scope": result["scope"],
            "denominators": result["denominators"],
            "records_written": result["records_written"],
            "units_by_type": result["units_by_type"],
            "batch_path": result["batch_path"],
            "batch_valid": result["batch_validation"]["valid"],
        }
    )
    return 0 if result["ok"] else 1


def cmd_ku_fidelity(args) -> int:
    root = Path(args.vault_root)
    if not root.is_dir():
        print(f"error: vault root is not a directory: {root}", file=sys.stderr)
        return 1
    cross_paths: list[str] | None = None
    if args.cross_check_glob:
        import glob as _glob

        cross_paths = sorted(p for p in _glob.glob(args.cross_check_glob) if Path(p).is_file())
    try:
        result = kufidelity_mod.check_batches(
            args.batches,
            args.vault_id,
            root,
            args.manifest,
            kus_schema=args.kus_schema,
            cross_check_paths=cross_paths,
            allow_processed=args.allow_processed,
        )
    except kufidelity_mod.FidelityError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    payload = {"command": "ku-fidelity", "result": result}
    report_path = getattr(args, "report", None)
    if report_path:
        try:
            dest = ensure_dest_safe(report_path, [root])
        except PathSafetyError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        write_json_report(dest, "ku-fidelity", payload, args=vars(args) | {"report": str(dest)}, repo_root=REPO_ROOT)
    _emit_summary(
        {
            "ok": result["ok"],
            "vault_id": result["vault_id"],
            "batches_checked": result["batches_checked"],
            "records_total": result["records_total"],
            "records_with_errors": result["records_with_errors"],
            "cross_check_ids_preloaded": result["cross_check_ids_preloaded"],
            "id_collisions": len(result["id_collisions"]),
            "per_batch": [
                {
                    "batch": Path(b["batch"]).name,
                    "records_total": b["records_total"],
                    "excerpt_byte_exact": b["excerpt_byte_exact"],
                    "ok": b["ok"],
                }
                for b in result["batches"]
            ],
        }
    )
    return 0 if result["ok"] else 1


def cmd_omission_pilot(args) -> int:
    explicit = getattr(args, "protected_root", None) or []
    if explicit:
        protected = [Path(p) for p in explicit]
    else:
        default = REPO_ROOT / "source-vaults"
        protected = [default] if default.is_dir() else []
    report = omission_mod.run_pilot(
        args.dest,
        protected_roots=protected,
        keep_mutations=args.keep_mutations,
        ku_schema_path=args.ku_schema,
    )
    payload = {"command": "omission-pilot", "result": report}
    report_path = getattr(args, "report", None)
    if report_path:
        try:
            dest = ensure_dest_safe(report_path, protected + [Path(args.dest)])
        except PathSafetyError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        write_json_report(dest, "omission-pilot", payload, args=vars(args) | {"report": str(dest)}, repo_root=REPO_ROOT)
    _emit_summary(
        {
            "verdict": report["verdict"],
            "summary": report["summary"],
            "fixture": {
                "ku_records": report["fixture"]["ku_records"],
                "output_files": len(report["fixture"]["output_files"]),
                "defects_declared": report["fixture"]["defects_declared"],
            },
            "source_immutability": report["source_immutability"]["sources_unchanged_during_pilot"],
        }
    )
    return 0 if report["verdict"]["pass"] else 1


def _default_protected_roots(explicit: list[str] | None) -> list[Path]:
    if explicit:
        return [Path(p) for p in explicit]
    default = REPO_ROOT / "source-vaults"
    return [default] if default.is_dir() else []


def cmd_overlap_candidates(args) -> int:
    protected = _default_protected_roots(args.protected_root)
    for dest_name in ("out", "report"):
        dest = getattr(args, dest_name, None)
        if not dest:
            continue
        try:
            ensure_dest_safe(dest, protected)
        except PathSafetyError as exc:
            print(f"error: {dest_name} destination: {exc}", file=sys.stderr)
            return 1
    try:
        result = overlap_mod.run_discovery(
            args.batches,
            args.terms,
            args.out,
            kus_schema=args.kus_schema,
            max_pairs_per_topic=args.max_pairs_per_topic,
        )
    except OverlapError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    payload = {"command": "overlap-candidates", "result": result}
    if args.report:
        try:
            ensure_dest_safe(args.report, protected)
        except PathSafetyError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        write_json_report(
            args.report,
            "overlap-candidates",
            payload,
            args=vars(args) | {"report": str(args.report)},
            repo_root=REPO_ROOT,
        )
    counts = result["counts"]
    _emit_summary(
        {
            "ok": True,
            "records_total": counts["records_total"],
            "topics_cross_vault": counts["topics_cross_vault"],
            "term_pairs": counts["term_pairs"],
            "confirmed_term_pairs": counts["confirmed_term_pairs"],
            "unconfirmed_only_term_pairs": counts["unconfirmed_only_term_pairs"],
            "exact_hash_pairs": counts["exact_hash_pairs"],
            "normalized_hash_pairs": counts["normalized_hash_pairs"],
            "truncated_topics": len(result["truncated_topics"]),
            "pairs_jsonl": result["pairs_jsonl"],
            "note": "candidates only; no overlap classification is assigned by this command",
        }
    )
    return 0


def cmd_kureg_apply_overlap(args) -> int:
    protected = _default_protected_roots(args.protected_root)
    try:
        result = kuregistry_mod.apply_overlap_classifications(
            args.db,
            args.classifications,
            schema_path=args.classifications_schema,
        )
    except RegistryError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    payload = {"command": "kureg-apply-overlap", "result": result}
    if args.report:
        try:
            ensure_dest_safe(args.report, protected)
        except PathSafetyError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        write_json_report(
            args.report,
            "kureg-apply-overlap",
            payload,
            args=vars(args) | {"report": str(args.report)},
            repo_root=REPO_ROOT,
        )
    _emit_summary(
        {
            "ok": True,
            "db_path": result["db_path"],
            "records_in_file": result["records_in_file"],
            "inserted": result["inserted"],
            "idempotent_skipped": result["idempotent_skipped"],
        }
    )
    return 0


def _parse_vault_manifests(manifest_args: list[str]) -> dict:
    """Parse VAULT=PATH manifest arguments into an ordered dict."""
    manifests: dict[str, str] = {}
    for arg in manifest_args:
        if "=" not in arg:
            raise DiscoveryError(
                f"manifest argument must be VAULT=PATH (got {arg!r})"
            )
        vault, path = arg.split("=", 1)
        if not vault.strip() or not path.strip():
            raise DiscoveryError(f"manifest argument must be VAULT=PATH (got {arg!r})")
        manifests[vault.strip()] = path.strip()
    return manifests


def cmd_discover_gaps(args) -> int:
    from .reporting import write_jsonl

    protected = _default_protected_roots(args.protected_root)
    for dest_name in ("out", "report"):
        dest = getattr(args, dest_name, None)
        if not dest:
            continue
        try:
            ensure_dest_safe(dest, protected)
        except PathSafetyError as exc:
            print(f"error: {dest_name} destination: {exc}", file=sys.stderr)
            return 1
    try:
        manifests = _parse_vault_manifests(args.manifests)
        result = discovery_mod.discover_candidates(
            args.batches,
            args.kus_schema,
            manifests,
            max_evidence_per_candidate=args.max_evidence,
        )
    except (DiscoveryError, OverlapError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if not result["ok"]:
        for err in result["errors"]:
            print(f"error: {err}", file=sys.stderr)
    write_jsonl(args.out, result["candidates"])
    report = result["report"]
    report["ok"] = result["ok"]
    report["candidates_path"] = str(args.out)
    if args.report:
        write_json_report(
            args.report,
            "discover-gaps",
            {"result": report},
            args=vars(args) | {"report": str(args.report)},
            repo_root=REPO_ROOT,
        )
    _emit_summary(
        {
            "ok": report["ok"],
            "candidates_emitted": report["denominators"]["candidates_emitted"],
            "by_kind": report["candidates_by_kind"],
            "by_status": report["candidates_by_status"],
            "coverage": report["coverage"],
        }
    )
    return 0 if result["ok"] else 1


def cmd_discovery_decide(args) -> int:
    from .reporting import write_jsonl
    from datetime import datetime, timezone

    protected = _default_protected_roots(args.protected_root)
    for dest_name in ("out", "report"):
        dest = getattr(args, dest_name, None)
        if not dest:
            continue
        try:
            ensure_dest_safe(dest, protected)
        except PathSafetyError as exc:
            print(f"error: {dest_name} destination: {exc}", file=sys.stderr)
            return 1
    decided_utc = args.decided_utc or datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        result = discovery_mod.apply_decisions(
            args.candidates,
            args.decisions,
            args.candidate_schema,
            decided_utc=decided_utc,
        )
    except (DiscoveryError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    for err in result["errors"]:
        print(f"error: {err}", file=sys.stderr)
    if not result["ok"]:
        return 1
    write_jsonl(args.out, result["records"])
    summary = {
        "ok": True,
        "records_written": len(result["records"]),
        "decisions_applied": sum(1 for r in result["records"] for h in r["decision_history"]),
        "decided_utc": decided_utc,
        "out": str(args.out),
    }
    if args.report:
        write_json_report(
            args.report,
            "discovery-decide",
            {"result": summary},
            args=vars(args) | {"report": str(args.report)},
            repo_root=REPO_ROOT,
        )
    _emit_summary(summary)
    return 0


def cmd_discovery_validate(args) -> int:
    try:
        result = discovery_mod.validate_candidates(
            args.candidates,
            args.candidate_schema,
            ku_batches=args.batches,
            kus_schema=args.kus_schema if args.batches else None,
        )
    except (DiscoveryError, OverlapError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    payload = {"command": "discovery-validate", "result": result}
    _write_report_safe(args, "discovery-validate", payload)
    _emit_summary(
        {
            "valid": result["valid"],
            "records_total": result["records_total"],
            "errors_total": result["errors_total"],
        }
    )
    return 0 if result["valid"] else 1


# ---------------------------------------------------------------------------
# FRAME-002: artifact lint, quality assessment, drift, gates, repair loop,
# prompt checking (CAP-018..CAP-021)


def cmd_lint_artifacts(args) -> int:
    path = Path(args.path)
    try:
        if path.is_dir():
            result = artifactlint_mod.lint_tree(
                path, skip_dirs=tuple(args.skip_dirs), check_links=not args.no_links
            )
        elif path.is_file():
            ctx = None if args.no_links else artifactlint_mod.build_link_context(path.parent)
            result = artifactlint_mod.lint_file(path, link_context=ctx)
        else:
            print(f"error: no such file or directory: {path}", file=sys.stderr)
            return 1
    except ArtifactLintError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    _write_report_safe(args, "lint-artifacts", {"result": result})
    if path.is_dir():
        summary = result["summary"]
        _emit_summary(
            {
                "files": summary["files"],
                "defects": summary["defects"],
                "errors": summary["errors"],
                "warnings": summary["warnings"],
                "infos": summary["infos"],
                "files_with_errors": summary["files_with_errors"],
            }
        )
        return 1 if summary["errors"] else 0
    _emit_summary(
        {
            "file": result["file"],
            "defects": result["defect_count"],
            "errors": result["error_count"],
            "warnings": result["warning_count"],
            "infos": result["info_count"],
        }
    )
    return 1 if result["error_count"] else 0


def _load_assessments(path: str) -> list[dict]:
    records = []
    with Path(path).open(encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise QualityError(f"{path}:{lineno} is not valid JSON: {exc}") from exc
    if not records:
        raise QualityError(f"no assessment records in {path}")
    return records


def cmd_assess_quality(args) -> int:
    from .reporting import write_jsonl

    try:
        provenance = notequality_mod.load_provenance(args.provenance) if args.provenance else None
        result = notequality_mod.assess_tree(
            args.root,
            provenance=provenance,
            ku_batches=args.ku_batches,
        )
    except (QualityError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.out:
        try:
            ensure_dest_safe(args.out, _default_protected_roots(None))
        except PathSafetyError as exc:
            print(f"error: out destination: {exc}", file=sys.stderr)
            return 1
        write_jsonl(args.out, result["notes"])
    _write_report_safe(args, "assess-quality", {"result": result})
    by_type: dict[str, int] = {}
    below_band = 0
    for note in result["notes"]:
        by_type[note["type"]] = by_type.get(note["type"], 0) + 1
        below_band += sum(1 for d in note["dimensions"].values() if d["band"] == "below_band")
    _emit_summary(
        {
            "notes_assessed": len(result["notes"]),
            "by_type": dict(sorted(by_type.items())),
            "notes_with_lint_errors": sum(1 for n in result["notes"] if n["lint_error_count"]),
            "dimensions_below_band": below_band,
        }
    )
    return 0


def cmd_quality_drift(args) -> int:
    try:
        assessments = _load_assessments(args.assessments)
        drift = notequality_mod.detect_drift(assessments, rel_drop=args.rel_drop, abs_drop=args.abs_drop)
    except (QualityError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    _write_report_safe(args, "quality-drift", {"result": drift})
    _emit_summary(
        {
            "verdict": drift["verdict"],
            "drifted_types": [e["type"] for e in drift["drifted_types"]],
            "clean_types": [e["type"] for e in drift["clean_types"]],
        }
    )
    return 0


def cmd_quality_gate(args) -> int:
    try:
        assessments = _load_assessments(args.assessments)
        expected = None
        if args.expected:
            expected = [
                ln.strip()
                for ln in Path(args.expected).read_text(encoding="utf-8").splitlines()
                if ln.strip() and not ln.strip().startswith("#")
            ]
        drift = None
        if args.drift_report:
            drift = json.loads(Path(args.drift_report).read_text(encoding="utf-8"))
            drift = drift.get("result", drift)
        waivers = {}
        for w in args.waivers or []:
            if "=" not in w:
                print(f"error: waiver must be 'key=reason', got: {w}", file=sys.stderr)
                return 1
            key, reason = w.split("=", 1)
            waivers[key.strip()] = reason.strip()
        gate = notequality_mod.batch_gate(
            assessments, expected_notes=expected, drift_report=drift, waivers=waivers
        )
    except (QualityError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    _write_report_safe(args, "quality-gate", {"result": gate})
    _emit_summary(
        {
            "verdict": gate["verdict"],
            "notes_assessed": gate["notes_assessed"],
            "failures": len(gate["failures"]),
        }
    )
    return 0 if gate["passed"] else 1


def _find_task(tasks: list[dict], repair_id: str) -> dict:
    for task in tasks:
        if task["repair_id"] == repair_id:
            return task
    raise RepairError(f"repair task not found: {repair_id}")


def cmd_repair_create(args) -> int:
    from .reporting import write_jsonl

    try:
        lint = json.loads(Path(args.lint_report).read_text(encoding="utf-8"))
        lint = lint.get("result", lint)
        existing = repair_mod.load_tasks(args.store)
        new = repair_mod.create_repair_tasks([lint], max_attempts=args.max_attempts)
        merged, added = repair_mod.merge_tasks(existing, new)
        repair_mod.save_tasks(args.store, merged)
    except (RepairError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    status = repair_mod.task_status(merged)
    _write_report_safe(args, "repair-create", {"result": {**status, "added": added, "store": args.store}})
    _emit_summary({"tasks_total": status["total"], "added": len(added), "by_status": status["by_status"]})
    return 0


def cmd_repair_record(args) -> int:
    from .reporting import write_jsonl

    try:
        tasks = repair_mod.load_tasks(args.store)
        task = _find_task(tasks, args.id)
        diff = Path(args.diff_file).read_text(encoding="utf-8") if args.diff_file else None
        updated = repair_mod.record_attempt(task, args.outcome, diff=diff, note=args.note)
        tasks = [updated if t["repair_id"] == args.id else t for t in tasks]
        repair_mod.save_tasks(args.store, tasks)
    except (RepairError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    _write_report_safe(args, "repair-record", {"result": updated})
    _emit_summary({"repair_id": updated["repair_id"], "status": updated["status"], "attempts": len(updated["attempts"])})
    return 0


def cmd_repair_verify(args) -> int:
    try:
        tasks = repair_mod.load_tasks(args.store)
        task = _find_task(tasks, args.id)
        current = Path(args.note_file).read_text(encoding="utf-8")
        original = Path(args.original_file).read_text(encoding="utf-8") if args.original_file else None
        verification = repair_mod.verify_repair(task, current, original_text=original)
        if verification["verified"]:
            updated = repair_mod.apply_verification(task, verification)
            tasks = [updated if t["repair_id"] == args.id else t for t in tasks]
            repair_mod.save_tasks(args.store, tasks)
    except (RepairError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    _write_report_safe(args, "repair-verify", {"result": verification})
    _emit_summary(
        {
            "repair_id": verification["repair_id"],
            "verified": verification["verified"],
            "reason": verification["reason"],
        }
    )
    return 0 if verification["verified"] else 1


def cmd_repair_list(args) -> int:
    try:
        tasks = repair_mod.load_tasks(args.store)
    except (RepairError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.status:
        tasks = [t for t in tasks if t["status"] == args.status]
    status = repair_mod.task_status(tasks)
    _write_report_safe(args, "repair-list", {"result": status})
    _emit_summary(status)
    return 0


def cmd_repair_prompt(args) -> int:
    try:
        tasks = repair_mod.load_tasks(args.store)
        task = _find_task(tasks, args.id)
        spec = promptspec_mod.build_repair_prompt(task, note_path=task["file"])
        ensure_dest_safe(args.out, _default_protected_roots(None))
        Path(args.out).write_text(json.dumps(spec, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    except (RepairError, OSError, PathSafetyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    _write_report_safe(args, "repair-prompt", {"result": {"repair_id": args.id, "prompt_path": args.out}})
    _emit_summary({"repair_id": args.id, "prompt_path": args.out})
    return 0


def cmd_check_prompt(args) -> int:
    try:
        spec = promptspec_mod.load_prompt_spec(args.spec)
        result = promptspec_mod.check_prompt(
            spec,
            ku_batches=args.ku_batches,
            context_budget_words=args.context_budget,
            max_requirements=args.max_requirements,
        )
    except (PromptSpecError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    _write_report_safe(args, "check-prompt", {"result": result})
    _emit_summary(
        {
            "ok": result["ok"],
            "failures": result["failures"],
            "estimated_context_words": result["estimated_context_words"],
            "context_budget_words": result["context_budget_words"],
        }
    )
    return 0 if result["ok"] else 1


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
    "audit-output": cmd_audit_output,
    "extract-kus": cmd_extract_kus,
    "ku-fidelity": cmd_ku_fidelity,
    "omission-pilot": cmd_omission_pilot,
    "overlap-candidates": cmd_overlap_candidates,
    "kureg-apply-overlap": cmd_kureg_apply_overlap,
    "discover-gaps": cmd_discover_gaps,
    "discovery-decide": cmd_discovery_decide,
    "discovery-validate": cmd_discovery_validate,
    "lint-artifacts": cmd_lint_artifacts,
    "assess-quality": cmd_assess_quality,
    "quality-drift": cmd_quality_drift,
    "quality-gate": cmd_quality_gate,
    "repair-create": cmd_repair_create,
    "repair-record": cmd_repair_record,
    "repair-verify": cmd_repair_verify,
    "repair-list": cmd_repair_list,
    "repair-prompt": cmd_repair_prompt,
    "check-prompt": cmd_check_prompt,
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
    except (
        PathSafetyError,
        NotADirectoryError,
        ValueError,
        RegistryError,
        AuditError,
        ArtifactLintError,
        QualityError,
        RepairError,
        PromptSpecError,
        DiscoveryError,
        FidelityError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
