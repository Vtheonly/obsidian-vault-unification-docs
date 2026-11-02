## Repository status

BINDING ACCELERATED-COMPLETION POLICY in force since session 17
(2026-11-01, ADR-0012): `docs/ACCELERATED_COMPLETION_POLICY.md` +
AGENTS.md §12. Final vault deadline: end of session 26 (user directive:
"less than 12 additional sessions"). Progress is measured by
deliverables only (dossier pairs classified / 69,185; KU dispositions
assigned / 27,536; release-gate predicates; verified notes); the
universal per-unit dual review is removed in favor of ADR-0011 tiered
verification; the quality floor (source immutability, full test suite,
machine-verified citations, release gates) is inviolate.

GATED SYNTHESIS IN PROGRESS (session 23, 2026-11-03 — SYNTH-001). Areas
04–14 are synthesized end-to-end and GREEN through the full gate chain:
**259/544 canonical notes** (04 - Machine Learning 27; 05 - Neural Network
Foundations 21; 06 - Computer Vision 79; 07 - Sequence Models 14; 08 -
Attention and Transformers 38; 09 - NLP and Language Models 11; 10 - Large
Language Models 7; 11 - Foundation Models and Multimodal 13; 12 - Generative
Models 12; 13 - Training and Adaptation 11; 14 - Inference and Production
26). Session 23 generated all 69 new notes via 33 bounded subagent groups,
ran all five audits to **valid=true with 0 findings** (3,252 KUs / 15,538
markers verified present: 14,521 term + 838 math + 179 code), lint 0 errors /
17 documented verbatim-source warnings, gates pass (3 evidence-backed
concept-type drift waivers with source math-density measurements; areas
13–14 clean). 28 + 5 round-2 anchored marker repairs (keep-both rule for
duplicated source content) + 2 lint fence-label repairs (F-0031 precedent).
744/744 tests; sources immutable 276/333 at start and end. REMAINING: 9
areas / 285 notes (sessions 24–25: areas 15–19, 01–03, 20), cross-batch
consistency + the three confirmed-gap treatments + corpus-wide drift
re-audit of all 10 waivers (session 25), final verification and delivery
(session 26).

DISPOSITION ASSIGNMENT IS COMPLETE (session 19, 2026-11-01 — the S21–22
phase target finished two sessions early). All 27,536/27,536 KUs received
exactly one disposition with planned destinations; Unaccounted = 0
(Preserved 18,478 / Consolidated 8,106 / Contextualized 950 / Superseded 2)
under the ADR-0014 rule engine (`vu assign-dispositions` + committed
ledger `state/dispositions/001-disp001-rule-driven.jsonl` + registry
overlay `vu kureg-apply-dispositions`; rebuilt registry validates green
with 0 warnings). The rule engine consumes the committed synthesis plan:
`state/synthesis/canonical-structure-v1.json` (20-area unified backbone,
544 planned canonical notes) and `state/synthesis/file-mapping-v1.jsonl`
(609 source files mapped by 13 bounded subagents + one
orchestrator-reviewed context group; machine-verified, 0 problems).
Session 19 also completed dossier v2 (EXT-011: six `<domain>-v2.json`
dossiers covering all 5,168 per-domain extension participants plus the 514
original participants; byte-identical `--check`), repaired finding F-0022
(all 7,034 evidence entries in 009..014 had empty `lines` — field-name bug
in the session-18 assembly script; new term-level schema +
`--extension-classifications` validator with batch cross-checks, ADR-0013),
and fixed F-0023 (registry destinations UNIQUE(path, heading) cannot
dedupe NULL headings). 708/708 tests.

DISC-002 signal-pool review is COMPLETE (session 16, 2026-11-01, ADR-0011
user-authorized accelerated mode). All 4,274 remaining signal-rule
candidates were decided in one session through a tiered pipeline:
calibrated bulk classes (zero counter-examples in the 2,063-decision
calibration set), 290 citation-backed covers, 3,666 parallel-subagent
review decisions with full orchestrator verification (mechanical citation
checks, 150-reject sample re-review at ~97% agreement, 11 citation-backed
overrides, one gap_watch overturned to cover). Result: 667 covers +
3,607 rejects + 0 new confirmed gaps (total remains 3: second moment,
bradley-terry, async def). Index status: 46,978 provisional (documented
low-signal exclusion) / 7,893 already_covered / 5,278 rejected / 3
confirmed_gap / 1 merged / 1 deferred; validate green; 663/663 tests.

