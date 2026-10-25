# Python Tooling Framework Specification

## Status and authority

This document specifies a framework the project agent must build, test, use, maintain, and expand. It is not evidence that implementation already exists. Every session must inspect actual code and test evidence before reporting capability status.

The framework is a first-class project subsystem, not a one-off script or a wish list. Its purpose is to turn repeatable mechanical work into reproducible commands with auditable outputs. The AI remains responsible for semantic interpretation and decisions that cannot safely be reduced to deterministic checks.

## 1. Governing principles

1. **Framework before scale:** implement and test the foundation before large-scale synthesis.
2. **Tool before manual mechanics:** if code can reliably count, enumerate, search, compare, validate, or test something, use a framework command rather than estimating or manually inspecting the corpus in model context.
3. **Evidence before claims:** results must come from commands actually executed, with inputs, scope, and outputs recorded.
4. **Incremental evolution:** build the smallest useful tool for a real task, then extend the framework as needs emerge. Do not build a speculative monolith or stop adding tools after bootstrap.
5. **Safe by default:** source vaults are read-only; writing requires explicit output paths and safety checks.
6. **Deterministic vs semantic:** exact counts, hashes, structural checks, and joins are deterministic. Meaning preservation, contradiction resolution, and prose quality require evidence-based review. Do not mislabel one as the other.
7. **Full-corpus fairness:** cover the full corpus or clearly report exclusions. No topic may be omitted because it is unfamiliar or rare.
8. **Reproducibility:** stable IDs, versioned schemas, command logs, machine-readable reports, and tests must let a fresh session reproduce findings.
9. **Fail visibly:** unsupported formats, parser errors, inaccessible assets, path collisions, and partial scans must be explicit.
10. **No metric laundering:** raw mentions, files processed, or units accounted for are not proof of semantic completeness.

## 2. Implementation ownership and placement

The agent must inspect the actual repository and runtime, then choose and document a maintainable layout. Suggested options are a small CLI under tools/ or a package under src/vault_unification/. Tests belong in tests/, schemas in schemas/, and generated reports/state in established project locations. Avoid duplicate implementations and competing command registries.

Inspect installed Python/runtime versions and offline packages before adding dependencies. Prefer the standard library for basic filesystem, hashing, JSON/CSV, CLI, and test functions. Add third-party packages only with documented benefits, version constraints, and an offline/recovery plan. Do not assume network access.

Expose a stable, discoverable command entry point and a capability inventory describing implementation, tests, limitations, and owning module. Choose one command name and keep it consistent.

## 3. Capability inventory

Each capability must have a stable ID and name; status; module/command and invocation; input/output contract; exit behavior and side effects; test paths and latest actual test evidence; limitations and false-positive/false-negative risks; and task/commit references.

Use these statuses: planned, partial, implemented, implemented-and-tested, blocked. Code existence alone does not qualify as implemented-and-tested. That status requires relevant tests to have actually passed against the current verified code state. Generate inventory details from code/tests where practical or validate the inventory against them.

## 4. Initial capability roadmap

Implement these capability families in bounded increments, adapting after repository inspection. If a capability is unsafe or infeasible, document why and provide the safest useful alternative.

### A. Environment and path safety
- Environment/dependency diagnostics and framework self-test.
- Validate source, temporary, and output roots; reject dangerous source/output overlap.
- Detect symlink/path traversal hazards and accidental overwrite/collision conditions.
- Read-only source mode by default; explicit destination required for writes.
- Detect source changes by comparing initial and later hashes.

### B. Inventory, hashing, and statistics
- Recursive file/directory inventory, extensions, sizes, and file types.
- Stable content hashes, manifests, and inventory diffs: added, removed, changed, unchanged.
- Counts for notes, assets, directories, headings, words, tokens, and characters with documented counting methods.
- Explicitly report unreadable, unsupported, ignored, or excluded files.
- Never equate inventory counts with semantic coverage.

