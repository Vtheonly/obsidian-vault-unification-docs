# Mandatory Agent Instructions

## 1. Mission

Reconstruct two large Obsidian vaults into one coherent, self-contained, consistently structured, high-quality knowledge vault by synthesizing and rewriting their combined knowledge. This is a long-running project executed across multiple fresh Z AI / GLM 5.3 sessions, potentially with subagents.

This may be the first session or a continuation. Never assume either. The repository and its verified records—not conversational memory—are the source of truth.

## 2. Mandatory startup protocol

Before making changes:

1. Inspect the current Git repository, branch, commit, working tree, and available files.
2. Read this file in full.
3. Read `README.md` and the relevant canonical documents in `docs/`.
4. Inspect the actual task queue, checkpoint, knowledge registry, current findings, reports, and latest handoff.
5. Verify prior completion claims against files, commit history, registry entries, and actual test evidence.
6. Identify the highest-priority valid unfinished task and its dependencies.
7. If state is missing, inconsistent, or untrustworthy, repair the project state safely before proceeding. Do not guess that work is complete.
8. Work only within a defined scope with explicit inputs, outputs, acceptance criteria, and forbidden side effects.

## 3. Non-negotiable preservation rules

- Both source vaults are immutable inputs during processing. Do not edit, delete, rename, or reorganize source files.
- Do not concatenate the vaults as the final solution.
- Generate a separate output vault with newly synthesized, coherent notes.
- Every source file, asset, and extracted knowledge unit must receive a recorded outcome.
- Never ignore material because it is short, obscure, unfamiliar, repeated only once, absent from a known topic list, or apparently unimportant.
- The user's examples (CNNs, VGG, attention, Transformers, deep neural networks, loss functions) are illustrative, not an exhaustive topic list or permission to prioritize only familiar concepts.
- Preserve meaning, assumptions, exceptions, equations, derivations, examples, implementation details, project insights, references, historical distinctions, and contextual information.
- Never silently discard unique details.
- A polished rewrite is not proof of preservation. Independent evidence-based verification is mandatory.
- Do not invent completion, test results, source evidence, or confidence.
- Never weaken tests merely to make them pass. Changes to acceptance criteria require documented justification and change control.

## 4. Editorial consistency

Every note must follow the same global editorial contract, adapted appropriately to its content. Maintain consistent folder hierarchy, filenames, numbering, titles, heading levels, section ordering, terminology, prose quality, formatting, mathematical conventions, code formatting, references, and Obsidian links.

Do not make the first notes excellent and later notes rough, bullet-only, shallow, or inconsistent. Every note receives equivalent editorial care. Equal care does not require identical note length or identical section templates; it requires the same quality bar appropriate to the content.

The canonical style guide is `docs/EDITORIAL_STYLE_GUIDE.md`. Agents must not invent competing standards. Proposed global changes must be documented, impact-assessed, and followed by appropriate corpus-wide consistency checks.

## 5. Multi-session operation

Each session must do the best verifiable bounded work possible without treating context-window exhaustion as a target. Save progress before context quality degrades. At session end, persist:
- actual completed work and exact changed paths;
- task and knowledge-unit state;
- commands and tests actually run, with results;
- unresolved findings and blockers;
- commit and working-tree state;
- next task, dependencies, inputs, outputs, and acceptance criteria;
- exact resume instructions.

The next session must verify the handoff against the repository. Do not rely on chat history. Do not restart the entire project or repeat completed work unless evidence shows it is invalid, incomplete, or regressed.

## 6. Subagents

Use subagents when they materially improve parallelism or independent review. Assign bounded scopes with clear input/output contracts. Prevent conflicting writes to shared files. Treat subagent results as unverified until reviewed. The orchestrator owns integration, consistency, tests, state updates, and handoff. Do not spawn agents merely to increase their number.

## 7. Verification and acceptance

Follow `docs/VERIFICATION_SPECIFICATION.md` and `docs/MILESTONES_AND_ACCEPTANCE.md`. Separate:
- file/asset inventory;
- extraction completeness;
- knowledge accounting;
- semantic preservation;
- technical correctness;
- editorial consistency;
- final integration acceptance.

