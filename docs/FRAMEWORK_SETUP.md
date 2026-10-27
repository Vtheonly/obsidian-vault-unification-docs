# Framework Setup and Usage (v0.5.0)

Implementation documentation for the Python tooling framework specified in
[TOOLING_FRAMEWORK.md](TOOLING_FRAMEWORK.md). This document describes what
actually exists, how to run it, what its outputs mean, and where it is
limited. The normative specification remains authoritative; this file records
the implemented surface and evidence.

## Status

- Version: 0.5.0 (BOOT-000 deliverable; `stats` added in BOOT-002 as CAP-015;
  KU registry commands added in BOOT-003 as CAP-011; omission-detection pilot
  and output auditor added in BOOT-004 as CAP-012; deterministic KU extraction
  added in EXT-001 as CAP-016, plus the first real extraction batch;
  cross-vault overlap candidate discovery + classification application added
  in EXT-003 as CAP-013)
- Layout: `src/vault_unification/` package, `tests/` pytest suite,
  `reports/framework/` + `reports/bootstrap/` evidence reports,
  `state/manifests/` hash manifests, `state/knowledge-units/` canonical KU
  store, `state/registries/` derived registry databases (git-ignored).
- Test evidence: 153 tests passed at BOOT-000; 178 after BOOT-002; 248 after
  the BOOT-003 registry addition; 285 after the BOOT-004 pilot; 338 after the
  EXT-001 extractor; 407 after the EXT-003 overlap addition — see
  `reports/extraction/ext003-pytest-report.json`.
- Capability inventory (verified against test runs):
  `reports/extraction/ext003-capabilities.json`. 16 code-backed capabilities
  verified `implemented-and-tested`; 1 roadmap capability `planned`
  (CAP-014).
- Source immutability evidence: per-task reports under
  `reports/bootstrap/boot-00N-immutable-*.json` (0 added/removed/changed
  before and after all session operations).

## Setup

No installation is required. Two equivalent invocation styles:

```bash
# style 1: environment variable (works from a fresh clone)
PYTHONPATH=src python3 -m vault_unification --help

# style 2: editable install (provides the `vu` console script)
python3 -m pip install -e .
vu --help
```

Runtime: Python >= 3.10. Optional dependencies (checked by `selftest`):

| Package | Used by | If missing |
|---|---|---|
| jsonschema >= 4 | `validate-registry` | validation reports an explicit error |
| PyYAML >= 6 | `structure` frontmatter | frontmatter block recorded with error |
| pytest + pytest-json-report | `run-tests`, `capabilities --verify` | commands fail visibly |

## Commands

