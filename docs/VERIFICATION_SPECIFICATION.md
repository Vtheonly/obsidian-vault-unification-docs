# Verification and Testing Specification

## Objective

Build an exhaustive, layered verification system designed to discover omissions, distortions, technical errors, inconsistencies, and regressions across the entire corpus. Testing is not a final cosmetic phase; it is continuous throughout inventory, extraction, synthesis, repair, and release.

No single metric or AI self-assessment proves correctness. Automated checks have limitations; unresolved uncertainty must be explicit.

## Verification layers

### 1. Inventory integrity
Detect missing, renamed, duplicated, unreadable, unexpectedly changed, or unclassified files and assets. Compare source snapshots and current inventories. Track unsupported formats and access failures.

### 2. Extraction integrity
Compare source file counts, extracted content, heading trees, links, tables, code fences, formulas, metadata, images, embeds, and attachments. Flag truncation, encoding problems, parser errors, OCR failures, and unhandled content. A PDF containing diagrams or a Markdown file containing image references requires asset-aware handling.

### 3. Knowledge accounting
Every extracted knowledge unit must have a disposition and a defensible destination or documented unresolved state. `Unaccounted` blocks acceptance. Track partial omissions by splitting compound units into independently testable claims when needed.

### 4. Lexical and structural regression
Track terms, aliases, rare phrases, named entities, identifiers, equations, code symbols, file names, heading depth, example labels, and other content markers. Compare source and output distributions. Frequency differences are alerts requiring investigation, not automatic proof of loss or proof of preservation.

### 5. Semantic preservation
Independently verify that meaning, assumptions, exceptions, caveats, scope, relationships, reasoning, practical implications, and level of detail survive. Look for weakened claims, overgeneralization, lost context, conflated concepts, and unsupported conclusions.

### 6. Cross-source reconciliation
Detect conflicting definitions, equations, conventions, terminology, version-specific behavior, and examples. Every contradiction must be resolved with evidence, explicitly contextualized, or remain an open finding. Never silently choose a source merely because it is more polished.

### 7. Technical/domain correctness
Use tests appropriate to the actual corpus. For mathematics, check notation, assumptions, derivation steps, dimensions, boundary conditions, and conventions. For code and algorithms, validate identifiers, behavior, dependencies, and examples when feasible. Examples such as convolution, attention, Transformers, VGG, deep neural networks, and loss functions can be pilot cases, but the system must discover and test all other relevant technical material too.

### 8. Provenance integrity
Verify every source reference, fingerprint, target path, heading anchor, and many-to-many relationship. Ensure each output note has valid supporting evidence and each source unit has a recorded outcome.

### 9. Obsidian integrity
Check wikilinks, Markdown links, aliases, embeds, anchors, attachment paths, tags, metadata, filename changes, orphan notes, and navigation structures. Distinguish intentionally external/broken links from accidental ones.

### 10. Editorial consistency
Check titles, filenames, numbering, heading hierarchy, terminology, section ordering, prose quality, formatting, note-type conventions, and cross-batch drift against the canonical style guide. Do not force all notes into one identical template.

### 11. Regression protection
After any repair or global style change, rerun relevant prior tests. Maintain tests for previously discovered defects so they do not recur. Do not overwrite accepted content without recording impact and validating affected knowledge units.

### 12. Independent acceptance audit
A reviewer other than the synthesis author checks the source registry, evidence bundles, output notes, findings, and test results. The reviewer must actively search for omissions rather than merely approve the author's explanation.

## Deliberate omission tests

The test harness must demonstrate that it can catch intentionally introduced defects before scaling:
- remove a unique claim from a candidate note;
- remove an equation or a derivation step;
- remove an example or caveat;
- alter a symbol, sign, dimension, or assumption;
- remove a minor concept mentioned in one obscure file;
- break an Obsidian link or attachment;
- change a heading/numbering convention;
- degrade one batch to bullet-only, shallow prose;
- create a contradiction that is silently resolved incorrectly;
- alter an accepted note during a later repair.

For each injected defect, record whether the relevant test detected it, whether it localized the issue, and any known false negatives. Do not claim the auditor is effective until these tests run and results are recorded.

## Metrics

At minimum report:
- inventory coverage;
- asset inspection coverage;
- extraction coverage and extraction-failure rate;
- knowledge units with source evidence;
- units with dispositions;
- units with valid destinations;
- units semantically validated;
- unique-detail retention;
- math/code/example integrity;
- unresolved contradictions;
- provenance completeness;
- broken links/assets;
- editorial violations and cross-batch drift;
- regressions introduced and repaired;
- open findings by severity and type;
- observed false-positive/false-negative rates where measurable;
- uncertainty and human-review burden.

