# Source Vault and Content Policy

## Immutable sources

Treat both original vaults as immutable inputs. Inventory and hash them before processing. Do not modify, rename, move, or delete source files during synthesis. Use a separate output directory or repository area for the unified vault.

Keep a recoverable backup and document the source paths, snapshot identifiers, hashes, and date of inventory. If sources are updated later, treat that as a new source version and reconcile changes explicitly.

## Supported content

Inventory all relevant content, including:
- Markdown and other text notes;
- headings and nested sections;
- equations, math notation, and derivations;
- fenced and inline code;
- tables, lists, callouts, metadata, and tags;
- internal links, aliases, embeds, and anchors;
- images, diagrams, screenshots, and scanned pages;
- PDFs and other attached documents;
- references, URLs, and source bibliographies;
- project notes, interview tips, examples, exercises, and practical observations;
- non-text assets and any additional formats found.

Do not assume the vault contains only Markdown. Discover the actual formats first.

## Extraction failures

Unsupported, corrupted, unreadable, encrypted, or ambiguous items must be recorded with paths, hashes, error details, and recovery options. Use OCR or figure inspection where appropriate and available. Never silently skip them.

## Repetition and contradiction

Repeated text may contain subtle differences. Compare claims and context, not only string equality. Preserve meaningful differences and unique details. Resolve contradictions through evidence or contextualize them explicitly. Do not assume the newer, longer, or more polished source is automatically correct.

## Obsolete material

Retain historical/version-specific details when they provide educational, comparative, implementation, or contextual value. Where information is superseded, record the rationale internally and preserve unique caveats or historical knowledge in an appropriate destination.

## Final-vault presentation

Ordinary notes should not narrate the merge process or refer to “Vault A” and “Vault B” as their source. Internal provenance records hold merge traceability. Keep legitimate citations, links, version context, and source references that belong to the subject matter.


## Enforcement through the framework

Source immutability is an executable safety requirement, not merely an instruction. The Python framework must validate source/output path separation, default to read-only source operations, record source hashes, and compare manifests around operations where practical. Any command that writes files must require an explicit destination and reject unsafe source overlap. Tests must prove these protections using temporary fixture vaults; never use original vaults as destructive test fixtures.

All inventory and extraction exclusions, failures, unsupported formats, and inaccessible assets must be emitted in machine-readable reports. Do not treat an item as handled merely because a command skipped it.
