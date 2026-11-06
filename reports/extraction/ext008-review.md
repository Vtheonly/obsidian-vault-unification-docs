# EXT-008 Independent Review (EXT-008-REVIEW)

- Reviewer: independent read-only review subagent (Task ID EXT-008-REVIEW). No repository
  state files, batches, term maps, dossiers, source vaults, task queue, or classification
  files modified; the only files written are this report, the permitted verification
  script `scripts/ext008_review_check.py`, and the worklog append.
- Date: 2026-10-27
- Scope: `state/classifications/005-ext008-clustering-dimreduction-overlap.jsonl` — the 27
  NEW records OC-ext008-0001..0027 (22 Semantic Duplicate + 4 Partial Overlap
  (0017/0018/0021/0027) + 1 Complementary Content (0010)), 89 evidence quotes over 62
  participating KUs (22 of 27 master-ai batch-006 units, 40 of 87 ai-course batch-007
  units). Batches: 006 (master-ai '04 - Clustering and Dimensionality Reduction.md',
  single file) + 007 (ai-course 03.5 K-Means, 1 file + 03.8 Dimensionality Reduction,
  2 files). Scope note verified independently: master-ai has NO dedicated SVM/kernel
  content (its `03 - Machine Learning/Supervised Learning` holds only Linear/Logistic
  Regression and Decision Trees/Gradient Boosting; SVM/support-vector appears only as
  passing mentions in 6 overview/math/roadmap/framework files), so the task record's own
  contingency clause (choose another unextracted domain pair with evidence) legitimately
  covers the clustering/DR extraction. The committed classification files
  001-ext003/002-ext004/003-ext005/004-ext007 must remain byte-unchanged.
- Method (all read-only, run from `/home/z/my-project/repo`):
  - `python3 scripts/ext008_review_check.py` — Check 1 (byte-exact substring test of
    every quote against the referenced KU's `excerpt` in batches 006/007), Check 2
    (locate every quote in the ORIGINAL source file under `source-vaults/AI /Master AI`
    / `source-vaults/AI /AI Course` — note the space in `AI ` — requiring an occurrence
    to start at EXACTLY the stated line, multi-line quotes verified inside the joined
    stated-line slice, plus a stated-line-within-KU-span check), Check 3 (structural:
    required fields, evidence ku_ids == record ku_ids, cross-vault in ku_ids AND
    evidence, sequential ids, duplicate quotes within/across records, jsonschema
    validation), Check 6 (sha256 of all four committed classification files vs
    `git show HEAD`; `git status` audit of modified/untracked paths).
  - `PYTHONPATH=src python3 -m vault_unification validate-registry --tasks
    state/task-queue.jsonl --classifications
    state/classifications/005-ext008-clustering-dimreduction-overlap.jsonl` → valid,
    0 problems.
  - Full manual reading of the ENTIRE master-ai source file (152 lines), all three
    course source files (175 + 101 + 121 lines), all 62 cited KU excerpts in full, and
    the source context around every cited line.
  - Rationale fact-check by targeted greps (master file: perplexity, explained
    variance/95%/eigenvalue, K-Means++/n_init/restart/median, Euclid, curse, simple,
    outlier, silhouette, UMAP determinism; course files: simple/silhouette; course
    vault: autoencoder chapter-10 file, 03.6 silhouette file; whole master-ai vault:
    silhouette, SVM/support vector).
  - Coverage analysis over the discovery report's 35 cross-vault topics and all 934
    pairs (both-unclassified cross-vault pair mining); consistency sweep over the four
    committed classification files; KU-id disjointness check (batches 001-005 vs
    006/007).
  - `python3 -m pytest tests -q` (415 tests) with the new file present.

## Verdict summary

**VERDICT: PASS-WITH-NOTES.** All 27 assigned overlap types are defensible (26 AGREE,
1 AGREE-BORDERLINE, 0 DISAGREE). All 89 evidence quotes are byte-exact in the batch KU
excerpts AND sit at exactly the stated original-source lines (0 off-by-one, 0 failures,
14 multi-line quotes slice-verified, 0 span violations). All 27 records are cross-vault;
structural checks and schema validation pass; the framework's own `validate-registry`
accepts the file. All four committed classification files are byte-unchanged vs HEAD;
git status shows no modified tracked files and only expected untracked EXT-008
artifacts. Coverage is complete — every one of the 35 cross-vault discovery topics maps
to a record or a justified non-record; the two deliberately-non-recorded single-vault
elaborations named in the brief (silhouette, curse of dimensionality) are verified
correct. No duplication against the four committed classification files. Three
required repairs are rationale-wording factual inaccuracies only (R1-R3, no type or
evidence changes), plus one required pre-commit process action (R4: the EXT-008 commit
must add the clustering dossier and rebuild the registry per the task's own acceptance
criteria). Five optional suggestions (S1-S5).

## Check 1 — Byte-exact quotes vs KU excerpts: 89/89 pass, 0 failures

Every one of the 89 evidence quotes is a byte-exact substring of the referenced ku_id's
`excerpt` field in batch 006 or 007. Per record: 2 quotes × 5 records, 3 × 12, 4 × 7,
5 × 3. All evidence `source_path` values equal the KU records' `source_path`.

## Check 2 — Quote line verification vs ORIGINAL source files: 89/89 exact, 0 off-by-one, 0 failures

All 89 quotes were located in the original source markdown (roots
`source-vaults/AI /Master AI` and `source-vaults/AI /AI Course`): every quote has an
occurrence starting at exactly its stated `lines[0]` — not one needed any tolerance.
All 14 multi-line quotes are contained in the joined slice of their stated line ranges.
Every stated line falls inside the citing KU's own `[line_start, line_end]` span (0
violations). Notable placements verified: master-ai L11 (three DIFFERENT fragments
quoted by 0009/0011/0015), L27 (two fragments by 0004/0005), L60 (two fragments by
0017/0024), L113 (code line, 0021), L131 (full line by 0016, tail fragment by 0018);
course PCA L6 (two fragments by 0012/0015), L53 (by 0013 and 0027), t-SNE file L4
(connections line, 0027), L92/L93 table rows (0024/0025), L105/L106 (0014/0020).

