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

The output must be newly synthesized and rewritten from combined source evidence—not merely concatenated. The sources remain immutable during processing. The unified vault must be independently audited before acceptance.

## Repository status

This is the project documentation and operating specification. It does not contain the two source vaults, and it does not claim that inventory, extraction, synthesis, or testing has already happened. The first agent must inspect the repository and establish actual state.

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
