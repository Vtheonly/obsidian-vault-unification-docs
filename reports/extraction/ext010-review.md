# EXT-010-REVIEW (independent, read-only)

Task ID: EXT-010-REVIEW (independent review subagent, read-only)
Reviewed: `state/classifications/007-ext010-training-stability-overlap.jsonl` (36 records, OC-ext010-0001..0036) against batches `010-ext010-master-ai-training-stability.jsonl` (117 KUs, master-ai 07+08) and `011-ext010-ai-course-04.3-init-gradients.jsonl` (382 KUs, ai-course 01-03), the readable digests (`/home/z/my-project/ext010-parts/digest-010-master.txt`, `digest-011-course.txt`, all 499 KU excerpts read in full), the original source files, `docs/KNOWLEDGE_AND_PROVENANCE.md` section 7, `AGENTS.md` sections 3/6/7, and the EXT-010 task record in `state/task-queue.jsonl`. No file was modified except this report; nothing was "fixed".

## Verdict: PASS-WITH-NOTES

No classification is wrong in a way that requires repair before commit, and no material cross-vault coverage gap exists. All 36 overlap_type assignments are defensible and well-evidenced (34 AGREE, 2 BORDERLINE, 0 DISAGREE). One state-completion item (R1) and one state-consistency note (F-R2 below) must be closed before/at commit; neither is a classification error.

## Machine checks summary

