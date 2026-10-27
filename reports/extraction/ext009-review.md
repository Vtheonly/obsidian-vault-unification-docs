# EXT-009 Independent Review (EXT-009-REVIEW)

- Reviewer: independent read-only review subagent (Task ID EXT-009-REVIEW). No repository
  state files, batches, term maps, dossiers, source vaults, task queue, or classification
  files modified; the only files written are this report, the permitted verification
  script `scripts/ext009_review_check.py`, and the worklog append.
- Date: 2026-10-27
- Scope: `state/classifications/006-ext009-generalization-overlap.jsonl` — the 25
  NEW records OC-ext009-0001..0025 (20 Semantic Duplicate + 3 Partial Overlap
  (0009/0014/0023) + 2 Complementary Content (0024/0025)), 86 evidence quotes over 66
  participating KUs (28 of 106 master-ai batch-008 units, 38 of 234 ai-course batch-009
  units). Batches: 008 (master-ai '03 - Machine Learning/Generalization' — 01 Bias
  Variance Tradeoff 325 L + 06 Regularization Techniques 199 L, the whole folder,
  exactly 2 files) + 009 (ai-course '04.3 - Training Dynamics and Stability' files
  05 Batch Normalization 597 L + 06 Dropout and Regularization 589 L + 07 Data
  Augmentation 734 L — the regularization-relevant subset, 3 of 7 files). The
  deliberate PARTIAL-FOLDER scope on the ai-course side was independently verified with
  evidence: 04.3/01+02 are weight initialization, 04.3/03 is vanishing/exploding
  gradients, 04.3/04 is LR-scaling/warmup/tuning (headings verified) — training-stability
  and optimization topics, not generalization/regularization; the deferred master-ai
  counterpart '11 - Training/Optimization/05 - Loss Spikes and Stability.md' exists
  (15,583 bytes, verified); the RL alternative was correctly ruled out (full ai-course
  grep 'q-learning|reinforcement learning|policy gradient|bellman' = 8 hits in 8 files,
  all passing mentions — re-verified, incl. the AutoAugment mention inside the in-scope
  file 07 itself); 'bias[- ]variance' is rare in ai-course (5 occurrences in 4 files,
  re-verified); the 3 selected files map section-by-section onto master-ai 06's
  BatchNorm/Dropout/Data-Augmentation headings. The committed classification files
  001-ext003/002-ext004/003-ext005/004-ext007/005-ext008 must remain byte-unchanged.
- Method (all read-only, run from `/home/z/my-project/repo`):
  - `python3 scripts/ext009_review_check.py` — Check 1 (byte-exact substring test of
    every quote against the referenced KU's `excerpt` in batches 008/009), Check 2
    (locate every quote in the ORIGINAL source file under `source-vaults/AI /Master AI`
    / `source-vaults/AI /AI Course` — note the space in `AI ` — requiring an occurrence
    to start at EXACTLY the stated line, multi-line quotes verified inside the joined
    stated-line slice, plus a stated-line-within-KU-span check), Check 3 (structural:
    required fields, evidence ku_ids == record ku_ids, cross-vault in ku_ids AND
    evidence, sequential ids, duplicate quotes within/across records, jsonschema),
    Check 6 (sha256 of all five committed classification files vs `git show HEAD`;
    `git status` audit incl. a pure-append verification of the one modified tracked
    file; KU-id disjointness vs batches 001-007).
  - `PYTHONPATH=src python3 -m vault_unification validate-registry --classifications
    state/classifications/006-ext009-generalization-overlap.jsonl` (and again with
    `--tasks state/task-queue.jsonl`) → valid, 0 problems both times.
  - Full manual reading of BOTH master-ai source files (325 + 199 lines) in full, all
    three course source files around every cited passage plus their complete heading
    structure, all 66 cited KU excerpts in full, and the source context around every
    cited line.
  - Rationale fact-check by targeted greps (course files: underfitting/underfits,
    double descent, learning curve, interpolating, LoRA, self-consistency, elastic,
    lasso, Santurkar, implicit, memorize, transformer; master files: batchnorm/
    LayerNorm/RMSNorm occurrences, model.eval, running/momentum, mixup; vault-wide:
    RL vocabulary, bias-variance phrase, chapter-summary file, Loss-Spikes file).
  - Coverage analysis over the discovery report's 40 cross-vault topics with COMPLETE
    per-KU topic membership (the 5 pair-truncated topics — dropout/noise/overfitting/
    regularization/variance, capped at 250 emitted pairs of 672/264/493/735/1512 —
    were mined through the report's complete topics section, not only the emitted
    pairs), both-unclassified cross-vault pair mining (1,333 emitted pairs, 190
    distinct unclassified KUs; plus 79 non-participating KUs visible only through
    truncated-topic membership and 61 in no cross-vault topic at all); consistency
    sweep over all five committed classification files.
  - `python3 -m pytest tests -q` (415 tests) with the new file present; 25-random-KU
    excerpt-vs-source spot check (25/25 byte-identical) corroborating the fidelity
    reports.

## Verdict summary

**VERDICT: PASS-WITH-NOTES.** All 25 assigned overlap types are defensible (25 AGREE,
0 AGREE-BORDERLINE, 0 DISAGREE; the closest calls are 0009/0015 — see the table and
Limitations). All 86 evidence quotes are byte-exact in the batch KU excerpts AND sit at
exactly the stated original-source lines (0 off-by-one, 0 failures, 2 multi-line quotes
slice-verified, 0 span violations). All 25 records are cross-vault; structural checks
and schema validation pass; the framework's own `validate-registry` accepts the file
(alone and together with the task queue). All five committed classification files are
byte-unchanged vs HEAD; KU-id disjointness holds (889 committed vs 340 new, 0 overlap).
Consistency: no duplication of any committed record's claim (four cross-domain
adjacencies documented below for synthesis). Coverage, however, is NOT complete: one
GENUINE cross-vault claim cluster participates in no record — the LayerNorm-for-
Transformers/NLP preference (master-ai 06 L123 × ai-course 05 L551), which the discovery
surfaced under BOTH the 'transformer' and 'normalization' topics and which 0018's
rationale explicitly (and inaccurately) characterizes as master-only (→ required repair
R1). Four rationale line-reference errors and two wording imprecisions were also found
(R2, S1/S2), plus the required pre-commit process action (R3). None of these changes an
overlap_type or an evidence quote.

