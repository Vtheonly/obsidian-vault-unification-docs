# Iteration Retrospective — Pre-Synthesis Phase (EXT-001..EXT-010 + Phase 0 Restart)

Task ID: RETRO-001 (mandated by the 2026-10-27 user direction, item 2)
Compiled: 2026-10-27, from repository evidence only (git history, state/findings.jsonl, reports/, worklog, task queue, test-suite runs). No memory, no assumptions.

Purpose: learn from the entire previous iteration before rebuilding the pipeline. Every issue below carries evidence, root cause where known, impact, fix status, the regression test that pins it, and remaining risk.

---

## A. Process failures (how work was recorded and handed off)

### A-1. "Completed" status recorded before commit — the interrupted session
- **Evidence**: `state/task-queue.jsonl` (pre-repair) marked REBASE-000/AUDIT-011/FRAME-001/DISC-001 `status: completed` with `completed_utc: 2026-10-27`, while `git status` showed the entire framework refactor uncommitted; local HEAD == origin/main == 460d7d5 (docs only). The four records carried `commit: null`.
- **Root cause**: the session was interrupted mid-flight between "update queue" (13:36) and "commit+push"; the queue edit jumped ahead of the commit that would justify it.
- **Impact**: the repository's own task records claimed work as done that did not exist in git — exactly the "documentation vs reality" failure mode the project charter forbids.
- **Fixed**: yes (this session). Records repaired to schema-conformant form; completion now recorded with the real work-commit hash only after the commit exists.
- **Regression test**: `tests/test_repo_state.py::TestRepositoryState::test_task_queue_cross_checks_pass` (schema + cross-checks) — it caught the breakage; it stays as the guard.
- **Remaining risk**: an agent can still edit the queue before committing. Mitigation is procedural (queue completion only after the feat commit hash exists).

### A-2. Final state edit invalidated the recorded test run
- **Evidence**: the interrupted session's `reports/rebaseline/frame001-disc001-final-pytest.json` (13:29) shows 486/486 passed; the task-queue edit at 13:36 then broke schema validation; my re-run found 482 passed / 4 failed. The 486/486 claim was true at 13:29 and false at 13:37.
- **Root cause**: no "re-validate after last state change" step in the session's closing protocol.
- **Impact**: 4 failing repo-state tests would have been pushed as "green suite".
- **Fixed**: yes — suite re-run green (563/563) after queue repair; this report records both runs.
- **Regression test**: the repo-state tests themselves.
- **Remaining risk**: same class as A-1 — always re-run the suite after the last mutation, before claiming results.

### A-3. Evidence quotes were once hand-typed (EXT-005..009 class)
- **Evidence**: EXT-009 review finding R2 (KU-id misattribution from hand-typed line numbers); EXT-010 worklog: "NEW X2 machine-locator … eliminates the EXT-009 R2 error class; first run caught five defects that hand-typing had introduced".
- **Root cause**: classification scripts located evidence by manually typed line numbers.
- **Impact**: 5 caught defects in EXT-010 alone before the locator existed; unknown number latent in earlier batches.
- **Fixed**: yes — FRAME-001 migrated the X2 locator into `vault_unification.locators` (L-13) with 15 dedicated tests; discovery candidates use it.
- **Regression test**: `tests/test_locators.py` (unique-occurrence requirement; loud failure on ambiguity).
- **Remaining risk**: new tooling that cites line numbers must be forced through locators (code-review discipline).

### A-4. Independent review subagent caught real defects every time it ran
- **Evidence**: EXT-010-REVIEW verdict PASS-WITH-NOTES: S2 KU-id misattribution caught by the orchestrator's re-verification; F-0009 recording gap (R1) caught by the reviewer; EXT-005 review confirmed committed work while push was blocked.
- **Root cause**: n/a (this is a positive finding).
- **Impact**: the review step is non-negotiable for committed classifications; skipping it for speed would have shipped errors.
- **Fixed**: institutionalized — forbidden_side_effects in queue records include "Do not skip the independent review".
- **Remaining risk**: none identified; keep the pattern for synthesis-time decisions.

---

## B. Framework defects (verified, fixed in FRAME-001 / this session)

