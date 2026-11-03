# Next Agent Handoff

## Project state

- Current milestone: **SYNTHESIS IN PROGRESS — AREAS 01–14 COMPLETE (327/544)**.
  Session 24 (2026-11-03) completed the user-directed batch: **area 01 -
  Foundations (20 notes), area 02 - Mathematics (18 notes), area 03 - Python
  and Data Tooling (29 notes), plus the 17 - Papers Swin Transformer
  pull-forward (1 note, covering BOTH Swin V1 and the Swin Transformer V2
  successor section)**. AdamW is covered by the area-02 Adam Optimizer
  Derivation note (dedicated "AdamW: decoupled weight decay" section). All
  four gates PASS with **zero waivers** (first zero-waiver session; 0
  dimensions below band across all 327 vault notes, no drift); all four
  audits **valid=true, 0 findings** over 1,058 + 1,354 + 398 + 45 = 2,855
  KUs; 4,983 markers verified present (2,538 term + 2,221 math + 224 code).
  Deliverable metric: canonical notes verified **259 → 327/544**.
- USER DIRECTIVE IN FORCE (2026-11-01): BINDING POLICY (ADR-0012): read
  `docs/ACCELERATED_COMPLETION_POLICY.md` and AGENTS.md §12–13 BEFORE planning.
  Budget after session 24: **2 sessions remaining (25–26)**. Deliverable-first
  reporting; a bookkeeping-only session is a FAILED session; every checkpoint
  carries the `accelerated_mode` block; continuous commit-and-push (§13).
- Completed and verified: BOOT-000..004, EXT-001..011, REBASE-000, AUDIT-011,
  FRAME-001, DISC-001, FRAME-002, REGEN-001, DISC-002, DISP-001. SYNTH-001 is
  in_progress (areas 01–14 done; 6 areas / 217 notes remain).
- Framework: 744/744 tests at session start AND end; sources byte-identical
  276/276 + 333/333 at start AND end.

## Session 24 summary (evidence-backed; includes an interruption recovery)

- Session 24 was STARTED by a predecessor session that was interrupted after
  generating 64 notes (pipeline prep committed as 732e8f6; 4 notes missing:
  the 3 orientation/MOC notes + Swin; no gates/audits run). This session
  verified the inherited state against the repo evidence (never assumed),
  generated the 4 remaining notes, and drove everything green.
- **Notes generated this session (orchestrator-written, gates as evidence):**
  Foundations MOC, Mathematics MOC, Python Language Overview (area-03 hub),
  Swin Transformer (area17swin pull-forward; both mermaid diagrams, stage and
  results tables, cyclic shift, relative position bias with the (2M-1) table,
  Swin V2 section with arXiv:2111.09883; links [[Attention and Transformers
  MOC]] as topical hub; NO links to future Papers-area siblings).
- **Lint**: 0 errors; 20 warnings = 17 pre-existing (s23-documented) + 3 new
  verbatim-source dollar-price artifacts (AI vs ML vs DL "$0.04/$0.001–$0.06"
  from master-ai "02 - AI vs ML vs DL vs GenAI vs Agentic AI.md" line 263;
  Introduction to Machine Learning + Types of Learning "($350,000)" from
  ai-course "08. Foundations of Machine Learning (Summary).md" line 90).
- **Lint repairs** (`scripts/s24_lint_repairs.py`): unescaped pipes inside
  table-cell math escaped (Outlier z-score rule, Cosine Manhattan/Jaccard)
  with keep-both prose carrying the source-verbatim unescaped math forms
  (KU-a91cd91, KU-9384b7f); NumPy prose `[0, 1)` inline-code → math.
- **Gate repairs** (`scripts/s24_gate_repairs_area03.py`): the 4 Exercise
  (tutorial) notes' examples/definitions bands — grounded discourse markers
  restored (e.g. the messy-Gender values 'Female','male','Male','female',
  'MALE' from the source data fence; "axis=0, for instance"; "is a model of").
  The ai-course exercise SOURCES carry 0 example markers and 0 definition
  patterns (measured) — repair, not waiver, because both dimensions measure
  discourse style, not content.