### C. Extraction and structure
- Extract Markdown headings and hierarchy, frontmatter, wikilinks, Markdown links, embeds, tags, code fences, tables, attachment references, and equations/math delimiters where feasible.
- Detect empty/truncated files, malformed fences, encoding problems, parser failures, and unsupported formats.
- Use explicit format adapters. For PDFs, images, scans, diagrams, and binary assets, track text extraction and visual inspection separately.
- Preserve source locations and stable content fingerprints.

### D. Search, matching, and term analysis
- Exact, case-insensitive, and normalized Unicode/whitespace search; configurable aliases and terminology maps.
- Phrase/token frequency with file distribution and exact match locations/snippets.
- Search rare phrases, identifiers, entities, equations, code symbols, and watch terms.
- Fuzzy/near-match discovery with algorithm, threshold, and limitations reported. Similarity is a candidate signal, not proof of equivalence.
- Compare source/output distributions and flag unexpected disappearance, concentration, or count shifts.
- Each count states scope, denominator, normalization rules, exclusions, and locations or a path to details.

### E. Duplication and reconciliation support
- Exact duplicate detection by hash and near-duplicate candidates with transparent thresholds.
- Cross-vault overlap and unique-content reports; compare heading trees and passage fingerprints.
- Support many-to-many source-to-output mapping.
- Never auto-delete or auto-merge solely because content looks similar; use similarity tools to identify candidates for evidence-based consolidation.

### F. Safe transformations and output management
- Controlled splitting/chunking with explicit selectors and destinations.
- Safe copy/extraction/staging that never overwrites inputs and validates destinations.
- Check folder/file creation, naming, duplicate names, case-only collisions, invalid paths, orphan assets, and unexpected files.
- Provide dry-run/preview for risky writes where practical.
- Verify source hashes before and after operations.

### G. Registry and provenance
- Validate schemas for source files, extracted units, concept dossiers, destinations, findings, tasks, decisions, and handoffs.
- Stable unit IDs based on source identity and content fingerprints; line numbers alone are insufficient.
- Queryable many-to-many links among source units, dispositions, evidence, destination notes/headings, and verification results.
- Support dispositions: Preserved, Consolidated, Contextualized, Superseded with rationale and unique detail retained, Needs review, and Unaccounted.
- Validate every source disposition and destination claim support; validate task dependencies, state transitions, findings, and checkpoints.

### H. Obsidian integrity and editorial lint
- Validate wikilinks, aliases, anchors, Markdown links, embeds, attachments, frontmatter, tags, and configured exclusions.
- Safely resolve filename moves and case sensitivity; distinguish intentional external links from accidental broken links.
- Detect orphan notes/assets and navigation gaps without assuming every orphan is invalid.
- Compare title patterns, heading hierarchy/order, numbering, terminology, note-type conventions, code/math formatting, and cross-batch drift.
- Treat editorial lint as review evidence; do not force identical templates on unlike note types.

### I. Testing and verification orchestration
- Documented commands for unit, integration, CLI/end-to-end, audit, mutation/omission, and acceptance tests.
- Report exact command, exit code, duration where practical, captured output, and skips/reasons.
- Negative tests for malformed data, missing files, permission errors, invalid encodings, path collisions, partial processing, and corrupt registries.
- Regression baselines for inventories, provenance, links, structure, and known defects.
- Deliberate omission/corruption tests that report detection and localization.

### J. Reports and statistics
- Machine-readable JSON/JSONL/CSV plus concise human summaries.
- Include run ID, framework version/commit, command, inputs/snapshot IDs, scope, denominator, exclusions, failures, and output paths.
- Calculate metrics in code and define numerator, denominator, method, and limitations.
- Separate scanned, extracted, accounted, destination-linked, and semantically validated counts.
- Do not use aggregate scores that allow polished prose to hide missing knowledge.

## 5. Command contracts

