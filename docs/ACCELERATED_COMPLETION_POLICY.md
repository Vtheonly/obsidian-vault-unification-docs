# Accelerated Completion Policy

**Status:** BINDING. User directive 2026-11-01, recorded as ADR-0012, enforced
through AGENTS.md §12. Every session operating this repository — orchestrator
or subagent — must read this file before planning work.

**Relationship to other contracts:** this policy changes HOW FAST the project
runs, never WHAT must be true at delivery. Where an older document implies a
slower universal mode (universal dual review, per-session byte replays,
multi-commit bookkeeping, unbounded phase durations), this policy controls.
Where this policy is silent, AGENTS.md, `docs/VERIFICATION_SPECIFICATION.md`,
and `docs/MILESTONES_AND_ACCEPTANCE.md` control unchanged. Nothing in this
policy licenses violating §6 (quality floor) or the preservation contract in
AGENTS.md §3 and §7.

## 1. Directive

Verbatim user direction (2026-11-01):

> "remove the universal review and do it fast then"
> "the final vault should be done in less than 12 additional sessions"

and (same day, follow-up):

> "make new policy to ensure the next agent follow the new decision of
> becoming faster"

The mission is unchanged: synthesize both source vaults into one coherent,
consistently structured, fully verified vault, preserving every meaningful
detail. The identified failure mode was structural — endless review batches,
checkpoints, replays, and handoffs while synthesis is perpetually deferred.
This policy exists to make that failure mode a documented violation instead of
a habit.

## 2. Budget contract

