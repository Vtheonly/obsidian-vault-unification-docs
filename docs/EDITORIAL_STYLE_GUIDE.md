# Editorial Style and Structural Consistency Guide

## Purpose

Ensure that the final vault reads as one coherent body of work, with consistent structure and the same standard of care throughout. This guide must be refined after inspecting the source vaults and testing a representative pilot. Once approved, it is the canonical style contract.

## Establishing the target style

The first agent must inspect both vaults to discover existing conventions and decide, with documented rationale, which conventions should define the unified vault. Do not assume either source vault's style is universally superior. Record the chosen policy before large-scale generation.

## Unified Vault Conventions v1 (recorded at synthesis start — session 20, SYNTH-001)

Derived from both vaults' observed conventions (AI Course: numbered-H1 course
notes, rich explanatory prose, `$`/`$$` LaTeX; Master AI: YAML frontmatter with
tags/aliases, TL;DR callouts, tables and mermaid diagrams). Recorded here, per
"Establishing the target style", before the first generation batch. Changing
any rule below requires the documented change-control procedure in this guide.

1. **File layout**: notes live at their planned canonical path
   (`state/synthesis/canonical-structure-v1.json`); folder names carry the
   `NN - Area/Subfamily` prefix scheme already fixed by the structure.
2. **Frontmatter** (every note): `title`, `type` (one of concept, reference,
   tutorial, derivation, overview, example), `aliases` (when the topic has
   known synonyms, including source-vault phrasings), `tags` (lowercase,
   hyphenated), `sources` (list of the SOURCE NOTE TITLES this note
   synthesizes — attribution metadata, not prose), `created_index` (generation
   order for drift detection).
3. **Body shape**: no H1 in the body (the filename is the title); the body
   opens with a 2–4 sentence orienting introduction; sections use `##` and
   subsections `###`, sentence case, unnumbered, no hierarchy skips; the note
   ends with a `## See also` section of wikilinks when siblings exist.
4. **Math**: `$...$` inline, `$$...$$` display, one convention everywhere (no
   `\(...\)` mixing). Equations from the source material are copied verbatim
   (whitespace-insensitive); surrounding prose is rewritten for coherence.
5. **Code**: fenced blocks always carry a language label; code from sources is
   preserved verbatim. Mermaid diagrams from sources are preserved (and must
   stay grammatically valid).
6. **Callouts**: `> [!info]`/`> [!warning]` etc. are allowed where they aid
   clarity (pitfalls, key distinctions); they are not mandatory. A short
   TL;DR-style opening callout is permitted for dense reference notes.
7. **Links**: Obsidian wikilinks. `[[Note Name]]` when the basename is unique
   vault-wide; `[[path/to/Note Name|Note Name]]` for the 32 known colliding
   basenames (path-based, unambiguous). During incremental area batches,
   links resolve within the generated set only; cross-area links are added in
   the cross-batch consistency pass once all areas exist. Every note links to
   its area MOC and at least two topical siblings.
8. **Tables and lists**: tables for genuine comparisons/lookups; lists only
   where enumeration is natural; no section is a bare bullet list (prose
   develops the reasoning).
9. **Provenance in prose**: notes never mention source vaults, merge history,
   file paths, or this project. Legitimate subject-matter citations, version
   distinctions, and historical context are kept.
10. **Depth**: notes match the depth of their evidence (see the preservation
    rules above); the per-type quality bands in the FRAME-002 tooling
    (`vu assess-quality`) operationalize the floor, never the ceiling.

The target must define:
- folder hierarchy and category boundaries;
- filename conventions and capitalization;
- title wording and title hierarchy;
- numbering conventions, including nested sections and lists;
- heading levels and section order;
- terminology, aliases, abbreviations, and notation;
- prose style and expected explanatory depth;
- mathematical notation and equation numbering where useful;
- code-block language labels and formatting;
- table, list, callout, citation, and reference conventions;
- Obsidian links, embeds, anchors, tags, and metadata;
- templates by note type where templates improve consistency;
- when to use cross-links, prerequisites, examples, summaries, or exercises.

## Equal editorial care

Every note must pass the same quality bar, regardless of length, popularity, or topic. Equal care does not mean forcing every note into the same template or word count. A derivation, project guide, reference sheet, and conceptual tutorial need different structures, but each must be coherent, complete for its purpose, accurate, and polished.

Do not let early notes become exemplary while later notes degrade into disconnected prose or bullet dumps. Use batch gates, cross-batch audits, and corpus-wide final checks to detect drift.

## Canonical note quality contract

Every note should be checked for:
1. Correct path, filename, title, numbering, and heading hierarchy.
2. Logical order and clear conceptual progression.
3. Consistent, precise terminology.
4. Explanations that develop reasoning rather than merely listing facts.
5. Appropriate depth and preservation of relevant source details.
6. Accurate equations, assumptions, derivations, examples, and implementation content.
7. Purposeful use of paragraphs, lists, tables, code, and mathematical notation.
8. Correct Obsidian links and references.
9. No avoidable repetition, contradictions, placeholders, abrupt fragments, or unfinished sections.
10. Consistency with related notes and the approved style guide.
11. Evidence-backed coverage of assigned source units.
12. No unsupported additions presented as source-derived facts.

## Synthesis principles

- Rewrite explanations into coherent prose; do not merely concatenate source passages.
- Consolidate genuinely redundant material, but retain differences that convey unique knowledge.
- Preserve intuitive, formal, practical, and historical explanations when they serve different purposes.
- Do not shorten a note just to make it look clean.
- Do not equate bullet count or word count with quality.
- Do not erase useful examples, edge cases, assumptions, caveats, or intermediate derivation steps.
- Prefer multiple linked notes over an overloaded note when the content has distinct pedagogical or practical purposes.
- The final vault must not expose merge history in ordinary notes.
- Maintain real citations and useful historical/version context where appropriate.

## Style changes

A session cannot unilaterally change global style rules. Propose the change in the decision register, identify affected note types and files, explain the benefit and risks, and specify migration/regression checks. Approved changes must be applied consistently, including to previously generated notes where necessary.

## Additional mandatory preservation and quality rules

The canonical note template is a quality scaffold, not a demand to invent irrelevant sections. A section may be omitted or marked not applicable only when the reason is genuine and the note's relevant knowledge has been preserved elsewhere with traceability. Never turn a rich technical source into a shallow bullet list merely to satisfy a uniform visual template.

Every note must preserve all applicable equations, symbol definitions, assumptions, intermediate derivation steps, proofs, dimensions, numerical examples, boundary conditions, code parameters, project-specific debugging lessons, interview distinctions, historical/API caveats, and failure modes. If content is too large for one canonical note, split it along meaningful conceptual boundaries and create navigable links; do not drop details to keep a note short.

Editorial quality must not decline as work progresses. Use the same depth, explanation, terminology discipline, mathematical rigor, examples, link quality, and review process for prominent topics and obscure or single-instance notes. Familiar examples are not a whitelist of what deserves attention.

Remove redundant repetition and conversational filler, but preserve the unique information contained inside repetitive passages. Resolve apparent contradictions only after identifying assumptions, versions, scope, and provenance. When uncertainty cannot be resolved from evidence, contextualize it or mark it for review rather than silently selecting one answer.

The final reader-facing vault must not narrate its own assembly. Source provenance belongs in the project registry and audit artifacts, not in ordinary explanatory prose. Legitimate technical citations, version distinctions, and historical explanations remain allowed.