- `reports/extraction/ext010-review-check.json` (scripts/ext010_review_check.py): **ok: true, failures: []** — 36 records, 157 quotes, 140 participating KUs (90 ai-course + 50 master-ai), 0 uncovered cross-vault discovery topics; 21 discovery topics truncated at the 250-pair cap are recorded as notes, not failures.
- Independently reproduced by this reviewer (own code, not the orchestrator's chain):
  - all 140 participating `ku_ids` exist in batches 010/011; every evidence quote's `source_path` equals its KU's `source_path` in the batch; 0 duplicate (ku_id, quote) pairs; ids sequential OC-ext010-0001..0036.
  - digests contain all 117 + 382 = 499 KU excerpts (no missing KUs).
  - committed files unchanged: `git diff HEAD -- state/classifications/ state/knowledge-units/` is empty; `git status` shows only `M state/task-queue.jsonl` (queued EXT-010 record) and untracked new files 007/010/011/term-map. Committed classification files 001-006 and batches 001-009 are byte-identical to HEAD — the worklog's claim is confirmed.
  - coverage/fidelity reports present for all 5 scope files (07→57, 08→60, 01→177, 02→25, 03→180 KUs; fidelity 117/117 + 382/382 byte-exact).

## Spot verification (10 quotes: record id, ku_id, stated lines, PASS/FAIL)

10 evidence quotes drawn uniformly at random (independent seed 20261027) from the 157 quotes; each checked byte-exact (substring at the stated 1-indexed lines, joined in order) in the ORIGINAL source file under `source-vaults/AI /...`:

| record | ku_id | source file | stated lines | result |
|---|---|---|---|---|
| OC-ext010-0008 | KU-07b9bf06f47cd2bc | course 01. Weight Initialization.md | L253 | PASS |
| OC-ext010-0003 | KU-7da12c8f153d4961 | course 01. Weight Initialization.md | L46 | PASS |
| OC-ext010-0007 | KU-4defd141c81dcaec | master 07 - Initialization Schemes.md | L143 | PASS |
| OC-ext010-0011 | KU-e7262bbf02e5e577 | master 07 - Initialization Schemes.md | L54 | PASS |
| OC-ext010-0035 | KU-231d2e1095fb8954 | course 03. The Vanishing and Exploding Gradient Problems.md | L867 | PASS |
| OC-ext010-0023 | KU-e9a40eb64de71774 | course 03. The Vanishing and Exploding Gradient Problems.md | L482 | PASS |
| OC-ext010-0005 | KU-7491a330351bce86 | course 02. Weight Initialization Techniques.md | L18 | PASS |
| OC-ext010-0013 | KU-33caf0d68e851a19 | master 07 - Initialization Schemes.md | L12 | PASS |
| OC-ext010-0002 | KU-902460e71973e997 | master 07 - Initialization Schemes.md | L16 | PASS |
| OC-ext010-0002 | KU-ef860a3e3a3e0183 | master 07 - Initialization Schemes.md | L22 | PASS |

**10/10 PASS — no off-by-one line numbers, no text mismatches.** (The machine locator approach — lines located in source at write time, not hand-typed — appears to have eliminated the EXT-009 R2 error class, as intended.)

## Per-record verdicts (36-row table)

Criteria: overlap types per `docs/KNOWLEDGE_AND_PROVENANCE.md` section 7 (Exact Duplicate / Semantic Duplicate / Partial Overlap / Complementary Content / Conflict or Historical Difference), judged against the full digests and source lines.

| record | verdict | one-line reason |
|---|---|---|
| OC-ext010-0001 | AGREE | Both vaults teach the identical product-of-factors mechanism (<1 vanish, >1 explode) — genuine SD; spectral-radius and compounding-table depth correctly split off as vault-specific. |
| OC-ext010-0002 | AGREE | PO correct: shared outcome claim ("init determines whether/how well you converge") is thin and explicit in both; landscape apparatus is course-only (no "landscape" wording exists in master 07/08 — grep-verified) and magnitude/symmetry mechanics are master's. |
| OC-ext010-0003 | AGREE | SD correct: both state the zero/identical-constant symmetry failure; full mechanism derivation (course) and CNN restatement (file 02) correctly treated as depth. |
| OC-ext010-0004 | AGREE | SD correct: both derive too-large-init explosion/divergence; the (n·c)^L, 3.4e38, overflow-to-inf detail is course-only and the rationale says so. |
| OC-ext010-0005 | AGREE | SD correct: mirror failure mode in both; "early layers stay frozen" is actually shared (master 08 L45) and constant-function collapse is course-only, partitioned in the rationale. |
| OC-ext010-0006 | BORDERLINE | SD stands on the genuinely shared variance-calibration requirement (master L32/L155 vs course key-insight L151), but the topic sentence names N(0,0.01)/N(0,1) — examples that exist ONLY in the course (grep-verified absent from master 07/08) — as if shared. |
| OC-ext010-0007 | AGREE | SD correct: both derive Var(w)=1/n_in and 1/n_out conditions; assumptions list and W^T observation correctly partitioned. |
| OC-ext010-0008 | AGREE | SD correct; the "averaged" vs "harmonic mean" nuance is correctly adjudicated (HM(1/n_in,1/n_out)=2/(n_in+n_out) — mathematically the same formula, not a conflict). |
| OC-ext010-0009 | AGREE | SD correct: identical Xavier normal/uniform samplers in both; uniform-bound rationale and N(0,σ) std-convention note course-only, recorded. |
| OC-ext010-0010 | AGREE | SD correct: both scope Xavier to symmetric, ~linear-near-zero saturating activations; sigmoid zero-centering caveat is course-only depth. |
| OC-ext010-0011 | AGREE | SD correct: both derive ReLU variance-halving and the factor-2 compensation (σ²/2(1−1/π) detail course-only); dating He 2015 consistent. |
| OC-ext010-0012 | AGREE | SD correct: same Kaiming samplers and fan_in/fan_out→forward/backward mapping in both; conv fan computation course-only, recorded. |
| OC-ext010-0013 | AGREE | SD correct: matching rule plus mismatch direction (Xavier-on-ReLU ~2× too small) in both; ReLU-family member lists differ complementarily and are recorded as single-vault detail. |
| OC-ext010-0014 | AGREE | SD correct: sigmoid ≤0.25 ceiling and saturation in both; maximization derivation and per-point values course-only, recorded. |
| OC-ext010-0015 | AGREE | SD correct: tanh max-derivative 1.0 / still-saturates / vanishes-more-slowly in both; decay table course-only, recorded. |
| OC-ext010-0016 | AGREE | SD correct: early-layers-untrained consequence in both; CNN feature-detector framing course-only, recorded. |
| OC-ext010-0017 | AGREE | SD correct: causes (init, high LR, RNN) and NaN/oscillation/huge-gradient symptom signature shared; five-symptom list and suddenness callout course-only, recorded. |
| OC-ext010-0018 | AGREE | SD correct: loss spikes as investigate-don't-ignore warnings in both vaults (three encodings master, symptom+clipping sides course). |
| OC-ext010-0019 | AGREE | SD correct: same-matrix-per-timestep RNN vulnerability in both; spectral-radius vs largest-singular-value nuance correctly recorded as terminology, not conflict. |
| OC-ext010-0020 | AGREE | SD correct: ReLU derivative-1 gradient pass-through and deep-network trainability in both; "single most important innovation" callout course-only emphasis, recorded. |
| OC-ext010-0021 | AGREE | SD correct: dying-ReLU problem and Leaky-ReLU small-negative-gradient fix in both; PReLU provenance/ELU/SELU course-only, recorded. |
| OC-ext010-0022 | AGREE | SD correct: normalization-as-stability-solution shared (master generic LayerNorm/BatchNorm line vs course BatchNorm mechanics); reduces-init-sensitivity and partners-not-substitutes correctly course-only. |
| OC-ext010-0023 | AGREE | SD correct: y=x+F(x) Jacobian I+dF/dx identity guarantee in both; worst-case product proof and ResidualBlock code course-only, interview-scale claim master-only, recorded. |
| OC-ext010-0024 | AGREE | SD correct: cap-norm-at-c rescaling, direction preservation, lr·c bound, and c=1.0 standard shared; threshold guidance (1.0–5.0) course-only, recorded. |
| OC-ext010-0025 | AGREE | SD correct: symptomatic-not-root-cause and can't-clip-zero philosophy in both; >10%-clipped red flag course-only, recorded. |
| OC-ext010-0026 | AGREE | SD correct: per-layer gradient-norm logging as primary diagnostic in both; code implementations differ and are recorded as complementary artifacts. |
| OC-ext010-0027 | AGREE | CC is exactly right: the two worked demonstrations (20-layer MNIST table vs 0.25-decay diagram + α^(L−l) table) are distinct artifacts that must both survive synthesis; neither duplicates the other. |
| OC-ext010-0028 | AGREE | PO correct: course's four families ⊂ master's seven; the combined-use/enables-very-deep claim is duplicated; union enumeration instruction for synthesis is sound. |
| OC-ext010-0029 | AGREE | SD correct: don't-re-init / init-is-pretrained / new-layers-only rule in both; LoRA A/B depth master-only, recorded. |
| OC-ext010-0030 | AGREE | SD correct: forward-a-random-input-and-check-variance verification practice in both; VarianceTracker and drift-remediation course-only, recorded. |
| OC-ext010-0031 | AGREE | SD correct: seed/scheme fixing for reproducibility in both of master's failure tables and the course's reproduce-results item. |
| OC-ext010-0032 | BORDERLINE | SD stands on the genuinely shared elements (in-place torch.nn.init functions, kaiming_normal_ fan_in/relu, zeros_ bias — all in master's worked example), but the topic names "kaiming_uniform_" and "a recursive init function applied via model.apply()" which exist ONLY on the course side (grep-verified absent from master 07/08); the rationale partitions correctly. |
| OC-ext010-0033 | AGREE | PO correct: master endorses framework defaults without specifying them; the Kaiming-Uniform-a=√5 specification (and file 02 agreement) is course-only; F-0009 caveat correctly embedded. |
| OC-ext010-0034 | AGREE | SD correct: pre-2010 ad-hoc-init history and principled-init-as-prerequisite in both; dating consistent (no F-0007-style discrepancy). |
| OC-ext010-0035 | AGREE | SD correct: NaN-first → suspect init/exploding-gradients diagnostic priority in both. |
| OC-ext010-0036 | AGREE | SD correct and carefully scoped: the shared claim is the zero-bias RECOMMENDATION (master "Standard: zeros"; course's init code zeroes biases); the course's contradictory PyTorch-default ATTRIBUTION is isolated as F-0009 rather than classified as shared truth. |

**Tally: AGREE 34 | BORDERLINE 2 (OC-ext010-0006, OC-ext010-0032) | DISAGREE 0.**
Both BORDERLINE cases share one cause (see F-R3/S1): the `topic` field is a merged cluster summary that can read as a fully-shared claim, while the `rationale` — the substantive field — always partitions correctly. The overlap_type assignments themselves are sound in both cases.

## Coverage gaps

**None found that require a new classification record.** I read both digests in full (all 117 master-ai KUs, all 382 ai-course KUs), mapped every substantive teaching of each of the 5 files to either a record (0001-0036), a declared single-vault non-record in the shared `method` field (whose declared list I verified item-by-item against the digests), or structural/frontmatter/link content. Specific hunts requested by the brief:

- **(a) weight-tying / embedding init:** master-ai has it (07 L68-71: "Embedding init: usually N(0, d_model^-1/2) or N(0, d_model^-1)", KU-d6f00a694ec2f11e) as part of the transformer recipe; the course files 01-03 contain ZERO embedding/weight-tying content (rg 'embed' over digest-011-course.txt: 0 hits). Single-vault, declared non-record → **not a gap**.
- **(b) 'gradients as products' framing variants:** every variant I found is either evidence in OC-ext010-0001 (master Jacobian-product L16/27/29 + TL;DR L11-12; course product-of-terms L13, Jacobian-product L39, three-way rule L61-63, fundamental equation L57) or a summary restatement of it (course L1022 "multiplicative structure of backpropagation", course takeaways; master spectral-radius formalism = declared master-only depth). → **not a gap**.
- **(c) 'loss landscape' / convergence:** master-ai 07/08 contain no 'loss landscape' wording at all (grep 0 hits) — the landscape apparatus (non-convexity, 2^N saddle estimate, parachute analogy) is course-only and declared; the shared convergence-outcome claim is classified as OC-ext010-0002; course's "bounce wildly around the loss landscape" (L81) is OC-ext010-0004 evidence. → **not a gap**.
- **(d) activation derivative values / saturation:** sigmoid 0.25 (0014), tanh 1.0/still-saturates (0015), ReLU 0/1 (0020), saturation-fix via normalization (0022) — all shared claims classified; per-point derivative tables and maximization derivations are declared course-only. → **not a gap**.
- **(e) practice claims:** seed (0031), monitoring (0026), init verification (0030), clipping threshold c=1.0 + direction preservation + lr·c bound (0024), root-cause/red-flag (0025), NaN-first priority (0035), loss-spike investigation (0018), defaults reliance (0033), fine-tuning (0029) — all classified. → **not a gap**.
- **Borderline candidate examined and cleared:** the shared PyTorch clipping-API usage — master 08 L84-86 (KU-3287f37867d5962e, byte-verified: `torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)`) vs course 03 L688 (KU-892e72cc63cf286a, byte-verified: "PyTorch provides a built-in function for gradient clipping by norm. The function is called **after** `loss.backward()` and **before** `optimizer.step()`:") plus the course's training-loop code. This is the implementation layer of OC-ext010-0024's already-classified teaching (same API, same c=1.0), not a distinct content cluster; both KUs are simply uncited cluster members. Judged **subsumed by OC-ext010-0024**; see S2 (optional evidence addition, not required).
- Also checked and cleared: master's "init as V&E solution" restatements (07 TL;DR, 08 L72 + solutions-table init row) vs course 03 L65 / 02 L25 — same teaching as OC-ext010-0006's cluster (variance calibration prevents V&E), not a separate record; BN γ=1/β=0 defaults, orthogonal/sparse init, LeCun, warmup/shallow-nets matters-less, FP16/attention/transformer-specific content, MuP/LoRA/Fixup — all single-vault within scope and all on the declared non-records list.

## Scope check

**The EXT-010 scope decision is legitimate and I confirm no in-scope file was skipped.**

- I re-ran the read-only probe (`/home/z/my-project/scripts/ext010_scope_probe.py`, mdextract authority) and reproduced the heading evidence cited in the task record verbatim:
  - master-ai `11 - Training/Optimization/05 - Loss Spikes and Stability.md` (289 L) is indeed LLM-pretraining OPERATIONS (Why Loss Spikes Happen — bad data batches/numerical instability/optimizer state/LR issues/model instability at scale; Detecting; Preventing — clipping, LR warmup, loss scaling FP16, weight decay, stable initialization; Handling — skip-batch, checkpoint rollback, reduce LR, switch to BF16; Production — spike logging, automated recovery). It is NOT the classical init/gradient theory that ai-course 01-03 teach; adjusting the EXT-009 reservation away from this file was correct and is documented with evidence in the queued task record, exactly as the EXT-009 handoff required ("explicitly required verifying the master-ai file covers init/gradient-stability content BEFORE committing").
  - master-ai 07 (259 L) headings pair section-by-section with course 01+02 (why init matters / symmetry / explosion / vanishing / uncalibrated random / Xavier fwd+bwd derivation + compromise + samplers / He factor-2 + fan modes / PyTorch defaults / manual init / when init matters) and master-ai 08 (293 L) with course 03 (mechanism / where each happens / sigmoid ceiling / exploding causes+symptoms / solutions incl. ReLU family, residual, normalization, init, clipping / diagnosing / worked examples / failure modes / interviews).
  - Deliberate exclusions verified by headings: master-ai `06 - Backpropagation.md` (315 L; center of mass = reverse-mode autodiff, BPTT, op-specific gradients, distributed backprop; only a short V&E subsection — the "distinct domain" judgment is accurate); `11 - Training/Optimization/04 - Mixed Precision Training.md` (LLM operations); ai-course `04.3/04 Hyperparameters and Network Configuration.md` (filters/stride/LR/batch size/optimizers/warmup/tuning — optimization/tuning domain, consistent with the standing EXT-009 reservation). All three exclusions are recorded as scope decisions (never preservation decisions) with files remaining eligible for future pairs.
- All 5 in-scope files were fully extracted (coverage reports: 57+60+177+25+180 = 499 KUs; 0 excluded/failed; fence-balanced); batches 010/011 are committed-pending with full byte-exact fidelity reports. The ai-course 04.3 folder is now 6 of 7 files extracted (only the reserved 04 remains), consistent with the task record.

## F-0009 verification

**CONFIRMED at source; genuine internal inconsistency in the AI Course vault, worth a finding.**

Byte-verified source lines:
- Course file 01 `01. Weight Initialization.md` **L407** (in the Conv2d PyTorch-default passage beginning L399): "…The choice of $a = \sqrt{5}$ is a historical artifact of PyTorch's implementation, but it works well in practice. **Biases are initialized to zero.**" — byte-exact at L407 (and the whole passage sits inside L399-407).
- Course file 01 **L415** (Linear section, L411-415, which opens "Fully-connected (`Linear`) layers use the same initialization as `Conv2d`: Kaiming Uniform with $a = \sqrt{5}$."): "**Biases are initialized using $U\left(-\frac{1}{\sqrt{m}}, \frac{1}{\sqrt{m}}\right)$.**" — byte-exact at L415.
- Course file 02 `02. Weight Initialization Techniques.md` **L68**: "…The bias is initialized from a uniform distribution $U(-1/\sqrt{fan_{in}}, 1/\sqrt{fan_{in}})$." — byte-exact at L68.

The inconsistency is real and internal to the course: file 01 asserts (in its Conv2d-defaults narrative) a zero bias default while its own Linear section — introduced as using "the same initialization as Conv2d" — and file 02 both give the uniform bound U(-1/√fan_in, 1/√fan_in). The latter matches PyTorch's actual `reset_parameters` for both Conv2d and Linear, so the "zero" attribution is the wrong branch; even under the most charitable reading (a recommendation rather than an attribution), it still contradicts the same file's Linear-section default statement. F-0009 is correctly cross-referenced from OC-ext010-0033/0036, whose rationales correctly isolate the course's zero-bias RECOMMENDATION (which master-ai shares) from the contradicted default ATTRIBUTION. The finding is synthesis-relevant (bias-default reconciliation) and worth recording.

**However (see R1):** F-0009 is not yet present in `state/findings.jsonl` — the file currently ends at F-0008 (8 records), and `git status` shows it unchanged. All 36 records' shared `method` field states F-0009 is "recorded in state/findings.jsonl", which is not yet true; the worklog says "to be appended". This must be completed before/at commit.

## Findings, suggestions (S1, S2, ...), and required repairs (R1, R2, ... if any)

Review findings (this review's own numbering, distinct from F-0001..F-0009 project findings):
- **F-R1:** All 36 classifications are correct-or-defensible with accurate, source-verified evidence; 10/10 independent source spot-checks PASS; no duplicate or misplaced evidence found.
- **F-R2 (state inconsistency):** the 007 records claim F-0009 is "recorded in state/findings.jsonl" but the file ends at F-0008; the worklog's "to be appended" is still pending. → R1.
- **F-R3 (style, non-blocking):** several `topic` fields are merged cluster summaries that bundle course-only specifics into a sentence that reads as the shared claim (most pronounced in OC-ext010-0006: N(0,0.01)/N(0,1) — absent from master 07/08; OC-ext010-0032: kaiming_uniform_ and model.apply() — absent from master 07/08; milder in 0004's overflow-to-inf/NaN detail). In every case the `rationale` states the correct partition, so no classification is wrong — but a consumer reading topics alone could misattribute course-only specifics to both vaults.

Required repairs (before commit):
- **R1:** Append F-0009 to `state/findings.jsonl` (status open, with the three verified loci: course 01 L407 vs course 01 L415 + course 02 L68; note that the uniform bound matches PyTorch's actual reset_parameters) so that the classification records' "recorded in state/findings.jsonl" statement is true at commit time, per the worklog's own plan. (No change to the 007 records themselves is needed — their content is correct.)

Suggestions (non-blocking):
- **S1:** For future classification generators, phrase `topic` as "shared claim (+ vault-specific depth: …)" or prefix with "cluster:" so the shared surface is distinguishable without reading the rationale (addresses F-R3; affects 0006/0032 most).
- **S2:** Optionally add master KU-3287f37867d5962e and course KU-892e72cc63cf286a (both byte-verified at source) to OC-ext010-0024's evidence, or note them in its rationale, to make the shared PyTorch clipping-API usage explicit. Not required — the teaching is already classified.
- **S3:** Add an explicit `committed_files_unchanged: true/false` field to the `ext010_review_check.py` report so the "001-006 unchanged vs HEAD" claim is self-contained in the JSON (I verified it via `git diff` this session).
- **S4:** At dossier/synthesis time, note that OC-ext010-0014 and 0015 both draw evidence fragments from the same master source line (08 L34, KU-b5227ef8a4524679) so the sigmoid and tanh sub-claims are not double-counted as separate master restatements.
- **S5:** When appending F-0009 (R1), also consider recording the course file 02 L68 formula-notation quirk ("a = sqrt(6 / ((1 + a^2) × fan_in)) and a^2 is the negative slope" — the a/a^2 symbol collision in the source) as a minor annotation inside the finding; it does not affect the inconsistency judgment.

## Reviewer limitations

- I personally verified 10 of the 157 evidence quotes at source (plus the three F-0009 loci and the S2 candidate quotes); the all-157 verification rests on the orchestrator's X1-X10 chain and its `ext010-review-check.json`, which I audited conceptually and spot-sampled rather than re-ran in full.
- I did not re-run the double-run determinism checks, the CAP-013 discovery, or the term-map verification; I relied on their reports plus my own independent checks of participation, ids, digests, and git state.
- Semantic SD/PO/CC boundary calls are judgment: a stricter reviewer could argue OC-ext010-0002 or OC-ext010-0003 toward SD, or OC-ext010-0006/0032 toward PO; in each case the written rationale makes the chosen type defensible, and the rationale's factual partitions all verified against the digests.
- F-0009's "actual PyTorch behavior" statement is based on the course's own internal contradiction (self-contained) plus my background knowledge of `reset_parameters`; I did not execute PyTorch in this environment to confirm.
- The master-ai 06 - Backpropagation exclusion was judged from headings (scope-probe output) only; I did not read that file's body, since it is out of scope by a documented, evidence-backed scope decision.
- I did not audit the 21 truncated discovery topics' un-emitted pairs beyond trusting the report's note that per-KU evidence in the topics section remains complete.

## Orchestrator addendum (post-review, 2026-10-27)

The orchestrator independently re-verified every review claim at source before applying repairs (EXT-005..009 precedent), then applied:

- **R1 APPLIED:** F-0009 appended to `state/findings.jsonl` via `scripts/ext010_findings.py` (idempotent; 9 findings now recorded). The finding carries the three verified loci, the expected synthesis-time condition (PyTorch's actual default is the uniform bias bound; the zero-bias statement survives as the manual-init recommendation, consistent with OC-ext010-0036), and S5's annotation about file 02's a/a^2 symbol collision is noted in the finding's observed text.
- **S2 APPLIED WITH CORRECTION:** the two additional evidence quotes were added to OC-ext010-0024 in the generator (`scripts/ext010_classifications.py`) and the file regenerated through the X1-X10 chain. CORRECTION of the reviewer's citation: the course quote `grad_norm = utils.clip_grad_norm_(` lives in **KU-32b1dde0ac8ea1de** (03. The Vanishing and Exploding Gradient Problems.md L690-748 training-loop code), NOT KU-892e72cc63cf286a — that KU is the one-line prose at L688 and does not contain the quote (orchestrator verification: the quote occurs exactly once in the file, inside KU-32b1dde0ac8ea1de's span). The master quote `torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)` is in KU-3287f37867d5962e (08 - Vanishing and Exploding Gradients.md L84-86) exactly as the reviewer stated. After regeneration: 36 records, **159** byte-exact quotes, **142** participating KUs, X1-X9 green; `ext010_review_check.py` re-run green with 0 uncovered topics and committed files 001-006 still byte-identical to HEAD.
- **S1 (topic-wording style), S3 (review-check JSON field), S4 (dossier note on shared master line 08 L34)**: recorded for future sessions; S3/S4 will be considered at the next review-check/dossier touch. F-R3 and the two BORDERLINE verdicts (0006, 0032) are accepted as style notes with no classification change - both records' rationales already partition shared vs vault-specific content correctly.
- **Suggestion for the next dossier build (from S4):** the training-stability dossier's sigmoid/tanh concept entries should cite master line 08 L34 once, not twice.

Review verdict stands as **PASS-WITH-NOTES**; all repairs required before commit are applied. The classification file's method-field claim about F-0009 being recorded in state/findings.jsonl is now true.