## Check 3 — Structural: all clean

- Required schema fields present in all 27 records; all validate against
  `schemas/overlap-classification.schema.json` (jsonschema Draft 2020-12, no
  additional properties); `task_id` = EXT-008 and `date` = 2026-10-27 in all 27;
  no `supersedes_classification_id` and no self-applied `review` field anywhere.
- Ids are unique and sequential OC-ext008-0001..0027 (namespaced — no collision with
  committed OC-ext003/ext004/ext005/ext007 ids).
- Evidence ku_ids == record ku_ids exactly (set equality) in all 27 records.
- 27/27 records cross-vault: `master-ai:` and `ai-course:` source prefixes both present
  in ku_ids AND both vaults quoted in evidence.
- No duplicate quotes within any record or across the file (89 distinct quotes).
- Framework validator: `vu validate-registry --tasks state/task-queue.jsonl
  --classifications 005-ext008-clustering-dimreduction-overlap.jsonl` →
  `{"valid": true, "problems_total": 0}`.
- Type census: 22 SD + 4 PO + 1 CC = 27 (matches the task record's claim).

## Check 4 — Semantic audit: 26 AGREE, 1 AGREE-BORDERLINE, 0 DISAGREE

Definitions applied (same as EXT-005/007-REVIEW): SD = same core claim, different
elaboration; PO = shared element AND substantial non-shared content; CC = same topic
area, non-overlapping facets synthesis must keep both; calibrated against the file's
own precedents (0004 one-liner-vs-subsection = SD; 0014 course-side extension of a
master rule to more methods = SD; 0017 acknowledgment-vs-procedure = PO).

| ID | Type | Verdict | Note |
|-----|------|---------|-------|
| 0001 | SD | AGREE (R1) | Both vaults anchor K-Means as the reference algorithm (master L17 "most-used"; course L35 "most popular"). BUT "simplicity" is not shared: the course never says K-Means is simple — its only characterizations are "most popular" (L35) and "fast and popular" (L149, uncited); "The simplest" is master-side. Wording repair R1. |
| 0002 | SD | AGREE | Identical algorithm cycle (master L19-22 four steps; course Assignment/Update L49/L72/L76); centroid-as-arithmetic-mean stated by both (course L46, master step 3). Course-only elaborations verified by grep (Euclidean formula, mermaid, 1D example, stop-condition itemization); master-only O(NK) verified (no cost note in course 03.5). |
| 0003 | SD | AGREE | Same optimization objective under the same two names (master L24 inertia; course L111 "WCSS ... also known as Inertia" + L117 goal); WCSS formula and K=N trap course-only (verified). S1: "the same objective stated as two distances" overstates the inter-cluster half (maximizing inter-cluster distance is not part of the WCSS objective). |
| 0004 | SD | AGREE | Master cons item "sensitive to initialization" vs the course's full Initialization-Trap subsection incl. the converges-but-suboptimal consequence; master names neither remedy (grep: zero K-Means++/n_init/restart hits); MiniBatchKMeans L130 correctly described as the different performance concern. |
| 0005 | SD | AGREE | "assumes spherical clusters of similar size" expanded by the course's Spherical-Assumption subsection; Euclidean explanation course-only (grep: zero 'Euclid' in master); complex-shapes remedy correctly routed to 0007. |
| 0006 | SD | AGREE | Elbow method prescribed by both and tied to the inertia/WCSS curve (master L29 + course procedure L126-134); heuristic character flagged by master L138; the course TIP is described accurately (no clear elbow → business context). Silhouette correctly master-only in scope: zero silhouette hits in course 03.5/03.8; the course's silhouette teaching lives in 03.6 (batch 005, outside). |
| 0007 | SD | AGREE | Near-verbatim DBSCAN definition (master L33 / course L38); shapes+outlier pairing on both sides (master L51, course L172-173); eps/min_samples and no-K-needed master-only (verified). |
| 0008 | SD | AGREE | Tree/dendrogram definition stated by both (master L42, course L37); agglomerative/divisive naming, dendrogram cutting, interpretable hierarchy, O(N²) caveat all master-only (the course has only the one-line types entry). |
| 0009 | SD | AGREE | Foundational definition duplicated (master TL;DR L11, course L4/L6); supervised/unsupervised contrast, library analogy, medical example course-only; "Regroupement" verified present in the term map (alias under 'clustering', verified at course L4). |
| 0010 | CC | AGREE | No hidden shared claim. Master-ai never says K-Means is outlier-sensitive (its cons line L27 has no outlier item; all master 'outlier' occurrences are DBSCAN noise L37/L51, embedding inspection L121, anomaly detection L124/L132 — grep verified); the course has no clustering-as-anomaly-detection content in scope; the DBSCAN-outlier shared claim is separately recorded in 0007 and explicitly acknowledged here. "Outliers break the clusterer" vs "the clusterer finds outliers" are genuinely complementary facets. CC right. |
| 0011 | SD | AGREE | DR definition duplicated (master L11 fragment, course L18); linear/non-linear taxonomy explicit in course, structural in master (L58 'Linear projection', L66 'Nonlinear reduction'); motivating examples + curse list course-only (grep: zero 'curse' in master). |
| 0012 | SD | AGREE | PCA max-variance definition effectively paraphrased across vaults; math deferred to the Matrix Decomposition note (master L58, outside batches); center/covariance/eigendecompose/project mechanics + SVD equivalence course-only (verified). |
| 0013 | SD | AGREE | Linear-only/global capability boundary stated by both (master L61-62, course L49-54 incl. swiss roll); class-structure/LDA miss course-only (L55, verified); autoencoder remedy correctly split to 0027. |
| 0014 | SD | AGREE | Standardize-before-PCA nearly verbatim (master pitfall L137, course L82 incl. the procedure); course repeats in walk-away (L94) and extends to t-SNE/UMAP with the distance-based reason (L105). The course-side-extension-to-more-methods shape is the same as 0024 — consistently SD. |
| 0015 | SD | AGREE | Use-case portfolio duplicated (visualization/compression/preprocessing; master TL;DR + L125, course L6/L75); denoising course-only; JPEG-2000 compression substantiation course-only (L71, verified). S3: the "(master-ai's TL;DR)" parenthetical loosely attaches compression to the TL;DR (which lists exploration/visualization/preprocessing) — the next sentence correctly credits L125. |
| 0016 | SD | AGREE | Preprocessing speed-up claim stated by both (master L131, course L67); accuracy effect + test-with-and-without caution course-side; the interpretability tail correctly split to 0018 with cross-reference. |
| 0017 | PO | AGREE | Shared element REAL: the number of components is the one choice PCA requires (master L60 parenthetical "no hyperparameters (except # components)"; course full how-to L38/L85). Asymmetry as described: master-ai never explains HOW to choose k in this file (grep: zero explained-variance/95%/eigenvalue/selection content; the only 'variance' hits are the L58 definition and a link). Course-unique mechanics substantial; master-unique nothing beyond the acknowledgment. PO right. |
| 0018 | PO | AGREE-BORDERLINE | Shared interpretability-loss claim real on both sides (master L131 "but loses interpretability"; course L84 component-level difficulty). PO defensible — the two sides instantiate the claim at different levels (pipeline trade-off vs component mechanism), each carrying its own context, and the rationale says exactly that ("complementary-in-mechanism but shares the interpretability-loss claim") — but SD is arguable under the 0004 one-liner-vs-subsection calibration. No change requested; flagged for the record. |
| 0019 | SD | AGREE | t-SNE character sketch identical in both vaults (visualization-optimized, local-not-global; master L66-69, course L12/L46); Gaussian/Student-t construction, KL objective, crowding rationale course-only (verified L16-36); misuse guidance correctly split to 0020. |
| 0020 | SD | AGREE | Visualization-only rule stated twice by master (L70, L136) and itemized by course (L46-48, L106) incl. the perplexity-dependence reason and use-a-real-algorithm remedy; NOT-for-downstream with the non-parametric reason course-side (L46). |
| 0021 | PO | AGREE | Master evidence is a code line (L113, inside the in-batch Worked-Example code KU) — ACCEPTABLE: the record is fully transparent about it ("solely through its worked example ... never explained", "name-only on the master-ai side"), the term map's own precedent flags code-block matches as informational, and evidence-based classification may cite any in-batch KU content. Verified: perplexity appears NOWHERE else in master-ai (single grep hit = L113); the course's dedicated treatment (L52 range/effect/advice + L20 algorithmic definition) is substantial course-unique content. PO right (CC would be wrong — the course content directly extends the shared element; SD would be wrong — master makes no prose claim). |
| 0022 | SD | AGREE (R3) | Three-item advantage profile matches item for item (master L77-79; course L60/61/63). Two rationale clauses imprecise (R3): the cross-reference "(recorded in OC-ext008-0024, where both vaults state it)" — only the PCA/t-SNE determinism contrast is both-vault there, the UMAP-determinism item is course-only; and "master-ai-only: the UMAP-vs-t-SNE framing 'Modern alternative to t-SNE'" — the course also frames UMAP against t-SNE (L58 "similar goals to t-SNE but several advantages"; L60 "much faster than t-SNE"); only the exact phrase is master-only. |
| 0023 | SD | AGREE | Both vaults identify exactly n_neighbors and min_dist as the meaningful UMAP knobs (master L80 + L140 warning; course L78-79 with ranges/defaults/effects); n_neighbors~perplexity bridge to 0021 accurate. |
| 0024 | SD | AGREE (R2) | Type consistent with 0014's course-side-extension calibration: the both-vault core is the PCA-deterministic/t-SNE-stochastic contrast (master L60 + L71; course L62 + table row L92). BUT the rationale overclaims: master-ai states NOTHING about UMAP determinism/reproducibility (its UMAP bullets L77-80 are faster/global-structure/new-points/hyperparameters — verified), so "the per-method determinism profile is stated by both vaults", "encode the identical PCA-yes/t-SNE-no/UMAP-yes profile", and "The profile is duplicated" are false as applied to the UMAP entry. Wording repair R2. |
| 0025 | SD | AGREE | Selection guidance duplicated on the overlapping assignments (visualization → t-SNE/UMAP; preprocessing/downstream → PCA/UMAP; master L92-95, course L97-99 + table L93); autoencoder/VAE rows master-only; "start with PCA" ordered recommendation course-only. S4: master's L62 "Good baseline and preprocessing step" is the attribute-level counterpart worth acknowledging so the course-only claim is scoped to the advice. |
| 0026 | SD | AGREE | Embedding-inspection practice stated by both (master L121 "Essential for inspecting embedding models" + L129 deploy-gate; course L41 word2vec/BERT/ViT); the topic's "standard" wording is anchored by the course's L6 ("the standard tools for visualizing embeddings"). |
| 0027 | PO | AGREE | Shared positioning REAL on both sides: master's full definition (L84 reconstruct-through-bottleneck) + the course's pointers from BOTH DR notes (PCA L53 "Use t-SNE, UMAP, or an autoencoder for non-linear structure"; t-SNE note L4 connections line). Asymmetric depth as described; the chapter-10 teaching verified to exist outside the batches ('10 - Generative Models/10.1 - Autoencoders/01. The Autoencoder - Compression as Learning.md'); master-only properties/variants verified (L86-88). PO right. |

Special-attention items from the review brief, resolved:

- **The 4 Partial Overlap records.** 0017: shared element real (the choice exists) and the
  asymmetry exactly as described (master acknowledgment-only — grep-verified absence of
  any selection mechanics). 0018: shared claim real; PO defensible but SD arguable (the
  one BORDERLINE verdict; the rationale's mechanism-vs-consequence framing is what makes
  PO defensible). 0021: code-only master evidence acceptable (transparent framing,
  in-batch code KU, term-map precedent; perplexity otherwise absent from master-ai —
  grep-verified). 0027: shared positioning real, asymmetric depth real, cross-domain
  pointer verified.
- **0010 (the CC record).** CC is right — no hidden shared claim exists between the cited
  evidence. The nearest both-vault outlier statement (DBSCAN marks outliers: master
  L37/L51 vs course L38) is a different claim, already recorded in 0007 and explicitly
  excluded here by the rationale. Master-ai's cons line contains no outlier item and the
  course contains no anomaly-detection content in scope (both grep-verified), so neither
  PO nor SD is available for this pair.
- **Same-source-line fragments in different records.** All verified genuinely distinct
  claim scopes: master L27 → 0004 (initialization) / 0005 (spherical+size), two
  different cons items with different course counterpart subsections; master L60 →
  0017 (components choice) / 0024 (determinism), two different attributes; master L131 →
  0016 (full line, speed-up) / 0018 (tail fragment, interpretability), each with its own
  course counterpart (L67 vs L84) and mutual cross-references; likewise master L11
  (0009/0011/0015), course PCA L6 (0012/0015), course PCA L53 (0013 limitation vs 0027
  remedy), course PCA L82/84/85 (0014/0018/0017 — different numbered caveats), master
  L136/137/138/140 (0020/0014/0006/0023 — different pitfalls), course t-SNE L60-64
  (0022 items 1/2/4 vs 0024 item 3), table rows L92/L93 (0024/0025). Every such record
  pair carries distinct quote sets and distinct claims; multi-participation is expected
  (ADR-0009).
- **0021's code-mention-only evidence.** Judged acceptable. The classification layer is
  evidence-based over committed KU batches, and the cited code unit IS an in-batch KU
  (unit_type 'code', heading 'Worked Example'); the term map already records code-block
  matches (n_components at master L110) as informational, and the record nowhere claims
  master-ai explains the parameter — the PO type itself encodes the name-only
  asymmetry. This is consistent with the committed set's precedent of citing code KUs
  as evidence (e.g. OC-ext005-0028's ConfusionMatrixDisplay block).

Rationale fact-check beyond the table: verified TRUE — 0002's O(NK) master-only and
Euclidean-formula course-only; 0004's "master-ai names neither" remedy; 0005's
Euclidean-explanation course-only; 0006's silhouette-teaching location (03.6, batch
005) and the TIP's content; 0008's four master-only elaborations; 0009's
'Regroupement' term-map presence; 0011's curse list course-only; 0012's
Matrix-Decomposition deferral; 0015's JPEG-2000 course-only; 0016/0018's mutual
split; 0017's "master-ai never explains HOW to choose k in this file"; 0019's
course-only mechanics; 0021's "Master-ai's prose never mentions perplexity" (single
vault-file hit = the code line); 0023's parameter pairing; 0025's autoencoder/VAE
master-only rows; 0026's "standard" anchoring; 0027's chapter-10 teaching location.
Three FALSE/overclaiming statements found → R1, R2, R3 below.

