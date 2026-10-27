"""AUDIT-011: framework capability audit + known-limitations report.

Assembles reports/rebaseline/framework-audit.json and
reports/rebaseline/known-limitations.json from the capability inventory
verified during the REBASE-000 battery plus the source-level audit performed
by reading every module in src/vault_unification/ (2026-10-27 session).

Evidence pointers cite module file + function for every claim so a reviewer
can verify each row against the actual code.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RB = REPO / "reports" / "rebaseline"


def main() -> int:
    caps = json.loads((RB / "rebase000-capabilities.json").read_text(encoding="utf-8"))

    capability_map = []
    for cap in caps["capabilities"]:
        capability_map.append(
            {
                "id": cap["id"],
                "name": cap["name"],
                "module": cap["module"],
                "command": cap["command"],
                "status_verified": cap["status_declared"],
                "verified_by": "vu capabilities --verify (REBASE-000 battery, exit 0; referenced tests 392/392 passed)",
                "audit_note": {
                    "CAP-000": "selftest.py checks mandatory deps; no defects found",
                    "CAP-001": "solid symlink + overlap checks; GAPS: no atomic-write helper, no TOCTOU re-check after resolve, no concurrent-run lock (see limitations L-08..L-10)",
                    "CAP-002": "content-based SHA-256 manifests; mtime informational only; symlinks recorded explicitly; no defects found",
                    "CAP-003": "single construct-detection authority shared with kuextract; LIMITATION: inline-math recount uses a second naive fence-scan that disagrees with the authoritative state machine in unclosed-fence files (see L-04); setext headings unsupported (L-05)",
                    "CAP-004": "GAPS: folders are not indexed -> intentional folder links reported 'broken' (F-0003 class, see L-02); _heading_exists re-parses the target file per anchor check -> O(links x re-parse), Master AI (333 files) never link-checked (L-03); percent-encoded URLs matched literally (L-06)",
                    "CAP-005": "GAP: all matching is per-line; no multi-line phrase search (L-01); term_stats is substring-count only, no word-boundary mode -> inconsistent with overlap.py semantics (L-07)",
                    "CAP-006": "per-record schema validation + cross-checks; no defects found",
                    "CAP-007": "writes reports non-atomically (L-08); timestamps make reports non-byte-reproducible by design (documented; determinism checks must exclude report_meta)",
                    "CAP-008": "pytest orchestration with JSON reports; no defects found",
                    "CAP-009": "inventory tied to real tests via --verify; must be updated in lockstep with FRAME-001/DISC-001 additions",
                    "CAP-010": "stable exit codes (0 ok / 1 validation failure / 2 usage error) verified across commands during battery",
                    "CAP-011": "derived SQLite registry over canonical JSONL; kureg-load documented atomic; registry rebuild deterministic (init --force + load + apply); no defects found",
                    "CAP-015": "word/heading/token statistics; inherits search binary-detection heuristic (L-11)",
                    "CAP-012": "omission pilot 12/12 detection + localization; reusable auditor; no defects found",
                    "CAP-016": "line-accounting invariant guarantees zero silent line loss; unclosed constructs preserved verbatim with warnings (F-0002 handling verified); excerpts normalize CR (documented); SEGMENTATION MUST STAY BYTE-STABLE for committed-batch regeneration (constraint on FRAME-001)",
                    "CAP-013": "word-boundary term/alias evidence with mermaid + code-block flags (F-0006 regression cases baked in); NO concept-gap discovery exists (this is the DISC-001 target)",
                    "CAP-014": "planned; NOT implemented; no code, no tests - honest status",
                }.get(cap["id"], ""),
            }
        )

    limitations = [
        {
            "id": "L-01",
            "severity": "medium",
            "category": "framework-defect",
            "component": "search.py",
            "summary": "No multi-line phrase search: all modes match per line; normalized mode normalizes per line",
            "evidence": "src/vault_unification/search.py:101-117 (per-line loop); docs/TOOLING_FRAMEWORK.md documented limitation",
            "fix": "FRAME-001: add phrase mode over whole-text normalized matching with (start_line,end_line) span locators",
            "status": "fix-scheduled-FRAME-001",
        },
        {
            "id": "L-02",
            "severity": "high",
            "category": "framework-defect",
            "component": "linkcheck.py",
            "summary": "Folders are not indexed; intentional Obsidian folder links are classified 'broken' (false-positive class behind F-0003's 175 broken links)",
            "evidence": "src/vault_unification/linkcheck.py:30-42 (build_vault_index indexes files only), :78-88 (broken resolution)",
            "fix": "FRAME-001: index directories, resolve folder targets as 'folder' kind, keep genuinely-missing targets broken",
            "status": "fix-scheduled-FRAME-001",
        },
        {
            "id": "L-03",
            "severity": "medium",
            "category": "framework-defect",
            "component": "linkcheck.py",
            "summary": "Anchor checks re-parse the target file on every link (_heading_exists -> extract_structure per check); O(links x file parses) makes vault-wide checks needlessly slow; Master AI has never been link-checked",
            "evidence": "src/vault_unification/linkcheck.py:91-97 (_heading_exists), :100-105 (_block_exists re-reads file)",
            "fix": "FRAME-001: per-run structure/text cache keyed by resolved path",
            "status": "fix-scheduled-FRAME-001",
        },
        {
            "id": "L-04",
            "severity": "low",
            "category": "framework-defect",
            "component": "mdextract.py",
            "summary": "inline_math_count recount uses a second, naive fence-skip that disagrees with the authoritative fence/math state machine in unclosed-fence files (the 14 F-0002 files) and does not skip math-block lines",
            "evidence": "src/vault_unification/mdextract.py:263-279 (naive visible_lines re-derivation) vs :142-209 (authoritative state machine)",
            "fix": "FRAME-001: compute inline math from the authoritative machine's line classification (safe: inline_math_count is NOT used by kuextract segmentation, so committed batches regenerate identically)",
            "status": "fix-scheduled-FRAME-001",
        },
        {
            "id": "L-05",
            "severity": "low",
            "category": "framework-limitation",
            "component": "mdextract.py",
            "summary": "Setext headings (===/--- underlines) are not detected; kuextract classifies the underline as excluded horizontal rule and setext text as prose",
            "evidence": "src/vault_unification/mdextract.py:28 (_HEADING_RE is ATX-only); kuextract.py docstring documents the limitation",
            "fix": "deferred: changing heading detection would shift committed batch segmentation; re-assess at REGEN-001 with a corpus scan for setext usage first",
            "status": "accepted-documented (defer with evidence)",
        },
        {
            "id": "L-06",
            "severity": "low",
            "category": "framework-limitation",
            "component": "linkcheck.py",
            "summary": "Percent-encoded internal Markdown link URLs are matched literally; block references checked by substring '^{id}' which can false-positive in prose/code",
            "evidence": "src/vault_unification/linkcheck.py:30 docstring; :100-105 (_block_exists substring check)",
            "fix": "FRAME-001: strict block-id regex (line-anchored ^[id] in block position) — percent-decoding deferred pending evidence of real encoded links in the corpus",
            "status": "partial-fix-scheduled-FRAME-001",
        },
        {
            "id": "L-07",
            "severity": "medium",
            "category": "framework-defect",
            "component": "search.py",
            "summary": "term_stats counts substrings (casefolded), not word-boundary matches: 'ridge' counts inside 'bridge'; inconsistent with overlap.py word-boundary semantics that exist precisely because of F-0006",
            "evidence": "src/vault_unification/search.py:176-183 (casefolded.count) vs overlap.py:134-142 (_boundary_pattern)",
            "fix": "FRAME-001: add word-boundary match mode to term_stats (default unchanged for backward compatibility)",
            "status": "fix-scheduled-FRAME-001",
        },
        {
            "id": "L-08",
            "severity": "high",
            "category": "framework-defect",
            "component": "reporting.py, inventory.py, kuextract.py",
            "summary": "No atomic writes anywhere: reports, manifests and KU batches are written with plain open(...,'w'); a crash mid-write leaves a truncated file that can be mistaken for a real artifact",
            "evidence": "src/vault_unification/reporting.py:66-72, :76-83; inventory.py:142-151; kuextract.py:593-597",
            "fix": "FRAME-001: atomic_write_text helper (temp file in same dir + fsync + os.replace) routed through all writers",
            "status": "fix-scheduled-FRAME-001",
        },
        {
            "id": "L-09",
            "severity": "low",
            "category": "framework-limitation",
            "component": "pathsafety.py",
            "summary": "TOCTOU window: paths are resolved at check time; a symlink appearing between check and write would be followed. Low practical risk in this single-writer environment",
            "evidence": "src/vault_unification/pathsafety.py:108-127 (ensure_dest_safe resolves once)",
            "fix": "documented + mitigated by atomic-write temp files created inside the (already checked) parent dir; full O_NOFOLLOW hardening deferred as not worth the portability cost now",
            "status": "accepted-documented",
        },
        {
            "id": "L-10",
            "severity": "low",
            "category": "framework-limitation",
            "component": "framework-wide",
            "summary": "No concurrent-run lock: two simultaneous extract/kureg-load/report runs on the same outputs can interleave",
            "evidence": "no lock implementation exists in src/",
            "fix": "accepted for the current single-agent operating model (AGENTS.md orchestrator owns integration); revisit if parallel subagents ever write shared state",
            "status": "accepted-documented",
        },
        {
            "id": "L-11",
            "severity": "low",
            "category": "framework-limitation",
            "component": "search.py",
            "summary": "Binary detection is a NUL-byte-in-first-8KB heuristic; a text file with an early NUL would be skipped, a binary file with no NUL in the first 8KB would be scanned",
            "evidence": "src/vault_unification/search.py:21-24",
            "fix": "accepted-documented (vaults are 100% markdown; no binary files exist in either manifest)",
            "status": "accepted-documented",
        },
        {
            "id": "L-12",
            "severity": "critical",
            "category": "missing-capability",
            "component": "framework-wide",
            "summary": "NO emergent-concept / knowledge-gap discovery capability exists: CAP-013 finds cross-vault PAIRS from a given term map; it cannot propose concepts, detect unexplained prerequisites, fragmented derivations, rare essentials, homonyms, or contradictions; no candidate schema, no statuses, no fixtures",
            "evidence": "src/vault_unification/overlap.py (pair evidence only); no discovery module; schemas/ has no candidate schema",
            "fix": "DISC-001: new discovery module + concept-candidate schema + CLI + synthetic fixtures with precision/recall measurement",
            "status": "implementation-scheduled-DISC-001",
        },
        {
            "id": "L-13",
            "severity": "medium",
            "category": "process-debt",
            "component": "scripts/",
            "summary": "55 task-local scripts accumulate repeated ad-hoc logic (X2 machine-locator in ext010, fidelity checkers, term-map verifiers) that should live in the framework instead of being re-implemented per task",
            "evidence": "scripts/ directory listing; EXT-009 R2 and EXT-010 X2 improvements were per-task code",
            "fix": "FRAME-001 migrates the machine-locator utility into the framework; DISC-001 reuses it for evidence locators; remaining scripts stay as one-time migration tooling per disposition",
            "status": "migrate-scheduled-FRAME-001",
        },
    ]

    source_defects = [
        {"id": "F-0001", "summary": "trailing-space source parent dir 'AI ' — handled: all commands quote literal paths; pathsafety does not normalize", "action": "keep quoting rule"},
        {"id": "F-0002", "summary": "14 AI Course unclosed fences/math — extractor preserves content verbatim + warns (kuextract unclosed_finding); inline-math recount disagreement is L-04", "action": "L-04 fix in FRAME-001"},
        {"id": "F-0003", "summary": "175 broken wikilinks + 10 missing anchors include intentional folder links — linkcheck cannot distinguish (L-02)", "action": "L-02 fix in FRAME-001; re-classify after"},
        {"id": "F-0007", "summary": "boosted-tree library dating differs across/within vaults", "action": "synthesis-time reconciliation (unchanged)"},
        {"id": "F-0008", "summary": "mAP name collision (ranking vs detection sense)", "action": "homonym handling exercised by DISC-001 fixtures"},
        {"id": "F-0009", "summary": "course internally inconsistent on PyTorch Conv2d default bias init", "action": "synthesis-time reconciliation (unchanged); contradiction detection lands with DISC-001"},
    ]
    documentation_discrepancies = [
        "None found in REBASE-000 claims check (8/8 CONFIRMED): README, handoff, checkpoint, capability inventory and registry counts all match repository evidence",
        "docs/TOOLING_FRAMEWORK.md capability table must be updated after FRAME-001/DISC-001 land (tracked in FRAME-001 acceptance)",
    ]

    audit = {
        "task_id": "AUDIT-011",
        "method": "full source read of all 17 src/vault_unification modules + CLI help + capability inventory cross-check against the verified battery",
        "capability_map": capability_map,
        "constraints_discovered": [
            "CRITICAL: mdextract construct-detection semantics (fence/math/heading spans) and kuextract segmentation MUST remain byte-stable: REGEN-001 must re-extract the 31 committed files byte-identically; FRAME-001 fixes therefore avoid any change that shifts spans (L-04 fix touches only inline_math_count, which segmentation does not use)",
            "linkcheck report changes (L-02/L-03 fixes) alter future reports vs committed bootstrap reports; committed reports remain historical evidence and are regenerated deliberately, not silently",
        ],
        "source_defects_revisited": source_defects,
        "documentation_discrepancies": documentation_discrepancies,
        "repair_priorities": [
            {"priority": 1, "limitation": "L-08 atomic writes", "reason": "corruption class affects every artifact the pipeline writes"},
            {"priority": 2, "limitation": "L-02 + L-03 linkcheck folder links + cache", "reason": "false-positive link class (F-0003) + enables first-ever Master AI link check"},
            {"priority": 3, "limitation": "L-01 multi-line phrase search", "reason": "documented gap needed for locator-based verification workflows"},
            {"priority": 4, "limitation": "L-07 word-boundary term stats", "reason": "closes the F-0006 false-positive class in statistics"},
            {"priority": 5, "limitation": "L-04 inline-math recount", "reason": "report correctness on the 14 unclosed-fence files"},
            {"priority": 6, "limitation": "L-06 strict block-id check", "reason": "cheap strictness improvement"},
            {"priority": 7, "limitation": "L-13 locator migration", "reason": "reusable evidence locator for FRAME/DISC work"},
            {"priority": 8, "limitation": "L-12 discovery capability", "reason": "DISC-001 (separate task, depends on this audit)"},
        ],
        "accepted_limitations": ["L-05 (deferred with evidence)", "L-09", "L-10", "L-11"],
    }

    known = {
        "task_id": "AUDIT-011",
        "limitations": limitations,
        "summary": {
            "total": len(limitations),
            "by_category": {
                "framework-defect": sum(1 for l in limitations if l["category"] == "framework-defect"),
                "framework-limitation": sum(1 for l in limitations if l["category"] == "framework-limitation"),
                "missing-capability": sum(1 for l in limitations if l["category"] == "missing-capability"),
                "process-debt": sum(1 for l in limitations if l["category"] == "process-debt"),
            },
            "scheduled_for_FRAME-001": [l["id"] for l in limitations if "FRAME-001" in l["status"]],
            "scheduled_for_DISC-001": [l["id"] for l in limitations if "DISC-001" in l["status"]],
            "accepted_documented": [l["id"] for l in limitations if l["status"].startswith("accepted")],
        },
    }

    RB.mkdir(parents=True, exist_ok=True)
    (RB / "framework-audit.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    (RB / "known-limitations.json").write_text(json.dumps(known, indent=2) + "\n", encoding="utf-8")
    print(f"framework-audit.json: {len(capability_map)} capabilities mapped, {len(source_defects)} source defects revisited")
    print(f"known-limitations.json: {len(limitations)} limitations "
          f"({known['summary']['by_category']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
