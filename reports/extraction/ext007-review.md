# EXT-007 Independent Review (EXT-007-REVIEW)

- Reviewer: independent read-only review subagent (Task ID EXT-007-REVIEW). No repository
  state files modified; the only files written are this report, the permitted verification
  script `scripts/ext007_review_check.py`, and the worklog append.
- Date: 2026-10-27
- Scope: `state/classifications/004-ext007-evaluation-addendum.jsonl` — the 4 NEW
  append-only records OC-ext007-0001..0004 (2 Semantic Duplicate + 2 Partial Overlap)
  adopted by the EXT-007 orchestrator from the four unreviewed candidate clusters C1-C4
  in `reports/extraction/ext005-independent-confirmation.md` section 3. 12 evidence
  quotes over 10 participating KUs (4 master-ai — all already participating in committed
  records; 6 ai-course — all first-time participants). The committed
  `003-ext005-evaluation-overlap.jsonl` (29 records) must remain byte-unchanged.
- Method (all read-only, run from `/home/z/my-project/repo`):
  - `python3 scripts/ext007_review_check.py` — Check 1 (byte-exact substring test of
    every quote against the referenced KU's `excerpt` in committed batches 004/005),
    Check 2 (locate every quote in the ORIGINAL source file under
    `source-vaults/AI /Master AI` / `source-vaults/AI /AI Course` — note the trailing
    space in `AI ` — requiring the quote to start at EXACTLY the stated line, plus a
    stated-line-within-KU-span check), Check 3 (structural: required fields, evidence
    ku_ids == record ku_ids, cross-vault in ku_ids AND evidence, sequential ids,
    duplicate quotes within/across records, schema validation via jsonschema, no
    `supersedes_classification_id`), Check 6 (003-ext005 working copy vs `git show HEAD`
    vs the sha256 recorded in the EXT-006 evaluation dossier provenance).
  - `PYTHONPATH=src python3 -m vault_unification validate-registry --tasks
    state/task-queue.jsonl --classifications
    state/classifications/004-ext007-evaluation-addendum.jsonl` → valid, 0 problems.
  - Full manual reading of all 10 cited KU excerpts in full, the complete master-ai
    source file (198 lines), and the course source context around every cited line
    (file 02 L520-538, file 03 L24-32 + L132-143, file 05 L62-74 + L118-128).
  - Participation cross-check of all 10 KUs against both classification files; targeted
    greps (master file: pixel/segmentation/IoU/mIoU/Dice, weighted; course file 03:
    default; committed 003 topics/rationales: single number / comprehensive / multiple
    metrics / macro / training loss / pixel / IoU / segmentation).
  - `python3 -m pytest tests -q` (415 tests) and `python3 scripts/ext006_dossiers.py
    --check` to test the interaction of the new file with the committed EXT-006
    artifacts.

## Verdict summary

**VERDICT: PASS-WITH-NOTES.** All 4 assigned overlap types are defensible (4 AGREE,
0 AGREE-BORDERLINE, 0 DISAGREE). All 12 evidence quotes are byte-exact in the committed
KU excerpts AND sit at exactly the stated original-source lines (0 off-by-one, 0
failures). All 4 records are cross-vault; structural checks and schema validation pass;
the framework's own `validate-registry` accepts the file. The committed 003-ext005 file
is byte-unchanged (sha256 matches HEAD and the EXT-006 dossier record). The adjudication
adopted all four candidates correctly — no adopt/reject decision should have gone the
other way, nothing material from C1-C4 was missed, and the four records do not duplicate
each other or any committed record. Three required repairs are rationale-wording
factual inaccuracies only (R1-R3, no type changes), plus one required pre-commit process
action (R4: regenerate the evaluation dossier and rebuild the registry — the new file's
presence makes one EXT-006 drift-guard test fail until the dossier is regenerated,
exactly as the EXT-006 notes anticipated). Five optional suggestions (S1-S5).

## Check 1 — Byte-exact quotes vs KU excerpts: 12/12 pass, 0 failures

Every one of the 12 evidence quotes is a byte-exact substring of the referenced ku_id's
`excerpt` field in the committed batch (004 or 005). Per record: 0001 = 3, 0002 = 3,
0003 = 4, 0004 = 2. All evidence `source_path` values equal the KU records'
`source_path`.

## Check 2 — Quote line verification vs ORIGINAL source files: 12/12 exact, 0 off-by-one, 0 failures

All 12 quotes were located in the original source markdown (roots
`source-vaults/AI /Master AI` and `source-vaults/AI /AI Course`): every quote starts at
exactly its stated `lines[0]` — not one needed any tolerance. All stated lines fall
inside the citing KU's own `[line_start, line_end]` span. Notable placements, all
verified: master-ai L20, L88, L112, L172, L174; course file-02 L532 and L538 (the
callout is one long line 532; records 0001 and 0004 quote DIFFERENT sentences of that
same line, both byte-exact); course file-03 L30 and L139; course file-05 L71 and L124.
File-02 is 537 newlines / 538 lines (no trailing newline) — L538 exists and carries the
summary quote.

## Check 3 — Structural: all clean

- Required schema fields present in all 4 records; all validate against
  `schemas/overlap-classification.schema.json` (jsonschema Draft 2020-12); no
  properties outside the schema's allowed set; `task_id` = EXT-007 and
  `date` = 2026-10-27 in all 4.
- Ids are unique and sequential OC-ext007-0001..0004 (namespaced — no collision with
  committed OC-ext003/ext004/ext005 ids).
- Evidence ku_ids == record ku_ids exactly (set equality) in all 4 records.
- 4/4 records cross-vault: `master-ai:` and `ai-course:` prefixes both present in
  ku_ids AND both vaults quoted in evidence.
- No duplicate quotes within any record or across the file (12 distinct quotes).
- No `supersedes_classification_id` and no self-applied `review` field anywhere — the
  addendum neither edits nor supersedes committed records.
- Framework validator: `vu validate-registry --classifications
  004-ext007-evaluation-addendum.jsonl` → `{"valid": true, "problems_total": 0}`.

## Check 4 — Semantic audit: 4 AGREE, 0 AGREE-BORDERLINE, 0 DISAGREE

Definitions applied (same as EXT-005-REVIEW): SD = same core claim, different
elaboration; PO = shared content AND substantial non-shared content; CC = no duplicated
claim, aspects that fit together; calibrated against the committed set's own precedents
(0002 SD, 0024 PO, 0025 CC).

| ID | Type | Verdict | Note |
|-----|------|---------|-------|
| 0001 | SD | AGREE | Both vaults state the reporting discipline "no single number suffices → report a comprehensive metric picture" (master L172 "Track multiple metrics" + two single-metric failure modes; course callout L532 sentence 1 + summary L538). Core claim duplicated; example sets differ = elaboration. Distinct from OC-ext005-0026 (see below). R1 wording repair. |
| 0002 | PO | AGREE | Shared: the transferable degenerate-majority-model argument (always-predict-majority → deceptively high metric → useless), present in master (spam, 99%) and re-instantiated by the course for pixel accuracy (90%/95% background). Substantial non-shared course content (segmentation context, mIoU/per-class-IoU remedy — verified absent from master). PO right; not CC (unlike 0025, there IS a shared claim); not SD (master has zero pixel/segmentation content). Distinct from committed OC-ext005-0002 (see below). |
| 0003 | PO | AGREE | Shared: MSE serves as a training loss (master "The default loss for regression" L88; course "MSE and MAE are both loss functions (used in training)…" L139) — and at vault level Huber-as-loss too (master L112; course L141, cited in 0022). Non-shared: course's explicit loss-vs-metric principle + divergence practice + constant-gradient rationale (L139/L30, all verified); master's default-loss designation and DL-loss context. PO right. Master KU citations fairly characterized (verified against full excerpts and a full read of the master file). |
| 0004 | SD | AGREE | Both vaults recommend macro-averaged metrics for imbalanced/rare-class situations (master L174 "prefer PR-AUC and macro F1 over accuracy"; course L532 sentence 3 "report macro-averaged metrics alongside weighted-averaged metrics to reveal performance on rare classes"). Core recommendation duplicated; macro-vs-weighted contrast verified course-only; over-accuracy framing master-side. Split from 0015 justified (see below). R2+R3 wording repairs. |

Special-attention items from the review brief, resolved:

- **0001 vs OC-ext005-0026 — genuinely distinct.** 0026 records WHICH metric to choose
  (business decision driven by error costs; its master evidence is L171, course L169 +
  L491); 0001 records HOW MANY metrics to report (comprehensive set, never one number;
  master L172, course L532-sentence-1 + L538). Orthogonal claims; the shared master-ai
  list KU (KU-d68fa9657e07ba54) participates in both via different lines — expected
  multi-participation (ADR-0009). SD is right for 0001: the "report multiple metrics /
  no single number" claim is stated in both vaults (verified: no committed record
  covers it — greps for 'single number'/'comprehensive'/'multiple metrics' over all 29
  committed topics+rationales return nothing).
