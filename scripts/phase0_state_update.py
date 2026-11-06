"""Update task-queue records for the Phase 0 session (REBASE-000..DISC-001).

Marks REBASE-000, AUDIT-011, FRAME-001, DISC-001 completed with actual
tests_run evidence from this session's battery. Appends nothing new; updates
the four records in place (the established EXT-series state pattern).
"""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
QUEUE = REPO / "state" / "task-queue.jsonl"

UPDATES = {
    "REBASE-000": {
        "status": "completed",
        "tests_run": [
            "vu selftest (exit 0)",
            "python3 -m pytest tests -q -> 415/415 (reports/rebaseline/rebase000-pytest.json)",
            "vu capabilities --verify -> 16 implemented-and-tested + 1 planned (reports/rebaseline/rebase000-capabilities.json)",
            "vu verify-manifest both vaults -> exit 0, sources unchanged (reports/rebaseline/rebase000-immutable-*.json)",
            "vu kureg-validate -> valid, 1728 KUs / 164 classifications / 514 participating (reports/rebaseline/rebase000-kureg-validate.json)",
            "vu validate-registry --tasks -> 21/21 valid (reports/rebaseline/rebase000-taskqueue-validate.json)",
            "vu validate-registry --classifications x7 -> all valid",
            "scripts/rebase000_reports.py -> phase-zero-baseline.json 8/8 claims CONFIRMED, 0 discrepancies + artifact-disposition.json",
        ],
        "completion_notes": (
            "Machine-backed baseline established 2026-10-27: all documented claims "
            "(415/415 tests, 16+1 capabilities, 1728 KUs, 164 classifications, 514 "
            "participating, 31/609 files, sources byte-unchanged, queue 21/21 valid, "
            "F-0009 recorded) verified against actual command evidence - 8/8 CONFIRMED, "
            "zero discrepancies. Artifact disposition list assigns reuse/recompute/"
            "migrate with rationale and revalidation requirements for every artifact "
            "class. Child tasks validated against the existing schema."
        ),
    },
    "AUDIT-011": {
        "status": "completed",
        "tests_run": [
            "full source read of all 17 src/vault_unification modules + CLI + capability inventory cross-check",
            "scripts/audit011_reports.py -> framework-audit.json (17 capabilities mapped to code/tests/limitations) + known-limitations.json (13 limitations: 6 framework defects, 5 documented limitations, 1 missing capability L-12, 1 process debt L-13)",
        ],
        "completion_notes": (
            "Audit enumerated 13 limitations with evidence pointers (file:line), "
            "separated source defects (F-0001/2/3/7/8/9) from framework defects "
            "(L-01/02/03/04/06/07/08) and documentation discrepancies (none found: "
            "8/8 claims confirmed). Repair priorities ordered: L-08 atomic writes, "
            "L-02/L-03 linkcheck, L-01 phrase search, L-07 word-boundary stats, "
            "L-04 inline-math recount, L-06 strict block ids, L-13 locator "
            "migration; L-12 discovery scheduled as DISC-001. Critical constraint "
            "discovered: mdextract/kuextract segmentation must stay byte-stable for "
            "committed-batch regeneration (verified after FRAME-001: 57/57 records "
            "byte-identical on re-extraction of a committed file)."
        ),
    },
    "FRAME-001": {
        "status": "completed",
        "tests_run": [
            "full suite after refactor: python3 -m pytest tests -q -> 486/486 (reports/rebaseline/frame001-disc001-final-pytest.json)",
            "new tests: 6 atomic-write (test_pathsafety), 4 inline-math L-04 (test_mdextract), 14 phrase+word-boundary (test_search), 7 folder-link/cache/strict-block (test_linkcheck), 15 locator (test_locators)",
            "re-extraction byte-identity: master-ai 07 - Initialization Schemes.md -> 57/57 records byte-identical vs committed batch 010 (reports/rebaseline/rebase000-reextract-07.json)",
            "vu check-links Master AI (FIRST EVER): 333 files / 5221 links / 338 broken / 29 ambiguous in 2.16s (reports/rebaseline/frame001-master-ai-linkcheck.json)",
            "vu check-links AI Course re-run: 121 broken + 54 folder_link = exactly F-0003's 175 (reports/rebaseline/frame001-ai-course-linkcheck.json); F-0010/F-0011 appended to findings",
            "vu capabilities --verify after changes: 17 implemented-and-tested + 1 planned",
        ],
        "completion_notes": (
            "Framework hardened per audit priorities, all fixes additive or "
            "report-level (committed-batch regeneration byte-stable, verified): "
            "L-08 atomic writes (temp+fsync+os.replace) routed through "
            "reporting/inventory/kuextract + symlink-leaf replacement (also "
            "mitigates L-09); L-02 folder-aware linkcheck (folder links resolve as "
            "folder_link evidence, files take precedence); L-03 per-run structure "
            "caches (O(files) parses; Master AI full check 2.16s); L-01 phrase "
            "search mode with (line_start,line_end) span locators; L-07 term-stats "
            "--match-mode word-boundary sharing ONE boundary_pattern authority "
            "with CAP-013; L-04 inline-math recount from the authoritative state "
            "machine (unclosed-fence files fixed); L-06 strict end-of-line block "
            "ids; L-13 X2 machine locator migrated to vault_unification.locators. "
            "Accepted-documented: L-05 (setext; deferred with evidence), L-09, "
            "L-10, L-11. Framework version 0.6.0. Backward compatible: all "
            "existing commands, modes and defaults unchanged."
        ),
    },
    "DISC-001": {
        "status": "completed",
        "tests_run": [
            "tests/test_discovery.py: 25/25 - all mandated fixture scenarios (unexplained prerequisite, explained-elsewhere no-false-gap, fragmented derivation, rare essential no-frequency-threshold, copied passages collapsed, homonyms flagged not merged, contradictions surfaced, coverage gate incl. confirm_gap refusal, merge/split history preservation, section-vs-standalone, determinism, precision/recall 1.0 vs labels, negative paths)",
            "tests/test_locators.py: 15/15 (X2 unique-occurrence locator)",
            "full suite green with discovery module: 486/486",
            "REAL corpus run: vu discover-gaps over all 11 committed batches (1728 KUs, 43768 terms analyzed) -> 6340 schema-valid candidates (4116 unexplained_prerequisite, 1111 rare_essential, 294 fragmented_derivation, 819 concept_sighting/already_covered); all gap statuses provisional_candidate (31/609 coverage, gate active); report reports/discovery/disc001-real-corpus-run.json",
            "vu discovery-validate on the real candidate file with all 11 batches cross-checked: valid, 6340/6340, 0 errors (reports/discovery/disc001-validate.json)",
        ],
        "completion_notes": (
            "Emergent concept discovery implemented as first-class capability "
            "CAP-017: src/vault_unification/discovery.py + "
            "schemas/concept-candidate.schema.json + CLI discover-gaps / "
            "discovery-decide / discovery-validate. Deterministic evidence "
            "collection (n-gram mining, definition/assumption/derivation "
            "relationship patterns, copied-passage collapse, homonym "
            "co-occurrence clustering, numeric contradiction pairs, coverage "
            "gate); semantic review applied via decision workflow with "
            "append-only history and merge/split provenance. Known bounds "
            "(documented in CAP-017 limitations): lexical definition detection "
            "misses paraphrases; single common words surface as low-value "
            "candidates (e.g. 'business', 'decreases' in the real run) - "
            "DISC-002 must add corpus-frequency-based RANKING (never emission "
            "gating) and semantic triage. Candidates persisted at "
            "state/concept-candidates/001-disc001-partial-corpus.jsonl; "
            "registry loading deferred to DISC-002 by design."
        ),
    },
}


def main() -> int:
    lines = QUEUE.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    updated = 0
    for line in lines:
        if not line.strip():
            continue
        record = json.loads(line)
        task_id = record.get("task_id")
        if task_id in UPDATES:
            patch = UPDATES[task_id]
            record["status"] = patch["status"]
            record["tests_run"] = patch["tests_run"]
            record["completion_notes"] = patch["completion_notes"]
            record["completed_utc"] = "2026-10-27"
            updated += 1
        out.append(json.dumps(record, ensure_ascii=False))
    QUEUE.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"updated {updated} task records")
    # validate the queue still passes
    import os
    import subprocess
    import sys

    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO / "src")
    r = subprocess.run(
        [
            sys.executable,
            "-m",
            "vault_unification",
            "validate-registry",
            "--tasks",
            "state/task-queue.jsonl",
            "--report",
            "reports/rebaseline/post-update-taskqueue-validate.json",
        ],
        cwd=REPO,
        env=env,
        capture_output=True,
        text=True,
    )
    report = json.loads((REPO / "reports/rebaseline/post-update-taskqueue-validate.json").read_text())
    print("queue valid:", report["valid"], "| problems:", report["problems_total"])
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    import os
    raise SystemExit(main())
