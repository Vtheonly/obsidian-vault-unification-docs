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

The dossier is an evidence pack, not necessarily a final note. It should be bounded enough for reliable reasoning while complete enough for the assigned scope.

## Source text and generated additions

Original vaults are authoritative for what knowledge must be preserved. General model knowledge can help interpret or validate content, but it must not be confused with source-derived content. New factual corrections or additions should be identified in internal records and independently verified where possible.
