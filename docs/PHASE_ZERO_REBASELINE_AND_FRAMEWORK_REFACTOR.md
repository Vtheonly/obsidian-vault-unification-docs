# Phase 0 Re-baseline and Framework Refactor

**Status:** Authorized direction as of 2026-10-27. This is a plan, not evidence of implementation.

## Purpose

Restart the knowledge-processing and generation pipeline from Phase 0. Do not erase the repository, source data, Git history, manifests, useful reports, extraction evidence, or working code. Audit and revalidate them, then reuse, recompute, migrate, quarantine, or retire derived artifacts with explicit evidence. The two source vaults remain immutable.

Current evidence says only 31 of 609 source files have been extracted into 1,728 knowledge units. That is partial coverage, not a complete concept map. Do not synthesize canonical notes until the framework, extraction, accounting, concept-discovery, and dossier gates pass.

## Phase 0 — Audit and re-baseline

1. Verify repository/branch/commit, actual files, both source roots, manifests, framework modules, tests, task queue, registry, checkpoint, findings, reports, and handoff.
2. Run self-test, complete tests, capability verification, registry validation, source-manifest checks, and relevant integration checks. Record actual commands, exit codes, logs, and report paths.
3. Compare claims in documentation, capability inventory, source code, tests, and generated state. Report discrepancies rather than guessing.
4. Enumerate every finding and known limitation. Separate source defects, framework defects, documentation defects, and expected source characteristics.
5. Produce a baseline report and artifact disposition list: reuse, recompute, migrate, quarantine for review, or retire with rationale.
6. Add valid task-queue records with dependencies and acceptance tests. Do not create a competing task queue.

**Exit gate:** source immutability is verified; current framework behavior is known; open problems are classified; the baseline is reproducible; and the refactor is broken into bounded tasks.

## Phase 1 — Refactor and harden the framework

Audit every capability against actual code, CLI, tests, output contracts, errors, documentation, and limitations. Keep one coherent Python package and CLI; do not add a parallel implementation of an existing tool.

Prioritize:
1. Source/output isolation, exact path handling, symlinks/traversal, overwrite prevention, atomic writes, recovery, and concurrent-run safety.
2. Extraction fidelity: source spans, headings, code, equations, tables, links, assets, malformed Markdown, and explicit warnings rather than silent loss.
3. Stable IDs, schemas, registry integrity, idempotence, provenance joins, resumable batches, and dependency-aware invalidation.
4. Search and matching: multi-line phrases, aliases, equations, code symbols, normalized text, exact locators, and transparent similarity limitations.
5. Link checking that distinguishes missing targets from intentional folder links, aliases, renamed targets, and anchor conventions.
6. Machine-readable reports with denominators, exclusions, partial-scan indicators, errors, input fingerprints, command, version, and exit status.
7. Capability verification tied to real code and tests, not hand-maintained claims alone.
8. Omission/corruption tests, negative-path tests, regression baselines, and performance benchmarks on representative large inputs.
9. Repeated task-local scripts: decide which reusable logic belongs in the framework and which should remain one-time migration tooling.

Do not optimize speculatively. Measure runtime and memory, retain a correctness baseline, and prove that optimizations preserve results. Review offline dependencies before adding them. Every code change requires unit, integration/regression, malformed-input/failure-path tests as appropriate, CLI help, documentation, and actual test evidence.

## Phase 2 — Implement emergent concept discovery

This must be a first-class tested framework capability, not a standalone permanent script or manual-only checklist. It must be integrated with extraction, overlap discovery, registry, concept/dependency graph, dossiers, synthesis planning, verification, and handoff.

Discover concepts that are implicit or unnamed; prerequisites repeatedly assumed; concepts used without adequate explanation; derivations split across notes; complementary fragments; rare but essential topics; contradictory claims; homonyms; and cases where the importance of a concept exceeds its explanatory depth. Do not rely only on headings, filenames, tags, a fixed topic list, or frequency thresholds.

Use deterministic analysis to collect and rank evidence. Use semantic review to decide concept identity, boundaries, teaching adequacy, and whether the right destination is a new note, an existing-note section, a merge, a split, or rejection/deferment. Similarity and recurrence are signals, not proof. Never mark a gap confirmed when the relevant corpus has not been searched.

