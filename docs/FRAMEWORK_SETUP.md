# Framework Setup and Usage (v0.1.0)

Implementation documentation for the Python tooling framework specified in
[TOOLING_FRAMEWORK.md](TOOLING_FRAMEWORK.md). This document describes what
actually exists, how to run it, what its outputs mean, and where it is
limited. The normative specification remains authoritative; this file records
the implemented surface and evidence.

## Status

- Version: 0.1.0 (BOOT-000 deliverable; `stats` command added in BOOT-002 as CAP-015)
- Layout: `src/vault_unification/` package, `tests/` pytest suite,
  `reports/framework/` evidence reports, `state/manifests/` hash manifests.
- Test evidence: 153 tests passed at BOOT-000
  (`reports/framework/boot-000-pytest-report.json`); 178 passed after the
  BOOT-002 `stats` addition — see `reports/bootstrap/boot-002-test-run-summary.txt`
  and the pytest json report referenced there.
- Capability inventory (verified against test runs):
  `reports/framework/boot-000-capabilities.json`. 11 code-backed capabilities
  verified `implemented-and-tested`; 4 roadmap capabilities `planned`.
- Source immutability evidence:
  `reports/framework/boot-000-immutable-master-ai.json` and
  `reports/framework/boot-000-immutable-ai-course.json` (0 added/removed/
  changed before and after all session operations).

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

## Known limitations (v0.1.0)

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