| Command | Purpose | Exit 0 | Exit 1 |
|---|---|---|---|
| `selftest` | environment diagnostics | mandatory checks pass | framework import broken |
| `check-paths --source S --output O` | validate root separation, symlink hazards | roots disjoint | overlap/symlink/missing problems |
| `inventory --root R --manifest M [--report P]` | recursive inventory + SHA-256 manifest | all files hashed | any unreadable file |
| `verify-manifest --root R --manifest M` | diff current files vs stored manifest | unchanged | added/removed/changed detected |
| `structure --file F [--report P]` | extract one note's structure | no parse errors | unclosed fence/math, bad frontmatter, missing file |
| `check-links --root R [--report P]` | wikilink/embed/anchor/block/md-link integrity | no problems | any broken/ambiguous/missing-anchor/missing-block/parse problem |
| `search --root R --term T [--mode M] [--json]` | exact / case-insensitive / normalized search | always (unless invalid args) | invalid term/mode/root |
| `term-stats --root R --terms-file F` | term + alias frequency with denominators | always | missing terms file |
| `stats --root R [--per-file F2]` | content statistics: words, headings, tokens, structures | no file errors | any unreadable/binary/non-UTF-8 or parse-error file (report still written) |
| `validate-registry --tasks F [--kus F2] [--classifications F3]` | JSONL records vs JSON schemas + cross-checks | valid | any schema/cross-check error |
| `kureg-init --db D [--force]` | create empty KU registry database | created | existing db without `--force`; db inside a protected root |
| `kureg-load --db D --kus F [--mint-ids]` | validate + atomically load a KU JSONL batch | batch valid and inserted (or identical re-load skipped) | any schema/cross-check/parse error or ID conflict (nothing written) |
| `kureg-query --db D [filters]` | query registry, reconstruct schema-shaped records | always (unless invalid args/missing db) | missing/corrupt db, unknown disposition filter |
| `kureg-validate --db D` | registry integrity + accounting report | no errors | any dangling reference, enum violation, missing Superseded rationale, corrupt JSON |
| `audit-output --source-root S --output-root O --ku-batch F [--accepted-manifest M]` | full omission/corruption audit of a candidate output vault (KU batch validity, drift vs accepted manifest, disposition/destination accounting, rare-term + equation + code marker retention, link integrity, heading-convention and prose-quality lint) | audit valid (no critical/major findings) | any blocking finding or unusable input |
| `extract-kus --root R --scope S --vault-id V --manifest M --out F [--unclosed-fence-finding ID]` | deterministic segmentation of source notes into schema-valid KU records with stable content-derived IDs, exact excerpts and a coverage report with per-file outcomes and line accounting | every scope file extracted or explicitly excluded; batch schema-valid | any failed file outcome (hash mismatch, encoding, internal inconsistency), scope/manifest problems, or batch validation failure |
| `ku-fidelity --batch F [--batch F...] --vault-id V --vault-root R --manifest M [--kus-schema S] [--allow-processed] [--cross-check-glob G]` | verify KU batches are byte-faithful to their immutable sources: schema validity, excerpt byte-exactness vs source line slices, excerpt hashes, source_file_hash vs disk AND manifest, id uniqueness within and across sibling batches, vault prefix, fresh-batch structural purity, span bounds, heading discipline (CAP-022; replaces the per-task fidelity scripts of EXT-001..010) | all checks pass for every record of every checked batch | any fidelity violation, unusable input, or report path inside the vault root |
| `omission-pilot --dest D [--keep-mutations]` | build the synthetic paired-source fixture, plant 12 declared defects one at a time into mutated copies, re-run the audit pipeline and report detection + localization, false positives and the verdict (hard gate before large-scale synthesis) | verdict pass (all defects detected and localized, clean baseline, sources unchanged) | verdict fail (any missed/unlocalized defect, false positives on the clean baseline, or audit error) |
| `overlap-candidates --batch B1 --batch B2 ... --terms T --out F [--max-pairs-per-topic N]` | cross-vault overlap candidate discovery: word-boundary term/alias evidence over committed KU batches (CAP-013; never assigns classifications) | candidates written | invalid batch/terms/schema, single-vault input, protected-root violation |
| `discover-gaps --batch B1 [--batch B2 ...] --manifest V=M ... --out F [--max-evidence N] [--report R]` | deterministic emergent-concept / knowledge-gap candidate generation over KU batches (CAP-017): n-gram term mining, relationship classification (defined/declared/assumed/derivation/used), independence collapsing, homonym/contradiction flags, coverage-gated statuses; byte-deterministic output. Optimized in DISC-002 for corpus scale (per-KU precomputation, lazy per-term pattern compilation, combined alternations, set-based mining index, precompiled schema validator): identical output to the DISC-001 implementation (proven byte-identical on the real 14-batch subset), ~3.3x faster, memory bounded well below the dict-of-lists reference structure | candidates written | undeclared vault, missing manifest, invalid batch/schema, protected-root violation |
| `discovery-decide --candidates F --decisions F --out F [--decided-utc T]` | apply reviewed semantic decisions (confirm/accept/reject/defer/merge/split/revise/cover) with append-only history; confirm_gap refused under incomplete coverage | updated candidates written | unknown candidate, invalid transition, duplicate decision id, bad merge/split payload |
| `discovery-validate --candidates F [--batch B ...] [--report R]` | schema + cross-check validation of candidate records (coverage gate integrity, evidence ku_id resolvability, history invariants) | no errors | schema violation, confirmed gap under incomplete coverage, unknown evidence ku_id |
| `kureg-apply-overlap --db D --classifications F` | validate + apply append-only overlap-classification records to the registry (pair-level, ADR-0009) | all records inserted or idempotently skipped | schema/cross-check violation, unknown KU id, single-vault group, self-supersede, db missing |
| `run-tests --tests-dir D --json-report P` | pytest orchestration, machine-readable | suite passed | suite failed |
| `capabilities [--verify]` | capability inventory | declared mode; verify mode with all referenced tests passing | verification failed |