## Check 1 — Byte-exact quotes vs KU excerpts: 86/86 pass, 0 failures

Every one of the 86 evidence quotes is a byte-exact substring of the referenced ku_id's
`excerpt` field in batch 008 or 009. Per record: 2 quotes × 6 records, 3 × 8, 4 × 6,
5 × 4, 6 × 1. All evidence `source_path` values equal the KU records' `source_path`.
A 25-random-KU excerpt-vs-source spot check (25/25 byte-identical slices) independently
corroborates the two fidelity reports (106/106 and 234/234 byte-exact).

## Check 2 — Quote line verification vs ORIGINAL source files: 86/86 exact, 0 off-by-one, 0 failures

All 86 quotes were located in the original source markdown (roots `source-vaults/AI
/Master AI` and `source-vaults/AI /AI Course`): every quote has an occurrence starting
at exactly its stated `lines[0]` — not one needed any tolerance. Both multi-line quotes
(0014's "- Input layer: 0.1–0.2.\n- Hidden layers: 0.3–0.5." at L72-73 incl. the en
dashes; 0017's "- Prevents the model from becoming overconfident.\n- Acts as
calibration regularization." at L115-116) are contained in the joined slice of their
stated line ranges. Every stated line falls inside the citing KU's own
`[line_start, line_end]` span (0 violations). Notable placements verified: master-ai 06
L15 (two fragments by 0001/0020), L33 (two by 0005/0007), the pitfall list L180/181/
182/183 (four different items by 0012/0011/0019/0015), L172-176 (two items by
0009/0008); course 06 L13 (three fragments by 0001/0001/0024), L21 (two by 0002), L33
(two by 0003), L58 (two by 0010/0011), L115 (two by 0013/0023), L392 (two by 0005/
0008); course 05 L533 (by 0014 and 0019); course 07 L734 (two fragments by 0022).

## Check 3 — Structural: all clean

- Required schema fields present in all 25 records; all validate against
  `schemas/overlap-classification.schema.json` (jsonschema Draft 2020-12,
  `additionalProperties: false`); `task_id` = EXT-009 and `date` = 2026-10-27 in all
  25; no `supersedes_classification_id` and no self-applied `review` field anywhere.
- Ids are unique and sequential OC-ext009-0001..0025 (namespaced — no collision with
  any committed OC-ext003/ext004/ext005/ext007/ext008 id; checked programmatically).
- Evidence ku_ids == record ku_ids exactly (set equality) in all 25 records.
- 25/25 records cross-vault: `master-ai:` and `ai-course:` source prefixes both present
  in ku_ids AND both vaults quoted in evidence.
- No duplicate quotes within any record or across the file (86 distinct quotes).
- Framework validator: `vu validate-registry --classifications
  006-ext009-generalization-overlap.jsonl` → `{"valid": true, "problems_total": 0}`;
  the same command WITH `--tasks state/task-queue.jsonl` (the 14-record queue incl.
  the appended EXT-009 task record) is also valid, 0 problems.
- Type census: 20 SD + 3 PO + 2 CC = 25 (matches the task brief and the generator's
  claim). Participating KUs: 66 (master-ai 28, ai-course 38) — matches.
- Same-source-line fragment pairs (master L15, L33; course L13, L58, L115, L392;
  course-05 L533) all verified genuinely distinct claim scopes (see Check 4); no two
  records share an identical ku_id set.

## Check 4 — Semantic audit: 25 AGREE, 0 AGREE-BORDERLINE, 0 DISAGREE

Definitions applied (same as EXT-005/007/008-REVIEW): SD = same core claim, different
elaboration; PO = shared element AND substantial non-shared content; CC = same topic
area, non-overlapping facets synthesis must keep both; calibrated against this file's
own and the committed set's precedents (EXT-008 0004 one-liner-vs-subsection = SD;
EXT-008 0014 course-side extension of a master rule = SD; EXT-008 0017
acknowledgment-vs-procedure = PO; OC-ext008-0021 code-KU evidence acceptable when the
claim lives in the code and the record is transparent; OC-ext005-0025 = CC precedent).