DISC-002 dossier-extension classification is COMPLETE (session 18,
2026-11-01, one session ahead of the S18–20 phase window): all 69,185
extension pairs decided (5,441 participate / 63,744 reject-pair; 5,168
distinct participant KUs; 294 extension records in
state/classifications/009..014; 4,893 review verdicts in 008) through a
calibrated tiering engine (state/term-maps/dext-tier-config-v1.json +
scripts/s18_dext_tiering.py; C1/C2 zero-counter-example calibration, two
ADR-0011 pull-backs after sampled wrong-class members) plus four subagent
review rounds with mechanical completeness/citation verification and
orchestrator sampling (99.4% reject agreement; Tier A residual ~17%
safe-direction over-inclusion documented). Next: dossier v2 regeneration
(ext006 config extension), disposition assignment (27,536 KUs, Unaccounted
→ 0), then gated synthesis — synthesis must start by session 23; final
vault by end of session 26.

## Suggested top-level layout

```text
AGENTS.md
README.md
docs/
  PROJECT_CHARTER.md
  SYSTEM_ARCHITECTURE.md
  KNOWLEDGE_AND_PROVENANCE.md
  EDITORIAL_STYLE_GUIDE.md
  VERIFICATION_SPECIFICATION.md
  OPERATING_PROTOCOL.md
  SESSION_HANDOFF.md
  MILESTONES_AND_ACCEPTANCE.md
  RISKS_AND_DECISIONS.md
  SOURCE_POLICY.md
  TOOLING_AND_SETUP.md

  TOOLING_FRAMEWORK.md
schemas/
state/
scripts/
tests/
reports/
source-vaults/       # only if deliberately stored here and safely managed
output/Unified-Vault/
```

The first agent may refine this layout after inspecting the actual repository, but must maintain one authoritative home per type of information and document any structural decision.


## Mandatory Python Tooling Framework

The project is **framework-first**. The AI agent must build, test, maintain, and progressively expand a local Python tooling framework in this repository. It must use the framework for deterministic operations instead of manually counting, searching, comparing, inventorying, validating, or claiming test results from model intuition.

Read [docs/TOOLING_FRAMEWORK.md](docs/TOOLING_FRAMEWORK.md) before implementation work. The framework does not exist merely because it is specified here: the agent must inspect the actual repository, implement the first usable version, test it, and record verified results. Do not claim a capability exists until its code and tests exist.

Initial implementation is a gate before large-scale synthesis. As new repetitive or verifiable work appears, add reusable tools and regression tests to the framework. Keep semantic judgments separate from deterministic measurements, and never present lexical counts as proof of meaning preservation.

## Preservation and synthesis contract

The expected corpus is larger than 5,000,000 tokens. Vault A is expected to contribute depth, derivations, implementation and debugging detail, interview insights, and historical caveats despite repetition; Vault B is expected to contribute uniform organization and concise presentation despite omissions of advanced material. These are tendencies to verify against the actual files, not assumptions that replace inspection. Neither vault is privileged as a whole.

The framework must account for all meaningful content before prose synthesis. It separates (1) overlap classification—Exact Duplicate, Semantic Duplicate, Partial Overlap, Complementary Content, or Conflict/Historical Difference—from (2) each knowledge unit's disposition—Preserved, Consolidated, Contextualized, Superseded with rationale, Needs review, or Unaccounted. Unaccounted units block release.

Before a canonical note is written, its concept dossier should cover all applicable evidence categories: definitions; mathematics, assumptions, and derivations; computational mechanics; alternate explanations; worked examples and edge cases; code; practical/project lessons; interview insights; historical versions; and critical distinctions. Rare and single-instance material receives the same quality standard as familiar headline topics. The taxonomy must remain open to new concepts discovered through cross-note analysis; do not limit it to existing filenames, headings, or an initial topic list. The agent must detect recurring unexplained prerequisites and fragmented derivations, propose dedicated notes or sections when justified, and persist the evidence and decisions.

## Mandatory pre-synthesis gates

1. Framework foundation: a tested repository-owned Python package/CLI performs deterministic inventory, SHA-256 hashing, path-safety checks, counting/search, link/anchor checks, extraction, and machine-readable reporting as capabilities are implemented.
2. Omission pilot: a synthetic test corpus deliberately injects known missing derivations, project caveats, equation corruption, and broken links. The auditor must detect and localize 100% of the injected defects before full-corpus synthesis begins.

Documentation is a specification, not proof of implementation. Report a capability as implemented only after inspecting code and running tests. Keep source vaults immutable, use bounded batches, independently audit authored notes, repair only affected sections, and persist verified state and the next task for every fresh session.