- **Marker repairs** (28 + 30 + 5 findings → 0 via anchored probe-idempotent
  scripts `scripts/s24_marker_repairs_area0{1,2,3}.py`): underscore-emphasis
  tokens restored (_faster, r-cnn_, _farabet, al._, pixel_, vehicle._,
  _example, _could_); ASCII-vs-typographic dashes (1950s-1980s, 1980s-2000s);
  dropped words (discussions, knowledge-based, unparalleled, backprops,
  adhere, skews, zooms, clicking, envs); mermaid label whitespace + 1 whole
  dropped Caution mermaid restored verbatim; the 5-filename series restored
  as historical context (s23 note-ID precedent); math-span granularity
  ($y, z$ as one span); **19 bare-fence equations restored as ```text fences**
  (master-ai statistics notes put display equations in bare fences; the
  in-batch Adam/Tensors precedent passes the audit with ```text) — this also
  restores the _map/argmin_/_unbiased/n_tests tokens; the dropped LLM-MLE
  autoregressive-likelihood example (p(tokens|θ) = Π p(token_i|token_<i, θ))
  restored; 2 See-also annotations (Brier score; z-tests/t-tests assume
  Gaussian).
- **NFKC lesson (new, record for future sessions):** the audit's output side
  NFKC-normalizes (²→2) before tokenizing, so a fence's `s²_unbiased`
  tokenizes as "s2_unbiased" while the source-side marker is "_unbiased" —
  such superscript-adjacent tokens need a prose reference (`` `_unbiased` ``)
  to survive; the fence itself stays verbatim for the code fingerprint.
- **Repair-idempotency incident (root-caused, fully repaired):** the area01
  script's first idempotency check was substring-unsafe for insertion
  repairs; during iterative fixing 3 insertions applied 4× (Caution mermaid,
  five-part-series sentence, "discussionssss"). All three removed
  byte-exactly, the script rewritten with probe-based idempotency
  (`probe in text and text.count(probe) == 1`), and consecutive full re-runs
  verified as complete no-ops BEFORE the final audit. All three repair
  scripts now carry probes on every insertion-type repair.
- Orchestrator independent review: 15/15 semantic probes; F-0014 marker
  headings absent from all 68 note bodies (matches inside verbatim fences
  only); self-contamination greps clean; no H1 in any body.

## Next task (SYNTH-001 continue — sessions 25–26)

1. **Read first**: AGENTS.md §12–13 → `docs/ACCELERATED_COMPLETION_POLICY.md`
   → this file → the session-24 checkpoint
   (`state/checkpoints/checkpoint-2026-11-03-synth001-session24.json`).
2. **Verify baseline** (policy §7): HEAD == origin/main, clean tree,
   `python3 -m pip install -e .`, full suite green (**744 expected**),
   manifests 276/276 + 333/333.
3. **Session 25 (bulk session 2 — ~200 notes)**: areas 15 - Agents and
   Tooling (41), 16 - Interpretability and Research (31), 17 - Papers minus
   Swin (55 — the Swin note ALREADY EXISTS, do not regenerate; the remaining
   area-17 notes need a FULL-area AREA_CONFIG entry, not the
   '17 - Papers :: area17swin' partial one), 18 - Projects (25), 19 -
   Reference and Practice (48). Leave area 20 (17) + spillover for session
   26 if the session runs out; prioritize in canonical order; push each
   green area immediately (§13). Waves capped at 4 notes / ~12K source
   words; orientation notes LAST.
4. Per area: full-area `AREA_CONFIG` entry (note types from canonical
   structure rationales; MOC target; colliding basenames — area 17's
   LoRA/vLLM/TensorRT-LLM paper copies link the area-13/14 path forms;
   Applications of Deep Learning now collides with the GENERATED area-01
   copy: link `[[01 - Foundations/AI ML and DL Hierarchy/Applications of
   Deep Learning|Applications of Deep Learning]]`; Jacobians and Hessians
   likewise has both generated copies) → extend/re-run the link-rules
   script → build inputs → check prompts → generate → `python3
   scripts/s21_run_gates.py <slug>` → `vu audit-output --source-root
   "source-vaults/AI " --output-root output/Unified-Vault --ku-batch
   scratch/synth/<slug>/audit-kus.jsonl --report reports/synthesis/s25-
   <slug>-audit.json` (source-root is BOTH vaults — the construction session
   24 validated) → root-cause findings with anchored PROBE-idempotent repair
   scripts (keep BOTH duplicate source treatments; hyphenated vs spaced
   forms are different markers; NFKC superscript lesson above).
