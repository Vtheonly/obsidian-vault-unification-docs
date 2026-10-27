# Knowledge Model and Provenance

## Goal

Every meaningful detail in the source vaults must be traceable to an explicit outcome in the unified vault or an unresolved finding. Traceability must work from a canonical note back to all contributing source passages and from any source passage forward to its final destination(s).

## Knowledge units

A knowledge unit is the smallest practical unit that can be evaluated for preservation. It may represent a claim, definition, distinction, equation, derivation step, assumption, exception, example, procedure, implementation detail, reference, historical note, project-specific observation, or another meaningful detail.

Do not split mechanically at every sentence if meaning depends on context. Do split compound passages when they contain separable claims that could be partially omitted. A paragraph with five claims and four preserved claims must not pass as wholly preserved.

## Suggested record fields

Each source unit should have fields equivalent to:

- `knowledge_unit_id`: stable unique identifier.
- `source_id`: source file identifier.
- `source_path`: original relative path.
- `source_file_hash`: content hash for the inventoried version.
- `source_format`: Markdown, image, PDF, code, etc.
- `heading_path`: complete heading/subheading hierarchy.
- `line_start` / `line_end`: helpful locators, not sole identity.
- `excerpt_hash`: fingerprint of the relevant passage.
- `excerpt` or secure evidence pointer: exact source evidence where feasible.
- `unit_type`: claim, equation, example, procedure, caveat, etc.
- `concept_ids`: one or more concepts, including discovered concepts.
- `parent_unit_id`: optional relationship for nested/compound evidence.
- `source_context`: surrounding context required for interpretation.
- `disposition`: explicit outcome.
- `destination_path` and `destination_heading`: one or more target locations.
- `supporting_unit_ids`: evidence used in synthesis.
- `verification_status`: extraction, accounting, semantic, technical, and editorial status.
- `finding_ids`: associated issues.
- `reviewer` / `review_method` / `review_date`: when applicable.

One source unit may support multiple output notes. One output note may synthesize many source units. Model this as many-to-many, not a single source-to-destination field.

## Stable identifiers

Do not rely on line numbers alone because edits shift lines. Use a stable ID plus file hash, heading path, excerpt hash, and contextual evidence. When a source file changes, detect the changed hash and explicitly reconcile old and new units; never silently reuse stale mappings.

## Disposition vocabulary

- `Preserved`: retained substantially intact.
- `Consolidated`: merged into a stronger explanation while preserving all unique information.
- `Contextualized`: retained in a suitable historical, practical, conceptual, or project context.
- `Superseded`: replaced by a demonstrably better treatment, with unique information preserved elsewhere and rationale recorded.
- `Needs review`: unresolved; must remain visible and may block acceptance.
- `Unaccounted`: no defensible outcome established; blocks acceptance.

Do not use `Superseded` as a synonym for deleted. If a source unit contains unique details, those details must survive even if the original wording does not.

## Source and output provenance

Maintain an internal audit/provenance layer separate from ordinary user-facing notes. Ordinary final notes should not contain merge logs or source-vault framing. They may include legitimate bibliographic citations, links, version distinctions, and references intrinsic to the subject.

## Evidence bundles and concept dossiers

Before synthesizing a canonical note, collect all relevant units from both vaults and other discovered related units. Include:
- definitions and aliases;
- formal mathematics and conventions;
- assumptions and derivations;
- examples and counterexamples;
- applications and limitations;
- implementation and project details;
- alternative explanations and levels of depth;
- contradictions and unresolved questions;
- references and relevant assets;
- source IDs and exact locations.

The dossier is an evidence pack, not necessarily a final note. It should be bounded enough for reliable reasoning while complete enough for the assigned scope. Dossiers may be required for concepts discovered by cross-note reasoning even when no source file or heading uses the proposed concept's name.

## Emergent concepts and explanatory gaps\n\nThe concept taxonomy is open-ended. Do not assume every concept that deserves teaching already appears as a filename, heading, tag, or explicit definition. Across notes, detect concepts that are repeatedly used but not adequately explained, prerequisites that are assumed, derivation steps that are scattered or abbreviated, and related evidence that collectively reveals a distinct topic. Also consider rare but essential concepts; recurrence is a discovery signal, not a prerequisite.\n\nFor each candidate, record a stable ID, proposed name and scope, source knowledge-unit IDs and exact locators, contexts where it is used or assumed, existing coverage found elsewhere, the specific gap, prerequisite/dependent concepts, suggested canonical destination, confidence, and rationale. Track states such as proposed, accepted, merged, split, rejected, or deferred. Before declaring a gap confirmed, search the processed corpus for adequate existing coverage and distinguish an unprocessed area from a true omission. A candidate may become a new note, a section in an existing note, a merge into an existing concept, or a rejected proposal; every decision needs evidence and rationale.\n\nAccepted discoveries become first-class registry concepts and receive dossiers, source-unit mappings, synthesis tasks, and verification criteria. New explanations must remain grounded in source evidence; independently verified additions must be marked in internal provenance records. See [Emergent Concept Discovery and Knowledge-Gap Detection](EMERGENT_CONCEPT_DISCOVERY.md) for required behavior and acceptance tests.\n\n## Source text and generated additions

Original vaults are authoritative for what knowledge must be preserved. General model knowledge can help interpret or validate content, but it must not be confused with source-derived content. New factual corrections or additions should be identified in internal records and independently verified where possible.

## 7. Accounting invariants and dossier completeness

Overlap classification and disposition answer different questions and must be stored separately. The overlap type describes the relationship between pieces of evidence: Exact Duplicate, Semantic Duplicate, Partial Overlap, Complementary Content, or Conflict or Historical Difference. Disposition records what happened to an individual knowledge unit: Preserved, Consolidated, Contextualized, Superseded, Needs review, or Unaccounted. A schema or implementation must not collapse these fields into one status.

A concept dossier should aggregate all applicable evidence in ten categories: (1) definitions and terminology; (2) mathematical foundations, notation, assumptions, derivations and proofs; (3) computational mechanics, shapes and complexity; (4) alternative explanations and interpretations; (5) worked examples and boundary/failure cases; (6) code and implementation details; (7) applications, project findings, debugging and engineering trade-offs; (8) interview questions, misconceptions and comparisons; (9) historical, version-specific and deprecated approaches; and (10) critical distinctions between neighboring concepts.

Accounting invariants:

1. Every extracted KU has a stable identifier, immutable source locator, excerpt fingerprint, unit type, and verification state.
2. Every KU has exactly one current disposition; Unaccounted is permitted during work but blocks release.
3. A Superseded decision includes rationale and evidence that unique details were preserved elsewhere or are genuinely obsolete without loss of relevant historical knowledge.
4. A Needs review unit remains visible in findings and cannot be silently treated as accepted.
5. Provenance is many-to-many: multiple KUs can support one destination, and one KU can contribute to multiple destinations.
6. Source-note-level links do not establish claim-level coverage; traceability must reach the atomic evidence unit and destination section.
7. All counts and coverage percentages include explicit numerators, denominators, scope, and exclusions.