Exit 2 (argparse usage error) applies to all commands for bad arguments.

## Output formats

Every `--report PATH` writes JSON with a standard metadata block:

```json
{
  "report_meta": {
    "framework": "vault_unification",
    "framework_version": "0.1.0",
    "report_schema_version": "1.0",
    "command": "inventory",
    "args": {},
    "utc_timestamp": "2026-10-25T16:00:00+00:00",
    "git_commit": "abc1234"
  }
}
```

Manifest records (JSONL) are content identities — path, size, sha256 — with no
timestamps, so manifest comparison is deterministic. Reports deliberately
include timestamps and commit identity for audit; they are not byte-stable
across runs.

Scope and denominators: search/term-stats reports include `files_scanned`,
`files_skipped_nontext`, `files_skipped_binary`, `files_skipped_unreadable`,
`skip_dirs`, and the exact text-extension list used. Inventory reports include
per-class counts and an explicit `unreadable_files` list.

## Safety model

- Source roots are never written to. `inventory` refuses a manifest
  destination inside the scanned root; all report writes pass through
  `ensure_dest_safe` against protected roots.
- `check-paths` rejects output roots that contain or are contained by the
  source, identical roots, and symlink components in either chain.
- Symlinks in inventories are recorded (`is_symlink: true`), not followed,
  unless `--follow-symlinks` is passed explicitly.
- Unit tests prove: write-into-source rejection, overlap rejection, symlink
  hazard detection, and source-unchanged detection after operations
  (`tests/test_pathsafety.py`, `tests/test_inventory.py`).

## Knowledge-unit registry (CAP-011)

The registry has two layers (ADR-0007):

- **Canonical store:** `state/knowledge-units/*.jsonl` — committed batch files,
  one JSON record per line, validated against
  `schemas/knowledge-unit.schema.json` (v1.1). This is the durable source of
  truth for every knowledge unit. The store currently holds 0 records; the
  first extraction task will create the first batches.
- **Derived index:** a SQLite database (convention: `state/registries/*.sqlite`,
  git-ignored) rebuilt with `kureg-init` + `kureg-load`. All writes flow
  through `kureg-load`: schema validation, cross-record checks, conflict
  detection and the atomic insert all happen there; there is no
  direct-to-database record creation.

Rebuild procedure (also the recovery procedure after any DB problem):

```bash
PYTHONPATH=src python3 -m vault_unification kureg-init --db state/registries/knowledge-registry.sqlite --force
PYTHONPATH=src python3 -m vault_unification kureg-load --db state/registries/knowledge-registry.sqlite --kus state/knowledge-units/<batch>.jsonl   # repeat per batch
PYTHONPATH=src python3 -m vault_unification kureg-validate --db state/registries/knowledge-registry.sqlite
```

Semantics worth knowing:

- **Stable IDs:** `kureg-load --mint-ids` mints deterministic IDs from source
  identity and content locators (source id + file hash + heading path + line
  range + excerpt hash). A record without any locator cannot be minted an ID
  and must carry an explicit one. When both are present, an explicit
  `excerpt_hash` is authoritative over `excerpt` text. If a source file ever
  changes, its new hash produces new IDs — stale mappings are never silently
  reused.
- **Idempotence:** re-loading an identical batch inserts nothing
  (`skipped_identical`); the same ID with different content is a conflict and
  the whole batch is rejected (atomic — a failed batch leaves the database
  byte-for-byte unchanged).
