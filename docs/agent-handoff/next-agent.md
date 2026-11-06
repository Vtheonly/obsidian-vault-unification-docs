# Next Agent Handoff

## Project state

**INTEGRATION CAMPAIGN IN PROGRESS (sessions 31–45, user directive commit
`77cf6cf`); S31–S35 COMPLETE — **AUDIT PHASE FINISHED: 1,233/1,233 items
judged (100%)**. The unified vault (544 notes, delivered session 28, gates
green) is being extended with the user's 1,233-item project taxonomy.
**INTEG-006 (S36: decision ledger — A/B/C/D + destination for every item;
integration wave plan) is queued as the next bounded unit.**

- **Campaign plan (binding):** `docs/INTEGRATION_CAMPAIGN_PLAN.md` — §5
  depth standard, §6 A/B/C/D decision rules (D-before-C, collision checks,
  A-quote verification), §7 architecture rules (project hubs, cluster-domain
  notes, provenance markers), §8 session allocation, §9 gates.
- **S34+ S35 (commits 6b62e66, 51023b5, a7a0939 + this session's close):
  SYNPATH+VAULTX 235/235 (36 covered / 6 equivalent / 41 partial / 152
  absent) and remaining clusters 374/374 (150 / 52 / 84 / 88).** Both budget
  sessions ran in one wall-clock session under the adaptive rule (S32+S33
  precedent). Validation: quotes verbatim-verified 235/235 and 374/374;
  re-reviews 33/33 (14.0%) and 42/42 (11.2%).
- **AUDIT-PHASE INVARIANT (F-0051):** the four canonical judgment files
  (`state/integration/judgments-{mednlp,2d3d,synpath,rest}-v1.jsonl`) join to
  EXACTLY the 1,233-item inventory, zero cross-file verdict conflicts.
  Campaign-wide: **277 covered / 77 equivalent / 253 partial / 626 absent.**
  Every judgment carries mechanically verified evidence; 35 records are
  F-0048 carry-overs (multi-cluster items judged once).
- **Findings this campaign so far:** F-0048 (one-item-one-judgment carry-over
  rule — binding), F-0049 (union-accounting denominators), F-0050 (SYNPATH
  layer analysis), F-0051 (S35 census + audit completion). Prior campaign
  findings: F-0032 (MEDNLP medical layer). The 77 equivalence mappings and
  the per-layer absent analyses are the S36 planning substrate.
- No vault mutations during either session's judging; sources 276/276 +
  333/333 byte-identical; 836/836 tests.
- Checkpoints: `checkpoint-2026-11-07-integ-session{34,35}.json`
  (accelerated_mode: 5 of 15 budget sessions consumed, 10 remaining, none
  failed).
- Execution note: S35 group-23's first subagent launch failed with an
  infrastructure timeout before writing anything; it was relaunched cleanly
  (s30 precedent) and the validator's per-group missing-file reporting makes
  any such failure detectable and resumable.

## If a future session runs

1. Follow the startup protocol (AGENTS.md §2): verify this handoff against
   repository evidence — the session-35 checkpoint, task-queue row INTEG-006,
   the four judgment files, and the re-runnable validators
   (`python3 scripts/s34_validate_judgments.py` → VALIDATION PASSED 235/235;
   `python3 scripts/s35_validate_judgments.py` → VALIDATION PASSED 374/374;
   scratch group outputs are gitignored but deterministically
   reconstructible from manifest + canonical file, or verify the canonical
   files directly with the same checks). The campaign union join is
   re-runnable: 4 files vs inventory must stay 1,233/1,233 set-exact with 0
   conflicts.
2. **Next task (INTEG-006, S36): decision ledger.** Build
   `state/integration/decisions-v1.jsonl`: one record per item id joining
   its SINGLE canonical judgment (35 carry-over records join once), with:
   - **A** for covered/equivalent verdicts (record + verify; cite the
     judgment's destination + mechanically-verified quote; no new note);
   - **B** for partial verdicts where one right home exists (expand that
     note/section using the list's project context);
   - **D** where the concept is explained across ≥2 notes (consolidate:
     canonical explanation + cross-links; prefer D/B over C);
   - **C** for absent verdicts (most appropriate existing location per plan
     §6 destination-selection ladder; `vu integ-coverage` collision report
     attached; create a note only when necessary).
   Expected shape: A ≈ 354, B/D = 253 partial, C ≤ 626 absent. Then the wave
   plan: B/C/D work items enumerated with destinations, cluster-ordered
   (largest first: SYNPATH, then MEDNLP, 2D3D, WEATHER/MAPDIG/NLME/
   MATHSOLVER/MASTER-INDEX), per-wave completion criteria + mutation battery.
   Write `scripts/s36_validate_decisions.py` (exact inventory join, decision
   integrity rules, A-quote verification) and close out with checkpoint +
   handoff + ledger row 36.
3. **Project-context authority rule (plan §2):** never invent project usage;
   the list's annotations (Repository: lines, distinctions, status notes in
   `state/integration/clusters-v1.json` context records) are the only
   authoritative project context. S36 records destinations; the S37+ waves
   add project context.
4. Budget position: 10 sessions remain (S36–S45 = planning + 7 execution
   waves + verification + close). The plan's adaptive rules (§8) apply: if
   the ledger shows < 500 B/C/D items, execution compresses to 5 sessions.
5. Environment notes: the sandbox venv may need `pip install -e .` before
   the suite passes; the repo must be cloned to `/home/z/my-project/repo`
   (session scripts hardcode that path); configure the git credential store
   before pushing (AGENTS.md §13 — the PAT comes from the user, never
   committed or printed).
6. Standing rules for any vault mutation (S37+): sources immutable; anchored
   probe-idempotent repair scripts; per-wave mutation battery (lint, links,
   full-corpus audit, dup-scan, see-also-audit, full suite, verify-manifest
   x2) after the last mutation; campaign provenance markers
   (`*Integrated from the user's project taxonomy (INT-NNNN, cluster).*`) on
   every new/expanded section; continuous commit-and-push with remote-ref
   verification (AGENTS.md §13).

## Explicit non-claims

- The audit is complete, but NO integration decisions exist yet: the A/B/C/D
  ledger opens at S36. No vault notes have been created, expanded, or
  modified by the campaign so far (the 544-note vault is exactly the
  session-28 delivered state).
- "Covered/equivalent" means concept-level coverage at the depth standard; it
  does NOT include the user's project usage — project context is integrated
  in the S37+ execution waves.
- The 253 partial and 626 absent verdicts are findings about the vault, not
  integration decisions; A ≈ 354 items need no new material beyond
  verification.
- Single-judge-per-item design is mitigated by mandatory multi-term search +
  the 10.3–14.0% re-reviews (41/41, 30/30, 33/33, 42/42); borderline calls
  carry judge-noted uncertainty in the rationales, and S44 re-verifies
  everything independently against the ORIGINAL list.
