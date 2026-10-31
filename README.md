# Obsidian Vault Unification

A persistent, evidence-driven project for reconstructing two large Obsidian vaults into one coherent, complete, consistently edited knowledge base. The project is operated across multiple independent Z AI sessions using GLM 5.3 and its available subagents.

## Start here

1. Read [`AGENTS.md`](AGENTS.md) before doing any work.
2. Read [`docs/PROJECT_CHARTER.md`](docs/PROJECT_CHARTER.md).
3. Follow [`docs/OPERATING_PROTOCOL.md`](docs/OPERATING_PROTOCOL.md).
4. Inspect the actual task queue, checkpoint, registry, Git state, audit findings, and latest handoff before deciding what to do.
5. Do not assume the repository is new or that previous work is complete.

## Core principle

Every source file and every meaningful knowledge unit in both vaults receives the same required standard of care. Examples such as CNNs, VGG, attention, Transformers, deep neural networks, and loss functions are illustrative only; they are not an exhaustive taxonomy or a priority list that permits other material to be neglected.

The output must be newly synthesized and rewritten from combined source evidence—not merely concatenated. The sources remain immutable during processing. The unified vault must be independently audited before acceptance. The system must also discover emergent concepts and explanatory gaps across notes, including concepts that are used repeatedly or assumed as prerequisites but are not adequately taught anywhere. See [Emergent Concept Discovery and Knowledge-Gap Detection](docs/EMERGENT_CONCEPT_DISCOVERY.md).

## Repository status

This repository is the project documentation and operating specification, and it also contains the two immutable source vaults under `source-vaults/` (committed in the repository's first commit; see `reports/bootstrap/boot-001-source-location.json` for the verified location record, file counts, and hash manifests). File-level inventory is complete (BOOT-000..004). **Phase 0 re-baseline (user-authorized restart) is COMPLETE and verified**: the framework was audited (17 capabilities mapped to code/tests/limitations; 13 known limitations L-01..L-13, 8 fixed in FRAME-001, 1 implemented as DISC-001, 4 accepted-documented), refactored and hardened, and extended with emergent-concept discovery (`vu discover-gaps`) and the FRAME-002 quality toolkit (artifact-integrity validation, note-type-aware quality assessment and drift detection, batch quality gates, the evidence-based targeted repair loop, generation-prompt validation). **REGEN-001 full-corpus re-extraction is COMPLETE**: all 609 source files are now extracted into 70 committed batches (11 revalidated pre-restart batches + 59 new REGEN batches; 27,536 KUs, every id globally unique); every batch was double-run byte-identically and verified against its immutable sources by the NEW reusable gate `vu ku-fidelity` (CAP-022, framework 0.8.0), which replaces the per-task fidelity scripts; the registry was rebuilt from all 70 batches plus the 7 classification overlays and validates green; full-corpus accounting shows 276/276 + 333/333 files covered exactly once with zero missing, extra, or multi-covered files and zero source hash mismatches (both vaults byte-unchanged). The two gate catches during the run — the empty_section heading design contract (F-0013) and a resume numbering instability that briefly minted duplicate batches (caught by the id-collision gate, duplicates verified byte-identical and removed) — are fixed and regression-tested. **DISC-002 is in progress**: corpus-wide discovery over the complete registry (609/609 coverage) produced 60,154 candidates; twelve decision rounds are applied (r1, r2, batch2..batch12 — 1,883 cumulative decision records). Review tranches proceed in bounded 60-candidate batches with individual evidence review, definitional-treatment coverage probes (fence-aware since session 10), targeted citation verification, and independent subagent cross-checks with orchestrator re-verification of every subagent correction AND of the orchestrator's own gap claims. The batch-11 tranche (27 evidence-cited covers + 33 noise rejects, subagent cross-checked 60/60 AGREE) resolved the gap-shaped candidate 'ddpm' as a cover (the acronym is expanded in the master-ai glossary '28 - Glossary/Acronyms/Acronyms Index.md:45' and the algorithm is the subject of the dedicated 3-note 10.4 Diffusion Models chapter — check the glossary indexes before claiming acronym absence). The batch-12 tranche (25 evidence-cited covers + 35 noise rejects, subagent cross-checked 59/60 first-pass AGREE) resolved the gap-shaped candidate 'cifar10' as a cover after the orchestrator's draft confirm_gap was overturned on re-verification: a TERM-SEPARATED definition exists in the Q11 quiz matching block ('c) CIFAR-10 dataset' at Q11:178 paired with 'n) A popular benchmark dataset for deep learning with 60,000 32x32 color images in 10 classes' at :182 — the definition line does not contain the string 'CIFAR', so term-only grep missed it; search property-based phrases near term occurrences before claiming definitional absence (extends the session-10 hyphenation and session-11 glossary lessons). Current state: 51,432 provisional / 7,167 already_covered / 1,550 rejected / 3 confirmed_gap (second moment, bradley-terry, async def — async def being the session-7 confirmed gap: Python's async/await execution model used in implementation position in 17 master-ai files with zero definitional treatment corpus-wide) / 1 merged / 1 deferred; the dossier-extension mechanical stage is complete (69,185 candidate pairs across six domains, semantic classification pending). The ADR-0010 replay was re-verified end-to-end in session 12 with twelve replayed rounds (the chain reproduces the committed index content-identically before the batch-12 apply; writer-divergence caveat F-0019; the replay ran clean on the first try). Remaining before gated synthesis: further review tranches (~4,454 still match the signal rule), per-domain classification of the dossier-extension pairs, and disposition assignment. The task queue in `state/task-queue.jsonl` records verified progress claims.

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