- **Accounting:** `kureg-validate` reports counts by disposition with the
  total as denominator, plus `unaccounted_count` (blocks release when
  non-zero) and `needs_review_count`. A `Superseded` unit without a
  non-empty `superseded_rationale` is an integrity error; a `Needs review`
  unit with no linked finding is a warning, not an error.
- **Safety:** `kureg-init`/`kureg-load` refuse databases under a protected
  root (`--protected-root`, defaulting to the repository's `source-vaults/`
  when present); registry commands never touch the source vaults.

## Omission-detection pilot and output auditor (CAP-012)

The hard gate before large-scale synthesis (AGENTS.md 7.5) has two halves:

- **`vu omission-pilot --dest D`** builds a synthetic paired-source fixture
  (never inside `source-vaults/`) with exact/semantic duplicates, partial
  overlap, complementary theory/code, a conflicting historical attribution,
  a rare fact, equations with intermediate derivation steps, a project
  caveat, code blocks and internal links; a known-good baseline synthesis;
  11 KU records with minted stable IDs and destinations; and an accepted
  manifest. It then plants each of 12 declared defects into a *copy* of the
  baseline, re-runs the audit pipeline and reports detection, localization
  to the expected KU + destination note, false positives on the clean
  baseline and an overall verdict. Exit 0 only when every defect is detected
  AND localized, the clean baseline audits with zero findings and the
  fixture sources stayed byte-identical.
- **`vu audit-output --source-root S --output-root O --ku-batch F
  [--accepted-manifest M]`** is the reusable real-work pipeline every
  synthesis batch must eventually pass: KU-batch validation, output drift
  against the accepted manifest, disposition/destination accounting,
  marker retention (rare-term, equation and code fingerprints per KU), link
  integrity, heading-convention and prose-quality lint. Findings always
  carry stable KU IDs, destination locators, expected/observed evidence and
  a repair hint.

Evidence from the BOOT-004 run: 12/12 defects detected and localized, 0
false negatives, 0 false positives on the clean baseline, source vaults
unchanged before and after (`reports/bootstrap/boot-004-omission-pilot.json`,
`reports/bootstrap/boot-004-run-summary.json`). Deterministic repetition:
`python3 scripts/boot004_pilot.py`.

The 12 defect classes mirror VERIFICATION_SPECIFICATION.md "Deliberate
omission tests" plus section 6: unique-detail omission, equation omission,
 derivation-step omission, caveat omission, sign alteration, obscure
one-file concept removal, wikilink break, heading-convention change,
bullet-only prose degradation, version-distinction loss (silent conflict
resolution), accepted-output drift during later repair, and code-parameter
deletion.

## Deterministic KU extraction (CAP-016)

`vu extract-kus` turns a bounded scope of source notes into the canonical KU
batch, deterministically and read-only:

```bash
PYTHONPATH=src python3 -m vault_unification extract-kus \
  --root 'source-vaults/AI /AI Course' \      # quoted: trailing-space parent (F-0001)
  --scope '03 - Machine Learning/03.1 - Regression' \  # root-relative dir or file
  --vault-id 'ai-course' \                   # stable across sessions; keep constant
  --manifest state/manifests/ai-course.jsonl \  # baseline hashes; scope verified against it
  --out state/knowledge-units/001-ext001-ai-course-03.1-regression.jsonl \
  --unclosed-fence-finding F-0002 \          # optional: link unclosed-construct units
  --report reports/extraction/ext001-coverage.json
```

What it guarantees:

- **Structural only.** Unit types describe Markdown block syntax
  (prose/list/table/code_block/math_block/callout/quote/frontmatter/
  empty_section). Every record starts as disposition `Unaccounted`; the
  extractor never assigns overlap types, concepts or destinations — those
  are later evidence-based decisions (EXT-002+).