## Check 5 — Coverage: complete; no missed cluster; no gaps

- **All 35 cross-vault discovery topics mapped.** 32 topics carry real shared claims and
  map onto the 27 records (DBSCAN→0007; K-means/centroid/initialization→0001-0006;
  PCA/variance/maximum variance/explained variance/projection→0012-0018, 0024-0025;
  UMAP/t-SNE/global-local structure/perplexity→0019-0025; clustering/cluster/
  unsupervised→0009; compression/noise→0015/0007; dendrogram/hierarchical→0008;
  dimensionality reduction/low-dimensional/nonlinear→0011/0013/0027; distance→0002/0005/
  0010-0013; elbow method/choosing k→0006/0017; embedding/visualization→0026/0015/0025;
  hyperparameters→0017/0021/0023; inertia→0003; manifold→0019-adjacent course-only
  mechanics; preprocessing/scale→0014/0016/0022). The remaining 3 topics are non-claim
  term collisions: 'labels' (master code L107 + master pitfall L139 × course PCA L55 —
  three unrelated claims), 'manifold' (master import L102 + citation L145 × course
  mechanics), 'sklearn' (library mentions both sides; the course L154 mention is already
  evidence in 0004).
- **Both-unclassified cross-vault pair mining (all 934 pairs).** Every cross-vault pair
  in which BOTH KUs are unclassified involves at least one non-content unit:
  frontmatter, See Also / Further Reading / 'Next' navigation links, walk-away
  restatements, or the 'scale' term collision (master L46 "doesn't scale" vs course L15
  "algorithms scale as O(d)" — different claims sharing a word; the term map itself
  flags 'scale' as a known spurious-match source). No genuine shared-claim pair is left
  unclassified.
