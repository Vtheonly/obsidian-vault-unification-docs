# Next Agent Handoff

## Project state

**INTEGRATION CAMPAIGN IN PROGRESS (sessions 31–45, user directive commit
`77cf6cf`); S31 (setup) and S32 (MEDNLP judgments) COMPLETE.** The unified
vault (544 notes, delivered session 28, gates green) is being extended with
the user's 1,233-item project taxonomy. **INTEG-003 (S33: 2D3D semantic
coverage judgments, 291 items) is queued as the next bounded unit.**

- **Campaign plan (binding):** `docs/INTEGRATION_CAMPAIGN_PLAN.md` — A/B/C/D
  decisions, depth standard, 100%-coverage hard gate, per-wave mutation
  battery, session allocation S31–S45 with adaptive rules.
- **S31 (complete, commit b451679):** deterministic inventory
  (`state/integration/inventory-v1.jsonl`, 1,233 items / 9 clusters / 85
  documented exclusions) + lexical coverage evidence
  (`coverage-lexical-v1.jsonl`: title 73 / heading 46 / partial 484 /
  body-multi 76 / body-single 18 / none 536 — evidence only, never
  decisions) + `vu integ-inventory` / `vu integ-coverage` commands (37 new
  tests; LaTeX-escaped alias bug fixed pre-generation; determinism probes
  byte-identical).
- **S32 (complete, INTEG-002):** MEDNLP cluster fully judged — **368/368
  items, full census (no sampling), 28 subagent groups, all first-run
  clean**. Result: **89 covered / 12 equivalent / 70 partial / 197 absent**.
  Every covered/equivalent/partial judgment carries a verbatim quote
  mechanically verified as a substring of its cited note
  (`scripts/s32_validate_judgments.py`: PASSED 368/368). Orchestrator
  re-review: stratified 41-item sample (11.1%) — **41/41 agreement**.
  Artifacts: `state/integration/judgments-mednlp-v1.jsonl`,
  `reports/integration/s32-mednlp-groups.json`,
  `reports/integration/s32-mednlp-judgments.json`.
- **S32 key findings:** the medical layer is ~54% genuinely missing — the
  entire terminology stack (UMLS, SNOMED CT, ICD-10, RxNorm, LOINC, MeSH,
  HGNC, OMIM, MONDO, HPO, Orphanet) has **zero vault occurrences**; likewise
  clinical IE (negation/assertion/temporality), the clinical-BERT family,
  RDF/OWL/SKOS + triple stores, the GNN/KG-embedding family, and
  ontology-based similarity. General-ML items are largely covered
  (attention, tokenization, embeddings, retrieval/ANN, metrics, sampling).
  70 partial items define the decision-B expansion workload. 12
  terminology-equivalence mappings recorded for the S36 decision ledger
  (Explainable AI≡interpretability, Bootstrap CIs≡The bootstrap,
  Retrieve-then-Rank≡Reranking, Deterministic Generation≡greedy decoding,
  Neural Ranker≡cross-encoder reranker, Structured Generation≡constrained
  decoding, …).
- No vault mutations during judging; sources 276/276 + 333/333
  byte-identical; 836/836 tests. Findings ledger F-0001..F-0047 unchanged.
- Checkpoints: `checkpoint-2026-11-06-integ-session31.json`,
  `checkpoint-2026-11-06-integ-session32.json` (accelerated_mode: INTEG
  session 2/15, 13 remaining, no failed session).

## If a future session runs

1. Follow the startup protocol (AGENTS.md §2): verify this handoff against
   repository evidence — the session-32 checkpoint, task-queue rows
   INTEG-002/INTEG-003, the judgment file + aggregate, and the validation
   script (re-runnable: `python3 scripts/s32_validate_judgments.py` must
   print VALIDATION PASSED 368/368).
2. **Next task (INTEG-003, S33):** 2D3D cluster semantic judgments (291
   items). Reuse the S32 machinery: adapt `scripts/s32_pack_groups.py` (the
   only cluster-specific parts are the cluster id, inventory filter, and
   output paths — parameterize or copy the pattern), run bounded judgment
   groups with the same instructions (grep surface + alternative terminology
   before any absent verdict; verbatim quotes ≥12 words for
   covered/equivalent), validate mechanically (same checks), re-review ≥10%,
   aggregate, queue INTEG-004 (S34: SYNPATH + VAULTX, 237 items).
3. Then S35 (MAPDIG + MATHSOLVER + WEATHER + NLME + MASTER-INDEX, 382
   items) completes the audit phase; S36 decision ledger; S37–S43 execution
   waves; S44 independent re-verification; S45 close.
4. 2D3D expectations (from S31 lexical evidence): high absent rate on
   3D-reconstruction vocabulary (NeRF/3DGS/MVS — the lexical none-band
   concentrated in SYNPATH/2D3D), covered/partial on general CV (SIFT,
   segmentation, camera geometry basics).
5. **Project-context authority rule (plan §2):** never invent project usage;
   the list's annotations are the only authoritative project context.
6. Environment note: the sandbox venv may need `pip install -e .` before the
   suite passes (environment artifact, not a regression).
7. Standing rules for any vault mutation: sources immutable; anchored
   probe-idempotent repair scripts; lint + links + full-corpus audit +
   dup-scan + see-also-audit + full suite after the last mutation;
   continuous commit-and-push with remote-ref verification (AGENTS.md §13).

## Explicit non-claims

- Judgments exist for MEDNLP only (368/1,233 = 29.8% of the inventory);
   2D3D, SYNPATH, VAULTX, MAPDIG, MATHSOLVER, WEATHER, NLME, MASTER-INDEX
   are not yet semantically judged.
- "Covered/equivalent" means concept-level coverage at the depth standard;
   it does NOT include the user's project usage — project context is
   integrated in the S37+ execution waves per the campaign plan.
- The 70 partial and 197 absent MEDNLP items are findings about the vault,
   not yet integration decisions; the A/B/C/D ledger opens at S36.
- Single-judge-per-item design is mitigated by mandatory multi-term search +
   the 11.1% re-review (41/41); borderline calls carry judge-noted
   uncertainty in the rationales.