Each persisted candidate must have a stable ID/status, supporting KU IDs, exact source locators, independent contexts, relationship types, current explanations, specific gap, proposed scope, prerequisites/dependents, destination recommendation, confidence/uncertainty, reviewer, rationale, and verification checks. Distinguish at least: not yet searched, provisional candidate, confirmed gap after sufficient coverage, already covered, accepted, merged, split, rejected, and deferred. Preserve history when candidates merge or split.

### Required synthetic tests

- A concept is explained in another fully searched note: no false confirmed gap.
- A concept is repeatedly used but nowhere adequately explained: detect and localize it.
- A derivation is split across multiple notes: connect evidence and preserve source spans.
- A rare but essential concept appears once: allow discovery without a frequency threshold.
- Copied passages do not count as independent recurrence.
- Homonyms are distinguished by context.
- Candidates can merge and split without losing provenance/history.
- Unprocessed regions produce provisional, not confirmed, gaps.
- The tool chooses a section when that is better than a standalone note.
- Contradictions are surfaced rather than silently resolved.
- Identical inputs produce equivalent results, excluding explicitly volatile metadata.

Measure precision and recall against known fixture labels; report uncertain cases and reviewer disagreements.

## Phase 3 — Regenerate the source evidence

Reverify all source manifests, then re-extract or validate all 609 files in deterministic batches. Preserve source hashes, spans, locators, code, equations, tables, links, assets, parser warnings, and stable IDs. Test repeatability. Account for every file, asset, and KU. Unsupported or ambiguous content remains visible and unresolved, not silently excluded. All unaccounted KUs block release.

## Phase 4 — Corpus-wide concept map and dossiers

Run discovery across the fully validated corpus, review candidate false positives/false negatives, construct an open concept/dependency graph, reconcile overlap and contradictions, and update dossiers. New evidence can change the taxonomy; keep versioned decisions and migration history. Every accepted concept must be linked to its source evidence and dependent topics.

## Phase 5 — Plan and synthesize

Only after all gates pass, map every KU to one or more canonical destinations and a recorded disposition. Preserve unique detail, document superseded claims, synthesize into a separate output vault, and apply the editorial standard consistently. Use bounded batches and targeted regeneration. A fluent note is not evidence of completeness.

## Phase 6 — Independent audit and release

Independently verify coverage, unique-detail retention, concepts/dependencies, equations/code, contradiction handling, links/assets/navigation, style consistency, provenance, and output independence. Synthetic omission/corruption fixtures must be detected and localized. Report numerators, denominators, exclusions, and per-file/domain results; aggregate percentages cannot hide a missing domain or critical unit.

## Known issues that Phase 0 must revisit

- F-0001: source parent directory has a trailing space; preserve the literal path.
- F-0002: 14 source notes contain unclosed fences/math blocks; extraction must preserve content and warn.
- F-0003: broken wikilinks/missing anchors may include intentional folder links; classify with context.
- F-0004: earlier README state contradicted repository evidence and was corrected; keep documentation evidence-aligned.
- The capability inventory documents possible path-safety races, delimiter-based inline math detection without LaTeX validation, anchor normalization edge cases, percent-encoded URL handling, lack of multi-line phrase search, heuristic binary detection, and timestamped reports. Verify whether each remains relevant.
- The latest checkpoint reports 16 tested capabilities and one planned capability; rerun verification before trusting it.
- Inspect all later findings, test reports, and repeated repairs. The list above is not exhaustive.

## Task and safety rules

Create a parent re-baseline task and child tasks for audit, framework refactor, discovery implementation, full extraction, corpus-wide discovery, dossier reconciliation, and later synthesis. Use the existing task schema; preserve history. Every task needs inputs, outputs, dependencies, acceptance criteria, forbidden side effects, tests, linked findings, and framework impact.

Do not edit source vaults. Do not delete prior work without a verified replacement and migration rationale. Do not start canonical-note synthesis before the gates pass. Do not claim tools or tests are implemented unless code exists and tests actually pass. At each handoff, record exact paths, commit, actual test results, unresolved issues, source immutability, and the next bounded task.