- **All 52 non-participating KUs accounted for**: course-only elaborations and examples
  (mermaid flowchart, 1D worked example, library analogy, medical-diagnosis example,
  WCSS formula, JPEG-2000, SVD, t-SNE algorithm math, UMAP manifold mechanics,
  high-dimensionality examples), master-only elaborations (hierarchical benefits/
  complexity, O(NK), MiniBatchKMeans, vector-DB indexing, labels-arbitrary pitfall,
  'Modern alternative' phrase, autoencoder variants), restatement units (walk-away
  lists, file intros, table remainders), navigation/frontmatter/references, and KUs
  whose claims are carried by cited sibling KUs of the same passage.
- **Deliberate non-records verified correct.** Silhouette is master-only WITHIN SCOPE
  (zero hits in course 03.5/03.8; the course's silhouette teaching is the 03.6
  clustering-metrics file, extracted in EXT-005 as batch 005 — outside this domain;
  the term map documents exactly this, and master-ai's only vault-wide silhouette
  occurrences are L29/L138 of this file). Curse of dimensionality is course-only (zero
  master-ai hits). Neither is a record — correct.
- **Cross-domain observation (not a gap).** The silhouette cluster (master L29/L138 ×
  course 03.6 file) spans batch 006 × batch 005 and is not recordable by any
  single-domain classification under the current scoping; it is correctly deferred to
  synthesis with documentation in the term map and in 0006's rationale.
