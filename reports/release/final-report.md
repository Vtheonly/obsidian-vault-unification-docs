# Final Acceptance Report — Unified Vault Release

**Date:** 2026-11-06 · **Session:** 28 (SYNTH-001 final phase) · **Prepared by:** s28 orchestrator (Z AI / GLM 5.3)

## 1. Deliverable

`output/Unified-Vault/` — **544 canonical notes** across 20 areas, synthesized and
rewritten (not concatenated) from two immutable source Obsidian vaults:

| Area | Notes | Area | Notes |
|---|---|---|---|
| 01 - Foundations | 20 | 11 - Foundation Models and Multimodal | 13 |
| 02 - Mathematics | 18 | 12 - Generative Models | 12 |
| 03 - Python and Data Tooling | 29 | 13 - Training and Adaptation | 11 |
| 04 - Machine Learning | 27 | 14 - Inference and Production | 26 |
| 05 - Neural Network Foundations | 21 | 15 - Agents and Tooling | 41 |
| 06 - Computer Vision | 79 | 16 - Interpretability and Research | 31 |
| 07 - Sequence Models | 14 | 17 - Papers | 56 |
| 08 - Attention and Transformers | 38 | 18 - Projects | 25 |
| 09 - NLP and Language Models | 11 | 19 - Reference and Practice | 48 |
| 10 - Large Language Models | 7 | 20 - Vault and Project Context | 17 |

Planned notes (canonical-structure-v1.json): **544**. Generated and verified:
**544/544**. Generated via bounded subagent groups (sessions 20–28), each group's
output machine-verified (never trusted on assertion).

## 2. Release-gate evidence (docs/MILESTONES_AND_ACCEPTANCE.md, Milestone 8)

| # | Criterion | Evidence |
|---|---|---|
| 1 | Source files/assets accounted for | Both vaults inventoried and manifest-verified byte-identical at s28 start, mid, and end: ai-course 276/276, master-ai 333/333 (`reports/synthesis/s28-immutable-*.json`); 609 source files → 27,536 knowledge units (`state/dispositions/001-disp001-rule-driven.jsonl`, registry validated) |
| 2 | Every KU has a defensible disposition | 27,536/27,536 assigned exactly one disposition with destinations: Preserved 18,478 / Consolidated 8,106 / Contextualized 950 / Superseded 2 (each with rationale) — registry rebuild s28: applied 27,536, revised 0, skipped 0 (`reports/synthesis/s28-kureg-apply.json`) |
| 3 | No Unaccounted units | `unaccounted_after: 0`, `unaccounted_count: 0`, `needs_review_count: 0` (`reports/synthesis/s28-kureg-validate.json`) |
| 4 | No critical unresolved findings | Full-corpus audit: **0 findings (0 critical / 0 major / 0 minor)** over all 27,536 KUs (`reports/synthesis/s28-final-full-corpus-audit.json`); findings ledger: 0 open (9 closed this session with evidence; F-0016 open-operational and F-0018 partially-fixed are documented environment/historical items, severities moderate/low) |
| 5 | Needs-review visibility | §5 below (documented exclusions and uncertainty — no claim of absolute completeness) |
| 6 | Full-corpus checks complete | All 8 audit checks over 27,536 KUs / 544 notes; corpus-wide quality assessment (0 dimensions below band); corpus-wide drift audit (§4); lint 0 errors / 85 classified warnings; 11,999 links checked, 0 problems |
| 7 | Equations/code/examples/unique details validated | Marker retention: **42,156 markers verified present, 0 missing** — 26,308 term + 14,119 math + 1,729 code fingerprints (full-corpus audit; whitespace-insensitive, F-0031/F-0034 semantics) |
| 8 | Provenance valid and traceable | Every note carries frontmatter `sources`; note→KU provenance via ledger + union provenance (544 notes / 28,754 memberships); KU→source via registry (byte-fidelity verified at extraction, `vu ku-fidelity`) |
| 9 | Links/anchors/embeds checked | `vu check-links`: 544 files, 11,999 links, 0 problems, 3 external (`reports/synthesis/s28-final-check-links.json`); lint LINK_BROKEN/LINK_AMBIGUOUS = 0 |
| 10 | Editorial consistency | Corpus assessment: all 544 notes within type bands on every measured dimension (0 below band); drift audit §4; single style contract (EDITORIAL_STYLE_GUIDE v1 conventions) enforced through per-area gates sessions 20–28 |
| 11 | No unexplained regressions | Full test suite **752/752** after the last mutation; sources immutable at every checkpoint; delta-verification arithmetic pre-written per batch |
| 12 | Independent usability | 0 references to source-vault paths, vault locators, or this project anywhere in the vault (mechanical grep s28); self-contained notes; navigation via area MOCs; archived project context isolated in area 20 |
| 13 | Final report with denominators | This document |
| 14 | Reproducible state | Sources in-repo + SHA-256 manifests; all pipeline scripts committed (deterministic, replay-verified — e.g. the s28 gap-treatment replay regenerated the discovery index byte-identically); git history with continuous push verification |

