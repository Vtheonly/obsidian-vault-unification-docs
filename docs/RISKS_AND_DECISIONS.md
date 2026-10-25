# Risk Register and Decision Log

## Active risk register

| ID | Risk | Required mitigation |
|---|---|---|
| R-001 | Small or obscure source details are omitted | Exhaustive source-unit accounting, rare-term alerts, semantic audit, deliberate omission tests |
| R-002 | AI rewrites into shallow summaries | Editorial contract, source evidence bundles, detail-retention checks, depth audits |
| R-003 | Early notes are polished but later notes degrade | Batch gates, cross-batch audits, full-vault editorial audit |
| R-004 | Known topics dominate and unknown topics are missed | Corpus-derived open taxonomy; no fixed topic whitelist; all-unit coverage |
| R-005 | Duplicate detection collapses meaningful distinctions | Semantic comparison, context-aware units, unique-detail review |
| R-006 | Contradictions are silently resolved incorrectly | Evidence-based reconciliation and explicit findings |
| R-007 | Context exhaustion causes lost state or hallucinated continuation | Persistent registry, tasks, checkpoints, tests, verified handoffs |
| R-008 | Subagents produce inconsistent changes | Bounded scopes, shared rules, controlled integration, independent review |
| R-009 | A polished note is mistaken for complete preservation | Separate accounting, semantic validation, technical tests, independent acceptance |
| R-010 | Source files/assets cannot be extracted | Explicit extraction status, OCR/alternate inspection, unresolved blocker reporting |
| R-011 | Global style changes cause drift | Decision control, impact analysis, corpus-wide migration and regression checks |
| R-012 | Metrics hide weak areas | Explicit denominators, per-file/per-type/per-topic breakdowns, no compensating aggregate |
| R-013 | Provenance becomes stale after edits | Hashes, stable IDs, change detection, registry migrations |
| R-014 | Agents trust previous session claims | Verify repository evidence, rerun tests if unsupported |
| R-015 | Output vault relies on source vaults to make sense | Standalone final-vault integration and navigation audit |

## Decision log format

Use stable IDs such as `ADR-0001`. Each decision records:
- status: proposed, accepted, superseded;
- context and problem;
- options considered;
- decision and rationale;
- risks and consequences;
- affected docs, schemas, scripts, and data;
- migration/verification plan;
- approval evidence if human approval is required.

## Initial decisions

### ADR-0001 — Synthesis rather than concatenation
**Decision:** Generate a new canonical vault from combined evidence.  
**Rationale:** Mechanical concatenation cannot resolve redundancy, contradiction, structure, or inconsistent explanations.  
**Consequence:** Requires source-unit provenance and independent verification.

### ADR-0002 — Immutable source vaults
**Decision:** Treat originals as read-only during processing and generate output separately.  
**Rationale:** Prevents accidental source loss and allows comparison and recovery.

### ADR-0003 — Persistent multi-session state
**Decision:** Repository artifacts are the durable source of truth across GLM 5.3 sessions.  
**Rationale:** Fresh sessions cannot depend on previous conversational context.

### ADR-0004 — Full-corpus care
**Decision:** All notes and knowledge units receive the same required preservation and editorial standard; examples do not form an exhaustive topic list.  
**Rationale:** Avoids selective excellence and hidden omissions.

### ADR-0005 — Independent verification
**Decision:** Synthesis cannot self-certify completeness; acceptance uses separate evidence-based audit.  
**Rationale:** A fluent, polished output can still omit or distort knowledge.

## Additional risks and mitigations

| ID | Risk | Severity | Mitigation |
|---|---|---|---|
| R-009 | Rare or one-off details disappear while high-frequency concepts look complete. | Critical | Atomic knowledge-unit accounting, per-concept coverage, frequency alarms, and deliberate omission mutation tests. |
| R-010 | Global coverage percentages hide an entirely missing domain, file, or unusual subtopic. | Critical | Report explicit numerators and denominators by vault, file, domain, concept, and KU; unresolved units block release. |
| R-011 | Tool documentation is mistaken for a working implementation. | High | Capability status must be generated from inspected code and actual test runs, with command, exit code, and report evidence. |
| R-012 | A parser silently drops unfamiliar Markdown, malformed math, embedded assets, or code blocks. | Critical | Preserve raw source locators, report unsupported cases, test malformed fixtures, and keep affected units unaccounted or under review until resolved. |
| R-013 | Automated similarity incorrectly labels complementary or conflicting content as duplicates. | High | Treat deterministic matching as candidate generation; retain independent semantic classification and explicit conflict review. |
| R-014 | Repairs erase already accepted content or regenerate too much of the vault. | High | Require targeted repairs with regression checks, preserve unaffected sections, and quarantine after three failed attempts. |

Coverage statistics and frequency distributions are diagnostic signals, not standalone proof of semantic preservation. A high percentage cannot override a single unaccounted critical knowledge unit, and a frequency drop must trigger investigation rather than automatic rewriting.

### ADR-0006 — Optional `notes` field on task records
**Status:** accepted (2026-10-25, BOOT-000 session)
**Context:** Cross-session handoffs need free-text context attached to specific
task records (e.g. preliminary evidence gathered while executing a
predecessor task). The original task schema had `additionalProperties: false`
and no place for such context, forcing either loss of context or schema
violations.
**Options considered:** (1) keep context only in handoff documents; (2) extend
task records with an optional `notes` string; (3) a separate task-notes file.
**Decision:** Option 2: add optional `notes` (string) to
`schemas/task.schema.json`.
**Rationale:** Task-attached context survives task-queue-first navigation and
cannot drift from its task; a separate file adds a second authority to keep in
sync. The field is optional and does not participate in state-machine
semantics, dependencies, or acceptance criteria.
**Impact / migration:** Backward compatible — existing records remain valid
(none used `notes` before). `validate-registry` (CAP-006) picks up the schema
change automatically; its tests are schema-driven and unaffected. Verified by
re-running `vu validate-registry --tasks state/task-queue.jsonl` after the
change (exit 0).
**Verification plan:** every future schema change follows the same pattern:
documented ADR + schema edit + validator re-run + suite re-run.
