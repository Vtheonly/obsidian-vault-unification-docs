# Next Agent Handoff

## Project state

- Current milestone: **SYNTHESIS IN PROGRESS — AREAS 04–14 COMPLETE**.
  Session 23 (2026-11-03) drove five full areas end-to-end: **area 10 -
  Large Language Models (7 notes), area 11 - Foundation Models and Multimodal
  (13 notes), area 12 - Generative Models (12 notes), area 13 - Training and
  Adaptation (11 notes), and area 14 - Inference and Production (26 notes)**,
  all GREEN through the complete gate chain (lint 0 errors → assess 0
  dimensions below band → drift explained → quality-gate PASS → audit-output
  **valid=true, 0 findings** over 397 + 632 + 315 + 552 + 1,356 = 3,252 KUs;
  15,538 markers verified present: 14,521 term + 838 math + 179 code).
  Deliverable metric: canonical notes verified **190 → 259/544**.
- USER DIRECTIVE IN FORCE (2026-11-01): BINDING POLICY (ADR-0012): read
  `docs/ACCELERATED_COMPLETION_POLICY.md` and AGENTS.md §12–13 BEFORE planning.
  Budget after session 23: **3 sessions remaining (24–26)**. Deliverable-first
  reporting; a bookkeeping-only session is a FAILED session; every checkpoint
  carries the `accelerated_mode` block; continuous commit-and-push (§13).
- Completed and verified: BOOT-000..004, EXT-001..011, REBASE-000, AUDIT-011,
  FRAME-001, DISC-001, FRAME-002, REGEN-001, DISC-002, DISP-001. SYNTH-001 is
  in_progress (areas 04–14 done; 9 areas / 285 notes remain).
- Framework: 744/744 tests at session start AND end; sources byte-identical
  276/276 + 333/333 at start AND end; registry rebuilt exactly as the
  session-20/21/22 checkpoints record (applied=27,536, Unaccounted=0, valid).

## Session 23 summary (evidence-backed; the pipeline recipe, now battle-tested on 259 notes)

- Baseline verified: clean tree, HEAD == origin/main == 6f7730e; 744/744
  first-run; manifests unchanged; derived registry rebuilt exactly as
  recorded via `scripts/s22_registry_rebuild.sh`.
- **Pipeline additions**: AREA_CONFIG entries for areas 10–14 in
  `scripts/s20_build_synthesis_inputs.py` (types: 6 MOC/roots overview, LLM
  Benchmarks reference, Multimodal AI Overview subfamily overview, 3
  derivations — Reparameterization Trick, KL Divergence Loss, DPO);
  `scripts/s23_link_rules.py` (deterministic colliding-basename path forms —
  4 in-batch: Chapter Overview→area 12 path form, LoRA, vLLM, TensorRT-LLM +
  28 generated + 2 future: Applications of Deep Learning, Jacobians and
  Hessians); `scripts/s23_pack_waves.py` + `scripts/s23_launch_manifest.py`;
  the binding editorial contract regenerated at
  `scratch/synth/s23-editorial-contract.md` (scratch is git-ignored and was
  recycled — regenerating it from `docs/EDITORIAL_STYLE_GUIDE.md` conventions
  v1 is the recorded procedure, see §"Standing rules").
- **69 notes by 33 bounded subagent groups in 5 waves** (cap 4 notes / 12K
  source words; orientation/MOC notes LAST with the full sibling list; waves
  sized 8/8/7/5/5 parallel agents — zero interruptions this session).
- **Lint**: 0 errors after 2 anchored fence-label repairs
  (`scripts/s23_lint_repairs.py`: the pgvector source embeds a mixed
  SQL+Python fence and the Guardrails source labels a Colang DSL fence as
  `python`; relabelled `python`→`text` with bodies byte-identical — F-0031
  precedent, the audit fingerprints bodies not labels). 17 warnings all
  documented verbatim-source artifacts: 7 pre-existing + 9 new (literal
  dollar prices: Reasoning Models cost table, Vision Foundation Models
  `$0.0001-0.001`, Multimodal AI Overview `$0.002`, Inference and Production
  MOC `$10k+/month`, LLM-as-Judge `$5–50`…, Failure Modes `$0.50`, LLM
  Security `> $X`; bracket artifacts: the `$130M…$100/H100` double-price
  line in Pretraining Objectives, the inline-code `{"name":` brace in
  Constrained Decoding) + 1 PLACEHOLDER_TEXT from the restored verbatim
  source marker `(TODO: cite, 2024)` in Sampling Strategies.
