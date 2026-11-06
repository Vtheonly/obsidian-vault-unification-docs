# Milestones and Definition of Done

## Milestone 0 — Repository and source discovery
- Inspect repository and locate both source vaults.
- Record source ownership, exact paths, formats, sizes, and hashes.
- Confirm source immutability strategy and backup/recovery plan.
- Record missing, inaccessible, or unsupported assets.
- No synthesis at scale yet.

## Milestone 1 — Operating foundation
- Establish `AGENTS.md`, canonical docs, task queue, checkpoint, registry schema, provenance rules, and editorial contract.
- Establish deterministic inventory and test commands.
- Establish a clear task and finding lifecycle.
- Document setup and recovery.

## Milestone 2 — Verification prototype
- Run a representative pilot with overlap, unique detail, contradictions, technical content, and assets.
- Intentionally inject omissions and formatting/technical errors.
- Demonstrate that the auditor detects and localizes defects.
- Record detection limits and false negatives.

## Milestone 3 — Complete inventory and extraction
- Every source file and asset is enumerated.
- Every item has a verified extraction result or explicit failure disposition.
- No unexplained inventory differences remain.

## Milestone 4 — Knowledge registry and concept discovery
- Meaningful source units have stable IDs and evidence pointers.
- Concepts and relationships are discovered from the corpus, not just a predefined topic list.
- Unknown/ambiguous material is preserved and flagged rather than dropped.

## Milestone 5 — Dossiers and canonical structure
- Related evidence from both vaults is assembled before synthesis.
- Unique details, contradictions, equations, examples, and contextual distinctions are visible.
- Target folder/file structure and editorial conventions are approved and versioned.

## Milestone 6 — Incremental synthesis
- Canonical notes are generated from combined evidence.
- Every batch passes knowledge accounting, technical checks appropriate to its content, provenance checks, and editorial checks.
- Batch progress and source dispositions persist in the registry.

## Milestone 7 — Repairs and corpus-wide consistency
- Findings are repaired through bounded tasks.
- Regression checks pass.
- Cross-batch editorial and terminology drift is audited.
- No note receives a lower quality standard due to topic size or session timing.

## Milestone 8 — Final acceptance
Release is permitted only when all applicable criteria below pass:
- Source files/assets are accounted for; extraction failures are explicitly reported and resolved or accepted through documented review.
- Every extracted knowledge unit has a defensible disposition.
- No `Unaccounted` units remain.
- No critical unresolved findings remain.
- `Needs review` items are explicitly reported and prevent overclaiming semantic completeness where relevant.
- Major and minor concepts alike have been audited; full-corpus checks are complete.
- Equations, code, examples, references, context, and unique details are validated to the extent stated in the report.
- Provenance is valid and traceable.
- Obsidian links, anchors, embeds, and attachments have been checked.
- Editorial standards are consistent across the entire vault.
- No unexplained regressions remain.
- The unified vault can be used independently of the source vaults.
- Final report describes coverage, denominators, methods, limitations, unresolved uncertainty, and evidence.
- Source backups and reproducible project state exist.

## Definition of done

“Done” means the release gates are satisfied with evidence, not merely that all files have been generated. If some material cannot be extracted or semantically verified, report the limitation honestly and do not claim absolute completeness.


## Additional mandatory framework gates

### Milestone 1A — Python framework foundation
- Inspect the actual runtime and repository before choosing implementation details.
- Implement a discoverable CLI, test harness, structured logging/report conventions, path safety, and capability inventory.
- Implement initial deterministic inventory, hashing, search/counting, Markdown structure/link checks, registry validation, and report commands in small tested increments appropriate to the actual repository.
- Add unit, integration, CLI, negative-path, and regression tests.
- Document setup, command examples, output schemas, limitations, and recovery.
- Do not claim any capability until its implementation and tests are present and run.

### Milestone 2A — Omission-detection pilot
- Use temporary test fixtures, not destructive edits to source vaults.
- Inject known missing facts, caveats, equations/steps, unique rare concepts, links/assets, and editorial drift into test copies.
- Demonstrate that the framework reports and localizes each defect type it claims to detect.
- Record detection rates using explicit numerator and denominator, false negatives, false positives, and unsupported cases.
- Block large-scale synthesis until this pilot has evidence-backed acceptance.

### Continuous framework evolution gate
For every project task, identify whether it exposes a recurring deterministic operation or verification gap. Add reusable tools when useful, with tests, documentation, and regression protection. Keep the capability inventory synchronized with actual code and test evidence. The framework is a living project subsystem, not a one-time bootstrap script and not a substitute for semantic review.

## Additional gate interpretation and acceptance evidence

The milestone sequence is a dependency contract, not a suggested order. Large-scale extraction/synthesis must not bypass the foundational tooling and omission pilot. The framework foundation is not complete merely because a CLI exists: the required commands must work on controlled fixtures, enforce source-vault write protection, emit auditable reports, and pass tests covering normal, boundary, malformed, and unsafe-path inputs.

The omission pilot must test the same core pipeline intended for the corpus. It must also test the emergent-concept discovery capability against a predefined manifest of expected discoveries and non-discoveries; keyword recurrence alone does not pass this gate. It must include exact duplicates, semantic candidates, partial overlap, complementary theory/code, conflicts across versions, rare details, intermediate derivation steps, project caveats, equation corruption, code snippets, and broken Obsidian links. A defect manifest defines the expected detections before the test runs. Acceptance requires 100% of planted defects detected and localized to the expected source unit and affected destination; no result may be inferred from an agent's recollection or a hand-written assertion without executable evidence.

For every milestone, persist actual commands, exit codes, test counts, report locations, measured coverage, known limitations, and unresolved findings. A milestone remains blocked when evidence is absent or contradictory. Never mark a source inventory complete if any discovered file is missing, unreadable, unsupported, or unaccounted for; record such cases explicitly and keep the gate open until disposition is justified.