| id | defect | evidence | fixed by | pinned by |
|----|--------|----------|----------|-----------|
| L-01 | no multi-line phrase search | docs/TOOLING_FRAMEWORK.md limitation; search.py per-line loop | `search.search_phrase` + span locators | tests/test_search.py (14 new) |
| L-02 | folder links reported broken (F-0003: 175) | frame001-ai-course-linkcheck.json: 121 broken + 54 folder_link = 175 exactly | folder-indexed resolver, `folder_link` evidence class | tests/test_linkcheck.py (7 new) |
| L-03 | O(links × re-parse) made Master AI check impractical (never run) | F-0011: first-ever check, 2.16 s for 333 files | per-run caches | tests/test_linkcheck.py |
| L-04 | inline-math recount disagreed with authoritative state machine in unclosed-fence files | mdextract.py second naive scan | single authority recount | tests/test_mdextract.py (4 new) |
| L-06 | block-id loose substring false positives | linkcheck strict `^id` at EOL | strict matcher | tests/test_linkcheck.py |
| L-07 | term-stats substring false positives ('ridge' in 'bridge') | F-0006 class | shared `boundary_pattern` authority (CAP-013-consistent) | tests/test_search.py |
| L-08 | no atomic writes (torn-output risk on interrupt) | pathsafety.py | atomic write helpers | tests/test_pathsafety.py (6 new) |
| L-12 | NO emergent-concept discovery capability | no discovery module pre-DISC-001 | `discovery.py` (916 lines, 25 tests, real-corpus run: 6,340 candidates, coverage-gated) | tests/test_discovery.py |
| F-0010 | 54 of F-0003's "broken" links were intentional folder links | findings.jsonl F-0010 | L-02 fix; reclassified | lint census cross-check (121 exact) |
| F-0011 | Master AI first link check: 338 broken + 29 ambiguous | findings.jsonl F-0011 | surfaced for synthesis disposition | lint census cross-check (338 exact) |

Cross-validation note: this session's independent artifactlint implementation reproduces the FRAME-001 linkcheck numbers EXACTLY (121 / 338) — two independent code paths, same counts.

## C. Source-corpus characteristics (constraints on synthesis, not defects)

From the FRAME-002 baseline lint (reports/rebaseline/frame002-lint-{ai-course,master-ai}.json):
- **AI Course (276 files)**: 164 errors — 121 broken links, 19 python-block syntax errors, 14 unclosed fences, 10 missing anchors; 152 warnings (79 mid-sentence endings, 54 unbalanced brackets outside code, 15 heading skips).
- **Master AI (333 files)**: 371 errors — 338 broken links, 29 ambiguous basenames, 3 python syntax; 950 info notes (762 empty sections, 188 unlabeled fences).
- Implication: the unified vault's link/disposition pass and the repair loop have real work queued; the numbers above are the pre-synthesis baseline to improve on.

## D. Tooling gaps closed this session (FRAME-002, user-mandated)

| gap | user requirement | delivered | tests |
|-----|------------------|-----------|-------|
| artifact integrity validation (fences, math, tables, headings, links, mermaid, code, truncation, placeholders) | item 6 | `artifactlint.py` + `vu lint-artifacts` + artifact-defect schema; 25 check families | 43 |
| note quality assessment + drift detection | item 4 | `notequality.py` + assess-quality/quality-drift; 7 note types, 9 dimensions, evidence-carrying scores, tertile drift with per-dimension evidence | 14 |
| batch quality gates | items 5, 8 | `vu quality-gate`: expected-notes, lint-clean, per-dimension bands, drift explanation, explicit waivers; per-note failure enumeration (averages can't hide failures) | 6 |
| targeted repair loop | item 7 | `repair.py` + repair-create/record/verify/list/prompt; bounded retries, regression re-opening, diff-scope discipline (anti-rewrite guard) | 13 |
| prompt precision checking | item 5 | `promptspec.py` + `vu check-prompt`; testable criteria, vague-language rejection, ku_id resolvability, context budget, requirements cap | 12 |
| CLI integration | — | 10 new commands, all path-safety checked | 8 end-to-end |

## E. Accepted, documented limitations (do not re-litigate without new evidence)

- L-05 setext headings unsupported (no corpus evidence of use).
- L-06 partial: percent-encoded markdown links matched literally (deferred pending corpus evidence).
- L-09/L-10/L-11: no TOCTOU re-check after resolve, no concurrent-run lock, search not indexed — accepted for single-agent operation; revisit if parallelism is introduced.
- Mermaid validation is a structural line-grammar heuristic, not a full AST; rendering validation is out of scope for now (recorded in every lint report's caveat).
- Semantic quality (correctness, adequacy) remains a review decision — the tools prepare evidence, they do not judge.

## F. Lessons for the next iteration (the pipeline restart)

1. **Queue completion only after the commit exists** — the record's `commit` field must point at real work.
2. **Re-run the full suite after the LAST mutation** of a session, never before.
3. **Every generation batch goes through**: check-prompt → bounded generation → lint-artifacts → assess-quality → quality-drift → quality-gate → repair loop for failures. A batch is complete only when its gate passes or exceptions are explicitly waived with reasons.
4. **Watch the drift detector's tertile comparison as batches accumulate** — the polished-early/thin-late pattern (user-observed in the larger source vault) must be caught at batch 2, not after 500 notes.
5. **Machine locators for every line citation** (locators.py X2 rule).
6. **Preserve sources immutably** — all lint/assessment outputs are evidence ABOUT sources, never edits OF sources.
7. **Two-commit pattern** (feat + state-with-hash) with push verification each time.
