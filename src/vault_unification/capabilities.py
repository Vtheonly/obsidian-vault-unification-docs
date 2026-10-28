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
        "name": "obsidian link/embed/anchor integrity (folder-link aware, cached)",
        "module": "vault_unification.linkcheck",
        "command": "vu check-links",
        "status_declared": "implemented-and-tested",
        "tests": ["tests/test_linkcheck.py"],
        "limitations": [
            "heading anchor matching is normalized text equality; exotic anchors may be flagged",
            "percent-encoded markdown links are matched literally (deferred pending corpus evidence)",
            "links inside code fences are excluded by design",
            "FRAME-001: folders are indexed; folder-target links resolve as folder_link evidence (never broken); files still take precedence over same-named folders",
            "FRAME-001: per-run caches parse each file at most once (O(files) parses)",
            "FRAME-001: block ids checked strictly (^id at end-of-line), rejecting mid-prose caret false positives",
        ],
    },
    {
        "id": "CAP-005",
        "name": "exact/case-insensitive/normalized/phrase search and term stats",
        "module": "vault_unification.search",
        "command": "vu search / vu term-stats",
        "status_declared": "implemented-and-tested",
        "tests": ["tests/test_search.py"],
        "limitations": [
            "normalized mode collapses whitespace per line; use the phrase mode (FRAME-001, L-01) for whole-file normalized matching across line breaks with (line_start, line_end) span locators",
            "binary detection is heuristic (null-byte sniff)",
            "term-stats substring mode (default) counts 'ridge' inside 'bridge'; select --match-mode word-boundary for CAP-013-consistent semantics (FRAME-001, L-07; shared boundary_pattern authority)",
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
        "id": "CAP-016",
        "name": "deterministic KU extraction from source notes",
        "module": "vault_unification.kuextract",
        "command": "vu extract-kus",
        "status_declared": "implemented-and-tested",
        "tests": ["tests/test_kuextract.py", "tests/test_cli.py"],
        "limitations": [
            "structural segmentation only: unit types describe Markdown block syntax (prose/list/table/code_block/math_block/callout/quote/frontmatter/empty_section), never meaning",
            "assigns no dispositions (every unit is 'Unaccounted'), no overlap_type, no concept_ids, no destinations; semantic classification is later evidence-based work",
            "extraction coverage is the accounting baseline, NOT proof of semantic preservation",
            "excerpts reconstruct lines with splitlines: CR characters from CRLF files are normalized inside excerpts (source bytes untouched)",
            "construct detection delegates to mdextract (CAP-003) and inherits its limitations: ATX headings only (setext underlines may be classified as excluded horizontal rules), delimiter-based math without LaTeX validation",
            "an unclosed fence/math block absorbs all remaining lines into one unit (content preserved verbatim, parse warning recorded, finding linkable via --unclosed-fence-finding)",
            "a blank line splits a list into separate units (no loose-list merging) - granularity, not loss",
            "markdown files only; non-markdown files get an explicit excluded_non_markdown outcome",
        ],
    },
    {
        "id": "CAP-013",
        "name": "duplicate/near-duplicate candidate discovery",
        "module": "vault_unification.overlap",
        "command": "vu overlap-candidates / vu kureg-apply-overlap",
        "status_declared": "implemented-and-tested",
        "tests": ["tests/test_overlap.py", "tests/test_cli.py"],
        "limitations": [
            "candidate generation only: no overlap_type is assigned or implied by the tool; every classification requires excerpt review",
            "word-boundary matching does not stem or inflect: 'ridges' does not match 'ridge' unless declared as an alias",
            "mermaid_node_suspect flags matches inside mermaid code blocks (node labels AND edge references like 'L1 --> L2') plus the immediate-'[' heuristic; other diagram syntaxes are not detected",
            "term coverage is exactly the provided terms/aliases map; topics outside it are invisible to a given run",
            "hash duplicates compare whole KU excerpts only, not fragments inside units",
            "pair cross-products are capped per topic (max_pairs_per_topic); excess topics are flagged and per-KU evidence stays complete",
            "classifications are pair-level overlay records (ADR-0009); per-KU overlap_type columns stay NULL because one unit can join multiple differently-typed pairs",
        ],
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
    {
        "id": "CAP-017",
        "name": "emergent concept discovery and knowledge-gap detection (DISC-001)",
        "module": "vault_unification.discovery",
        "command": "vu discover-gaps / vu discovery-decide / vu discovery-validate",
        "status_declared": "implemented-and-tested",
        "tests": ["tests/test_discovery.py", "tests/test_locators.py", "tests/test_cli.py"],
        "limitations": [
            "deterministic evidence collection and ranking ONLY: recurrence is a signal, never proof; semantic identity/boundaries/adequacy are review decisions applied via discovery-decide",
            "gap candidates are provisional_candidate until reviewed; confirmed_gap requires BOTH a reviewed decision AND complete corpus coverage (hard gate, enforced in apply_decisions and discovery-validate)",
            "term mining is statistical n-gram extraction with definition/assumption/derivation pattern classification; it is heading-agnostic (no fixed topic whitelist) but pattern-based relationship detection can miss paraphrases",
            "definition detection is lexical (definition patterns + heading declarations): a paraphrased definition without pattern markers is classified as usage; review can apply the cover action",
            "contradiction suspicion is a numeric-adjacent heuristic near definition contexts; surfaced with pairs, never resolved",
            "homonym clustering is co-occurrence-signature based; disjoint signatures flag the candidate but review decides whether senses truly differ",
            "registry loading of accepted candidates is deferred to DISC-002 (candidates persist as schema-validated JSONL, consistent with the classification overlay pattern before kureg-apply-overlap exists for candidates)",
        ],
    },
    {
        "id": "CAP-018",
        "name": "artifact integrity validation (fences, math, tables, headings, lists, links, mermaid, code, truncation, placeholders)",
        "module": "vault_unification.artifactlint",
        "command": "vu lint-artifacts",
        "status_declared": "implemented-and-tested",
        "tests": ["tests/test_artifactlint.py", "tests/test_cli.py"],
        "limitations": [
            "syntax/reference validation ONLY: a passing lint is necessary, never sufficient — semantic correctness requires review",
            "mermaid validation is a structural line-grammar heuristic for the common diagram kinds (flowchart, sequence, state, class, pie, gantt), NOT a full mermaid AST; unknown kinds fall back to block-balance checks",
            "python code blocks are AST-parsed (never executed); other languages are label-level checks only",
            "inline-math dollar parity is a warning-level heuristic (a lone $ in prose triggers it deliberately)",
            "percent-encoded markdown links remain matched literally (L-06 deferral inherited from linkcheck)",
            "rendering validation (actual render + visual inspection) is NOT implemented — this is syntax/reference validation; the distinction is recorded in every report",
        ],
    },
    {
        "id": "CAP-019",
        "name": "note quality assessment, quality-drift detection, and batch quality gates",
        "module": "vault_unification.notequality",
        "command": "vu assess-quality / vu quality-drift / vu quality-gate",
        "status_declared": "implemented-and-tested",
        "tests": ["tests/test_notequality.py", "tests/test_cli.py"],
        "limitations": [
            "deterministic measurement only (counts, patterns, coverage ratios): there is deliberately NO subjective AI-judge score; semantic adequacy is a review decision the tool prepares evidence for",
            "source_coverage requires a provenance mapping (note -> ku_ids); without one the dimension is reported 'unmeasured', never guessed",
            "drift detection compares first-third vs last-third means per note type; it detects systematic decline with evidence, it does not prove causation",
            "note types are inferred from frontmatter 'type' with a 'generic' fallback; wrong frontmatter yields the wrong standard (garbage in, garbage out)",
            "depth bands are intentionally permissive; the tool targets RELATIVE drift between comparable notes rather than absolute length policing",
        ],
    },
    {
        "id": "CAP-020",
        "name": "evidence-based targeted repair loop (bounded retries, verification, escalation)",
        "module": "vault_unification.repair",
        "command": "vu repair-create / vu repair-record / vu repair-verify / vu repair-list / vu repair-prompt",
        "status_declared": "implemented-and-tested",
        "tests": ["tests/test_repair.py", "tests/test_cli.py"],
        "limitations": [
            "repairs are performed by an agent (or human) against a repair prompt; the toolkit creates tasks, records attempts, verifies outcomes and enforces bounds — it does not edit files itself",
            "verification re-runs the originating check + whole-file lint + (with the original file) diff-scope discipline; semantic correctness of the fix remains a review decision",
            "repair-scope discipline uses an 8-line locality window around the defect line; a justified wider edit is flagged, not blocked (review decides)",
            "a defect that returns after a verified fix re-opens its task with a recorded regression attempt",
        ],
    },
    {
        "id": "CAP-021",
        "name": "generation-prompt specification and validation (testable criteria, boundedness, evidence resolvability)",
        "module": "vault_unification.promptspec",
        "command": "vu check-prompt / vu repair-prompt",
        "status_declared": "implemented-and-tested",
        "tests": ["tests/test_promptspec.py", "tests/test_cli.py"],
        "limitations": [
            "prompt checks are deterministic structural/quality checks (presence, resolvability, testability, budget); they cannot judge whether the instructions are pedagogically ideal",
            "vague-language detection is a fixed term list; it catches common unoperationalized criteria, not all of them",
            "context estimation counts words of criteria/requirements/constraints/excerpts — a proxy, not an actual token count",
            "ku_id resolvability requires the caller to pass the KU batches; without them the check is skipped and reported as such",
        ],
    },
    {
        "id": "CAP-022",
        "name": "KU batch fidelity verification against immutable sources (excerpt byte-exactness, hashes, id uniqueness, manifest agreement)",
        "module": "vault_unification.kufidelity",
        "command": "vu ku-fidelity",
        "status_declared": "implemented-and-tested",
        "tests": ["tests/test_kufidelity.py", "tests/test_cli.py"],
        "limitations": [
            "byte-exact excerpt verification proves mechanical fidelity to source lines, not semantic completeness or correctness of the segmentation itself",
            "heading-boundary authority is mdextract.extract_structure_text; setext headings remain unsupported (L-05)",
            "cross-check batches are only preload-checked for id collisions, not fidelity",
            "structural purity check assumes fresh batches by default; post-disposition verification requires --allow-processed",
        ],
    },
    {
        "id": "CAP-023",
        "name": "Compact candidate index projection for corpus-scale discovery outputs (drops quote payloads, keeps ku_id joins and decision state)",
        "module": "vault_unification.discovery",
        "command": "vu discovery-index",
        "status_declared": "implemented-and-tested",
        "tests": ["tests/test_discovery.py"],
        "limitations": [
            "the index is a projection, not a replacement: evidence quotes are recoverable only by joining ku_ids against the committed KU batches or regenerating the full candidates file with the recorded discovery command",
            "ku_ids and source files are capped at --max-ku-ids (default 12) per record; counts stay complete in the full file",
            "index records carry no JSON Schema of their own; they inherit validity from the source candidates file",
        ],
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