- **0002 — PO right; distinct enough from OC-ext005-0002.** Verified mechanically:
  the master-ai Evaluation file contains NO pixel/segmentation/IoU/mIoU/Dice content
  (case-insensitive grep over the full 198-line file: zero hits; the only
  image-related text is the top-k "ImageNet-style eval" mention, which is neither), so
  SD is impossible and the rationale's claim is true. The pixel KUs
  (KU-5066df82e1779ad5, KU-74cf83af5ba96d3d) participate in NO committed record —
  committed 0002 cites five different course KUs (file-01/file-02 accuracy-trap units)
  for the classification-accuracy claim. Different claim scope, different course KUs;
  the shared master anchor KU (KU-f353ec8719844bc0) participates in both records
  (committed 0002 quotes the full line including the "misleading on imbalanced data"
  lead-in; the new record quotes only the pattern sentence — intentional, both
  byte-exact). PO over CC: the course KUs do not merely complement master-ai's trap
  content, they RE-state its argument shape for a new metric family — a genuine shared
  claim, exceeding the 0025 CC bar ("neither side subsumes the other; joined they form
  one argument").
- **0003 — PO right; master citations fairly characterized.** Both master quotes are
  verbatim from the KU excerpts; a full read of the master file confirms every "loss"
  occurrence (L72 log loss "standard loss for classification", L88, L112) is a
  role-designation inside the metric catalogue — the file never states the
  loss-vs-metric distinction as a principle, exactly as the rationale claims. The
  course-side claims (both-roles principle, train/evaluate divergence,
  constant-gradient rationale at L30) all verified verbatim. "Master-ai-only: the
  default-loss designation" verified (course file 03 contains no "default").
- **0004 — SD right; split from OC-ext005-0015 justified.** Read 0015 in full: its
  evidence (master L64, course L292/L296) and rationale cover ONLY the
  PR-AUC-over-ROC-AUC preference — nothing about macro averaging. The macro-for-
  imbalance recommendation is a distinct both-vault claim with no committed record
  (0016 is the macro DEFINITION record — different claim, zero shared KUs). Since 003
  is append-only, a new record in the addendum is the only way to record the claim —
  the rationale's stated reason is accurate. Also verified the course-only
  macro-vs-weighted contrast (master file has no "weighted" anywhere; course carries
  it at L532 and again at L538 in the summary KU).

Rationale fact-check (beyond the four main verdicts): verified TRUE — 0001's "the
course states the principle twice" (callout L532 + summary L538); 0001's
characterization of 0026; 0002's "OC-ext005-0002 already records [the pattern] as a
Semantic Duplicate" and "The master-ai KU also participates in 0002"; 0003's "The two
master-ai KUs already participate in OC-ext005-0018/0022"; 0004's "0015's evidence and
rationale do not cover the macro-averaging recommendation" and "the committed 003
file is append-only". Three FALSE statements found → R1, R2, R3 below.

## Check 5 — Coverage: complete; no missed material; no mutual duplication

- **All four candidates adjudicated, all adopted, all quotes carried.** C1 → 0001
  (3/3 candidate quotes); C2 → 0002 (3/3); C3 → 0003 (4/4 — the course L139 evidence
  quote is the tail fragment of the candidate's fuller passage; the master Huber quote
  is the full line, longer than the candidate's fragment); C4 → 0004 (2/2 macro-side
  quotes). Every adopt decision is supported: greps over the 29 committed
  topics+rationales confirm none of the four claims was already recorded
  ('single number'/'comprehensive'/'multiple metrics' → no hits; the pixel KUs → no
  committed participation; the loss-vs-metric principle → no hits — 0018's rationale
  mentions "use as training loss" only as a passing elaboration note inside the
  MSE-definition record; macro-for-imbalance → 0016 definition-only, 0015 PR-AUC-only).
  No reject decision should have gone the other way.
- **C4's PR-AUC half correctly left to 0015's claim coverage.** The candidate's course
  quote included the callout's PR-AUC sentence ("For imbalanced datasets (>10:1
  ratio), supplement with PR-AUC instead of ROC-AUC"); the claim it carries is already
  classified by 0015 (from master L64 + course L292/L296). That third instance is
  uncited as an instance, which is acceptable under claim-level classification (the
  containing KU participates in 0001/0004); see S5 if instance-level noting is wanted.
