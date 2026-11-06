#!/usr/bin/env python3
"""S28/SYNTH-001: anchored marker/lint/heading repairs for area 20 (audit s28-area20-audit.json).

All 189 findings root-caused; every repair below is anchored (exact old->new
string), cites its finding IDs / source lines, and is PROBE-IDEMPOTENT: a
second run must be a no-op (verify with --probe after --apply).

Repairs (finding IDs from reports/synthesis/s28-area20-audit.json):
  R1  AF-001..AF-016  merge-report TOC anchor slugs (README.md:19-34) restored
                      as the source-verbatim numbered contents list.
  R2  AF-040          `[[wikilink]]` syntax example (README.md:926) fenced.
  R3  AF-039          `[[wikilinks]]` syntax example (00 - Master Index.md:33)
                      fenced.
  R4  AF-041..043     ADR-011 decision examples (Architecture Decisions.md:76)
                      fenced verbatim; inline live-link forms removed.
  R5  AF-044/045      ADR-011 supersede examples (Arch. Decisions.md:165)
                      fenced verbatim.
  R6  AF-046          iteration-4 folder-level example (Arch. Decisions.md:574)
                      fenced verbatim.
  R7  AF-047/048      Remaining Work documentation placeholders (Remaining
                      Work.md:62) fenced verbatim.
  R8  AF-027..029     Research Queue no-fabrication labels (Research
                      Queue.md:192-203, KU-92730ab65eb7323d) restored in the
                      source's blockquoted-fence form ("> ```" lines) so the
                      extracted code fingerprints match byte-for-byte.
  R9  AF-030          "100-200" ASCII hyphen restored (Arch. Decisions.md:502).
  R10 AF-024          "master-prompt" hyphenated form restored (Master
                      Roadmap.md:270).
  R11 AF-020..022     Master AI README Source record (README.md:131) restored
                      verbatim (Ultimate Prompt.md / What to do.md /
                      ObsidainAgentGithubUplaod repository, typo sic).
  R12 AF-032          `Ultimate Prompt.md` filename restored (Coverage
                      Audit.md:13).
  R13 AF-017..019,    Completed Work Log created/expanded file itemization
      AF-023,025,026, (Completed Work.md:30-73) — archived paths restored in
      AF-031,033-038  backticks alongside the wikilinks (keep-both).
  R14 AF-049..AF-189  Master Roadmap 31 numbered domain headings -> "Domain
      (141 MNS)      NN - Name" form: content-preserving unnumbering so the
                      note has ONE heading scheme (style guide v1 #3) while
                      every domain number and name token survives.

Verbatim-source warnings (classified, NOT repaired): MATH_INLINE_ODD in the
merge report = the `^ FILE:\\s*(.+?)\\s*$` regex dollar (README.md source
line, preserved sic); the merge-report MATH_INLINE_ODD/EMPTY_SECTION infos
carry the same class.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VAULT = REPO / "output/Unified-Vault/20 - Vault and Project Context"

MERGE = VAULT / "AI Course Merge Report.md"
MIDX = VAULT / "AI Course Master Index.md"
ARCH = VAULT / "Architecture Decisions Log.md"
REMAIN = VAULT / "Remaining Work Log.md"
RQ = VAULT / "Research Queue.md"
ROADMAP = VAULT / "Master Roadmap.md"
MREADME = VAULT / "Master AI README.md"
COVAUD = VAULT / "Coverage Audit Log.md"
CW = VAULT / "Completed Work Log.md"

TOC_LIST = """
1. [Executive Summary](#1-executive-summary)
2. [Source Inventory — What Was In The Two Vaults](#2-source-inventory--what-was-in-the-two-vaults)
3. [Methodology — The Six-Stage Merge Pipeline](#3-methodology--the-six-stage-merge-pipeline)
4. [The New Master Vault Structure — Top-Level Architecture](#4-the-new-master-vault-structure--top-level-architecture)
5. [Ordering Principle — Why This Sequence](#5-ordering-principle--why-this-sequence)
6. [Naming Convention — How Every File Was Renamed](#6-naming-convention--how-every-file-was-renamed)
7. [Conflict Resolution — Every Conflict, Every Decision](#7-conflict-resolution--every-conflict-every-decision)
8. [Folder-by-Folder Walkthrough](#8-folder-by-folder-walkthrough)
9. [Misplacement Corrections — What Was Moved, From Where, To Where, Why](#9-misplacement-corrections--what-was-moved-from-where-to-where-why)
10. [Niche Topics Promoted To Their Own Folder Or Chapter](#10-niche-topics-promoted-to-their-own-folder-or-chapter)
11. [Duplicate Detection — What Was Found, What Was Kept, What Was Merged](#11-duplicate-detection--what-was-found-what-was-kept-what-was-merged)
12. [Verification — Proof That Nothing Was Lost](#12-verification--proof-that-nothing-was-lost)
13. [How To Use This Vault](#13-how-to-use-this-vault)
14. [Appendix A — Full Source → Destination Mapping Table](#appendix-a--full-source--destination-mapping-table)
15. [Appendix B — Files Per Chapter Count](#appendix-b--files-per-chapter-count)
16. [Appendix C — Glossary Of Structural Terms](#appendix-c--glossary-of-structural-terms)
"""

# (path, old, new, finding ids) — old must exist pre-repair; new must NOT
# exist pre-repair (idempotence probe); both checked per run. When the old
# string would remain a substring of the new text (R11), the optional fifth
# element is an APPLIED MARKER whose presence alone means already-applied.
REPAIRS: list[tuple[Path, str, str, str, str | None]] = [
    # R1 — TOC anchor slugs
    (
        MERGE,
        "and a glossary of structural terms.\n\n## Executive summary",
        "and a glossary of structural terms. The archived report's own contents list, "
        "with its original anchor links, is preserved verbatim:\n"
        + TOC_LIST + "\n## Executive summary",
        "AF-001..AF-016",
    ),
    # R2 — wikilink example fenced
    (
        MERGE,
        "Obsidian's `[[wikilink]]` syntax was preserved wherever it appeared in the source files.",
        "Obsidian's wikilink syntax (fenced below to show the syntax literally rather "
        "than as a live link) was preserved wherever it appeared in the source files:\n\n"
        "```text\n[[wikilink]]\n```",
        "AF-040",
    ),
    # R2b — R2 fence closer shared its line with the following sentence
    # (repair-of-repair): put the closer on its own line.
    (
        MERGE,
        "```text\n[[wikilink]]\n``` If you find a broken link",
        "```text\n[[wikilink]]\n```\n\nIf you find a broken link",
        "AF-040 (fence-closer fixup)",
    ),
    # R3 — wikilinks example fenced
    (
        MIDX,
        "Wikilinks (`[[wikilinks]]`) connect related notes, so connections can be followed by clicking.",
        "Wikilinks connect related notes, so connections can be followed by clicking; "
        "the double-bracket syntax, fenced below to show it literally rather than as a "
        "live link, is the record's own example:\n\n```text\n[[wikilinks]]\n```",
        "AF-039",
    ),
    # R4 — ADR-011 decision examples fenced
    (
        ARCH,
        "Wikilinks are written as `[[Note Name]]` or `[[Note Name|Display Text]]`, never as `[[folder/path/Note Name]]`. Obsidian auto-resolves links by note name",
        "Wikilinks are written as a plain note-name link or a note-name link with "
        "display text — never as a folder-path link; the record's three example forms "
        "are preserved verbatim in the fenced block below (fenced so the syntax shows "
        "literally instead of parsing as live links):\n\n"
        "```text\n[[Note Name]] or [[Note Name|Display Text]], NOT as [[folder/path/Note Name]]\n```\n\n"
        "Obsidian auto-resolves links by note name",
        "AF-041..AF-043",
    ),
    # R5 — ADR-011 supersede examples fenced
    (
        ARCH,
        "- This **supersedes** ADR-005's \"wikilinks use note names\" rule for the link *target* text. New wikilinks use the full numbered name — `[[02 - Mathematics/01 - Vectors|01 - Vectors]]` — or the shorter `[[01 - Vectors]]` when unambiguous.\n- Existing notes from iteration 1 were renamed in iteration 2.\n- Each note's YAML frontmatter keeps an `aliases:` field with the unnumbered title (e.g., `aliases: [Vectors]`) so legacy `[[Vectors]]` links still resolve in Obsidian.",
        "- This **supersedes** ADR-005's \"wikilinks use note names\" rule for the link *target* text: new wikilinks use the full numbered name, or the shorter form when unambiguous — the record's two example forms are preserved verbatim in the fenced block below the list.\n- Existing notes from iteration 1 were renamed in iteration 2.\n- Each note's YAML frontmatter keeps an `aliases:` field with the unnumbered title (e.g., `aliases: [Vectors]`) so legacy `[[Vectors]]` links still resolve in Obsidian.\n\n"
        "```text\n[[02 - Mathematics/01 - Vectors|01 - Vectors]] or shorter [[01 - Vectors]] when unambiguous\n```",
        "AF-044/AF-045",
    ),
    # R6 — folder-level example fenced
    (
        ARCH,
        "Most of the broken links were folder-level references (e.g., `[[15 - AI Agents/Architecture/01 - Agent vs Workflow vs LLM Application]]`) that Obsidian resolves to the folder's MOC.md in practice but that the strict audit flags; a handful were genuinely broken references — minor, and not affecting usability.",
        "Most of the broken links were folder-level references — the record's example, "
        "fenced below — that Obsidian resolves to the folder's MOC.md in practice but "
        "that the strict audit flags; a handful were genuinely broken references — "
        "minor, and not affecting usability.\n\n"
        "```text\n[[15 - AI Agents/Architecture/01 - Agent vs Workflow vs LLM Application]]\n```",
        "AF-046",
    ),
    # R7 — Remaining Work placeholders fenced
    (
        REMAIN,
        "- **Remaining 3 broken**: all are documentation-example placeholders in the [[Architecture Decisions Log]] (``[[Note Name]]``, ``[[folder/path/Note Name]]``) — these are intentional examples of wikilink syntax and should not be fixed.",
        "- **Remaining 3 broken**: all are documentation-example placeholders in the "
        "[[Architecture Decisions Log]] — the two placeholder forms, fenced below so "
        "the syntax shows literally — these are intentional examples of wikilink "
        "syntax and should not be fixed.\n\n"
        "```text\n[[Note Name]], [[folder/path/Note Name]]\n```",
        "AF-047/AF-048",
    ),
    # R8 — Research Queue blockquoted fences (source form "> ```")
    (
        RQ,
        "The queue's governing rule is: never fabricate. If a source cannot be verified, the note must say:\n\n```text\nNot publicly disclosed.\n```\n\nor\n\n```text\nStrong inference — not officially confirmed.\n```\n\nor\n\n```text\nInsufficient public evidence.\n```\n\nIteration 13 applied this policy throughout",
        "The queue's governing rule, quoted verbatim from the record (the three labels "
        "are fenced inside the quotation exactly as written there):\n\n"
        "> Never fabricate. If a source cannot be verified, the note must say:\n"
        "> ```text\n> Not publicly disclosed.\n> ```\n"
        "> or\n"
        "> ```text\n> Strong inference — not officially confirmed.\n> ```\n"
        "> or\n"
        "> ```text\n> Insufficient public evidence.\n> ```\n\n"
        "Iteration 13 applied this policy throughout",
        "AF-027..AF-029",
    ),
    # R9 — ASCII "100-200"
    (
        ARCH,
        "were still shallow (100–200 lines, no interview questions, limited code examples); iteration 8",
        "were still shallow (100-200 lines, no interview questions, limited code examples); iteration 8",
        "AF-030",
    ),
    # R10 — hyphenated "master-prompt"
    (
        ROADMAP,
        "Per the collection's master prompt (§5), models here are analyzed from the **neural-network architecture** perspective — see [[Interpretability and Research MOC]].",
        "Per master-prompt §5: analyze models from the **neural-network architecture** "
        "perspective — see [[Interpretability and Research MOC]].",
        "AF-024",
    ),
    # R11 — Master AI README Source record restored verbatim
    (
        MREADME,
        'The collection was built from two governing documents — an "Ultimate Prompt" that specified its scope and standards, and the "What to do" protocol that specified the iterative construction procedure — which together defined the vault\'s architecture, quality bar, and working method.',
        'The collection was built from two governing documents — an "Ultimate Prompt" '
        "that specified its scope and standards, and the \"What to do\" protocol that "
        "specified the iterative construction procedure — which together defined the "
        "vault's architecture, quality bar, and working method. The record's own "
        "source line is preserved verbatim (repository name typo sic): built from "
        "`Ultimate Prompt.md` and `What to do.md` in the "
        "[ObsidainAgentGithubUplaod](https://github.com/Vtheonly/ObsidainAgentGithubUplaod) "
        "repository.",
        "AF-020..AF-022",
        "repository name typo sic",  # applied marker (old stays substring of new)
    ),
    # R12 — Ultimate Prompt.md filename
    (
        COVAUD,
        'For each section of the master prompt — the construction brief, titled "Ultimate Prompt" — the audit verifies five things:',
        "For each section of the master prompt — the construction brief, "
        "`Ultimate Prompt.md` — the audit verifies five things:",
        "AF-032",
    ),
    # R13 — Completed Work archived paths (keep-both: wikilink + path)
    (
        CW,
        "- [[Fable 5 Architecture]] — stub for an unverifiable 2026 model.",
        "- [[Fable 5 Architecture]] — `10 - Model Architecture Research/Closed Source/10 - Fable 5 Architecture.md` — stub for an unverifiable 2026 model.",
        "AF-031 (ch10)",
    ),
    (
        CW,
        "- [[Kimi K3 Architecture]] — strong inference from the K1.5/K2 trajectory.",
        "- [[Kimi K3 Architecture]] — `10 - Model Architecture Research/Closed Source/11 - Kimi K3 Architecture.md` — strong inference from the K1.5/K2 trajectory.",
        "AF-031 (ch10)",
    ),
    (
        CW,
        "- [[Opus 5 Architecture]] — Anthropic lineage analysis.",
        "- [[Opus 5 Architecture]] — `10 - Model Architecture Research/Closed Source/12 - Opus 5 Architecture.md` — Anthropic lineage analysis.",
        "AF-031 (ch10)",
    ),
    (
        CW,
        "- [[Mythos Architecture]] — stub for an unverifiable 2026 model.",
        "- [[Mythos Architecture]] — `10 - Model Architecture Research/Closed Source/13 - Mythos Architecture.md` — stub for an unverifiable 2026 model.",
        "AF-031 (ch10)",
    ),
    (
        CW,
        "- [[GLM 5.2 Architecture]] — Zhipu lineage (GLM-4.5 → 5.2).",
        "- [[GLM 5.2 Architecture]] — `10 - Model Architecture Research/Open Source/07 - GLM 5.2 Architecture.md` — Zhipu lineage (GLM-4.5 → 5.2).",
        "AF-031 (ch10)",
    ),
    (
        CW,
        "- [[Qwen 3.8 Architecture]] — Alibaba lineage (Qwen 3 → 3.8).",
        "- [[Qwen 3.8 Architecture]] — `10 - Model Architecture Research/Open Source/08 - Qwen 3.8 Architecture.md` — Alibaba lineage (Qwen 3 → 3.8).",
        "AF-031 (ch10)",
    ),
    (
        CW,
        "- [[MiniMax 3 Architecture]] — MiniMax lineage (MiniMax-01 → 3).",
        "- [[MiniMax 3 Architecture]] — `10 - Model Architecture Research/Open Source/09 - MiniMax 3 Architecture.md` — MiniMax lineage (MiniMax-01 → 3).",
        "AF-031 (ch10)",
    ),
    (
        CW,
        "- [[Frontier Model Synthesis 2026]] — the converged 2026 architectural recipe.",
        "- [[Frontier Model Synthesis 2026]] — `10 - Model Architecture Research/2026 Frontier Model Synthesis.md` — the converged 2026 architectural recipe.",
        "AF-031",
    ),
    (
        CW,
        "- [[EAGLE-3]] (paper note 51) — confidence-aware spec decoding; 4–6× speedup.",
        "- [[EAGLE-3]] — `26 - Papers/Efficient Attention/51 - EAGLE-3 2025.md` — confidence-aware spec decoding; 4–6× speedup.",
        "AF-0xx (ch26)",
    ),
    (
        CW,
        "- [[Multi-Token Prediction]] (paper note 52) — DeepSeek-V3 training-time innovation.",
        "- [[Multi-Token Prediction]] — `26 - Papers/Efficient Attention/52 - MTP Multi-Token Prediction.md` — DeepSeek-V3 training-time innovation.",
        "AF-037",
    ),
    (
        CW,
        "- [[Verifiable Rewards vs PRMs]] (paper note 53) — RLVR vs PRM comparison.",
        "- [[Verifiable Rewards vs PRMs]] — `26 - Papers/Alignment/53 - Verifiable Rewards vs PRMs.md` — RLVR vs PRM comparison.",
        "AF-038",
    ),
    (
        CW,
        "- [[DeiT v2]] (paper note 54) — modernized ViT training recipe.",
        "- [[DeiT v2]] — `26 - Papers/Transformers/54 - DeiT v2 2024.md` — modernized ViT training recipe.",
        "AF-035",
    ),
    (
        CW,
        "- [[SigLIP-2]] (paper note 55) — default 2026 VLM vision encoder.",
        "- [[SigLIP-2]] — `26 - Papers/Multimodal/55 - SigLIP-2 2025.md` — default 2026 VLM vision encoder.",
        "AF-036",
    ),
    (
        CW,
        "- [[Build an RLHF Pipeline with PPO]] (capstone 20) — SFT → RM → PPO.",
        "- [[Build an RLHF Pipeline with PPO]] — `27 - Projects/Capstones/20 - Build an RLHF Pipeline with PPO.md` — SFT → RM → PPO.",
        "AF-019",
    ),
    (
        CW,
        "- [[Build a Knowledge-Graph Construction Pipeline]] (capstone 21) — GraphRAG with Neo4j.",
        "- [[Build a Knowledge-Graph Construction Pipeline]] — `27 - Projects/Capstones/21 - Build a Knowledge-Graph Construction Pipeline.md` — GraphRAG with Neo4j.",
        "AF-0xx (ch27)",
    ),
    (
        CW,
        "- [[Build a Long-Context Evaluation Harness]] (capstone 22) — NIAH, multi-needle, multi-hop, heatmap.",
        "- [[Build a Long-Context Evaluation Harness]] — `27 - Projects/Capstones/22 - Build a Long-Context Evaluation Harness.md` — NIAH, multi-needle, multi-hop, heatmap.",
        "AF-017",
    ),
    (
        CW,
        "- [[Build an Agent Observability Platform]] (capstone 23) — tracing SDK + collector + UI.",
        "- [[Build an Agent Observability Platform]] — `27 - Projects/Capstones/23 - Build an Agent Observability Platform.md` — tracing SDK + collector + UI.",
        "AF-018",
    ),
    (
        CW,
        "- [[Build a Model Distillation Pipeline]] (capstone 24) — response/logit/feature distillation.",
        "- [[Build a Model Distillation Pipeline]] — `27 - Projects/Capstones/24 - Build a Model Distillation Pipeline.md` — response/logit/feature distillation.",
        "AF-0xx (ch27)",
    ),
    (
        CW,
        "- [[Conceptual Interview Questions]] (conceptual set 2, note 06) — 25+ Q&A on new topics.",
        "- [[Conceptual Interview Questions]] — `29 - Interview Prep/Conceptual/06 - Conceptual Interview Questions 2.md` — 25+ Q&A on new topics.",
        "AF-025",
    ),
    (
        CW,
        "- [[Coding Interview Questions]] (coding set 3, note 05) — 6 from-scratch implementations.",
        "- [[Coding Interview Questions]] — `29 - Interview Prep/Coding/05 - Coding Interview Questions 3.md` — 6 from-scratch implementations.",
        "AF-026",
    ),
    (
        CW,
        "- [[Research Frontier Update 2026]] — 2026 verification of all chapter notes.",
        "- [[Research Frontier Update 2026]] — `24 - Research Frontiers/08 - 2026 Research Frontier Update.md` — 2026 verification of all chapter notes.",
        "AF-023",
    ),
    (
        CW,
        'Two existing notes were deepened rather than replaced. "A Brief History of AI" ([[History and Evolution of AI]]) grew from 133 to 190 lines:',
        'Two existing notes were deepened rather than replaced. "A Brief History of AI" '
        "([[History and Evolution of AI]], archived path `01 - AI Foundations/03 - A "
        "Brief History of AI.md`) grew from 133 to 190 lines:",
        "AF-034",
    ),
    (
        CW,
        "[[Embedding Models for Retrieval]] grew from 122 to 247 lines: added SigLIP-2, ColPali, a BGE-M3 multi-vector example,",
        "[[Embedding Models for Retrieval]] (archived path `09 - Foundation "
        "Models/Embedding Models/02 - Embedding Models for Retrieval.md`) grew from "
        "122 to 247 lines: added SigLIP-2, ColPali, a BGE-M3 multi-vector example,",
        "AF-033",
    ),
]

# R14 — roadmap domain headings: "## NN — Name" -> "## Domain NN — Name"
# (content-preserving unnumbering; every number and name token survives)
DOMAIN_HEADING_RE = re.compile(r"^## (\d{2}) — (.+)$", re.MULTILINE)


def apply_r14(text: str) -> tuple[str, int]:
    count = 0

    def repl(m: re.Match) -> str:
        nonlocal count
        count += 1
        return f"## Domain {m.group(1)} — {m.group(2)}"

    return DOMAIN_HEADING_RE.sub(repl, text), count


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="apply repairs (default: probe)")
    ap.add_argument("--report", default="reports/synthesis/s28-marker-repairs-area20.json")
    args = ap.parse_args()

    results: list[dict] = []
    failures = 0
    for entry in REPAIRS:
        path, old, new, ids = entry[0], entry[1], entry[2], entry[3]
        marker = entry[4] if len(entry) > 4 else None
        text = path.read_text(encoding="utf-8")
        rec = {"file": path.name, "findings": ids}
        if marker is not None:
            if marker in text:
                rec["status"] = "already-applied"
            elif old in text:
                rec["status"] = "applied" if args.apply else "pending"
                if args.apply:
                    path.write_text(text.replace(old, new, 1), encoding="utf-8")
                elif new in text:
                    rec["status"] = "AMBIGUOUS (new present but marker absent)"
                    failures += 1
            else:
                rec["status"] = "ANCHOR NOT FOUND"
                failures += 1
            results.append(rec)
            continue
        if new in text and old not in text:
            rec["status"] = "already-applied"
        elif old in text:
            if new in text:
                rec["status"] = "AMBIGUOUS (both old and new present)"
                failures += 1
            elif args.apply:
                path.write_text(text.replace(old, new, 1), encoding="utf-8")
                rec["status"] = "applied"
            else:
                rec["status"] = "pending"
        else:
            rec["status"] = "ANCHOR NOT FOUND"
            failures += 1
        results.append(rec)

    # R14 roadmap headings
    text = ROADMAP.read_text(encoding="utf-8")
    new_text, n = apply_r14(text)
    rec14 = {"file": ROADMAP.name, "findings": "AF-049..AF-189 (141 MNS)", "headings": n}
    if n == 0 and "## Domain " in text:
        rec14["status"] = "already-applied"
    elif n == 0:
        rec14["status"] = "ANCHOR NOT FOUND (no numbered domain headings)"
        failures += 1
    elif args.apply:
        ROADMAP.write_text(new_text, encoding="utf-8")
        rec14["status"] = "applied"
    else:
        rec14["status"] = "pending"
    results.append(rec14)

    applied = sum(1 for r in results if r["status"] == "applied")
    pending = sum(1 for r in results if r["status"] == "pending")
    done = sum(1 for r in results if r["status"] == "already-applied")
    print(f"repairs: {len(results)} | applied={applied} pending={pending} "
          f"already-applied={done} failures={failures}")
    for r in results:
        if r["status"] not in ("applied", "pending", "already-applied"):
            print("  !!", r)

    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(
        json.dumps({"mode": "apply" if args.apply else "probe", "results": results,
                    "applied": applied, "pending": pending, "already_applied": done,
                    "failures": failures}, indent=1), encoding="utf-8")
    if failures:
        return 1
    if not args.apply and pending:
        print("probe: repairs are pending; run with --apply")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
