# Next Agent Handoff

## Project state

**INTEGRATION CAMPAIGN IN PROGRESS (sessions 31–45, user directive commit
`77cf6cf`); S31 (setup), S32 (MEDNLP), S33 (2D3D) COMPLETE — 659/1,233
items judged (53.4%).** The unified vault (544 notes, delivered session 28,
gates green) is being extended with the user's 1,233-item project taxonomy.
**INTEG-004 (S34: SYNPATH + VAULTX semantic judgments, 237 items) is queued
as the next bounded unit.**

- **Campaign plan (binding):** `docs/INTEGRATION_CAMPAIGN_PLAN.md` — A/B/C/D
  decisions, depth standard, 100%-coverage hard gate, per-wave mutation
  battery, session allocation S31–S45 with adaptive rules.
- **S31 (commit b451679):** deterministic inventory (1,233 items / 9
  clusters / 85 documented exclusions) + lexical coverage evidence +
  `vu integ-inventory` / `vu integ-coverage` commands (37 tests).
- **S32 (commit 1616e7a, INTEG-002):** MEDNLP census **368/368 — 89
  covered / 12 equivalent / 70 partial / 197 absent** (medical layer ~54%
  missing: terminology stack, clinical IE, clinical-BERT family,
  RDF/OWL/SKOS, triple stores, GNN/KG-embeddings, ontology similarity all
  at zero occurrences). Validation: quotes verbatim-verified 368/368;
  re-review 41/41.
- **S33 (INTEG-003):** 2D3D census **291/291 — 28 covered / 8 equivalent /
  64 partial / 191 absent** (3D-reconstruction layer ~66% missing: camera
  models/calibration, epipolar+multi-view, MVS, bundle adjustment, point
  clouds, neural depth, TSDF/fusion, meshes, NeRF/3DGS — "radiance" never
  occurs —, building decomposition, primitives; general CV largely covered:
  SIFT/ORB descriptors+matching, ViT/CNN, norm/activation/ResNet blocks).
  Validation: quotes verbatim-verified 291/291; re-review 30/30.
  Artifacts: `state/integration/judgments-{mednlp,2d3d}-v1.jsonl`,
  `reports/integration/s3{2,3}-*-{groups,judgments}.json`.
- **Judgment machinery (reusable):** `scripts/s32_pack_groups.py` /
  `s33_pack_groups.py` (parameterize cluster id + paths),
  `s32/s33_validate_judgments.py` (schema + exact set coverage + verbatim
  quotes + absent discipline), closeout scripts. The judging prompt template
  and evidence rules are embedded in the packer scripts' INSTRUCTIONS.
- No vault mutations during judging in either session; sources 276/276 +
  333/333 byte-identical; 836/836 tests. Findings ledger F-0001..F-0047
  unchanged.
- Checkpoints: `checkpoint-2026-11-06-integ-session{31,32,33}.json`
  (accelerated_mode: INTEG sessions 1–3 of 15, 12 remaining, none failed).
  Note: S32 and S33 ran in one wall-clock session under the plan §8
  adaptive rule (audit sessions may absorb the next cluster when throughput
  allows) — both recorded as separate budget sessions.

## If a future session runs

1. Follow the startup protocol (AGENTS.md §2): verify this handoff against
   repository evidence — the session-33 checkpoint, task-queue rows
   INTEG-003/INTEG-004, the judgment files, and the re-runnable validators
   (`python3 scripts/s33_validate_judgments.py` must print VALIDATION
   PASSED 291/291).
2. **Next task (INTEG-004, S34):** SYNPATH + VAULTX clusters (237 items:
   SYNPATH 209 = geometric deep learning, equivariant architectures
   (PaiNN/Equiformer), molecular generation, GFlowNets, protein
   representation; VAULTX 28 = additional AI concepts). Reuse the S32/S33
   machinery end-to-end: pack groups by section (≤18 items), run bounded
   judgment groups (grep surface + alternative terminology before any
   absent verdict; verbatim quotes ≥12 words for covered/equivalent),
   validate mechanically, re-review ≥10%, aggregate, queue INTEG-005 (S35:
   MAPDIG + MATHSOLVER + WEATHER + NLME + MASTER-INDEX, 382 items).
3. Expected S34 profile (from S31 lexical evidence): high absent rate on
   geometric/equivariant items (the vault has no GNN note; "geometric deep
   learning" occurs nowhere), covered/partial on general deep-learning
   items (attention variants, normalization, optimizers, diffusion if
   present in SYNPATH's generative sections).
4. Then S35 completes the audit phase; S36 decision ledger (A/B/C/D +
   destinations for all 1,233 items, reusing the 20 recorded equivalence
   mappings); S37–S43 execution waves; S44 independent re-verification;
   S45 close.
5. **Project-context authority rule (plan §2):** never invent project
   usage; the list's annotations (Repository: lines, distinctions, status
   notes) are the only authoritative project context.
6. Environment note: the sandbox venv may need `pip install -e .` before
   the suite passes (environment artifact, not a regression).
7. Standing rules for any vault mutation: sources immutable; anchored
   probe-idempotent repair scripts; lint + links + full-corpus audit +
   dup-scan + see-also-audit + full suite after the last mutation;
   continuous commit-and-push with remote-ref verification (AGENTS.md §13).

## Explicit non-claims

- Judgments exist for MEDNLP + 2D3D only (659/1,233 = 53.4%); SYNPATH,
  VAULTX, MAPDIG, MATHSOLVER, WEATHER, NLME, MASTER-INDEX are not yet
  semantically judged.
- "Covered/equivalent" means concept-level coverage at the depth standard;
   it does NOT include the user's project usage — project context is
   integrated in the S37+ execution waves.
- The 134 partial and 388 absent verdicts (MEDNLP+2D3D) are findings about
   the vault, not yet integration decisions; the A/B/C/D ledger opens at
   S36.
- Single-judge-per-item design is mitigated by mandatory multi-term search +
   the 10.3–11.1% re-reviews (41/41, 30/30); borderline calls carry
   judge-noted uncertainty in the rationales.
