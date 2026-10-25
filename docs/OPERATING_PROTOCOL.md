# Operating Protocol for GLM 5.3 Sessions

## Every session begins with state discovery

1. Inspect Git status, current commit, branches, uncommitted changes, and repository structure.
2. Read `AGENTS.md` and the relevant canonical documentation.
3. Read `state/current-state.json`, the task queue, checkpoint, latest reports, and handoff if they exist.
4. Verify the last task's claims against actual outputs and test evidence.
5. Identify the next valid task, dependencies, risks, and acceptance criteria.
6. If state is missing or contradictory, resolve it conservatively and document the correction.

## Session planning

Select a bounded task with clear inputs, outputs, and stopping conditions. Prefer substantial verified progress over broad, shallow work. Do not aim to consume the full context window. Preserve time/context for integration, testing, checkpointing, and handoff.

A session may stop after a completed task or at a safe checkpoint if blocked. It must not stop with unpersisted critical state.

## Subagent delegation

Use available subagents when helpful. Each assignment must specify:
- task ID and scope;
- exact inputs and evidence to read;
- output paths and expected format;
- acceptance criteria;
- restrictions and forbidden side effects;
- whether work is exploratory, draft, or accepted;
- required tests and reporting.

Do not allow simultaneous uncoordinated writes to the same canonical notes or registry records. The orchestrator reviews outputs, resolves conflicts, runs integration checks, and owns state updates. Subagent completion claims are not verification.

## Task lifecycle

Recommended states:
`queued -> ready -> in_progress -> blocked | review_required | completed`

A task cannot become `completed` until its explicit acceptance criteria and required tests pass. A blocked task records the cause, attempted recovery, and condition needed to unblock it. Keep stable task IDs across sessions.

Each task should record:
- task ID and title;
- status and priority/risk;
- dependencies;
- input paths/record IDs;
- expected outputs;
- acceptance criteria;
- forbidden side effects;
- assigned worker(s);
- test commands and results;
- linked findings and commits.

## Checkpoint discipline

Checkpoint after meaningful work, before risky changes, after completing a task, and before handoff. Include:
- current stage and task;
- last verified state;
- changed paths;
- registry/task counts where available;
- test results;
- unresolved findings;
- Git state;
- safe resume command or procedure.

Avoid checkpoints that merely say “continue working.” They must let a fresh session resume concretely.

## Change control

Changes to architecture, registry schema, editorial rules, acceptance criteria, source policy, or verification thresholds require a documented decision and impact assessment. Migrate records and rerun affected tests. Never silently redefine completion criteria.

## Recommended workflow state machine

`Inventory -> Extraction -> RegistryValidation -> ConceptDiscovery -> ConceptDossiers -> Synthesis -> DeterministicAudit -> SemanticAudit -> Acceptance -> Integration -> RegressionAudit -> ReleaseCandidate`

Failures go to `Repair`, followed by relevant audits and regression checks. Do not skip stages without a documented, justified exception and authorized acceptance.

## End-of-session procedure

1. Finish the task or save a safe checkpoint.
2. Run required tests and record actual output.
3. Review the diff and ensure no source-vault modifications occurred.
4. Update registry, task queue, checkpoint, findings, and reports.
5. Commit a coherent unit of work when repository workflow permits.
6. Write `docs/agent-handoff/next-agent.md` or the canonical handoff path established by the project.
7. Identify the next exact task and its acceptance criteria.
8. Report verified results, limitations, and unresolved issues.


## Framework-first work protocol

Before any sizeable corpus operation, inspect the framework capability inventory and run relevant existing commands. Do not manually count, search, compare, inventory, validate, or calculate results that the framework can deterministically produce.

If a required capability is missing:
1. Create a bounded tooling task with stable ID, use case, input/output contract, safety constraints, acceptance criteria, and regression scope.
2. Implement the smallest reusable tool that safely meets the need.
3. Add unit tests for normal, boundary, malformed, and failure cases; add integration tests when the tool touches files, registry data, or other commands.
4. Add CLI help, machine-readable output, error/exit semantics, and documentation.
5. Run the new tests and relevant existing regression suite.
6. Update the capability inventory, task queue, checkpoint, and handoff with actual evidence.
7. Only then rely on the new tool for the original task.

Do not pause every task to build speculative features. Add tools incrementally when needed, while ensuring the mandatory foundation and omission-detection pilot pass before large-scale synthesis. For unsafe or inherently semantic work, explain why deterministic automation is insufficient and use structured evidence bundles and independent review.

Every task must state whether it builds/changes framework capabilities or consumes existing ones. Any framework change must be reviewed for source immutability, output path safety, deterministic behavior, and regression risk.