`Unaccounted` source knowledge blocks acceptance. `Needs review` must remain visible and must prevent claims of complete semantic verification where it could affect correctness. Every reported metric needs a defined denominator and method. File processing is not proof of knowledge preservation; accounting is not proof of semantic correctness.

## 8. First-session behavior

If the project is genuinely at its beginning, establish the infrastructure first: read-only source inventory, asset and extraction report, persistent registry/task queue/checkpoint, style specification, test harness, and an omission-detection pilot. Do not immediately attempt to rewrite both entire vaults.

If the project is already underway, validate its state and continue from the last verified checkpoint.

## 9. Completion report

At every session end, report:
1. Task ID and status.
2. Work completed and exact paths.
3. Tests/commands executed and real outcomes.
4. Verification coverage and limitations.
5. Open findings, risks, blockers, and decisions.
6. Git/working-tree state.
7. Next task and precise resume procedure.

Do not claim the overall project is complete until all release gates pass.


## 10. Mandatory framework-first execution and continuous tool-building

The project must be operated through a Python tooling framework that the agent itself builds and evolves in this repository. The framework specification is [docs/TOOLING_FRAMEWORK.md](docs/TOOLING_FRAMEWORK.md); it is a requirement, not evidence that implementation already exists.

- Before doing manual repetitive work, check whether a framework command already supports it. If not, determine whether a reusable deterministic tool should be added before proceeding.
- Do not use model attention/context as the source of truth for file counts, folder existence, hashes, exact/fuzzy search results, term frequency, link validation, duplicate detection, registry integrity, provenance joins, test outcomes, or regression comparisons when code can compute them.
- The agent owns framework implementation: design, code, tests, CLI/help, documentation, integration, maintenance, and incremental expansion. Do not expect the user to supply the framework.
- Build a small reliable foundation first, then add capabilities as concrete project needs emerge. Each tool must have defined inputs, outputs, exit behavior, error handling, and tests.
- Tool output must be machine-readable where practical (JSON/JSONL/CSV plus a human-readable summary), reproducible, and explicit about scope, denominator, exclusions, and failures.
- A successful command is not automatically proof of semantic correctness. Keep deterministic checks, AI-assisted review, and independent acceptance as separate evidence classes.
- Never invent a command's result or claim a test passed unless it was actually run. Preserve logs/reports sufficient for another session to verify it.
- Every new tool or change must include unit tests, appropriate integration/regression tests, a documentation update, and a check that existing tools still work. Test failure paths and malformed inputs, not only happy paths.
- Do not let the framework silently mutate either source vault. Source operations are read-only by default; output-writing commands must require explicit destination paths and guard against source/output overlap.
- Before large-scale synthesis, complete the framework foundation and an omission-detection pilot that demonstrates detection and localization of deliberately injected defects.
- At each session's end, identify repeated manual actions or verification gaps encountered; either add a bounded framework task or document why automation would be unsafe or not worthwhile.

The canonical specification defines initial modules, interfaces, tool lifecycle, testing, reports, and expansion policy. Do not create competing undocumented tool inventories.

## 7. Corpus-Scale Preservation Contract (Expanded)

The source corpus is expected to exceed five million tokens and to contain thousands of notes, code examples, equations, diagrams, project logs, and interview-preparation material. Treat that scale as a planning constraint, not as permission to sample, summarize, or skip content.

### 7.1 Source asymmetry
- Vault A is the rich, iterative, noisy source: it may contain deeper mathematics, full derivations, implementation details, debugging lessons, inference optimizations, interview questions, and historical/API caveats, mixed with repetition and conversational wording.
- Vault B is the comparatively uniform, concise source: it may have better hierarchy and consistency while omitting extensions, proofs, edge cases, project-specific knowledge, and implementation nuance.
- Neither source is the winner. The target is synthesized from both. Never infer that a detail is unimportant because it appears once, in an awkward paragraph, in an unfamiliar topic, or in only one vault.

### 7.2 No selective excellence
Apply identical extraction, synthesis, and verification standards to every domain and note. Familiar examples such as CNNs, VGG, attention, Transformers, deep neural networks, and loss functions are examples only. Rare footnotes, isolated equations, obscure hardware constraints, and one-off failures must receive equal care.

