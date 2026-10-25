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


## Required Python framework

The project must maintain a reusable, tested Python CLI under a repository-owned location such as tools/ or src/vault_unification/, with a documented entry point and tests. The agent must choose the exact layout after inspecting the repository and record the decision. See [TOOLING_FRAMEWORK.md](TOOLING_FRAMEWORK.md) for the normative specification.

The framework is built by the AI agent during the project; it is not assumed to exist at bootstrap. The first implementation task is to inspect the environment, create the minimal architecture and test harness, and establish repeatable commands. Never delay this work by beginning full-vault rewriting first.

At minimum, document and provide commands for environment/dependency checks; source/output path safety; recursive inventory and hashing; Markdown/text extraction; exact and normalized search and term statistics; duplicate candidate discovery; heading/code/math/link/embed/attachment checks; registry/task/finding validation; provenance joins; safe chunking/splitting and controlled output; deterministic report generation; regression comparison; and unit, integration, end-to-end, mutation/omission, and acceptance tests.

Each command must have discoverable help, stable output formats, non-zero exit status on actionable failure, useful errors, and tests for malformed input and failure cases. Avoid unnecessary dependencies; pin or constrain dependencies where justified. Provide offline-friendly operation where possible and do not assume network access.

The framework capability list must be generated from or checked against actual code and tests, not maintained as a wish list. Mark capabilities planned, partial, implemented, implemented-and-tested, or blocked, with evidence and limitations. Keep generated data, caches, secrets, embeddings, and large artifacts out of Git unless a documented decision explicitly requires them.

## Tool improvement loop

At the end of each bounded task, ask what repeated manual operation or verification gap appeared, whether a safe deterministic tool can cover it, whether an existing command already covers it, what tests prove a new tool, and which regression checks must run. Create tasks for worthwhile gaps and implement incrementally. Do not build a huge speculative framework in one pass, but do not omit important tools just because they were not anticipated at bootstrap.