- **Base:** session 16 was the first session under the directive.
- **Hard deadline:** the final vault is delivered by the **end of session 26**
  (sessions 16–26 = 11 sessions, the strict reading of "less than 12
  additional"). The session-16 handoff's "session 27" wording was the looser
  reading; this policy adopts the stricter one and controls.
- **Phase allocation (targets, not deadlines to slip against):**

| Sessions | Phase | Deliverable metric |
|---|---|---|
| 17 | Policy binding (this session; user-directed) | this policy + AGENTS.md §12 + ADR-0012 |
| 18–20 | Dossier-extension classification | pairs classified / 69,185 (six domains) |
| 21–22 | Disposition assignment | KU dispositions / 27,536; Unaccounted → 0 |
| 23–25 | Gated synthesis | canonical notes generated + gated; 3 confirmed gaps given dedicated treatment |
| 26 | Final verification and delivery | release-gate predicates n/n; final audit |

- Overrunning a phase target triggers §5 recovery (compress via wider
  calibrated tiers, more automation, more parallelism), never a silent
  deadline slip. Only the user may extend the deadline (§9).
- Every session states its budget position at start and end: session number,
  sessions consumed, sessions remaining (see §8 ledger).

## 3. Deliverable-first measurement

Progress is **only** these metrics, each with an explicit denominator:

1. dossier-extension pairs classified / **69,185** (per domain: regression
   9,211; tree-based 10,833; evaluation 10,603; clustering 6,672;
   generalization 11,275; training-stability 20,591);
2. KU dispositions assigned / **27,536** (release requires Unaccounted = 0);
3. synthesis release-gate predicates satisfied (n/n, enumerated in
   `docs/MILESTONES_AND_ACCEPTANCE.md`);
4. canonical notes generated and verified / planned notes;
5. final verification pass rate.

The following are **never** progress and must never be reported as
achievement: sessions or batches started/finished, checkpoints written,
indexes rebuilt, replays re-run, handoff documents updated, reports produced,
ADRs filed, tooling polished without a pipeline need.

**Failed-session rule:** a session whose only output is bookkeeping — no
deliverable metric moved — is a FAILED session under this policy. Its
checkpoint and report must say so explicitly, with cause and correction. One
failed session is recoverable; hiding it is a violation of the honesty
contract.

## 4. Speed rules (authorized removals and streamlines)

1. **Universal dual review is REMOVED.** Verification is tiered per ADR-0011:
   (a) every confirm_gap and merge decision: individual semantic review +
   independent cross-check + independent re-verification; (b) mechanical bulk
   classes: admissible only with zero counter-examples in the calibration
   set, then 5% random sample (min 30) re-verified per applied batch, any
   sample disagreement pulls the whole class back to individual review;
   (c) the residual class: orchestrator individual review with probe evidence
   bundles, no universal subagent re-check.
2. **Rejected units get rationale only.** No citation verification on rejects
   (outside the tier-(b) samples). Verification effort concentrates on
   accepts/covers and gap decisions — the outcomes that can affect knowledge.
3. **Replay and byte-identity checks are periodic, not per-session.** Run the
   full decide/classify-chain replay when (i) ~10 new decision rounds have
   accumulated, (ii) discovery/extraction code changed structurally, or
   (iii) a regression is suspected. The **source-vault manifest check remains
   every session** (cheap; immutability is a floor item, §6).
4. **Continuous commit-and-push is mandatory** (AGENTS.md §13): commit each bounded, coherent, checked unit and push it immediately; do not wait until session end. Keep the unpushed window near zero and verify the remote ref after every push. This replaces the former one-work-commit-per-session cadence. Do not create recursive bookkeeping commits merely to record a push; record verification in the existing checkpoint/handoff.
5. **Checkpoints are lightweight JSON every session; full handoff rewrites
   only at phase boundaries** (or on user-directed course changes). Mid-phase
   sessions update only the handoff's session-ledger row and next-task
   pointer if stale.
6. **Scratch and replay chains stay scripted and idempotent**
   (delete-as-consumed pattern). If sandbox recycling deletes them, re-run
   the recorded script; never hand-rebuild.
7. **Regeneration before consultation:** before asking the user anything,
   check whether the repository or a script already answers it.
8. **Subagents are for parallel review/generation slices** (session-16
   pattern), with mechanical verification of every cover citation, reject
   sampling, and personal re-check of flagged borderlines. Do not spawn
   subagents for bookkeeping, and do not trust their outputs unverified.

## 5. Anti-stall rules

1. **Synthesis must start no later than session 23** (gates permitting). If
   the dossier or disposition phases threaten this date, compress by widening
   calibrated auto-classes and parallelism — never by skipping calibration,
   safety arguments, or the quality floor.
2. **No new process layers.** The framework is built (v0.9.0, 663 tests). Do
   not invent new universal checks, review tiers, registries, indexes, or
   reporting artifacts without explicit user approval recorded as an ADR.
   Extend tooling only for concrete pipeline needs.
3. **No re-performance of verified work.** Completed reviews, replays, and
   validations are not re-run "for confidence" without a regression trigger.
4. **Blocked → bounded workaround + record.** Do not spend a session on
   meta-analysis. If the primary metric is blocked, advance a different
   deliverable metric in the same session.
5. **Deadline–floor conflicts are escalated, never resolved by weakening.**
   If the quality floor and the deadline cannot both hold, stop, quantify the
   conflict, and request a minimal concrete extension from the user. Silent
   deadline slip or silent floor weakening are both violations.

## 6. Quality floor (inviolate)

Speed removes redundant process, never preservation or evidence:

1. Source vaults are immutable; manifest byte-check at every session start
   (276/276 AI Course, 333/333 Master AI expected).
2. Full test suite green at session start (after the editable install) and
   re-run after the session's last mutation. Never weaken tests to pass them.
3. Every accepted/cover citation is machine-verified against the corpus;
   every confirm_gap decision keeps full individual probe discipline
   (ADR-0011 binding 3: glossaries, quiz Group-B lines, notation symbol
   glosses, operational definitions, spelling variants, colon-glosses).
4. Delta-verification with pre-written arithmetic for every state transition.
5. Unaccounted KUs block release; all release gates in
   `docs/MILESTONES_AND_ACCEPTANCE.md` must pass before the project is called
   complete.
6. Honesty: no invented completion, no fabricated evidence, explicit
   non-claims preserved (e.g. the 46,978 low-signal exclusion remains
   documented, not silently "resolved").
7. Every completion claim carries a report path or recorded test run.

## 7. Session compliance checklist (enforcement)

**Session start:**
1. Read AGENTS.md → this policy → ADR-0011 (docs/RISKS_AND_DECISIONS.md) →
   `docs/agent-handoff/next-agent.md`.
2. Verify baseline: HEAD == origin/main, clean tree, editable install, full
   suite green, source manifests identical.
3. Write down before working: session number, budget sessions remaining, the
   ONE deliverable metric this session will move, and the numeric target.

**Session end:** the checkpoint JSON must include an `accelerated_mode` block:

```json
"accelerated_mode": {
  "session_number": 17,
  "budget_sessions_consumed": 2,
  "budget_sessions_remaining": 9,
  "deliverable_metric_moved": "<metric name or null>",
  "before": <number or null>,
  "after": <number or null>,
  "denominator": <number or null>,
  "failed_session": false,
  "cause_if_failed": null
}
```

**Session report to the user** leads with: (1) deliverable metrics moved with
denominators, (2) budget position, (3) evidence paths. Bookkeeping is listed
last, if at all.

## 8. Session ledger (append one row per session)

| Session | Date | Deliverable moved | Result | Remaining (of 11) |
|---|---|---|---|---|
| 16 | 2026-11-01 | signal-pool candidates decided | 4,274/4,274; pool verified empty; 667 covers, 3,607 rejects, 0 new gaps | 10 |
| 17 | 2026-11-01 | policy bound (user-directed) | this policy + AGENTS.md §12 + ADR-0012 committed | 9 |
| 18 | 2026-11-01 | dossier-extension pairs classified | 69,185/69,185 (5,441 participate / 63,744 reject-pair; 5,168 participant KUs; 294 extension records; tiered ADR-0011 pipeline, 2 calibration pull-backs, 4 review rounds) | 8 |
| 19 | 2026-11-01 | KU dispositions assigned | 27,536/27,536; Unaccounted = 0 (Preserved 18,478 / Consolidated 8,106 / Contextualized 950 / Superseded 2; ADR-0014 rule engine + synthesis mapping 609 files / 544 notes + dossier v2 + F-0022 repair + F-0023 fix) | 7 |
| 20 | 2026-11-02 | canonical notes generated + verified (area 04 end-to-end) | 27/544 notes green through lint/assess/drift/gate + audit-output 0 findings over 1,829 KUs; framework F-0024..F-0029 fixed (708→725 tests, pilot re-verified 12/12); editorial conventions v1 recorded | 6 |
| 21 | 2026-11-02 | canonical notes generated + verified (areas 05 + 06 end-to-end) | 127/544 notes (21 + 79); both audits valid=true 0 findings over 7,394 KU memberships (5,686 math + 3,929 term + 554 code markers verified present); gates pass (4 evidence-backed drift waivers); lint 0 errors/6 documented source-format warnings; F-0030/F-0031 fixed (725→740 tests, pilot re-verified 12/12); pipeline generalized (AREA_CONFIG) + reusable s21_run_gates.py | 5 |
| 22 | 2026-11-02 | canonical notes generated + verified (areas 07 + 08 + 09 end-to-end) | 190/544 notes (14 + 38 + 11); all three audits valid=true 0 findings over 2,692 KU memberships (9,979 markers verified present: 7,793 term + 2,073 math + 113 code); gates pass (3 evidence-backed drift waivers, content-family artifacts with source math-density measurements); lint 0 errors/7 documented warnings (1 real defect repaired); F-0032 fixed (740→744 tests, pilot re-verified 12/12); 22 subagent groups + anchored 3-round repair chain; one server-shutdown interruption recovered with zero data loss | 4 |
| 23 | 2026-11-03 | canonical notes generated + verified (areas 10 + 11 + 12 + 13 + 14 end-to-end) | 259/544 notes (7 + 13 + 12 + 11 + 26); all five audits valid=true 0 findings over 3,252 KU memberships (15,538 markers verified present: 14,521 term + 838 math + 179 code); gates 5/5 pass (3 evidence-backed concept-type drift waivers with source math-density measurements: area-10/11/12; areas 13-14 clean, no waiver); lint 0 errors/17 documented warnings (7 pre-existing + 9 verbatim-source artifacts + 1 restored source TODO placeholder); 33 subagent groups (5 waves incl. orientation wave), 28 + 5 round-2 anchored marker repairs + 2 lint fence-label repairs (F-0031 precedent); 744/744 tests at start and end; sources 276/333 immutable at start and end | 3 |

## 9. Amendment

- **Only the user** may: extend the deadline, weaken the quality floor, add
  phases, or reauthorize universal review.
- Agents may propose changes via an ADR with impact analysis. Tightening that
  demonstrably does not delay the deadline needs no approval; any loosening
  needs explicit user approval.
- This policy self-expires at delivery: after the final vault passes its
  release gates, normal change control resumes.


## 10. Continuous commit-and-push persistence (USER DIRECTIVE — BINDING)

The user explicitly requires that progress be pushed continuously so it is visible and recoverable if a session is interrupted or terminated. This is a persistence requirement, not an optional workflow preference.

- **Commit after each bounded, coherent unit of work**, once its applicable checks pass, and **push that commit immediately**. Do not wait for session end, a phase boundary, or the final handoff.
- Keep at most one newly created commit unpushed whenever technically possible. Push before creating the next commit.
- For long-running tasks, create recovery boundaries before risky/long operations and delegation, and after each independently recoverable batch. Push each checkpoint immediately.
- The canonical destination is `origin/main`. If direct pushes are prohibited by branch protection, push the active head branch immediately and merge it into `main` as soon as checks and approvals permit. Do not leave completed work stranded on a feature branch.
- After every push, fetch/inspect the remote ref and verify that the intended commit is reachable from it. Record SHA, branch, result, and verification evidence in the existing checkpoint/session record or handoff.
- On rejection or concurrent remote movement: fetch, inspect, merge/reconcile without discarding either side, rerun affected tests, push, and verify. **Never force-push** to make the remote match a local branch.
- A local commit is not durable progress until the remote contains it. If authentication or connectivity prevents pushing, stop accumulating changes, preserve a safe local checkpoint if possible, and report the precise blocker.
- Never embed PATs or other credentials in prompts, tracked files, logs, or command history. Use secure authenticated Git credentials or environment/secret storage. Never ask the user to paste a token into a tracked file.
- Do not create recursive bookkeeping commits just to record that a push-verification record was itself pushed. Verify the remote ref and record evidence in the existing session artifacts.

**Precedence:** This section and AGENTS.md §13 supersede §4.4's former one-work-commit-per-session cadence and any older session-end-only push wording. They do not authorize committing known-broken work, weakening tests, or adding bookkeeping-only sessions. The accelerated deliverable and quality-floor rules remain binding.