## 3. Knowledge accounting (denominators explicit)

- **Source corpus:** 609 files (276 ai-course + 333 master-ai), ~5M+ tokens.
- **Knowledge units:** 27,536 extracted, schema-validated, byte-faithful to sources
  (`vu ku-fidelity` at extraction; 71 committed batches).
- **Dispositions:** 27,536/27,536 = Preserved 18,478 + Consolidated 8,106 +
  Contextualized 950 + Superseded 2 (rationales recorded) + Unaccounted **0**.
- **Dossier-extension classification:** 69,185/69,185 pairs decided (5,441
  participate / 63,744 reject-pair), sessions 18–19.
- **Confirmed gaps:** 3/3 given dedicated treatments (s28, §6).
- **Markers verified present:** 42,156/42,156 (0 missing).

## 4. Corpus-wide drift re-audit (all 14 recorded waivers re-checked)

Corpus assessment over all 544 notes with the union provenance
(`reports/synthesis/s28-corpus-assess.json`): **0 dimensions below band**.
Corpus drift (`reports/synthesis/s28-corpus-drift.json`):

- **concept (388 notes), example (45), overview (23), tutorial (33): no systematic
  drift** — the ten per-area concept/example waivers from sessions 21–23 do not
  survive at corpus scale, confirming they were batch-composition artifacts.
- **derivation (10 notes):** examples dimension 0.867 → 0.533 (rel 0.38), overall
  mean flat 0.944 → 0.944. Root cause measured: the derivation TYPE spans two
  source families — the first tertile (backprop-family) sources carry 32
  example-discourse markers, the last tertile (KL-divergence loss,
  reparameterization trick, SVM Lagrangian dual) sources carry **2**. Per-note
  retention verified (2→2, no loss).
- **reference (45 notes):** examples dimension 0.773 → 0.640 (rel 0.17, barely
  above the 0.15 threshold), overall mean flat 0.906 → 0.904. Per-note marker
  retention is net-positive in both tertiles (90→92 and 105→108); the residual
  per-note losses are discourse-style consolidations (verified for the largest
  case, Backpropagation.md 27→13: all concrete example content — pixel values,
  0.01 learning rate, Iris/Setosa, house price, f(x)=ax — present; the losses are
  lecture-style "let's" framing and duplicated "e.g." phrasing; knowledge
  markers all audit-verified).
- The area-20 and area-04 reference waivers (tertile-composition /
  small-sample ordering) re-verified with source measurements this session.

Conclusion: both corpus-scale drifts are content-family/tertile-composition
artifacts with flat overall means, 0 below band, and verified per-note content
retention — no editorial decline between early and late notes.

## 5. Limitations and unresolved uncertainty (honest disclosure)

