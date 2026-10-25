# Framework Setup and Usage (v0.2.0)

Implementation documentation for the Python tooling framework specified in
[TOOLING_FRAMEWORK.md](TOOLING_FRAMEWORK.md). This document describes what
actually exists, how to run it, what its outputs mean, and where it is
limited. The normative specification remains authoritative; this file records
the implemented surface and evidence.

## Status

- Version: 0.2.0 (BOOT-000 deliverable; `stats` added in BOOT-002 as CAP-015;
  KU registry commands added in BOOT-003 as CAP-011)
- Layout: `src/vault_unification/` package, `tests/` pytest suite,
  `reports/framework/` + `reports/bootstrap/` evidence reports,
  `state/manifests/` hash manifests, `state/knowledge-units/` canonical KU
  store, `state/registries/` derived registry databases (git-ignored).
- Test evidence: 153 tests passed at BOOT-000; 178 after BOOT-002; 248 after
  the BOOT-003 registry addition — see
  `reports/bootstrap/boot-003-pytest-report.json`.
- Capability inventory (verified against test runs):
  `reports/bootstrap/boot-003-capabilities.json`. 13 code-backed capabilities
  verified `implemented-and-tested`; 3 roadmap capabilities `planned`.
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
| `validate-registry --tasks F [--kus F2]` | JSONL records vs JSON schemas + cross-checks | valid | any schema/cross-check error |
| `kureg-init --db D [--force]` | create empty KU registry database | created | existing db without `--force`; db inside a protected root |
| `kureg-load --db D --kus F [--mint-ids]` | validate + atomically load a KU JSONL batch | batch valid and inserted (or identical re-load skipped) | any schema/cross-check/parse error or ID conflict (nothing written) |
| `kureg-query --db D [filters]` | query registry, reconstruct schema-shaped records | always (unless invalid args/missing db) | missing/corrupt db, unknown disposition filter |
| `kureg-validate --db D` | registry integrity + accounting report | no errors | any dangling reference, enum violation, missing Superseded rationale, corrupt JSON |
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

## Known limitations (v0.2.0)

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