- **The four records do not duplicate each other.** 0001 (how many metrics) vs 0004
  (which averaging scheme) share both source KUs (master list KU, course callout KU)
  but quote different lines/sentences (L172 vs L174; callout sentence 1 vs sentence 3)
  and record different claims; 0002 and 0003 share nothing with the others. Verified
  mechanically (distinct quote sets) and semantically (distinct claims).
- **Participation effect:** the addendum brings 6 previously-unparticipating ai-course
  KUs (the callout, the file-02 summary, two pixel KUs, two regression-metrics KUs)
  into the classified set for the first time — a real coverage improvement; the 4
  master-ai KUs were already participants (the production-list KU now participates in
  five records across 0026/0027/0029/ext007-0001/ext007-0004, each anchored to a
  different line/claim — consistent with ADR-0009 and the many-to-many provenance
  invariant in KNOWLEDGE_AND_PROVENANCE.md section 7).

## Check 6 — Append-only discipline: verified

- `git status`: no modified tracked files; the only untracked paths are the two EXT-007
  artifacts (the new 004 file and `scripts/ext007_classifications.py`).
- sha256 of `003-ext005-evaluation-overlap.jsonl`: working copy
  `b958c3923dd9664012409961929f3ad4dd0da0e1afd03f33b6ae7e3e5a5b0700` ==
  `git show HEAD:...` == the sha256 recorded in the committed EXT-006 evaluation
  dossier provenance (`state/dossiers/evaluation-v1.json`,
  `provenance.classification_files[0]`, 29 records). Byte-unchanged.