Every metric must define its numerator, denominator, measurement procedure, and limitations. Separate accounted-for from semantically validated. Do not report 100% merely because every file was opened or every unit received a status. Do not use a single aggregate score that lets good prose compensate for missing technical content.

## Finding record

Each finding should include a stable ID, severity, category, affected source-unit IDs, source evidence, target note/heading, expected condition, observed failure, reproduction steps, repair recommendation, status, and verification evidence after repair.

## Acceptance behavior

- Any `Unaccounted` unit blocks acceptance.
- `Needs review` remains visible and blocks a claim of complete semantic validation where it could affect correctness.
- Critical math, code, project implementation, or source-coverage findings must be resolved or explicitly accepted through documented human review.
- Extraction failures and inaccessible assets must be reported and handled, not hidden.
- Full-corpus audits are required; sampling may help during development but cannot replace final checks.
- A polished note is not proof of completeness.


## 13. Framework-backed verification is mandatory

The Python framework specified in [TOOLING_FRAMEWORK.md](TOOLING_FRAMEWORK.md) must be the operational implementation of this verification specification. This document defines what must be verified; the framework provides repeatable commands and machine-generated evidence. A written checklist alone does not satisfy this requirement.

For every verification class, identify the command/module, input scope and exclusions, output schema/report path, exit/failure semantics, unit and integration tests, and known limitations. At minimum, automate inventory and hashes, extraction coverage/failures, exact/normalized phrase search, term and marker distributions, heading/structure differences, link/embed/asset integrity, registry schemas, source-to-output provenance joins, task/finding state, and regression diffs. Add checks whenever project work reveals a repeatable verification need.

Testing layers include unit tests, integration tests across temporary vault fixtures, CLI/end-to-end tests, negative/error-path tests, and deliberate omission/corruption tests. Include fixtures for unique facts, equations and derivation steps, caveats, obscure one-off concepts, broken links, asset loss, heading drift, and malformed registry records. Verify both detection and localization of defects. Record false positives and false negatives.

Use scripts to calculate counts, ratios, denominators, and diffs. The model may interpret evidence but must not silently recompute or replace script results with estimates. Reports identify command/version, inputs or inventory snapshot IDs, scope, denominators, exclusions, timestamp, and failures. Store evidence so a fresh session can reproduce the result.

A framework test passing proves only the behavior covered by that test. Lexical frequency is a triage signal, not semantic proof. Semantic audits remain evidence-based and independent; decisions should be recorded against stable source-unit IDs.

## 5. Corpus-wide coverage and omission controls

Verification must apply the same gates to every domain, including notes with very few source mentions. Familiar concepts are not allowed to consume disproportionate audit effort while obscure derivations, footnotes, project failures, hardware caveats, or unusual equations remain unchecked.

Frequency regression is a triage mechanism. Establish source baselines for technical terms, aliases, phrases, model names, and relevant mathematical notation; compare them with accepted output using deterministic tooling. A sharp drop (for example, a term appearing hundreds of times in source material but only a couple of times in output) triggers a localized audit. It does not automatically prove omission, because legitimate consolidation changes frequencies; nor does a stable frequency prove that all meanings survived.

Every report must disclose its scope, excluded file types, unreadable inputs, unknown parser cases, numerator, denominator, and unresolved items. Do not use one corpus-wide percentage to hide an unprocessed file, domain, or knowledge unit. Report coverage by source vault, file, domain/concept, and KU wherever possible.

## 6. Adversarial omission pilot — release blocker

Use synthetic copies and a reproducible baseline fixture. Plant and enumerate omissions/corruptions such as: removing a rare derivation step, dropping a project-specific caveat, altering an equation, deleting an implementation parameter, removing a historical/version distinction, and breaking an internal link or attachment reference. Run the real pipeline and verify that each defect is detected and localized to the exact KU and affected output section.

The mandatory pass criterion is 100% detection/localization of all declared injected defects and zero false negatives for the fixture. Record false positives separately, along with commands, exit codes, tool versions, fixture manifest, defect manifest, and machine-readable results. Never mutate the original source vaults to run the pilot. Any missed planted defect blocks large-scale synthesis.

## 7. Repair policy

Repairs must be evidence-targeted and non-destructive. Give the repair task the accepted note, the missing or corrupted source units, their provenance, and the exact destination section. Do not regenerate the whole vault or rewrite unaffected accepted sections. Rerun focused checks and the relevant regression suite after each repair. Stop after three unsuccessful attempts, set the affected item to Needs review, create a finding, and include it in the handoff.