- **Line-accounting invariant.** Every line of every processed file is
  accounted for in exactly one bucket (unit span, heading context, excluded
  blank, excluded horizontal rule); a violation fails the run. Content
  cannot silently disappear between reported lines.
- **Immutable-locator provenance.** Records carry source id/path/hash,
  heading path, line range, exact excerpt and excerpt hash; IDs are minted
  via `kuregistry.mint_ku_id` from that basis, so re-extracting unchanged
  sources is byte-identical and idempotent on re-load.
- **Explicit outcomes.** The coverage report enumerates every scope file
  with exactly one outcome: `extracted` (with per-type unit counts, warnings
  and line accounting), `excluded_non_markdown` (reason recorded), or a
  `failed_*` outcome (hash mismatch, encoding, missing from manifest/disk,
  internal inconsistency) that makes the run exit 1.
- **Batch self-validation.** The written batch is re-validated against the
  KU schema + cross-checks before the tool reports success.

Vault-id discipline: `ai-course` and `master-ai` are the pinned identifiers
for the two source vaults (recorded in the handoff); using a different id
for the same vault would mint different source ids and KU ids — treat that
as an explicit reconciliation, never an accident.

First real batch (EXT-001): `state/knowledge-units/001-ext001-ai-course-03.1-regression.jsonl`
— 6/6 files extracted, 298 records, all `Unaccounted`, evidence in
`reports/extraction/ext001-*.json`.

## Cross-vault overlap candidates and classifications (CAP-013)

`vu overlap-candidates` discovers cross-vault overlap candidates over
committed KU batches — deterministically and without ever assigning a
classification:

```bash
PYTHONPATH=src python3 -m vault_unification overlap-candidates \
  --batch state/knowledge-units/001-ext001-ai-course-03.1-regression.jsonl \
  --batch state/knowledge-units/002-ext002-master-ai-supervised-learning.jsonl \
  --terms state/term-maps/regression-domain-v1.json \
  --out reports/extraction/ext003-overlap-candidates-pairs.jsonl \
  --report reports/extraction/ext003-overlap-candidates.json
```

What it guarantees:

- **Word-boundary matching only (F-0006).** Terms/aliases match via
  `(?<!\w)term(?!\w)` lookarounds, so `bridge` never matches `ridge`.
  There is no stemming: `ridges` does not match `ridge` unless declared as
  an alias.
- **Mermaid-node suspicion.** Every match inside a mermaid code block (node
  labels like `L1[...]` AND edge references like `L1 --> L2`) plus any match
  immediately followed by `[` is flagged `mermaid_node_suspect` and NEVER
  counts toward a candidate's confirmed evidence. Flagged-only candidates
  are still emitted but marked `unconfirmed_only: true`.
- **Candidates, not classifications.** The output is a candidate-pair list
  with per-side match positions, context snippets and excerpt references;
  every overlap_type assignment requires human/agent excerpt review and is
  recorded separately (append-only) in `state/classifications/`.
- **Determinism.** Sorted outputs, no timestamps in the pairs JSONL;
  re-running on unchanged batches is byte-identical.
- **Pair capping.** Per-topic cross-products are capped
  (`--max-pairs-per-topic`, default 250); excess topics are flagged in
  `truncated_topics` and their per-KU evidence stays complete in the
  `topics` section.

Classification records (`schemas/overlap-classification.schema.json`) are
validated by `vu validate-registry --classifications F` (file level) and
applied to the registry by `vu kureg-apply-overlap` (which additionally
resolves every ku_id against loaded KUs, enforces cross-vault groups and
records the pair-level overlay per ADR-0009 — per-KU overlap columns stay
NULL because one unit can join multiple differently-typed pairs).

First real use (EXT-003): 363 KUs → 44 topics (20 cross-vault), 651 term
pairs (633 confirmed, 18 unconfirmed-only), 0 exact/normalized hash
duplicates; 14 evidence-based classifications (7 Semantic Duplicate, 7
Partial Overlap) over 60 participating KUs — evidence in
`reports/extraction/ext003-*.json` and
`state/classifications/001-ext003-regression-overlap.jsonl`.