- **No coverage gaps.** CG-0.

## Check 6 — Append-only discipline: verified

- `git status`: NO modified tracked files; the only untracked paths are the EXT-008
  artifacts (batches 006/007, term map, discovery reports, fidelity/determinism/
  coverage/term-map-verification reports, generator scripts, the classification file)
  plus this review's own script — all expected.
- sha256 of the four committed classification files, working copy == `git show HEAD`:
  001-ext003 `34be3a97cf01bee713d5ccc85a0bb80d356506fce15f1a3e9e0009fdec84af6e`,
  002-ext004 `cb81adc170db4ad481d3d636e818e02e3030a615645ff204c0a22713b2dbcf36`,
  003-ext005 `b958c3923dd9664012409961929f3ad4dd0da0e1afd03f33b6ae7e3e5a5b0700`
  (also matches the EXT-006 evaluation-dossier provenance record),
  004-ext007 `5d52987dcba389639f22351e86c43b1fbfa19a50b27982f33b955088d36697be`.
  Byte-unchanged, all four.
- The new file contains no `supersedes_classification_id` and no `review` field; ids are
  namespaced OC-ext008-*; nothing edits, replaces, or claims to supersede any committed
  record. KU-id disjointness verified: batches 001-005 (775 ids) ∩ batches 006/007
  (114 ids) = ∅, and all committed records reference only batches 001-005.