Every command must have discoverable help, examples, safety notes, argument validation, useful errors, stable structured output, and documented exit behavior. Return non-zero for actionable failures or incomplete runs when completeness was requested. Distinguish warnings from errors; never swallow exceptions silently. Record scope and skipped items. Avoid writes into source roots. Support dry-run for risky writes and idempotence where practical.

Prefer small composable commands over one giant command. Share parsing, path-safety, logging, and report utilities.

## 6. Testing requirements for each tool

Every new or modified tool needs appropriate tests before it is relied upon:
1. Unit tests for core logic and boundaries.
2. Negative tests for invalid arguments, missing/corrupt input, and failure handling.
3. Integration tests with temporary fixture vaults and representative assets.
4. CLI tests for arguments, output format, exit codes, and help.
5. Regression tests for previously discovered defects.
6. Mutation/omission tests when the tool claims to detect loss or corruption.
7. Documentation examples that are checked where practical.

Use synthetic fixtures or temporary copies. Never inject test defects into original vaults. Prove source immutability by comparing hashes/manifests around read-only operations. Record tests actually run, not merely configured.

## 7. Omission-detection pilot is a hard gate

Before large-scale synthesis, create a small representative synthetic fixture with source overlap, unique material in each source, an obscure one-off concept, an equation and derivation, examples, caveats, a contradiction, code/identifiers, links, and assets. Create a known-good expected synthesis/registry, then deliberately mutate temporary copies by removing or altering one feature at a time.

For every defect, test whether the system detects it, identifies the affected source-unit ID and destination note/heading, classifies type/severity, and provides reproducible evidence and a repair path. Record injected defect, expected detector, actual result, localization quality, false positives/negatives, and limitations. A global mismatch without useful localization is not full effectiveness. Large-scale synthesis remains blocked until this pilot passes documented criteria.

## 8. Framework vs AI responsibilities

Use tools for enumeration, exact counts, search, matching, hashing, parsing, schema checks, link resolution, provenance joins, statistics, test execution, and regression comparisons.

Use AI for concept taxonomy discovery, semantic equivalence, nuanced contradictions, evidence-based synthesis, argument quality, and repair recommendations. Bound these tasks with evidence bundles and stable IDs. Independent reviewers must inspect source evidence and search for counterexamples rather than merely accepting the synthesizer's explanation.

## 9. Continuous expansion loop

At each task and handoff:
1. Identify repeated manual work, costly searches, missed checks, and new failure modes.
2. Check existing code and capability inventory before proposing a tool.
3. Create a bounded task with a stable ID and concrete use case.
4. Implement the smallest reusable, safe capability.
5. Add tests, CLI help, schema/report updates, and documentation.
6. Run new tests and affected regression suites.
7. Update capability inventory, task queue, findings, checkpoint, and handoff with actual evidence.
8. Record why rejected automation ideas would be unsafe, unreliable, or not worth maintenance.

Do not weaken tests or acceptance criteria to accommodate a new tool. Document migrations and test affected consumers when interfaces change.

## 10. Framework readiness gate

The foundation is ready for the omission pilot only when:
- setup works in a fresh environment or has a documented offline setup;
- CLI help and self-test work;
- path safety and source immutability are tested;
- inventory and hashing produce reproducible manifests;
- search/counting returns correct fixture results and locations;
- Markdown structure/link checks run and report unsupported cases;
- registry validation catches malformed fixtures;
- test orchestration produces honest structured results;
- reports include scope, denominators, exclusions, failures, and code/version identity;
- relevant unit, integration, and CLI tests pass in the recorded run.

Framework readiness is not project completion. The omission pilot must then pass, and semantic preservation remains separately gated.

## 11. Session-end evidence

Record capabilities used, added, changed, or missing; exact commands and actual exit codes/results; tests run and skipped tests with reasons; report paths; source immutability checks; limitations and unresolved defects; and next task priority. Never report “framework complete” without specifying which capabilities are implemented, tested, partial, planned, or blocked.