1. **Marker retention is lexical, not semantic.** The 42,156 verified markers
   prove preservation of rare terms, equations (normalized LaTeX), and code
   fingerprints. Claims carried only by common vocabulary, and legitimately
   reworded passages, are covered by the marker net only partially;
   human/AI-reading-level semantic equivalence is a separate evidence class
   that this project performed via per-area generation review + spot audits,
   not a full per-unit semantic proof (ADR-0011 removed the universal dual
   review under the user's accelerated directive).
2. **46,978 low-signal provisional discovery candidates** remain a documented
   exclusion (single/few-occurrence, low-evidence terms that never reached the
   decision threshold). Their content is not lost — it lives in the preserved
   KUs — but they never received standalone concept treatment.
3. **Tier A dossier-extension auto-accepts** retain ~17% single-side
   over-inclusion (safe direction: material included rather than dropped;
   documented in the session-18 report).
4. **Source-internal contradictions preserved, not adjudicated** (keep-both
   rule): e.g. the Conv2d bias-initialization discrepancy (F-0009) is preserved
   as both source statements; the reader sees the inconsistency of the record.
5. **Area 20 is the archival layer**: the source vaults' own management records
   (roadmaps, decision logs, status snapshots) are preserved as project context
   with their internal inconsistencies kept sic (documented per note).
6. **F-0016/F-0018**: environment characteristics (background-process reaping;
   historical helper scripts with sandbox-absolute paths) — operational
   constraints, documented, not release-relevant.
7. **Equation matching is string-based**: mathematically equivalent but
   differently formatted LaTeX counts as different markers (conservative
   direction: more markers required).

## 6. Confirmed-gap treatments (s28)

All three DISC-002 confirmed gaps received dedicated sections through the
sanctioned discovery machinery (accept decisions D-DISC002-B17-0001..0003;
index: exactly 3 records confirmed_gap → accepted; discovery-validate green
over 60,154 records):

- **Second Moment** → "## First and second moments" in
  `04 - Machine Learning/Optimization Algorithms/Optimizers and Learning Rate Schedulers.md`
- **Bradley-Terry** → "### MLE for preferences is the Bradley-Terry model" in
  `02 - Mathematics/Probability/Probability Essentials.md` + cross-link from
  `DPO Derivation.md`
- **Async Def** → "## Asynchronous functions (async def)" in
  `03 - Python and Data Tooling/Python Programming/Functions and Lambda Expressions.md`

Affected areas re-verified after insertion: audits 02/03/04/13 all valid=true
0 findings; gates 4/4 pass. Record: `state/synthesis/gap-treatments-v1.json`.

## 7. Verification methods (summary)

- Deterministic framework `vu` (752 tests green; every command reports scope,
  denominator, exclusions).
- Per-area pipeline: build inputs (deterministic, committed-state-only) →
  check-prompt → bounded subagent generation → lint → omission/corruption
  audit (marker retention, link integrity, heading convention, prose quality)
  → quality drift → quality gate. Every area passed; 14 evidence-backed drift
  waivers, all re-audited at corpus scale this session (§4).
- Full-corpus audit (s28): all 8 checks, 27,536 KUs, 544 notes, 0 findings.
- Source immutability: SHA-256 manifests verified at every session start/end
  and mid-session (276/276 + 333/333 throughout).
- Continuous commit-and-push (ADR-0015/§13): every green unit committed and
  pushed immediately with remote-ref verification; s28 pushes: 1dc506e
  (area-20 prep), d1213a6 (area-20 complete), 44367c6 (gap treatments), plus
  this final state commit.

## 8. Verdict

All release-gate predicates pass with machine-verified evidence, within the
limitations stated in §5. The unified vault is complete: **544/544 notes,
27,536/27,536 knowledge units dispositioned, Unaccounted = 0, 42,156/42,156
markers verified, 0 audit findings, 0 lint errors, 11,999/11,999 links
resolving, 752/752 tests, sources byte-identical throughout.**