- **Audits**: 28 round-1 findings → 0 via anchored, asserted, idempotent
  scripts `scripts/s23_marker_repairs_area{10,11,12,13,14}.py` (each repair
  cites finding id + source locator; classes: dropped capstone/see-also
  glosses with dead links, source-spelling quirks preserved verbatim
  (`preill`), note-ID cross-references restored as historical context
  (`03.8`, `05.5`, chapter roadmap `de-duplication`), source-verbatim ASCII
  vs typographic variants (`2-10x` vs `2-10×`, `English-training`), dollar
  price-run math fingerprints, exact inline-math forms); 4 residual round-2
  findings → 0 via `scripts/s23_marker_repairs_round2.py` — **the round-2
  keep-both lesson re-confirmed: when a source carries the same content twice
  with different wording (main text + interview answer), BOTH treatments must
  survive; a repair that swaps one form for the other just moves the finding
  to the other KU** (2-10×/2-10x, `\alpha = 0.7, k = 4`/`acceptance rate
  $\alpha = 0.7$ gives ~2.5x`, hedge/hedges, `interview prep` spaced form —
  the tokenizer keeps hyphens inside tokens, so hyphenated vs spaced forms
  are DIFFERENT markers).
- **Gates**: areas 13 and 14 pass clean (no waiver); areas 10/11/12 each
  carry one evidence-backed concept-type drift waiver (content-family
  artifacts, three-part evidence: 0 dimensions below band + audit 0 findings
  + source math-density measurements — e.g. LLaVA/Whisper sources are
  math-free surveys while Embedding Model Training carries the InfoNCE
  math). Recorded verbatim in the gate reports; **10 total waivers now
  pending the session-25 corpus-wide drift re-audit** (4 area-06 + 3
  sessions-22 + 3 session-23).
- Orchestrator independent review: 10/10 semantic probes across 10 notes
  (two probe strings initially mismatched the SOURCE's own form — plain
  commas in the KV-cache arithmetic, code-block InfoNCE in CLIP — and were
  hand-verified against the sources); F-0014 marker headings confirmed
  absent; self-contamination greps clean.

## Next task (SYNTH-001 continue — sessions 24–25)

1. **Read first**: AGENTS.md §12–13 → `docs/ACCELERATED_COMPLETION_POLICY.md`
   → this file → the session-23 checkpoint (the pipeline recipe is
   battle-tested on 259 notes).
2. **Verify baseline** (policy §7): HEAD == origin/main, clean tree,
   `python3 -m pip install -e .`, full suite green (**744 expected**),
   manifests 276/276 + 333/333. Rebuild the derived registry via
   `scripts/s22_registry_rebuild.sh`.
3. **Session 24 (the bulk session — 200+ notes)**: areas 15 - Agents and
   Tooling (41), 16 - Interpretability and Research (31), 17 - Papers (56),
   18 - Projects (25), 19 - Reference and Practice (48), 01 - Foundations
   (20), 02 - Mathematics (18), 03 - Python and Data Tooling (29) — 268
   notes; leave area 20 (17, the Contextualized archival layer —
   presentation decided at release audit) plus any spillover for session 25.
   Widen subagent waves (more parallel groups, still ≤ 4 notes / ~12K source
   words — the cap is a context-budget safety, not a floor to break).
