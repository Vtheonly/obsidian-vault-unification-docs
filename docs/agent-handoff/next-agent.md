# Next Agent Handoff

## Project state

**TWO PHASES COMPLETE + INTEGRATION CAMPAIGN OPEN (session 31, 2026-11-06).**
(1) The unified vault was delivered at session 28 and re-verified through
sessions 29–30 (544/544 notes, all gates green). (2) The user then supplied a
new directive (commit `77cf6cf`: `index of the missing things.txt` + a
binding commit-message methodology) and a **15-session budget (S31–S45)**.
Session 31 completed the campaign setup; **INTEG-002 (S32: MEDNLP semantic
coverage judgments) is queued as the next bounded unit.**

- **Campaign plan (binding):** `docs/INTEGRATION_CAMPAIGN_PLAN.md` — A/B/C/D
  integration decisions with D-before-C rule, depth standard (what/why/how/
  project-use/details/relations), 100%-coverage hard gate
  (fully-addressed / 1,233 unique items), per-wave mutation battery, session
  allocation S31–S45 with adaptive reallocation rules.
- **Inventory (S31):** `vu integ-inventory` parsed the taxonomy
  deterministically — **1,283 raw / 1,233 unique items** across 9 clusters
  (MEDNLP 368, 2D3D 291, SYNPATH 209, NLME 97, MATHSOLVER 91, MAPDIG 81,
  WEATHER 78, MASTER-INDEX 35, VAULTX 28); 85 documented exclusions (1
  preamble + 84 transcript-noise lines 719–802, every line recorded with
  number + reason); 24 context records (Repository: lines, group labels,
  distinctions — they constrain integration content). Outputs:
  `state/integration/inventory-v1.jsonl` + `clusters-v1.json`; regression pin
  `tests/test_integration.py::test_real_taxonomy_regression_pin`.
- **Lexical coverage (S31):** `vu integ-coverage` matched every item's
  surfaces (name + alias, Brit/US/plural-flexible) against the 544 notes:
  **title 73 / heading 46 / partial 484 / body-multi 76 / body-single 18 /
  none 536** (`state/integration/coverage-lexical-v1.jsonl`,
  `reports/integration/s31-coverage-lexical.json`). Lexical bands are
  **evidence, never decisions** — e.g. `Message Passing Neural Networks` is
  lexically `none` but GNN concepts live in the vault under other surface
  forms, while `Geometric Deep Learning` (also `none`) is genuinely absent
  from both source vaults.
- **Tooling:** new module `src/vault_unification/integration.py` + CLI
  commands `vu integ-inventory` / `vu integ-coverage` (path-safe, atomic
  writes, JSON reports with git stamps); 37 new tests (836/836 total);
  determinism probes byte-identical; sources 276/276 + 333/333 byte-identical.
- **Session-31 recovery note:** two earlier sessions were interrupted
  mid-implementation (uncommitted WIP: campaign plan, integration module,
  partial CLI wiring). The WIP was recovered from the working tree, reviewed
  line-by-line, completed, and tested; a real alias-split bug
  (LaTeX-escaped parentheticals) was caught by the new unit tests and fixed
  **before** any state was generated.
- Findings ledger F-0001..F-0047 unchanged (0 open).
- Checkpoint: `state/checkpoints/checkpoint-2026-11-06-integ-session31.json`
  (accelerated_mode: INTEG session 1/15, 14 remaining, no failed session).

## If a future session runs

1. Follow the startup protocol (AGENTS.md §2): verify this handoff against
   repository evidence — the session-31 checkpoint, the task-queue rows
   INTEG-001/INTEG-002, `state/integration/*`, and
   `reports/integration/s31-*.json`. Do not redo completed work without a
   regression trigger.
2. **Next task (INTEG-002, S32):** semantic coverage judgments for the
   **MEDNLP cluster (368 items)** per campaign plan §5: one judgment per item
   (`covered` / `partial` / `absent` / `equivalent`) at the depth standard,
   from bounded subagent groups reading the destination notes; every
   covered/equivalent judgment cites a destination + verbatim evidence quote
   (mechanically verified as a substring — reuse the s29/s30 machinery);
   orchestrator re-reviews ≥10%. Lexical bands from
   `coverage-lexical-v1.jsonl` are per-item hints inside the judging prompts;
   terminology-equivalence search is mandatory (e.g. `K-Nearest Neighbour
   Matching` ≡ American-spelling notes; `MPNN` ≡ GNN note). No vault mutation
   during judging.
3. Then S33 (2D3D), S34 (SYNPATH+VAULTX), S35 (rest) per plan §8; S36
   decision ledger; S37–S43 execution waves; S44 independent re-verification;
   S45 close. Adaptive rules in plan §8 (evidence-driven reallocation, never
   silent).
4. **Project-context authority rule (plan §2):** the list and its
   annotations are the ONLY authoritative source of project usage. Never
   invent project usage, code, or results. Where the user's earlier project
   notes exist inside the source vaults, those notes remain the source of
   record and are cited normally.
5. Environment note: the sandbox venv may need `pip install -e .` before the
   suite passes (subprocess test imports the package outside the repo root);
   environment artifact, not a regression.
6. Standing rules for any vault mutation: sources immutable; anchored
   probe-idempotent repair scripts; lint + links + full-corpus audit +
   dup-scan + see-also-audit + full suite after the last mutation; continuous
   commit-and-push with remote-ref verification (AGENTS.md §13).

## Explicit non-claims

- The lexical coverage report is **surface-form evidence only**; it does not
  decide coverage for any item (the 484 `partial` and 536 `none` bands
  especially await semantic judgment).
- No integration decisions (A/B/C/D) exist yet; the decision ledger opens at
  S32+ judgments and is formalized at S36.
- 44 of 81 master-index principal-concept crossrefs are surface-unmatched
  (recorded in `clusters-v1.json`); they are cross-references, not items, and
  are resolved during the semantic phase.
- The delivered vault's metrics are unchanged this session (no mutations);
  the campaign's coverage metric (0 → 1,233 inventoried) is setup evidence,
  not integrated knowledge.