- The new file contains no `supersedes_classification_id` (checked mechanically) and no
  `review` field; ids are namespaced OC-ext007-*; nothing in the addendum edits,
  replaces, or claims to supersede any committed record.

## Additional finding — interaction with the committed EXT-006 artifacts (→ R4)

With the new classification file present, `python3 -m pytest tests -q` gives
**414/415**: `tests/test_concept_dossier.py::TestCommittedDossiers::
test_dossiers_regenerate_byte_identically` fails for `[evaluation]` —
`scripts/ext006_dossiers.py --check` reports "regenerated bytes differ from committed"
(regression and tree-based dossiers still check OK). Cause: the EXT-006 dossier
config auto-includes `004-ext007-evaluation-addendum.jsonl` once it exists, so the
regenerated evaluation dossier now contains the 4 new concepts (33 instead of 29) and
updated provenance. This is NOT a defect in the EXT-007 records — the EXT-006 task
notes explicitly anticipated it ("the dossier config auto-includes … once that file
exists, so the evaluation dossier will be regenerated (same v1, updated provenance) as
part of EXT-007's commit"). It does, however, make the regeneration a REQUIRED part of
the EXT-007 commit (the task's own acceptance criteria require the full suite to pass
and kureg-validate to be clean).

## Required repairs (before commit; R1-R3 are wording-only, no type/evidence changes; R4 is a process action)

- **R1 — OC-ext007-0001 (rationale factual inaccuracy).** "The master-ai and guide
  KUs already participate in 0026" is FALSE for the guide KU
  (KU-e5b1649f3f9449ce, the one-paragraph metric-selection guide callout): it
  participates in NO committed record (its first participation is this addendum).
  Only the master-ai KU (KU-d68fa9657e07ba54) participates in OC-ext005-0026. The
  summary KU (KU-1b6540442eead81d) is also a first-time participant. Fix: reword to
  e.g. "The master-ai KU already participates in 0026 (its L171 line anchors that
  record); the two course KUs are first classified here — KU multi-participation
  across differently-scoped records is expected (ADR-0009)."