| ID | Type | Verdict | Note |
|-----|------|---------|-------|
| 0001 | SD | AGREE | Two-part definition duplicated (fits-train/fails-unseen + the gap as signature): master L15 + regime-table L32 vs course L13 (three fragments incl. 'the hallmark of overfitting'). Framings differ exactly as disclosed (high-variance row → 0024; student analogy at course L17 verified present, uncited). |
| 0002 | SD | AGREE | Same detection procedure: master diagnosis list L86 + mandatory-held-out L114 vs course L21 (both curves + named divergence point). Course-only numeric calibration verified at L27 (99%/75%, 2-5 vs 20+ points); master-only learning-curve diagnostics verified at L254-269 (the L111 reference is wrong — R2a). |
| 0003 | SD | AGREE | The brief's 'judgment classification': capacity→fits-noise (master, bias-variance vocabulary, L49 + polynomial example L23) vs capacity→memorizes (course, L33 'death by capacity'). The identification is sound — 'fits noise' and 'memorizes rather than learning generalizable features' are the same causal claim in two vocabularies (EXT-003 precedent); the rationale is fully transparent about resting on the quoted claims, not term counts. Course-only causes 2/3 (L34-35) and master-only U-curve/double-descent (L48-62, 184-201; zero course hits — grep-verified) correctly scoped out. |
| 0004 | SD | AGREE | Family definition + member-set duplication: master TL;DR L11 vs course L384 + L589 + comparison table L550-557 (verified: rows dropout/L2/L1/early-stopping/label-smoothing/BN) + dedicated file 07 for augmentation. Member sets coincide as claimed; master-only elastic net/weight tying/transformer-LLM lists (L44-50, L125-140) and the course's explicit-vs-implicit framing (L384 'explicit', L215/L347/L359 'implicit' — grep-verified) accurate. |
| 0005 | SD | AGREE | Formula + mechanism duplicated (master R(w)=‖w‖₂² L29-31, shrinks-toward-zero L33 vs course L388/L392, formula at L390 via rationale, decay algebra at L396 — all verified). Different notation is presentational (EXT-003 precedent); Gaussian-prior/MAP vs decaying-update derivations correctly marked complementary. |
| 0006 | SD | AGREE | Same precise optimizer-level claim: decoupled decay applies to weights not gradient + prefer AdamW (master L35 vs course L426-427 incl. the explicit recommendation). The adaptive-LR reason, both-optimizers code (L402-424), the Adam-derivation link, and the citation difference are all as stated. |
| 0007 | SD | AGREE | L1 mechanism (exact zeros → sparsity/feature selection) + L1-vs-L2 contrast + L2-as-DL-default positioning ('The standard' vs 'less commonly used') duplicated; gradient-shape derivation (course L435), Laplace prior (L42), elastic net (L44-50), l1_penalty code (L439-470), interpretability rationale (L437) all correctly attributed; 'lasso'/'elastic net' absent from all three course files (grep-verified). |
| 0008 | SD | AGREE | Bias-exclusion core duplicated (master L176 vs course L392); master's extension to norm parameters is a disclosed master-only addition (SD per the 0014 extension calibration). The L443-446 range for the weights-only filter is wrong (filter at L455-456, code block L439-470) — R2b. |
| 0009 | PO | AGREE | Closest PO call, but right. Shared element REAL: concrete weight-decay value guidance (master 0.01-0.1 'reasonable default'; course 1e-4..1e-2 + 1e-4..5e-4 CNN + 1e-2 AdamW, all verified in the code comments). The ranges are architecture/regime-specific (master production-context vs course SGD-CNN recipes; only 0.01=1e-2 coincides), so PO's keep-both-with-referents is the correct encoding — merging (SD) or splitting (CC) would lose information. Code-comment evidence acceptable per the OC-ext008-0021 precedent, transparently cited. Two wording issues → R2c (L423→L422) and S2 (validation-anchor and 'AdamW-era' clauses). |
| 0010 | SD | AGREE | Mechanism-level dropout definition duplicated (master L54 vs course L58); course-only Bernoulli-mask algebra verified at L62-72; the scaling half correctly split to 0011. |
| 0011 | SD | AGREE | Inverted-dropout design + purpose duplicated (master L181 PyTorch-behavior framing vs course L58 exact factor + L74 expected-value preservation, E[h̃ᵢ]=hᵢ at L72 verified); historical contrast master-only; both pseudocode walkthroughs (master L56-63, course L161-198) verified present. |
| 0012 | SD | AGREE | Operational eval-mode discipline duplicated (master pitfall L180 vs course L138 + L153); MC-dropout aside (L142) and the BN-side model.eval() callout (file 05 L142-143, verified) correctly scoped; BN running-statistics mechanics correctly course-only (master has no BN train/eval content — grep-verified). |
| 0013 | SD | AGREE | The strongest structural match: co-adaptation prevention near-verbatim (master L68 vs course L109) + ensemble/model-averaging both sides (L67/L69 vs L113/L115); third-reason difference (noise injection vs redundant representations + Gal & Ghahramani L121) and the cat-face example (L107) disclosed as course-only; the averaging-power claim correctly split to 0023. |
| 0014 | PO | AGREE | Both shared elements real: (a) strongest dropout on the largest FC layers (master hidden 0.3-0.5 + input 0.1-0.2 vs course FC 0.5 + conv 0.2-0.3, table at L355-360 verified), (b) modern reduce/omit-because-other-regularizers (master L77 data-scale-in-LLMs vs course L351 ResNet/EfficientNet-BN + file-05 L533 rule). PO right: the rate tables target different architectures (transformer-anatomy vs CNN-anatomy) — the shape is duplicated, the numbers are context-specific guidance synthesis must keep with referents. |
| 0015 | SD | AGREE | Output-layer exclusion genuinely duplicated (master pitfall L183 'typically you skip the output layer' — general regularizers — vs course L374 'never' for dropout with the zeroed-predictions reason); master-general ↔ course-specific identification is sound (dropout is a member of master's own toolkit list). The concentrate-on-large-FC element is course-explicit (L366) / master-implicit (rate table, 0014) — disclosed in the rationale, and the VGG-16 example (L370) and ordering convention (L378) verified course-only. |
| 0016 | SD | AGREE | Identical technique: stop at the validation divergence, patience, keep the best checkpoint (master L81/L99 + pseudocode L83-97 with patience 3 vs course L474/L476 with 5-20 guidance + implementation L478-510 with load_state_dict — all verified); endorsement strength master-only as stated. |
| 0017 | SD | AGREE | Label smoothing duplicated at definition, strength (0.1 both), purpose, and even the illustrative ~0.9 vector (master L113/L115-116 vs course L517/L521/L523 — the 10-class [0.01×9, 0.9] at L521 verified); Szegedy provenance and CrossEntropyLoss(label_smoothing=0.1) code (L525-544) correctly attributed; ε-vs-α presentational. |
| 0018 | SD | AGREE (R1) | The BN-noise-regularizes causal claim is duplicated (master L121 vs course L215 incl. the dropout-noise analogy + L217 strength comparison, course-only as stated). BUT the rationale's 'the LayerNorm-preferred-in-NLP note (L123, master-only)' is INACCURATE: the course states the same LayerNorm-for-Transformers/NLP preference at file-05 L551 — that unrecorded cluster is coverage gap CG-1 (R1). Master's BN coverage being one paragraph + note (plus the TL;DR list mention in 0004) is otherwise accurate. |
| 0019 | SD | AGREE (S1) | Over-regularization→underfitting principle duplicated (master general pitfall L182 vs course BN+Dropout context L533). The clause 'the course never uses the word underfitting in these three files' is literally true (and term-map-probe-accurate) but sits next to this record's own quote containing 'underfits' — see S1. Master-only high-bias-regime teaching (L26-33, 85-94) verified (no course counterpart). |
| 0020 | SD | AGREE | The regularization bargain duplicated (master L15 trade vs course L50 'the regularized model is actually better' in the 92/88-vs-89/89 callout — verified, including the 'Always compare validation metrics' operationalization, course-only); master's mechanism list L16-18 handled as rationale context with a defensible reason (the course states no capacity-limiting mechanism list). |
| 0021 | SD | AGREE | Near-verbatim definition (master L103 vs course L5) + positioning (data-limited remedy / most practical way to increase effective data; ImageNet reliance vs CNN focus). Label-preserving condition shared via the course's domain-awareness rule (L120-121 — verified quote 'does the resulting image still have the same label?'); invariance philosophy (L15), flip-doubles arithmetic (L40), and essentially-free framing (L28) verified course-only; text/audio modality lists (L106-107) master-only. |
| 0022 | SD | AGREE | Master's six-item image list covered item-for-item by the course's sections and summary (geometric flips/crops/rotations, pixel color jitter, advanced mixup/cutmix — L734 fragments + the L717-728 summary table with its Domain Caution column, verified). Depth is not a type criterion (EXT-008 0004 calibration); master's mixup/cutmix mechanics genuinely absent from scope (grep: master mixup only L105 list + L190 citation — the L189 reference is wrong, R2d); Gaussian noise/random erasing/RandAugment/RandomResizedCrop parameters course-only; course mixup formula (L242-243) and CutMix area-weighted labeling (L249) verified. |
| 0023 | PO | AGREE | Shared element real: averaging many models beats any single model (master L66 with the 1/√M variance scaling; course L115 'consistently more accurate and more robust' via error cancellation). PO right: master's variance-reduction theorem with a rate vs the course's qualitative robustness intuition in the dropout-ensemble context — same conclusion, different evidential depth and context (EXT-008 0017 calibration). Connections to 0013 accurate; the production note (L117) master-only. Cross-domain adjacency with the EXT-004 ensemble records → S4. |
| 0024 | CC | AGREE | Fits the ADR-0009/OC-ext005-0025 CC pattern: both vaults explain overfitting with different conceptual apparatus (master: decomposition + derivation + U-curve + double descent + LLM complications, none of it stated by the course — grep-verified zero 'double descent'/'learning curve'/'bias-variance' hits in the three course files; course: memorization incl. noise + student analogy + numeric gap calibration), the two framings assert different content, and synthesis must keep both. Not PO: the noise-fitting identification between the two framings is already recorded as 0003 (cross-referenced both ways). |
| 0025 | CC | AGREE | Fits the same CC pattern: two evaluation-data-hygiene rules protecting held-out data against DIFFERENT failure modes (master L122 selection leakage — tune on validation, evaluate once on test; course L262/L378 stochastic contamination — never random-augment validation/test, with the reproducibility reason verified). Neither vault states the other's rule in scope; neither subsumes the other. Cross-domain adjacency with OC-ext005-0029 → S3. |

Special-attention items from the review brief, resolved:

- **0003 (judgment classification)** — upheld. Different vocabularies for one phenomenon,
  identification grounded in the quoted claims, all single-vault material correctly
  scoped out, fully transparent rationale.
- **0009 (weight-decay values PO, code-comment evidence)** — upheld. Code-comment
  evidence acceptable (OC-ext008-0021 precedent, transparently cited); PO correctly
  encodes regime-specific ranges that must not be merged. Two wording fixes (R2c, S2).
- **0014 (dropout rates PO, different architectures)** — upheld. Shared guidance-shape
  + modern-reduction trend; architecture-specific tables kept with referents.
- **0015 (output-layer exclusion, general vs dropout-specific)** — upheld. The shared
  core is real on both sides; the general↔specific identification is sound; the
  master-implicit placement element is disclosed.
- **0018 (BN regularization SD)** — type upheld (one-paragraph vs subsection, the
  EXT-008 0004 calibration); the LayerNorm clause is wrong (R1/CG-1).
- **0022 (inventory SD, one list line vs full treatment)** — upheld (depth is not a
  type criterion); mixup/cutmix mechanics genuinely master-absent (citation-line fix
  R2d).
- **0023 (ensembling PO)** — upheld; cross-domain scoping note S4.
- **0024/0025 (CC records)** — both fit the ADR-0009 CC definition and the OC-ext005-
  0025 precedent (complementary treatments of one topic, neither side subsumed, both
  must survive synthesis); neither hides an unrecorded shared claim (the nearest shared
  claims — noise-fitting for 0024, the definitional gap for 0001 — are separately
  recorded and cross-referenced).

Rationale fact-check beyond the table — verified TRUE: 0001's student-analogy location
(L17); 0002's L27 calibration and L254-267 learning curves; 0004's table rows L550-557
and member-set coincidence; 0005's L390/L396 course math and L33 MAP reading; 0006's
L426-427 reason and no-year-in-excerpt; 0007's L435 gradient shapes, Laplace prior,
elastic net, and code L439-470; 0009's three code-comment values; 0010's L62-72
algebra; 0011's L72 derivation and both pseudocode locations; 0012's L142 aside and
file-05 L142-143 callout; 0013's L107 example, L121 Bayesian aside, and near-verbatim
co-adaptation; 0014's L355-360 table and file-05 L533; 0015's L370 VGG-16 and L378
ordering; 0016's pseudocode locations, patience 3 vs 5-20, and load_state_dict;
0017's L521 vector, L523 rationale, L525-544 code, and L117 provenance; 0018's
one-paragraph master BN coverage; 0019's L26-33/L85-94 master-only underfitting
teaching; 0020's L16-18 mechanism list and 92/88-vs-89/89 callout; 0021's L15/L40/
L28/L120-121 course content and L106-107 master-only lists; 0022's L242-243/L249
course mechanics and L717-728 table; 0023's L117 production note; 0024's zero course
bias-variance/double-descent content; 0025's rule asymmetry. FALSE: four rationale
line references (0002 L111→L115; 0008 L443-446→L455-456 in L439-470; 0009 L423→L422;
0022 L189→L190) and one vault-attribution clause (0018's LayerNorm master-only) —
R1/R2 below.

## Check 5 — Coverage: ONE genuine gap (CG-1); all claimed non-records otherwise justified

- **39 of the 40 cross-vault discovery topics map onto the 25 records or documented
  non-claims**: AdamW→0006; L1/L2/penalty/sparse→0005/0007/0008; batchnorm→0018
  (+0014); bias/variance→0003/0023/0024 (+documented BN-parameter sense collision);
  capacity→0003; co-adaptation→0013; color jitter/crop/rotation/translation/mixup/
  cutmix→0022 (+0021); data augmentation→0021/0022/0025; dropout/inverted dropout/
  dropout-related-epoch→0010-0015/0019; early stopping→0016 (+0002 fixes); ensemble/
  memorize→0013/0023/0001/0003/0024; generalization→0001/0020; hyperparameter
  (bridged)→0009/0016; inference→0012; label smoothing→0017; noise→0013/0018 (+the
  term-map sense-collision documentation, see below); overfitting→0001/0002/0003/
  0024; regularization→0004/0020; scaling→0011 (+documented Scaling-Laws/ToTensor
  sense collisions); test set/training set/validation (bridged)→0001/0002/0021/0016/
  0025; weight decay→0005/0006/0008/0009; SGD→0009 (+master-only implicit-SGD claim);
  PyTorch/pipeline→non-claim library/pipeline word collisions (the PyTorch-bearing
  master line L181 is already 0011's evidence).
- **CG-1 (GENUINE GAP — required repair R1): the LayerNorm-for-Transformers/NLP
  preference cluster.** Master-ai 06 L123 ('in NLP/Transformers, BatchNorm is rarely
  used — LayerNorm/RMSNorm is preferred because sequence lengths vary') × ai-course 05
  L551 ('Layer Normalization is the standard choice for Transformer architectures and
  sequence models, where batch sizes may vary and the concept of "batch statistics"
  is less meaningful') state the SAME core claim — LayerNorm, not BatchNorm, is the
  standard/preferred normalization for Transformers/NLP because sequence/batch
  statistics vary — with the same underlying rationale. The discovery surfaced these
  pairs under BOTH the 'transformer' topic (4 both-unclassified pairs) and the
  'normalization' topic; both KUs are non-participating; no record and no rationale
  captures the correspondence (0018's rationale calls the master note 'master-only';
  the method field lists 'GroupNorm/LayerNorm/InstanceNorm alternatives' as
  course-only — true for the mechanics, not for the preference claim). This is a
  one-line-vs-subsection SD by the EXT-008 0004 calibration (course context: the
  'Alternatives When Batch Size Is Small' section, L539-556; master additionally has
  RMSNorm and a See-Also link, course additionally the per-sample statistics
  mechanics and GN/IN). The EXT-005-REVIEW CG-1 → OC-ext005-0029 precedent is exactly
  this situation.
- **Both-unclassified cross-vault pair mining (1,333 emitted pairs; 28 topics).** All
  adjudicable as non-claims, sense collisions, or sibling restatements of recorded
  claims: the memorize pairs (course conv/SFT memorization wording × master LLM SFT
  list — different claims sharing a word; master SFT content documented master-only);
  the ensemble pairs (course L123-124 tip + L142 MC-dropout aside × master
  how-to-reduce-variance/derivation/LLM-table/interview items — the ensemble claims
  are recorded in 0023 via L66/L115, these are sibling restatements); the capacity
  pairs (course L31/L339/mermaid × master L16-18/L265 — recorded in 0003 or
  sense-adjacent); the scaling pairs (dropout scaling vs the Scaling-Laws See-Also
  link — documented sense collision); SGD pairs (course optimizer code × master
  implicit-regularization prose — master-only claim, non-claim pairing); pipeline
  pairs (sklearn pipeline import vs transform pipelines — word collision); the large
  bias/variance/normalization/noise/overfitting/regularization/dropout/training-set/
  validation/weight-decay masses (BN file's statistical vocabulary × master's
  decomposition/derivation material = the term map's documented sense collisions;
  code blocks; frontmatter; navigation; worked examples; restatements of claims
  already recorded via sibling KUs).
- **Pair truncation handled.** 5 topics were pair-truncated at the 250 cap (dropout
  672, noise 264, overfitting 493, regularization 735, variance 1512 actual pairs). To
  close this hole I mined the report's COMPLETE per-KU topic membership: 79
  non-participating KUs are visible only through truncated-topic membership and 61
  non-participating KUs appear in no cross-vault topic at all. Every potentially
  content-bearing combination among the 79 was examined (master's generic/L1/elastic
  penalty formulas × course L390/L431 formulas — sibling formulas of claims recorded
  in 0005/0007; the course rates table L355-360, VGG-16 L370, ordering L378, mixup
  formulas L242-243 — all cited in the corresponding rationales; master
  derivation/double-descent/LLM/weight-tying material — master-only). No additional
  genuine gap beyond CG-1.
- **Claimed non-records verified justified.** (a) BN train/eval + running-statistics
  mechanics: course-only — master's entire BN content is the L121 paragraph, the L123
  note, and the L11 TL;DR mention (grep-verified: no running/momentum/train-eval
  mechanics in either master file; master's only model.eval() mention is the dropout
  pitfall, 0012's evidence). (b) Master-ai's bias-variance derivation/cross-entropy/
  double-descent/learning-curve/LLM material: master-only — zero course hits for
  double descent / learning curve / interpolating / LoRA / self-consistency /
  Domingos (grep-verified). (c) mixup/cutmix mechanics: master-ai has only the L105
  list entry (participating in 0022) and the L190 paper citation — no mechanics, so
  no separate mechanics record is correct. (d) The sense-collision terms
  (noise/translation/shift/scaling/inference, plus bias/variance/L1/L2) are all
  documented in the term map `_comment` with per-pair adjudication reflected in the
  method field's closing paragraph; spot-adjudications re-checked and sound.
- **Cross-domain observations (not gaps, noted for synthesis):** (a) the course
  file-07 transforms.Normalize/ImageNet-statistics teaching corresponds to master-ai
  standardization content OUTSIDE this domain (regression files, OC-ext003-0014) —
  correctly out of scope here, deferred to synthesis like EXT-008's silhouette case;
  (b) the concept-level 'implicit regularization' family (master SGD L62; course
  weight-sharing L347/L359 and code L215; BN-noise already in 0018) and the
  noise-as-augmentation cross-modality correspondence (master audio 'noise injection'
  L107 × course image Gaussian-noise section L156-204) are distributed/unrecorded at
  the concept level — see S5.

## Check 6 — Append-only discipline: verified (with one disclosed deviation from the brief's expectation)

- sha256 of the five committed classification files, working copy == `git show HEAD`:
  001-ext003 `34be3a97cf01bee713d5ccc85a0bb80d356506fce15f1a3e9e0009fdec84af6e`,
  002-ext004 `cb81adc170db4ad481d3d636818e02e3030a615645ff204c0a22713b2dbcf36`,
  003-ext005 `b958c3923dd9664012409961929f3ad4dd0da0e1afd03f33b6ae7e3e5a5b0700`,
  004-ext007 `5d52987dcba389639f22351e86c43b1fbfa19a50b27982f33b955088d36697be`,
  005-ext008 `650a4ab8ab85eb76e5f6f705154f692a25531eff954e829e29a5c88face9e27f`.
  Byte-unchanged, all five.
- `git status` shows NO renamed/deleted/staged-change tracked files and only expected
  untracked EXT-009 artifacts (batches 008/009, term map, discovery reports,
  fidelity/coverage/determinism/term-map/kureg/immutable reports, the nine ext009
  scripts, the classification file) plus this review's own script. ONE deviation from
  the review brief's stated expectation: `state/task-queue.jsonl` is modified. Verified
  to be a PURE APPEND: all 13 HEAD lines byte-unchanged, exactly 1 line added — the
  EXT-009 task record (status 'ready') written by `scripts/ext009_queue.py` (an
  idempotent append-only script that aborts if EXT-009 is already queued), containing
  the scope-decision evidence the review brief itself references. The modified queue
  validates (`vu validate-registry --tasks` → 14 records, 0 problems). This state
  update happened pre-review rather than at commit time (the EXT-007/EXT-008
  sequencing); it violates no forbidden side effect (the task queue is the
  orchestrator's own state file) and nothing was rewritten — recorded as a process
  observation, not a repair.
- KU-id disjointness verified: batches 001-007 (889 ids) ∩ batches 008/009 (340 ids)
  = ∅. The new file contains no `supersedes_classification_id` and no `review` field;
  ids are namespaced OC-ext009-*; nothing edits, replaces, or claims to supersede any
  committed record.

## Check 7 — Consistency with committed records: no duplication; four cross-domain adjacencies for synthesis

Keyword sweep of all six classification files (committed 001-005 + the new 006) over
this domain's vocabulary:

- **OC-ext009-0023 (ensembling PO) vs the EXT-004 tree/RF records** — no duplication:
  OC-ext004-0005 ('averaging many trees reduces variance without increasing bias'),
  OC-ext004-0016 (bagging mechanics incl. the course's σ²/B), and OC-ext004-0026 (RF
  ensemble formula vs variance analysis) are TREE/RF-scoped claims over batches 002/003
  (master '03 - Decision Trees and Gradient Boosting.md', course '02. Random Forests
  and Bagging.md'); OC-ext009-0023 is the GENERAL ensemble-averaging principle over
  batches 008/009 (master bias-variance L66 with the 1/√M rate; course dropout-context
  L115). Disjoint KU sets, disjoint source passages, different claim scopes. The
  variance-reduction mathematics (σ²/M family) appears on different sides of the two
  domain pairs (course-quantified there, master-quantified here) — an expected
  consequence of per-domain-pair classification; flagged for synthesis (S4).
- **OC-ext009-0025 vs OC-ext005-0029** — the master-side discipline (tune on
  validation / evaluate once / leakage) is the SAME claim family recorded from a
  DIFFERENT master file and paired with a DIFFERENT course counterpart (EXT-005:
  course split protocol, PO; EXT-009: course deterministic-transforms rule, CC).
  Disjoint KUs and different pair-level relationships — not a duplication, but a
  cross-reference is warranted (S3).
- **OC-ext009-0016 vs OC-ext004-0010** — master's early-stopping one-liner also
  appears (different file, as part of the GBM tuning doctrine) in the EXT-004 record;
  the 009 record is the full NN treatment. Concept-adjacent, sources disjoint (S4).
- **OC-ext003-0014** ('Standardize features before applying L1/L2') — regression-
  domain scaling practice; the 009 records cover the L1/L2 techniques themselves.
  Different claim scope, disjoint sources (same shape as the EXT-008 review's
  OC-ext003-0014 vs OC-ext008-0014 note).
- No EXT-005/EXT-007 evaluation record duplicates the 009 overfitting/validation-
  monitoring claims (OC-ext005-0027/0029 are the CV protocol and locked-test-set
  discipline; 0002 is overfitting detection via loss curves — different claims,
  disjoint sources).

## Additional finding — EXT-006 dossier/registry interaction (→ R3)

With the new classification file present, `python3 -m pytest tests -q` gives
**415/415** — no drift-guard failure (scripts/ext006_dossiers.py DOMAINS still covers
only regression/tree-based/evaluation/clustering, and 'generalization' is not yet in
the concept-dossier schema enum). The EXT-009 task record's own outputs/acceptance
criteria require the commit to add the generalization domain (additive schema-enum
extension with in-schema justification, DOMAINS extension, generate
`state/dossiers/generalization-v1.json` byte-identically, rebuild the registry with
batches 001-009 and all six classification files, re-run the suite) and to update the
task record/current-state/checkpoint/handoff. Required pre-commit process action, not
a defect of the classification records.

## Required repairs (before commit; R1/R2 are record-content wording + one new record; R3 is a process action)

- **R1 — Coverage gap CG-1 + OC-ext009-0018 rationale correction.** Record the
  LayerNorm-for-Transformers/NLP preference cluster — master-ai 06 L123 × ai-course 05
  L551 (course context L539-556) — as a new record (e.g. OC-ext009-0026; SD by the
  one-line-vs-subsection calibration, with master-only RMSNorm/See-Also and
  course-only per-sample-statistics/GN/IN mechanics disclosed) or extend 0018's
  evidence/rationale to cover it; either way fix 0018's clause 'the
  LayerNorm-preferred-in-NLP note (L123, master-only)' — the preference claim is
  both-vault (course L551: 'Layer Normalization is the standard choice for Transformer
  architectures and sequence models'); only the note's RMSNorm mention and its
  placement are master-only. Regenerate via scripts/ext009_classifications.py so every
  new quote is verified in-excerpt AND at-source before writing (the discovery pairs
  for this cluster exist under topics 'transformer' and 'normalization').
- **R2 — Rationale line-reference corrections (wording-only; regenerate the file).**
  (a) OC-ext009-0002: 'learning-curve-by-training-size diagnostics (L111, L254-267)'
  — L111 is blank; the Plot-learning-curves bullet is L115 (and the section runs
  L254-269). (b) OC-ext009-0008: 'again in its manual L1 implementation (weights
  only, L443-446, code-block KU)' — the weights-only filter ('Only apply L1 to weight
  parameters, not biases') is at L455-456 inside the L439-470 code block; L443-446 is
  the function def + docstring head. (c) OC-ext009-0009: '1e-2 shown for AdamW at
  L423' — it is L422. (d) OC-ext009-0022: 'a paper citation at L189' — the mixup
  citation (Zhang et al., 2017) is at L190; L189 is the Szegedy label-smoothing
  citation.
- **R3 — pre-commit process action (per the EXT-009 task record's own acceptance
  criteria).** As part of the EXT-009 commit: extend
  `schemas/concept-dossier.schema.json` domain enum additively with 'generalization'
  (justification in the schema description, EXT-008 precedent) and
  `scripts/ext006_dossiers.py` DOMAINS with the generalization domain (batches
  008+009, `006-ext009-generalization-overlap.jsonl`, `generalization-domain-v1.json`);
  generate `state/dossiers/generalization-v1.json` (byte-identical double-run,
  `--check` exit 0); rebuild the registry (kureg-init --force + kureg-load ×9 +
  kureg-apply-overlap ×6 + kureg-validate); re-run the full suite (must remain green;
  currently 415/415); update the task-queue EXT-009 record (status/notes/tests_run),
  current-state, checkpoint, and handoff.

## Suggested improvements (optional, non-required)

- **S1 — OC-ext009-0019**: qualify 'the course never uses the word "underfitting" in
  these three files' — the course does use the verb form 'underfits' at file-05 L533,
  inside this record's own quoted evidence. Suggested wording: 'the course never uses
  the noun "underfitting" (its single verb use, "underfits", is the quoted L533
  over-regularization passage) and carries no high-bias-regime teaching in scope'.
- **S2 — OC-ext009-0009**: (a) scope the validation-anchor clause to master-ai — the
  course's weight-decay code and prose never mention validation; 'the course via its
  early stopping/monitoring teaching' is an inference, and the record can simply say
  the tuning anchor is explicit only on the master-ai side; (b) either drop
  'master-ai speaks for AdamW-era LLM-scale defaults' or ground it explicitly (the
  quoted line says 'for most training'; the AdamW/LLM reading rests on the
  Production-Implications context L170-176 and the worked example's AdamW
  weight_decay=0.01 at L161 — cite one of them if the characterization is kept).
- **S3 — OC-ext009-0025**: add a cross-reference to OC-ext005-0029 (the same
  master-ai test-set discipline, recorded in the evaluation domain from the
  Evaluation-Metrics file) so synthesis knows the master rule participates in two
  domain records with different course counterparts.
- **S4 — OC-ext009-0016 and OC-ext009-0023**: symmetric cross-domain notes — master's
  early-stopping one-liner also participates in OC-ext004-0010 (Decision-Trees file,
  GBM tuning doctrine), and the averaging-reduces-variance family is recorded
  tree/RF-scoped in OC-ext004-0005/0016/0026 (where the σ²/B quantification is
  course-side) vs 0023's general-ensemble scope (quantification master-side).
- **S5 — Coverage documentation for synthesis**: note the two concept-level families
  that no single record captures: (a) 'implicit regularization' — master SGD L62 vs
  course weight-sharing L347/L359 (code L215) and BN-noise (0018); the instances are
  recorded, the concept-level link is not; (b) noise-as-augmentation across
  modalities — master's audio-list 'noise injection' (L107) vs the course's image
  Gaussian-noise section (L156-204); modality-different and term-map-documented, but
  worth a synthesis note so the augmentation dossier mentions both.

## Limitations

- The reviewer is the same model family (GLM 5.3) as the orchestrator; independence is
  procedural (separate session, read-only scope, independently written verification
  script), not architectural.
- Semantic verdicts are judgment calls against the section-7 taxonomy, calibrated to
  this file's own and the committed set's precedents. This review returns 25 AGREE /
  0 BORDERLINE / 0 DISAGREE, but honesty requires naming the arguable calls: 0009
  (PO vs SD — the shared element is value-guidance whose ranges barely overlap; PO is
  the information-preserving choice), 0015 (SD with a disclosed course-explicit/
  master-implicit second element), 0024 (CC vs PO — the nearest shared element between
  its two quotes is recorded separately as 0003, which is what makes CC clean).
- Coverage analysis was scoped to the committed discovery report (65 terms, 40
  cross-vault topics, 2,961 emitted pairs + complete per-KU topic membership for the
  5 pair-truncated topics), the 66 participating and 274 non-participating KUs of
  batches 008/009, all five source files read (the two master files in full; the three
  course files around every cited passage and in heading structure), and targeted
  greps; CAP-013 discovery was not re-run, and content invisible to the term map's 65
  terms is out of scope of the discovery design (documented limitation of the method).
- The committed files' own quotes were not re-verified (EXT-005-REVIEW and
  EXT-007/008-REVIEW already provide that for 001-005; this review's Check 1/2 scope
  is the 86 new quotes).
- The registry was not rebuilt and no dossier was generated (both are the
  orchestrator's post-review steps; R3) — the 415/415 test result reflects the
  pre-commit state with the untracked 006 file present.
- The task-queue deviation noted in Check 6 was assessed as a state-file append, not
  re-derived from the handoff document; its content (scope evidence) was, however,
  independently re-verified against the vaults (see Scope in the header).

## Final verdict

VERDICT: PASS-WITH-NOTES — apply R1 (record the LayerNorm cluster + fix 0018's
master-only clause), R2 (four rationale line-reference corrections), and R3
(generalization dossier + registry rebuild + state updates) before commit; S1-S5
optional.

---

## Orchestrator addendum (post-review, pre-commit)

All required repairs and suggestions were applied to
`scripts/ext009_classifications.py` and the file was regenerated before
commit. Each fact cited below was independently re-verified at its source
line by the orchestrator BEFORE acceptance (master 01 L115/L254-269; master
06 L161/L167/L173/L190/L123; course 06 L422/L455-456; course 05 L551).

- **R1 applied.** New record OC-ext009-0026 (Semantic Duplicate, LayerNorm-
  preference cluster): master `KU-bbd3111786c76e44` L123 × course
  `KU-c35e357516d553a7` L551, both quotes byte-exact in excerpts and at
  their source lines; master-only RMSNorm/See-Also and course-only
  per-sample-statistics/GN/IN mechanics disclosed in the rationale.
  OC-ext009-0018's rationale now attributes the note's cross-vault
  counterpart (course 05 L551) to OC-ext009-0026 instead of calling it
  master-only.
- **R2 applied.** (a) 0002: L111 → L115 (and the section span corrected to
  L254-269); (b) 0008: L443-446 → "weights-only parameter filter at
  L455-456"; (c) 0009: L423 → L422; (d) 0022: L189 → L190.
- **S1 applied.** 0019's rationale acknowledges the course's single verb use
  ("underfits" inside the quoted L533 passage) and scopes the non-claim to
  the noun "underfitting" and the absent high-bias-regime teaching.
- **S2 applied.** 0009's validation-anchor clause is now scoped to master-ai
  ("Tune on validation", L173; the course's weight-decay code and prose
  never mention validation), and the AdamW-era characterization is grounded
  ("a reasonable default for most training" L173; AdamW worked example
  weight_decay=0.01 L161; modern-LLM-recipe framing L167).
- **S3 applied.** 0025 cross-references OC-ext005-0029 (same master-ai
  test-set discipline, different domain record and course counterpart).
- **S4 applied.** 0016 notes the OC-ext004-0010 adjacency (tree-domain early
  stopping); 0023 now names OC-ext004-0005/0016/0026 explicitly as the
  tree/RF-scoped averaging family (course-side sigma^2/B quantification
  there vs master-side here).
- **S5 recorded for synthesis** in the session handoff's cross-domain
  connections section (implicit-regularization family; noise-as-augmentation
  across modalities), not in records, since no single record captures them.
- **Regeneration result**: 26 records (21 SD + 3 PO + 2 CC), 68 participating
  KUs, 88 byte-exact quotes (86 reviewed + 2 new), chain X1-X9 all green;
  `vu validate-registry --classifications` valid (0 problems) — evidence:
  reports/extraction/ext009-classifications-validate.json. Committed
  classification files 001-005 remain byte-unchanged (X9).
- Process note: part of the R1(0018-clause)/R2/S1/S3/S4-partial wording had
  been applied to the generator script by the orchestrator session that was
  interrupted mid-repair; the completing session re-verified every edited
  clause against source before regeneration (the X1-X9 chain re-verifies all
  88 quotes on every run regardless).