## Known limitations (v0.5.0)

- Inline `$...$` math detection is delimiter-based; currency-style dollar
  signs can produce false positives; no LaTeX syntax validation.
- Heading-anchor matching is normalized text equality; exotic anchors may
  be flagged as missing (false positive).
- Percent-encoded Markdown links are matched literally.
- Normalized search collapses whitespace per line; multi-line phrase
  matching is not supported.
- Binary detection is a null-byte sniff (first 8 KiB).
- `stats` word counts are whitespace tokens over the full decoded text
  (frontmatter, headings, code and math included); `words_outside_fences`
  excludes code-fence and display-math block lines (unclosed constructs
  extend to end-of-file). `tokens_estimate` is `chars // 4`, a rough
  BPE-style approximation — not an exact tokenizer count. All are lexical
  measurements, never semantic coverage claims.
- `stats` exits 1 when any analyzed file has read/decode/parse errors
  (e.g. unclosed fences — genuine source defects, see F-0002); the JSON
  report and per-file JSONL are still written in full.
- `check-links` reports links to vault folder names as broken; Obsidian
  treats folder wikilinks differently. Source vaults use such links (see
  finding F-0003); interpretation is deferred to synthesis-time review.
- Counts are lexical/structural evidence only — never proof of semantic
  preservation (see TOOLING_FRAMEWORK.md principle 10).
- No concurrency control: simultaneous runs on the same tree can race.
- The registry database is single-writer (no locking); rebuild it rather than
  repairing it. Query reconstruction uses grouped SQL queries per result set —
  fine at project scale, not benchmarked for millions of rows.
- The conditional Superseded-rationale rule and the overlap/disposition
  separation are enforced by cross-check code, not by JSON Schema
  (ADR-0008): a record with a bad conditional value passes pure-schema
  validation but fails `validate-registry --kus` and `kureg-load`.
- CAP-012 auditor limitations (full list in `vu capabilities` and in every
  audit/pilot report): term markers are frequency-based and cannot cover
  claims carried only by common vocabulary; no stemming or grammar-level
  matching, so reworded claims are caught only through shared distinctive
  vocabulary; equation/code matching compares normalized source strings;
  heading-convention detects mixed schemes per note only; prose-quality is
  a word-count heuristic; drift detection requires an accepted manifest;
  link findings attribute KU ownership by destination note plus wikilink
  presence in the excerpt; the pilot fixture is small by design and
  corpus-scale noise must be re-measured on real extraction batches.
- CAP-013 limitations (full list in `vu capabilities` and in every
  candidate-discovery report): candidate generation only — no overlap_type
  is assigned or implied by the tool; no stemming/inflection (`ridges` is
  not `ridge` unless aliased); mermaid detection covers mermaid code blocks
  and the immediate-`[` heuristic, not other diagram syntaxes; term
  coverage is exactly the provided terms/aliases map; hash duplicates
  compare whole excerpts only; per-topic pair cross-products are capped;
  classifications are pair-level overlays (per-KU overlap columns stay
  NULL by design, ADR-0009).

## Recovery and troubleshooting

- Fresh session: `PYTHONPATH=src python3 -m vault_unification selftest` must
  pass before trusting other commands.
- If a report looks stale, regenerate it; reports always carry the git
  commit and timestamp of their run.
- If pytest json reports are missing, check that `pytest-json-report` is
  installed (`selftest` reports it as `optional:pytest_jsonreport`).
- Test suite: `PYTHONPATH=src python3 -m pytest tests -q` (or
  `vu run-tests --tests-dir tests --json-report <path>`).

## Extending the framework

Follow the continuous expansion loop in
[TOOLING_FRAMEWORK.md](TOOLING_FRAMEWORK.md) §9: check the capability
inventory first; create a bounded tooling task; implement the smallest safe
tool; add unit + negative + integration + CLI tests; run the suite; update
`capabilities.py` (the inventory is generated from that module, not from
prose) and this document; record evidence in `reports/framework/`.
