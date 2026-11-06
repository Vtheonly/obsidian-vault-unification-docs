# Next Agent Handoff

## Project state

**INTEGRATION CAMPAIGN IN PROGRESS (sessions 31–45, user directive commit
`77cf6cf`); S31 (setup), S32 (MEDNLP), S33 (2D3D), S34 (SYNPATH+VAULTX)
COMPLETE — 894/1,233 items judged (72.5%).** The unified vault (544 notes,
delivered session 28, gates green) is being extended with the user's
1,233-item project taxonomy. **INTEG-005 (S35: MAPDIG + MATHSOLVER +
WEATHER + NLME + MASTER-INDEX, 374 unique items / 345 fresh) is queued as
the next bounded unit and completes the audit phase.**

- **Campaign plan (binding):** `docs/INTEGRATION_CAMPAIGN_PLAN.md` — A/B/C/D
  decisions, depth standard, 100%-coverage hard gate, per-wave mutation
  battery, session allocation S31–S45 with adaptive rules (S34/S35 rows now
  carry the F-0049 union-accounting denominators).
- **S34 (commit bc7f6e9 → this session):** SYNPATH+VAULTX census **235/235 —
  36 covered / 6 equivalent / 41 partial / 152 absent** (64.7% absent; the
  vault has ZERO molecular-chemistry, geometric-deep-learning, GFlowNet, or
  protein-backbone content — synthon/torsion/PaiNN/SE(3)/GFlowNet/Equiformer
  families all 0 occurrences; the general attention/training core IS
  covered: QKV, cross-attention, softmax attention, autodiff, gradient
  clipping, activation checkpointing, mixed precision, NaN detection,
  checkpoint recovery, self-supervised pretraining). Validation: quotes
  verbatim-verified 235/235; re-review 33/33 (14.0%).
- **F-0048 (binding rule for S35):** one item = one judgment. Items already
  judged in a prior canonical judgment file are carried over verbatim
  (verdict/destination/quote/rationale preserved, `carry_over_from`
  provenance added), never re-judged. S35 has 29 carry-overs (23 from
  MEDNLP/2D3D, 6 more from SYNPATH) — the S34 validator
  (`scripts/s34_validate_judgments.py`) shows the reference implementation
  (carry-over block reading prior files, manifest carry_over list, rationale
  suffix convention).
- **F-0049 (denominator correction):** cluster counts in the plan's session
  table were naive sums; unique-item denominators are SYNPATH+VAULTX = 235
  (not 237) and the S35 set = 374 (not 382). No coverage gap — dual-cluster
  items are judged once, in their first-occurrence cluster section.
- Artifacts: `state/integration/judgments-{mednlp,2d3d,synpath}-v1.jsonl`,
  `reports/integration/s3{1,2,3,4}-*.json`; findings F-0048..F-0050 appended
  to `state/findings.jsonl`.
- **Judgment machinery (reusable):** `scripts/s34_pack_groups.py` (handles
  multiple clusters + carry-over exclusion; INSTRUCTIONS embed the
  chemistry/equivariance/RL terminology hints), `s34_validate_judgments.py`
  (carry-over merge + all mechanical checks),
  `s34_closeout.py` (aggregate + findings + queue + checkpoint).
- No vault mutations during judging; sources 276/276 + 333/333
  byte-identical; 836/836 tests.
- Checkpoint: `state/checkpoints/checkpoint-2026-11-07-integ-session34.json`
  (accelerated_mode: INTEG sessions 1–4 of 15 consumed, 11 remaining, none
  failed).

## If a future session runs

1. Follow the startup protocol (AGENTS.md §2): verify this handoff against
   repository evidence — the session-34 checkpoint, task-queue row INTEG-005,
   the judgment files, and the re-runnable validator
   (`python3 scripts/s34_validate_judgments.py` must print VALIDATION
   PASSED 235/235; the scratch group outputs are gitignored but
   deterministically reconstructible from manifest + canonical file — see
   the session-34 startup for the reconstruction snippet, or just verify
   schema+quotes+set-coverage of the canonical file directly).
2. **Next task (INTEG-005, S35):** remaining clusters MAPDIG (81) +
   MATHSOLVER (91) + WEATHER (78) + NLME (97) + MASTER-INDEX (35) = 374
   unique items (19 cross-cluster duplicates inside the set), 345 fresh
   after 29 F-0048 carry-overs. Reuse the S34 machinery end-to-end: pack
   groups by cluster+section (≤18 items, sections never merged), run
   bounded judgment groups (grep surface + alternative terminology before
   any absent verdict; verbatim quotes ≥12 words for covered/equivalent),
   validate mechanically, re-review ≥10%, aggregate, then open INTEG-006
   (S36: decision ledger A/B/C/D + destinations for all 1,233 items).
3. Expected S35 profile (from S31 lexical evidence + S32–S34 results): the
   general-ML core (attention variants, normalization, optimizers,
   tokenization, retrieval, evaluation) mostly covered/partial;
   domain-specific layers likely absent — MAPDIG geospatial/time-series
   (weather is its own cluster), MATHSOLVER OCR/document parsing/symbolic
   math, WEATHER meteorology (Numerical Weather Prediction, GFS/ERA5-style
   data, graphCast-family), NLME long-context/memory architectures (check
   what S32's MEDNLP judgments already cover for attention/memory items —
   23 of S35's items were pre-judged there), MASTER-INDEX 35 cross-field
   items (many may resolve to covered/equivalent via existing notes).
4. S36 after S35: decision ledger for all 1,233 items — reuse the 26
   equivalence mappings recorded so far (12 MEDNLP, 8 2D3D, 6 SYNPATH) and
   the F-0050 layer analysis for wave sizing. The SYNPATH wave is the
   largest B/C/D workload and runs first in S37+.
5. **Project-context authority rule (plan §2):** never invent project
   usage; the list's annotations (Repository: lines, distinctions, status
   notes) are the only authoritative project context.
6. Environment notes: the sandbox venv may need `pip install -e .` before
   the suite passes; the repo must be cloned to `/home/z/my-project/repo`
   (the session scripts hardcode that path); configure the git credential
   store before pushing (AGENTS.md §13 — the PAT comes from the user, never
   committed or printed).
7. Standing rules for any vault mutation: sources immutable; anchored
   probe-idempotent repair scripts; lint + links + full-corpus audit +
   dup-scan + see-also-audit + full suite after the last mutation;
   continuous commit-and-push with remote-ref verification (AGENTS.md §13).

## Explicit non-claims

- Judgments exist for MEDNLP + 2D3D + SYNPATH/VAULTX only (894/1,233 =
  72.5%); MAPDIG, MATHSOLVER, WEATHER, NLME, MASTER-INDEX are not yet
  semantically judged (INTEG-005/S35 does this).
- "Covered/equivalent" means concept-level coverage at the depth standard;
  it does NOT include the user's project usage — project context is
  integrated in the S37+ execution waves.
- The 244 partial and 540 absent verdicts (MEDNLP+2D3D+SYNPATH) are
  findings about the vault, not yet integration decisions; the A/B/C/D
  ledger opens at S36.
- Single-judge-per-item design is mitigated by mandatory multi-term search +
  the 10.3–14.0% re-reviews (41/41, 30/30, 33/33); borderline calls carry
  judge-noted uncertainty in the rationales.