4. Per area: add the `AREA_CONFIG` entry (note types from the canonical
   structure rationales; MOC target; colliding basenames — for area 17 the
   LoRA/vLLM/TensorRT-LLM notes are the PAPER copies: links from area-17
   notes to the topical area-13/14 copies use the area-13/14 path forms;
   Applications of Deep Learning (areas 01/19) and Jacobians and Hessians
   (areas 01/02) become in-batch collisions) → `python3
   scripts/s23_link_rules.py` after extending it (or a new s24 variant) →
   build inputs → check prompts → generate (orientation notes last) →
   `python3 scripts/s21_run_gates.py <slug>` (waivers only with three-part
   evidence) → `vu audit-output --source-root "source-vaults/AI /AI Course"
   --output-root output/Unified-Vault --ku-batch scratch/synth/<slug>/
   audit-kus.jsonl --report reports/synthesis/s24-<slug>-audit.json` →
   root-cause findings with anchored idempotent repair scripts (keep BOTH
   duplicate source treatments; hyphenated vs spaced forms are different
   markers).
5. **Session 25 (planned)**: area 20 + any spillover; cross-batch
   consistency (terminology, cross-area wikilinks now that all notes exist,
   corpus-wide drift re-audit incl. ALL 10 waivers from areas 06–12) + the
   three confirmed-gap dedicated treatments (second moment, bradley-terry,
   async def) + area-20 presentation decision.
6. **Session 26 (planned)**: final verification and delivery — release-gate
   predicates from `docs/MILESTONES_AND_ACCEPTANCE.md`, final audit-output
   over ALL 27,536 KUs, final report with denominators.

## Standing rules (enforced)

- Never mark a task completed before its commit hash exists in the record.
- Re-run the full suite after the LAST mutation of the session.
- Sources are immutable; all outputs are evidence, never edits.
- Every completion claim needs a report path or test run as evidence.
- Marker-retention repairs go through anchored, asserted, idempotent scripts
  citing their source KUs — never hand-edits without a record. When a source
  carries content twice (main text + interview/recap), keep BOTH forms.
- Drift waivers are for EXPLAINED artifacts with evidence (0 below band +
  audit 0 findings + source math-density measurement), never for hiding a
  real regression; re-check the arithmetic before waiving; re-audit
  corpus-wide at session 25 (10 waivers now pending).
- **Continuous persistence (ADR-0015 / AGENTS.md §13):** after every bounded,
  coherent unit passes its applicable checks, commit and push it immediately
  to `origin/main`; do not wait for session end. Keep the unpushed window
  near zero, verify the remote ref after each push, and record the SHA/result
  in the existing checkpoint or handoff. This session ran 4 verified pushes
  (6084a39 pipeline prep → 1773652 waves A+B → f7b4854 waves C+D → final).
- ADR-0011 discipline stands; subagent outputs are verified (gates +
  audits + sampling), never trusted.
- Delta-verification discipline: write the arithmetic of expectations down
  BEFORE running.
- Fresh-sandbox setup: `python3 -m pip install -e .` BEFORE the baseline
  pytest. F-0016: long runs must fit one tool call (< 10 min). F-0020:
  invoke via `vu`. F-0014 (open): marker headings must never be copied as
  knowledge — verified absent in areas 04–14; re-check per area.
- Scratch (editorial contract, link rules, bundles, wave plans) is
  git-ignored and regenerable: rerun `scripts/s23_link_rules.py`,
  `scripts/s23_pack_waves.py`, `scripts/s23_launch_manifest.py` and the s20
  input builders after a sandbox recycle — never hand-rebuild.
- Display artifact: the IM channel strips `[m` from displayed output —
  verify suspected defects byte-level (hex) before acting.

## Explicit non-claims

- 68 of the 69 session-23 notes were subagent-written; the GATES (not
  subagent self-reports) are the acceptance evidence.
- Marker retention proves lexical/formula preservation of every KU excerpt;
  the semantic-fidelity layer for the rewritten prose is the session-25
  cross-batch consistency pass plus the release audit.
- Cross-area wikilinks beyond areas 04–14 do not exist yet by design; they
  are added once all areas are generated (session 25).
- The 46,978 low-signal provisional discovery candidates remain a documented
  exclusion (not silently resolved).
- The three confirmed gaps (second moment, bradley-terry, async def) still
  need their dedicated treatments at synthesis time.
- Tier A dossier-extension auto-accepts retain ~17% single-side
  over-inclusion (safe direction, documented in the session-18 report).
- Areas 01–03 and 15–20 are NOT synthesized yet; the unified vault currently
  contains areas 04–14 (259/544 notes) only.
