## Repository status

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
Next: dossier-extension classification (69,185 pairs), disposition
assignment, then gated synthesis — final vault targeted within the
user's 12-session budget (by session 27).

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