### 7.3 Overlap and disposition are separate decisions
Classify relationships between overlapping content as exactly one of: Exact Duplicate, Semantic Duplicate, Partial Overlap, Complementary Content, or Conflict or Historical Difference. Separately assign each knowledge unit a disposition: Preserved, Consolidated, Contextualized, Superseded (with rationale and unique information retained), Needs review, or Unaccounted. Do not confuse an overlap classification with a disposition. Any Unaccounted unit blocks release.

### 7.4 Synthesis evidence contract
Before drafting a canonical note, assemble a concept dossier from all related evidence. Cover, where applicable: definitions; mathematical foundations and proofs; computational mechanics; alternative explanations; worked examples; code implementations; practical applications and project insights; interview pitfalls; historical/era-specific material; and critical distinctions. Record source locators and evidence links for every meaningful claim. A source-note citation alone does not prove that every claim inside it was accounted for.

### 7.5 Hard gates
Large-scale synthesis is prohibited until both conditions have verified evidence:
1. Framework foundation: a working, tested Python package and CLI with path-safety enforcement, recursive inventory and hashing, search/counting, link validation, and machine-readable reports.
2. Omission-detection pilot: a synthetic fixture with intentionally removed or corrupted details demonstrates detection and exact localization of every injected defect, including obscure derivations, project caveats, equations, and broken links.

Do not mark either gate passed based on documentation, planned tests, or an agent's own unsupported assertion. Preserve command, exit code, report path, scope, and limitations.

### 7.6 Non-destructive repair
Audits must produce findings tied to source knowledge-unit identifiers and target destinations. Repairs are narrow: modify only the affected note/section, preserve accepted material, rerun relevant tests and regression checks, and cap retries at three. After three unsuccessful attempts, quarantine as Needs review, explain the blocker, and hand it off rather than looping or silently dropping the unit.

### 7.7 Honest state and handoffs
Never state that source vaults have been located, inventoried, backed up, protected, or processed unless repository evidence confirms it. Never claim tests passed unless they were actually run. At every session end, update the task queue, checkpoint, registry when applicable, reports, and canonical session handoff with exact paths, commands, real exit codes, metrics, blockers, and the next bounded task.

## 11. Authorized Phase 0 re-baseline (2026-10-27)

The user explicitly authorized a controlled restart of the knowledge-processing pipeline. Follow [docs/PHASE_ZERO_REBASELINE_AND_FRAMEWORK_REFACTOR.md](docs/PHASE_ZERO_REBASELINE_AND_FRAMEWORK_REFACTOR.md) and the revised [ENTRY_PROMPT.md](ENTRY_PROMPT.md).

Return to Phase 0, audit actual repository evidence, rerun verification, enumerate findings and capability limitations, refactor the real Python framework, implement and test integrated emergent-concept discovery, then revalidate/re-extract the corpus and rediscover concepts before synthesis.

This directive authorizes revalidation and regeneration of derived artifacts, not deletion of the repository or valid history. Preserve source vaults byte-for-byte. Reuse derived artifacts only after they pass the new checks; otherwise recompute, migrate, quarantine, or retire them with rationale. Preserve task history and add valid tasks to the existing queue. Do not synthesize canonical notes until framework, full extraction/accounting, concept-discovery, and dossier gates pass. Documentation alone is not implementation; never claim tests passed unless actually run.

## 12. Accelerated completion policy (user directive 2026-11-01 — BINDING)

This project operates under [docs/ACCELERATED_COMPLETION_POLICY.md](docs/ACCELERATED_COMPLETION_POLICY.md) (ADR-0012). Read it immediately after this file, before planning any work. Headline bindings:

