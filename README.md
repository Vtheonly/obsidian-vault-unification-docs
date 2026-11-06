## Repository status

**PROJECT COMPLETE — UNIFIED VAULT DELIVERED (session 28, 2026-11-06).**
`output/Unified-Vault/` holds **544/544 planned canonical notes** across 20
areas, synthesized and rewritten from both source vaults. Final acceptance
evidence: `reports/release/final-report.md`.

**INTEGRATION CAMPAIGN IN PROGRESS (sessions 31–45, user directive commit
`77cf6cf`).** The user supplied a taxonomy of 1,283 raw / 1,233 unique
concepts from their real projects to be integrated into the delivered vault
under a 100%-coverage hard gate, without duplication or disconnection.
Binding methodology: `docs/INTEGRATION_CAMPAIGN_PLAN.md`. Session 31 (setup)
completed the deterministic inventory (9 clusters, documented exclusions) and
the lexical coverage mechanism. **Sessions 32–35 completed the ENTIRE audit
phase: 1,233/1,233 items judged (100%) with mechanically verified evidence —
277 covered / 77 equivalent / 253 partial / 626 absent; re-review agreements
41/41, 30/30, 33/33, 42/42; zero cross-file verdict conflicts (F-0048
one-item-one-judgment rule).** The vault's general ML/attention/training core
is thoroughly covered; the project-domain layers are entirely absent
(medical terminologies F-0032, 3D reconstruction, molecular chemistry +
geometric DL + GFlowNets + protein backbones F-0050, mathematical
OCR/symbolic solving, forecasting formulation, physics-informed ML,
power-engineering faults, classical associative memory, graph learning, GIS
topology F-0051). Next: S36 decision ledger (A/B/C/D + destinations for all
1,233 items), then S37–S43 execution waves, S44 independent re-verification,
S45 close.
Campaign state: `state/integration/`; reports: `reports/integration/`.

- **Knowledge accounting:** 27,536/27,536 KUs dispositioned (Preserved 18,478
  / Consolidated 8,106 / Contextualized 950 / Superseded 2); Unaccounted = 0;
  registry validated (needs_review = 0).
- **Full-corpus audit (s28):** all 8 checks over 27,536 KUs / 544 notes —
  **0 findings**; **42,156 markers verified present, 0 missing** (26,308 term
  + 14,119 math + 1,729 code).
- **Links:** 11,999 checked, 0 problems; lint 0 errors / 85 classified
  verbatim-source warnings.
- **Corpus-wide drift re-audit:** concept/example/overview/tutorial clean at
  corpus scale; derivation/reference drifts root-caused as content-family
  tertile artifacts (flat overall means, 100% verified per-note marker
  retention). All 14 per-area waivers re-audited.
- **Confirmed gaps:** 3/3 treated via dedicated sections (Second Moment,
  Bradley-Terry, Async Def) through the sanctioned discovery machinery
  (`state/synthesis/gap-treatments-v1.json`).
- **Findings ledger:** 0 open (9 closed with evidence at s28).
- **Tests:** 752/752; sources byte-identical to manifests throughout
  (276/276 + 333/333).
- **Deadline record (honest):** the ADR-0012 deadline (end of session 26) was
  missed; sessions 27–28 completed verification and delivery under the §5.5
  honesty rule — the quality floor was never weakened. Delivered at session 28.
- Known limitations (lexical-not-semantic marker verification, 46,978
  low-signal provisional candidates documented as an exclusion, Tier A ~17%
  over-inclusion, keep-both source contradictions) are stated in the final
  report §5.

Earlier phase history: DISC-002 signal-pool + dossier-extension + dispositions
(sessions 16–19), gated synthesis areas 04–14 (sessions 20–24), areas 15–19
(sessions 25–27), area 20 + final verification (session 28).

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
  INTEGRATION_CAMPAIGN_PLAN.md
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
