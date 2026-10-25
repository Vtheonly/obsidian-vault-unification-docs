# Knowledge-Unit Canonical Store

This directory is the **canonical, committed record** of every knowledge unit
(KU) extracted from the source vaults (ADR-0007). The SQLite registry
databases under `state/registries/` are derived indexes that are always
rebuildable from the batch files committed here.

## Current status

**0 records.** No extraction has been performed yet (BOOT-003 delivered the
registry mechanism only). The first extraction task will create the first
batch files here. Do not fabricate seed records to "test" the store — the
mechanism is covered by the test suite
(`tests/test_kuregistry.py`, `tests/test_cli.py`) and the demonstration
report in `reports/bootstrap/boot-003-kureg-demo.json`.

## Conventions

- One JSON record per line, validated against
  [`schemas/knowledge-unit.schema.json`](../../schemas/knowledge-unit.schema.json)
  (v1.1) before any use.
- File naming: `<sequence>-<task-or-batch-id>.jsonl`, e.g.
  `001-ext-001-master-ai-001.jsonl`. Batches are append-only: never edit a
  committed batch; issue a new batch instead (conflicting re-loads are
  rejected by the registry).
- Dispositions: `Preserved`, `Consolidated`, `Contextualized`, `Superseded`
  (requires non-empty `superseded_rationale`), `Needs review`, `Unaccounted`
  (blocks release). Overlap classification (`overlap_type`) is a separate
  field from disposition — never collapse them
  (docs/KNOWLEDGE_AND_PROVENANCE.md section 7).
- Stable IDs: minted deterministically from source identity and content
  locators (source id + file hash + heading path + line range + excerpt
  hash) — see `vault_unification.kuregistry.mint_ku_id`. Line numbers are
  part of the locator, never the sole identity.

## Working with the registry

```bash
# validate a batch file (schema + cross-checks)
PYTHONPATH=src python3 -m vault_unification validate-registry --kus state/knowledge-units/<batch>.jsonl

# rebuild / update the derived index
PYTHONPATH=src python3 -m vault_unification kureg-init --db state/registries/knowledge-registry.sqlite --force
PYTHONPATH=src python3 -m vault_unification kureg-load --db state/registries/knowledge-registry.sqlite --kus state/knowledge-units/<batch>.jsonl

# integrity + accounting report
PYTHONPATH=src python3 -m vault_unification kureg-validate --db state/registries/knowledge-registry.sqlite
```

See `docs/FRAMEWORK_SETUP.md` ("Knowledge-unit registry") for full semantics
and limitations.
