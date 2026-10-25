# Tooling, Setup, and Recovery

## Initial rule

The first agent must inspect the actual environment, repository, and available tools before selecting implementation details. Do not assume a particular operating system, API, package manager, model API, or agent framework. GLM 5.3 and Z AI are the intended execution environment; use the subagent capabilities actually available there.

## Suggested implementation approach

Use deterministic local scripts for:
- recursive inventory;
- hashes and change detection;
- metadata and heading extraction;
- link/attachment checks;
- code fence and math marker counts;
- structured registry validation;
- task/checkpoint validation;
- deterministic report generation;
- regression comparisons.

Use AI for bounded tasks requiring semantic interpretation:
- concept discovery and clustering;
- synthesis of evidence bundles;
- contradiction analysis;
- semantic preservation review;
- editorial review;
- targeted repair recommendations.

Do not make AI responsible for arithmetic, file counts, or deterministic comparisons when scripts can provide reproducible results.

## Persistent data

Choose a durable registry format after inspecting corpus scale. SQLite is a reasonable default for relational provenance and querying; JSONL can be useful for append-only task/finding events. Keep a documented schema, migrations, and validation tests. Do not rely only on transient agent context.

## Git and large assets

- Use Git commits as recovery points, not proof of semantic coverage.
- Keep source snapshots immutable.
- Make small, coherent commits with stable task IDs in commit messages where practical.
- Avoid committing credentials, API keys, private data, transient caches, model downloads, or unnecessary embeddings.
- Decide how large binary assets and source vaults should be stored before committing them.
- Do not move or upload large source vaults without checking size, privacy, licensing, and repository limits.
- Record actual commands and tool versions where relevant.

## Setup documentation to complete

Once the actual environment is known, document:
- required runtimes and versions;
- dependencies and installation commands;
- configuration files and safe defaults;
- environment variables without exposing secrets;
- inventory/extraction commands;
- registry migration and validation commands;
- test and audit commands;
- checkpoint/resume procedure;
- backup and restore;
- troubleshooting and known limitations.

## Recovery

If a session is interrupted:
1. inspect Git state and uncommitted changes;
2. inspect checkpoint and task queue;
3. validate registry integrity;
4. rerun the last task's deterministic validation;
5. identify outputs that are complete, partial, or invalid;
6. resume from the last verified boundary or safely rerun the bounded task;
7. record the recovery in the handoff.

Never infer that a task completed because an output file exists.