5. **Session 26 (planned)**: area 20 (17, the Contextualized archival layer —
   presentation decided at release audit) + any spillover; cross-batch
   consistency (terminology, cross-area wikilinks now that all notes exist,
   corpus-wide drift re-audit incl. ALL 10 waivers from sessions 21–23) +
   the three confirmed-gap dedicated treatments (second moment,
   bradley-terry, async def) + final verification and delivery (release-gate
   predicates from `docs/MILESTONES_AND_ACCEPTANCE.md`, final audit over ALL
   27,536 KUs, final report with denominators).

## Standing rules (enforced)

- Never mark a task completed before its commit hash exists in the record.
- Re-run the full suite after the LAST mutation of the session.
- Sources are immutable; all outputs are evidence, never edits.
- Every completion claim needs a report path or test run as evidence.
- Marker-retention repairs go through anchored, PROBE-idempotent scripts
  citing their source KUs — never hand-edits without a record. When a source
  carries content twice (main text + interview/recap), keep BOTH forms.
  Insertion repairs where `good` embeds `bad` MUST use a probe.
- Drift waivers are for EXPLAINED artifacts with evidence (0 below band +
  audit 0 findings + source measurement), never for hiding a real
  regression; re-audit corpus-wide at session 26 (10 waivers pending).
- **Continuous persistence (ADR-0015 / AGENTS.md §13):** after every bounded,
  coherent unit passes its applicable checks, commit and push it immediately
  to `origin/main`; keep the unpushed window near zero; verify the remote
  ref after each push; record the SHA/result in the checkpoint or handoff.
- ADR-0011 discipline stands; subagent outputs are verified (gates +
  audits + sampling), never trusted.
- Delta-verification discipline: write the arithmetic of expectations down
  BEFORE running.
- Fresh-sandbox setup: `python3 -m pip install -e .` BEFORE the baseline
  pytest. F-0016: long runs must fit one tool call (< 10 min). F-0020:
  invoke via `vu`. F-0014 (open): marker headings must never be copied as
  knowledge — verified absent in areas 01–14; re-check per area.
- Scratch (editorial contract, link rules, bundles, wave plans) is
  git-ignored and regenerable: rerun the recorded scripts after a sandbox
  recycle — never hand-rebuild.
- Display artifact: the IM channel strips `[m` from displayed output —
  verify suspected defects byte-level (hex) before acting.

## Explicit non-claims

- 63 of the 68 session-24 notes were written by the interrupted
  predecessor's subagents and 4 by this session's orchestrator; the GATES
  (not authorship) are the acceptance evidence.
- Marker retention proves lexical/formula preservation of every KU excerpt;
  the semantic-fidelity layer for the rewritten prose is the session-26
  cross-batch consistency pass plus the release audit.
- Cross-area wikilinks to areas 15–20 do not exist yet by design; the
  Foundations MOC's reading-path links target only existing areas (01–14)
  and mention future-area topics as plain text.
- The area-17 Swin note is a PARTIAL batch (--only pull-forward with its own
  AREA_CONFIG entry); the remaining 55 area-17 notes need the full-area
  entry and must NOT reuse the partial one.
- The 46,978 low-signal provisional discovery candidates remain a documented
  exclusion (not silently resolved).
- The three confirmed gaps (second moment, bradley-terry, async def) still
  need their dedicated treatments at synthesis time.
- Tier A dossier-extension auto-accepts retain ~17% single-side
  over-inclusion (safe direction, documented in the session-18 report).
- Areas 15–20 are NOT synthesized yet; the unified vault currently contains
  areas 01–14 (327/544 notes) only.
