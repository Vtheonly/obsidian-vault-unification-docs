# Project Charter

## Purpose

Unify two very large Obsidian vaults—containing millions of tokens of accumulated material—into one coherent, complete, carefully written knowledge base. The project is expected to require many independent GLM 5.3 sessions and may use the model's own subagents.

The two original vaults were produced through different workflows. One may be richer but more repetitive or inconsistent; the other may be more consistent but less complete. The task is to combine the knowledge, not select one vault as the winner.

## Intended result

The final vault should feel as though it was designed and written as one integrated body of work from the beginning. Ordinary final notes should not narrate the fact that two vaults were merged or expose merge-session history. Legitimate references, citations, version distinctions, and useful historical context must remain.

The final vault may have a new coherent folder and file structure. Multiple source notes may contribute to one canonical note; a single source note may contribute to several canonical notes.

## Non-goals

- Blindly concatenating text or copying two folder trees together.
- Summarizing everything into shallow notes.
- Optimizing only for a short list of familiar or prominent topics.
- Trusting AI self-assessment as evidence of completeness.
- Rewriting source vaults in place.
- Treating Git commits, file counts, or processed-file percentages as proof of semantic preservation.
- Claiming absolute certainty where extraction or semantic limitations remain.

## Equal corpus-wide care

Every file and every meaningful knowledge unit receives the same required preservation and quality standard. Computation can vary with risk and complexity; scrutiny cannot be omitted because a file is small, obscure, or difficult to understand.

Examples mentioned during planning—CNNs, VGG, attention, Transformers, deep neural networks, and loss functions—are examples of topics the user recognizes. Many other deep or unfamiliar topics may exist. The system must discover the actual taxonomy from the corpus and continue discovering categories as it works.

## User's requirements

1. Inventory and inspect both complete vaults.
2. Preserve all meaningful information, including unique details and context.
3. Reconcile overlap and contradiction using source evidence.
4. Generate newly written canonical notes from combined evidence.
5. Apply consistent folder structure, filenames, numbering, titling, section ordering, prose, formatting, and quality across all notes.
6. Independently verify every source file and knowledge unit.
7. Build exhaustive tests that actively detect omissions, corruption, drift, and regressions.
8. Document architecture, procedures, decisions, tools, state, limitations, and handoffs for future agents.
9. Operate in repeatable, persistent iterations across fresh GLM 5.3 sessions.
10. Use the repository—not conversational memory—as the project's durable source of truth.


## Required self-built Python tooling subsystem

The AI agent—not the user—must implement and maintain a Python framework for the project's repeatable operations and verification. The framework must grow incrementally as work exposes new requirements. It should turn mechanical work into reproducible commands with evidence-bearing outputs rather than consuming model context with manual counting, searching, file inspection, arithmetic, matching, or unsupported test claims.

The framework must support inventory and statistics, exact/normalized/fuzzy searching and matching, controlled extraction/chunking/splitting/output operations, duplicate detection, structural and Obsidian integrity checks, registry and provenance validation, automated test execution, omission/corruption detection, regression comparison, and machine-readable reports. This is an evolving capability set: the agent must add further tools whenever concrete work demonstrates a useful, safe, testable need.

Automation does not remove the requirement for semantic reasoning. Scripts measure and validate defined properties; evidence-based semantic review determines whether knowledge and reasoning survived. Neither should impersonate the other.