## Consistency with committed records: no duplication

Keyword sweep over all committed topics+rationales for this domain's vocabulary found
only two adjacent records, neither a duplication: OC-ext003-0014 "Feature scaling /
standardization practice" (regression domain: GD-conditioning / Min-Max / Z-score /
L1-L2 motivation, evidence from the regression files — a different claim scope and
disjoint source passages and KU sets from OC-ext008-0014's standardize-before-PCA
rule) and OC-ext004-0028 (the word "cluster" appears only in the phrase "claim
cluster"). No EXT-005/EXT-007 evaluation record touches clustering/DR content. The four
committed files and the new file duplicate no claim.

## Additional finding — EXT-006 dossier/registry interaction (→ R4)

With the new classification file present, `python3 -m pytest tests -q` gives
**415/415** — no drift-guard failure (unlike the EXT-007 situation, because
`scripts/ext006_dossiers.py` DOMAINS covers only regression/tree-based/evaluation and
no committed dossier includes the clustering domain). However, the EXT-008 task
record's own outputs/acceptance criteria require the commit to add the clustering
domain to the dossier config (batches 006+007, classification file 005, term map
clustering-domain-v1.json), generate `state/dossiers/clustering-v1.json`
(byte-identical double-run), rebuild the registry (kureg-init --force + kureg-load ×7 +
kureg-apply-overlap ×5 + kureg-validate), and update task-queue/current-state/
checkpoint/handoff. This is a required pre-commit process action, not a defect of the
classification records.

## Required repairs (before commit; R1-R3 are wording-only, no type/evidence changes; R4 is a process action)

- **R1 — OC-ext008-0001 (rationale factual inaccuracy).** "The shared claim (dominance +
  simplicity) is duplicated" is FALSE for simplicity: the course never characterizes
  K-Means as simple — its only characterizations are "the most popular" (L35, the cited
  evidence) and "fast and popular" (L149, uncited); "The simplest" is master-ai's
  wording (L17) and master-ai's pro "simple, fast" (L26). Fix: reword to e.g. "The
  shared claim (K-Means as the dominant/reference clustering algorithm) is duplicated;
  master-ai additionally stresses simplicity ('The simplest', 'simple, fast'), which
  the course does not echo (it says 'fast and popular')." The topic ("default,
  most-used") needs no change.