- **R2 — OC-ext007-0004 (rationale factual inaccuracy).** "Both KUs also participate
  in OC-ext005-0026/0015" is FALSE for the course callout KU
  (KU-e5b1649f3f9449ce): it participates in neither 0015 nor 0026 (nor any other
  committed record). The master-ai KU does participate in 0026; both KUs participate
  in OC-ext007-0001. Fix: reword accordingly.
- **R3 — OC-ext007-0004 (rationale factual inaccuracy).** "…OC-ext005-0015, which
  records the PR-AUC preference from adjacent parts of the same two source passages"
  misdescribes 0015's evidence: it comes from the master AUC section (L64) and the
  course ROC-limitations section (L292/L296) — other passages of the same two source
  FILES, not adjacent parts of the passages cited here (master production list L174,
  course callout L532). Fix: reword to "…which records the PR-AUC preference from
  other passages of the same two source files (the PR-AUC recommendation also recurs
  in the adjacent sentence of the same course callout and inside the same master-ai
  production item)". The distinctness argument itself is sound and needs no change.
- **R4 — pre-commit process action (anticipated by EXT-006 notes, now mandatory).**
  As part of the EXT-007 commit: regenerate `state/dossiers/evaluation-v1.json`
  (same v1, updated provenance, now 33 concepts / 100 participating KUs for the
  evaluation domain) via `scripts/ext006_dossiers.py`, re-run the dossier tests, and
  rebuild the registry with the new classification file
  (kureg-init --force + kureg-load ×5 + kureg-apply-overlap ×4 + kureg-validate), then
  re-run the full suite (must return to 415/415) and `vu capabilities --verify`. Until
  then the suite fails exactly one pre-anticipated drift-guard test (414/415).

## Suggested improvements (optional, non-required)

- **S1 — OC-ext007-0003**: extend the course L139 evidence quote to include its
  leading sentence "MSE and MAE are both loss functions (used in training) and
  metrics (used in evaluation)." — the explicit both-roles assertion is the core of
  the record's topic and is currently quoted only inside the rationale prose, not in
  the evidence.