- **Deadline:** the final vault is delivered by the end of session 26 (user: "less than 12 additional sessions"; session 16 was the first under the directive).
- **Deliverable-first measurement:** progress is only the metrics enumerated in the policy (dossier pairs classified / 69,185; KU dispositions assigned / 27,536; release-gate predicates; verified canonical notes; final verification pass rate). Checkpoints, indexes, replays, handoffs, and reports are never progress. A bookkeeping-only session is a FAILED session and must be reported as one.
- **Tiered verification only:** the universal per-unit dual review is REMOVED (ADR-0011). Do not reinstate it or invent equivalent process layers, registries, or reporting artifacts without explicit user approval recorded as an ADR.
- **Anti-stall:** synthesis must start no later than session 23. Verified work is not re-run without a regression trigger. A blocked phase is compressed via wider calibrated tiers and parallelism, never by skipping calibration or weakening checks.
- **Quality floor is inviolate:** source immutability with per-session manifest checks; full test suite green at session start and after the last mutation; machine-verified citations for every accept/cover; full individual probe discipline for every gap decision; delta-verification with pre-written arithmetic; Unaccounted KUs block release. If the deadline and the floor conflict, escalate to the user — never weaken the floor, never silently slip the deadline.
- **Compliance:** every session checkpoint includes the `accelerated_mode` block defined in the policy (session number, budget remaining, deliverable metric moved with before/after/denominator, failed-session flag), and every session report leads with deliverable metrics and budget position.

Where an older document in this repository implies a slower universal mode, this section and the policy control on matters of speed and process overhead; they never license weakening the preservation contract (§3, §7) or the verification and acceptance rules (§7 of this file, `docs/VERIFICATION_SPECIFICATION.md`).




## 13. Mandatory continuous commit-and-push persistence (USER DIRECTIVE — BINDING)

Git persistence is continuous, not a session-end activity. The canonical remote branch is `main`. This rule applies to the orchestrator, every fresh session, and every subagent that is authorized to modify repository files.

1. **Commit and push each bounded, coherent unit of work immediately.** Do not accumulate a large batch of uncommitted work, and do not wait for the session to end. As soon as a meaningful unit is complete and its applicable checks pass, create a descriptive commit and push it to `origin/main` (or push the active work branch immediately if repository policy requires a branch, then merge it into `main` promptly).
2. **Keep the unpushed window as close to zero as possible.** After every commit, push immediately. Do not create a second commit while the previous commit remains unpushed, except when a technical limitation makes that unavoidable; if unavoidable, stop adding work, explain the blocker, and push the pending commits as soon as possible.
3. **Create recovery checkpoints during long tasks.** Before risky operations, long-running batches, context-heavy work, or delegation, commit and push the current verified state. During a long task, split work into independently recoverable units and push each completed unit. Do not leave generated deliverables, reports, state transitions, repairs, or handoff updates stranded only in the session workspace.
4. **Verify every push.** After pushing, fetch the remote and verify that the intended commit is reachable from the remote branch and that the remote head contains the commit. Record the commit SHA, branch, push result, and verification evidence in the existing checkpoint/session record or handoff. A successful local commit is NOT proof of a successful push.
5. **Recover safely from remote movement or rejection.** Never force-push or overwrite remote history to resolve a rejection. Fetch the latest `origin/main`, inspect the divergence, preserve both histories, merge/reconcile, rerun affected checks, then push and verify. If another session has advanced `main`, integrate its work rather than resetting it.
6. **Keep `main` current.** Push directly to `main` when permitted. If branch protection or repository policy requires a head branch/PR, push that head branch immediately and merge it into `main` as soon as the required checks/approval permit. Do not leave completed work indefinitely on an unmerged branch.
7. **Never sacrifice correctness for a push.** Do not commit knowingly broken or unreviewed changes merely to create activity. A recovery checkpoint must represent a coherent, accurately described state; unfinished work may be committed only when it is safe, clearly marked as incomplete, and does not break repository integrity. Run required tests before the work commit and after the final mutation, as applicable.
8. **No credential leakage.** Never put PATs, passwords, private keys, or other credentials in prompts committed to the repository, source files, logs, or command history. Use the authenticated Git credential manager, GitHub App connection, or environment/secret store. Never print a secret. If authentication is unavailable, stop and report the exact blocker; do not request that the user paste a token into a tracked file.
9. **No bookkeeping loop.** Push verification must use remote-ref inspection and existing session records. Do not create endless commits whose only purpose is to record that a previous verification record was pushed. The required behavior is immediate push plus verifiable remote evidence, not recursive verification commits.

This section supersedes any older instruction that implies work may remain local until session end or that limits commits to one per session. The accelerated-completion policy remains in force: continuous commits are small recovery boundaries, not permission to create unnecessary process layers or bookkeeping-only sessions.