- **R2 — OC-ext008-0024 (rationale factual inaccuracy).** "The per-method determinism
  profile is stated by both vaults", "encode the identical PCA-yes/t-SNE-no/UMAP-yes
  profile", and "The profile is duplicated" overclaim: master-ai states ONLY the
  PCA-deterministic (L60) and t-SNE-stochastic (L71) entries; its UMAP bullets (L77-80)
  say nothing about determinism or reproducibility (verified — no other mention in the
  file). Fix: scope the duplicated claim to the PCA/t-SNE determinism contrast and mark
  the UMAP-determinism entry as course-side extension, mirroring how 0014 handles the
  t-SNE/UMAP extension of the standardization rule (e.g. "...the course's UMAP item
  and table row extend the same contrast to UMAP, which master-ai's UMAP profile does
  not address; the shared core — PCA deterministic, t-SNE stochastic — is duplicated").
  The SD type stands.
- **R3 — OC-ext008-0022 (rationale factual inaccuracies, two clauses).** (a) "the
  determinism/reproducibility item (recorded in OC-ext008-0024, where both vaults state
  it)" — in 0024 both vaults state only the PCA/t-SNE contrast; the UMAP-determinism
  item itself is course-only (see R2). (b) "master-ai-only: the UMAP-vs-t-SNE framing
  'Modern alternative to t-SNE'" — the framing is shared (course L58: "a newer
  algorithm with similar goals to t-SNE but several advantages"; L60: "much faster than
  t-SNE"); only the exact phrase is master-only. Fix: "(recorded in OC-ext008-0024,
  which classifies the both-vault PCA/t-SNE determinism contrast and the course-only
  UMAP entry)" and "master-ai-only: the 'Modern alternative to t-SNE' phrasing (the
  comparative framing itself is shared — the course introduces UMAP as 'similar goals
  to t-SNE but several advantages')".
- **R4 — pre-commit process action (per the EXT-008 task's own acceptance criteria).**
  As part of the EXT-008 commit: extend `scripts/ext006_dossiers.py` DOMAINS with the
  clustering domain (batches 006+007, `005-ext008-clustering-dimreduction-overlap.jsonl`,
  `clustering-domain-v1.json`), regenerate dossiers (new
  `state/dossiers/clustering-v1.json`, byte-identical double-run, `--check` exit 0),
  rebuild the registry with the two new batches and the new classification file
  (kureg-init --force + kureg-load ×7 + kureg-apply-overlap ×5 + kureg-validate), and
  re-run the full suite (must remain green; currently 415/415). Update task-queue,
  current-state, checkpoint, and handoff, including the SVM→clustering scope-switch
  evidence in the task record.

## Suggested improvements (optional, non-required)

- **S1 — OC-ext008-0003**: soften "which is the same objective stated as two
  distances" — the intra-cluster half restates the WCSS objective, but maximizing
  inter-cluster distance is a broader geometric goal that is NOT part of the K-Means
  objective; e.g. "which restates the intra-cluster half of the objective and adds the
  inter-cluster side".
- **S2 — OC-ext008-0006**: optionally add the course's choosing-K challenge KU
  (KU-32e9305f6e0072c7, L106 "One of the biggest challenges ... How many clusters
  ($K$) should I choose?") and/or master L27's "need to choose $K$" fragment as
  evidence for the challenge premise of the elbow record; optionally reword "Both also
  flag the method's heuristic character" for the course side (the TIP flags the
  no-clear-elbow failure mode, adjacent to but not identical with heuristicality).
- **S3 — OC-ext008-0015**: fix the "(master-ai's TL;DR)" parenthetical — the TL;DR
  (L11) carries exploration/visualization/preprocessing; compression comes from the
  Feature-compression line (L125), which the next sentence already credits correctly.
  Optionally add the course EDA item (t-SNE file L42, KU-28ead0adb7538ca8 — already
  participating in 0026) as the exploration-side elaboration.
- **S4 — OC-ext008-0025**: acknowledge master L62 "Good baseline and preprocessing
  step" when marking the start-with-PCA advice course-only, so the claim is scoped to
  the ordered recommendation (advice) rather than the baseline characterization
  (attribute), which both vaults carry.
- **S5 — OC-ext008-0026**: optionally add the course's t-SNE-file intro KU
  (KU-9d0490a96d5c297f, L6 "the standard tools for visualizing embeddings") to anchor
  the topic's "standard inspection practice" wording on the course side with a quote.

## Limitations

- The reviewer is the same model family (GLM 5.3) as the orchestrator; independence is
  procedural (separate session, read-only scope, independently written verification
  script), not architectural.
- Semantic verdicts are judgment calls against the section-7 taxonomy, calibrated to
  this file's own precedents (0004/0014 SD, 0017 PO) rather than an external rubric;
  0018 is the one genuinely arguable call (PO vs SD); 0024's SD is accepted on the
  0014 calibration with a required wording repair.
- Coverage analysis was scoped to the committed discovery report (35 cross-vault
  topics, 934 pairs), the 62 participating and 52 non-participating KUs of batches
  006/007, the four source files read in full, and targeted greps; CAP-013 discovery
  was not re-run, and content invisible to the term map's 51 terms is out of scope of
  the discovery design (documented limitation of the method).
- The committed files' own quotes were not re-verified (EXT-005-REVIEW and
  EXT-007-REVIEW already provide that for 001-004; this review's Check 1/2 scope is
  the 89 new quotes).
- The registry was not rebuilt and no dossier was generated (both are the
  orchestrator's post-review steps; R4) — the 415/415 test result reflects the
  pre-commit state with the untracked 005 file present.

## Final verdict

VERDICT: PASS-WITH-NOTES — apply R1-R3 (rationale rewording, regenerate the file) and
R4 (clustering dossier + registry rebuild + state updates) before commit.

## Orchestrator addendum (repairs applied, pre-commit)

All required repairs and all five suggestions were applied by the orchestrator
after re-verifying each claim; the file was regenerated via
scripts/ext008_classifications.py, which re-verifies EVERY quote (old and new)
byte-exact inside the KU excerpt AND at the stated original-source line before
writing — exit 0.

- R1 (OC-ext008-0001): reworded — the shared claim is now K-Means' standing as
  the most-used/most-popular clustering algorithm; simplicity explicitly
  marked master-ai-only with the course's 'fast and popular' wording cited.
- R2 (OC-ext008-0024): reworded — shared core is now the PCA-deterministic +
  t-SNE-stochastic contrast (stated by both vaults); UMAP determinism (and the
  table's PCA column entry) explicitly marked course-only; the record's SD
  type rests on the shared contrast (0014 calibration), not on the
  three-method profile.
- R3 (OC-ext008-0022): both sub-fixes applied — the 0024 cross-reference now
  states the shared/course-only split correctly, and master-ai-only is now
  only the specific phrase 'Modern alternative to t-SNE' (the comparative
  framing marked shared via the course's 'a newer algorithm with similar
  goals to t-SNE').
- S1 (0003): reworded — the intra/inter framing now 'restates the
  intra-cluster half of the objective and adds the inter-cluster side', with
  the broader-geometric-goal caveat spelled out.
- S2 (0006): evidence extended with the course's choosing-K challenge KU
  KU-32e9305f6e0072c7 (L106, quote verified at its source line BEFORE
  adding); rationale now distinguishes master-ai's heuristicality flag from
  the course's no-clear-elbow failure mode and names the challenge premise
  (course section head; master-ai cons-line 'need to choose $K$' item).
- S3 (0015): the parenthetical now credits the TL;DR with
  exploration/visualization/preprocessing and compression separately to the
  'Feature compression' line; the course EDA item added as evidence
  (KU-28ead0adb7538ca8, L42, verified at source line).
- S4 (0025): the course-only claim is now scoped to the ordered
  start-with-PCA recommendation; the baseline attribute marked shared via
  master-ai's 'Good baseline and preprocessing step' (participates in 0013).
- S5 (0026): evidence extended with the course's t-SNE-file intro sentence
  'They are the standard tools for visualizing embeddings, clusters, and
  high-dimensional data.' (KU-9d0490a96d5c297f, L6, verified at source line),
  anchoring the topic's 'standard inspection practice' wording.

Final state: 27 records (22 Semantic Duplicate + 4 Partial Overlap +
1 Complementary Content), 64 participating KUs, 92 byte-exact quotes.
Overlap types unchanged (all repairs and suggestions were wording/evidence
extensions; no type or KU-set changes except the three evidence additions,
each in-scope and machine-verified). R4 (clustering dossier + registry
rebuild + state updates) executed as part of the EXT-008 commit.

No further independent re-review of the post-repair file was performed; the
changes are exactly the review's own R1-R3 wording fixes and S1-S5
suggestions, each machine-verified by the generator script.