- **S2 — OC-ext007-0003**: similarly, the L30 evidence quote ("This is why MAE is
  rarely used as a training loss…") omits the antecedent gradient clause its "This is
  why" points at; extend it to include "The gradient is constant magnitude regardless
  of error size…" so the constant-gradient cause is evidence-quoted, not only
  rationale-described.
- **S3 — OC-ext007-0003**: the rationale's "Shared: both vaults assert that
  MSE/Huber serve as training losses" is true at vault level, but the Huber leg's
  course side (L141, "A common pattern: train with **Huber loss** … evaluate with MAE
  or RMSE", KU-4e48e5d89286d256) is not in this record's evidence (it is cited in
  OC-ext005-0022). Optionally add that KU here too (multi-participation is expected).
- **S4 — OC-ext007-0004**: mention OC-ext005-0016 (macro-averaging definition record)
  in the rationale as the definition-side companion — mirroring how 0001 relates its
  neighbor 0026 — and optionally list it in `candidate_ref`; the current text names
  only 0015.
- **S5 — OC-ext007-0004 (or 0001)**: optionally note in the rationale that the course
  callout's preceding sentence (L532, "For imbalanced datasets (>10:1 ratio),
  supplement with PR-AUC instead of ROC-AUC") is a third, uncited instance of the
  PR-AUC claim recorded by 0015 — documenting the adjacency without a new record.

## Limitations

- The reviewer is the same model family (GLM 5.3) as the orchestrator; independence is
  procedural (separate session, read-only scope, independently written verification
  script), not architectural.
- Semantic verdicts are judgment calls against the section-7 taxonomy, calibrated to
  the committed set's own precedents rather than an external rubric; all four were
  clear-cut under those precedents (no borderline calls needed).
- Coverage analysis was scoped to the C1-C4 candidate list, the four records'
  neighborhoods (all committed records whose topics/rationales could plausibly
  overlap: 0002, 0015, 0016, 0017, 0018, 0022, 0024, 0025, 0026, 0027, 0029 — all
  read in full), and targeted greps; CAP-013 discovery was not re-run.
- The committed 003 file's own 105 quotes were not re-verified (EXT-005-REVIEW already
  provides that; this review's Check 1/2 scope is the 12 new quotes).
- The registry was not rebuilt and the evaluation dossier was not regenerated (both
  are the orchestrator's post-review steps; R4) — the 414/415 test result reflects the
  pre-commit state with the untracked 004 file present.

## Final verdict

VERDICT: PASS-WITH-NOTES — apply R1-R3 (rationale rewording, regenerate the file) and
R4 (dossier regeneration + registry rebuild) before commit.

---

## Orchestrator addendum (post-review changes, 2026-10-27)

The review above covered the pre-repair draft (12 quotes, 10 participating
KUs). After accepting the verdict, the orchestrator:

- Independently re-verified every repair claim before applying it (R1: the
  course callout KU KU-e5b1649f3f9449ce is indeed absent from
  OC-ext005-0026's ku_ids; R2: it is also absent from OC-ext005-0015's;
  R3: 0015's evidence cites master-ai line 64 and course lines 292/296 —
  other passages of the same files, not the same passages).
- Applied R1-R3 (rationale wording only; no overlap_type changes).
- Applied ALL suggestions S1-S5 after verifying each new quote byte-exact at
  its original source line first: S1 added the both-roles sentence (course
  file 03 line 139); S2 extended the line-30 quote to include the
  constant-gradient clause; S3 added the course Huber KU KU-4e48e5d89286d256
  (line 141, 'train with **Huber loss** ... evaluate with MAE or RMSE') to
  OC-ext007-0003; S4 added the OC-ext005-0016 companion reference to
  OC-ext007-0004's rationale; S5 noted the uncited third PR-AUC instance
  (course file 02 line 532) in OC-ext007-0004's rationale.
- Regenerated the file (now 4 records, 14 byte-exact quotes, 11 participating
  KUs; 2 SD + 2 PO unchanged) via scripts/ext007_classifications.py, which
  re-verifies EVERY quote (old and new) byte-exact inside the KU excerpt AND
  at the stated original-source line before writing — exit 0.
- Performed R4: registry apply-overlap for the addendum (4 inserted, 0
  rejected; kureg-validate valid: 775 KUs, 75 classifications, 240
  participating), regenerated state/dossiers/evaluation-v1.json (33 concepts,
  97 participating KUs, byte-identical double-run, --check exit 0), and
  re-ran the full suite: 415/415.

No further independent re-review of the post-repair file was performed; the
changes are exactly the review's own R1-R3 wording fixes and S1-S5
suggestions, each machine-verified by the generator script.
