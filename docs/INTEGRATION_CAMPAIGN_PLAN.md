# Integration Campaign Plan — "Index of the Missing Things" (INTEG)

**Campaign ID:** INTEG · **Sessions:** 31–45 (15 sessions) · **Established:** session 31, 2026-11-06
**Directive source:** user commit `77cf6cf` (commit message + `index of the missing things.txt`), binding per AGENTS.md §13–§14.

## 1. Mandate

The unified vault (544 notes, delivered session 28, all gates green) is an
established knowledge system. The user supplied a taxonomy of **1,283 raw /
1,233 unique named concepts** (deterministic parse, `vu integ-inventory`,
pinned by `tests/test_integration.py::test_real_taxonomy_regression_pin`)
drawn from **seven of their real projects**
(SynPath, Map Digitizer v2, Math Solver, Weather, InfiniChatbot/NLME, Medical
NLP, 2D3D) plus a 35-field master index. Every item must be accounted for and
appropriately integrated — **100% coverage is a hard gate** — without
duplication, disconnection, or lowering the delivered vault's quality.

The objective is **not more notes**. It is higher quality, completeness,
interconnectedness, and practical usefulness: the user built these projects and
wants to understand the technologies *through* that project context.

## 2. Inputs and their authority

| Input | Role | Mutability |
| --- | --- | --- |
| `index of the missing things.txt` (commit 77cf6cf) | authoritative item list + project context (repositories, distinctions, status notes) | immutable input; never edited |
| Commit message of 77cf6cf | authoritative methodology directive | immutable |
| `source-vaults/AI /AI Course`, `source-vaults/AI /Master AI` | immutable source corpora (276 + 333 files) | byte-identical at every session start/end |
| `output/Unified-Vault/` (544 notes) | the knowledge system being extended | mutable only via this campaign's rules |
| `state/knowledge-units/`, registry, dispositions | source-accounting universe (27,536 KUs) — **not extended by this campaign** | read-only |
| `state/integration/*` | campaign state (inventory, decisions, coverage reports) | campaign-owned |

**Project-context authority rule.** The list and its annotations are the only
authoritative source of project usage. Campaign content may state exactly what
the list documents (which repository used a concept, its pipeline role, the
list's explicit distinctions — e.g. "the microgrid fault classifier is
rule-based on DWT energy patterns, not a trained neural classifier").
**Never invent** project usage, code, results, or implementation details not
stated by the list. Where the user's earlier project notes exist inside the two
source vaults, those notes remain the source of record and are cited normally.

## 3. Campaign objectives and the coverage definition

1. Every inventory item receives a traceable status and an explicit integration
   decision recorded in the decision ledger.
2. Coverage = items fully addressed / total unique items × 100 = **100%** at
   campaign close. "Fully addressed" means **verified sufficient explanation or
   verified adequate existing coverage** — a mention, a bare link, or a title
   match does NOT count.
3. No duplicated or competing explanations; shared fundamentals explained once
   with project-specific applications linked to that central explanation.
4. All new/modified material is connected into the existing vault architecture
   (areas, MOCs, links, terminology).
5. The delivered vault's verification floor stays green at every step: sources
   byte-identical, tests green, lint/links/audit/dup-scan clean.

## 4. Item inventory (deterministic parse)

`vu integ-inventory` parses the list into `state/integration/inventory-v1.jsonl`:

- **Clusters** (top-level projects): the file has two halves — sections 1–7
  (SynPath, Map Digitizer, Math Solver, Weather, InfiniChatbot, "Additional AI
  concepts", master index) and, after a transcript-noise block, Medical NLP and
  2D3D. Cluster ids: `SYNPATH`, `MAPDIG`, `MATHSOLVER`, `WEATHER`, `NLME`,
  `VAULT-X` (§6 additional concepts), `MASTER-INDEX`, `MEDNLP`, `2D3D`.
- **Items:** `- ` bullet lines (any indent) and compact carrier lines
  (`Genes:`, `Proteins:`, `Drugs:`, `Drug Brand Names:`, `Procedures:` —
  payload split into typed entities). Master-index table rows are tab-separated:
  the *field* column is the item; the *principal concepts* column items are
  deduplicated against the rest of the inventory (they are cross-references).
- **Aliases:** trailing parentheticals (`Long Short-Term Memory (LSTM)` →
  name + alias `LSTM`).
- **Dedup:** one item per normalized name (lowercase, ASCII-folded,
  punctuation→space, British→American spelling, whitespace-collapsed); every
  occurrence (cluster, section, line) is retained on the item record.
- **Context records:** `Repository:`, `Important distinction:`, `Status note:`,
  named-list preamble lines and similar annotations are retained as cluster
  context (not items) — they constrain later integration content.
- **Exclusions (documented, never silent):** the transcript-noise block between
  the `TAHT ISNTA …` line and the `You're right. I missed two major project
  folders…` line (chat artifacts: status lines, progress notes, URLs already
  captured as cluster context). Every excluded line is recorded in the
  inventory report meta with its line number.

Inventory item ids: `INT-0001…` in first-occurrence order (stable across
re-runs; deterministic).

## 5. Coverage evidence model

Two evidence classes, kept separate (AGENTS.md §10):

**Lexical (deterministic, `vu integ-coverage`).** For each item, match surface
forms (name + alias, normalized; plus singular-folded forms) against the 544
notes: note titles, headings, frontmatter aliases, and body word-boundary
occurrences. Bands: `title` (normalized equality with a note title), `heading`
(equality with a heading), `body-multi` (word-boundary occurrences in ≥1 notes
with ≥2 total), `body-single`, `none`. Report: per-item JSONL + aggregate.
Lexical evidence **never** decides coverage alone — terminology differs
(`K-Nearest Neighbour Matching` vs the vault's American-spelling notes;
`Message Passing Neural Networks` vs a `Graph Neural Networks` note).

**Semantic (subagent judgment, recorded per item).** A judgment assigns:
`covered` (an existing note/section explains the concept at the depth standard,
with destination + verbatim evidence quote), `partial` (mentioned or
below-depth), `absent` (no adequate explanation), or `equivalent` (covered
under a different name — destination cited). Judgments come from bounded
subagent groups reading the destination notes; the orchestrator independently
re-reviews ≥10% per session; every evidence quote is mechanically verified as a
verbatim substring of the cited note (`s29/s30` machinery).

**Depth standard** (from the user's directive; the bar for "covered"): the
explanation conveys (as applicable) what the concept is, why it exists / what
problem it solves, how it works at a conceptual level, how it relates to other
vault concepts, and — when the list documents project usage — how it was used
in the user's project. Not a word count; a sufficiency judgment against this
template, recorded with evidence.

## 6. Integration decision rules

Every item gets exactly one decision in the decision ledger
(`state/integration/decisions-v1.jsonl`, one record per item id):

| Decision | Criterion | Action |
| --- | --- | --- |
| **A — adequately covered** | semantic judgment `covered`/`equivalent` at depth, destination cited with verbatim evidence | none (record + verify; no new note) |
| **B — covered, insufficient** | judgment `partial`: right home exists, explanation below depth | expand that note/section using project context from the list |
| **C — missing** | judgment `absent` | integrate in the most appropriate existing location (see §7); create a note only when necessary |
| **D — distributed** | concept partially explained across ≥2 notes | consolidate: one canonical explanation + cross-links/See Also at the others; never competing versions |

**Decision integrity rules:**

- **D before C:** if any existing note covers the concept partially, the
  decision must be B or D, never C-with-new-competing-note.
- **C collision check:** before creating, `vu integ-coverage` must show no
  title/heading/alias collision; semantic judgment must confirm no equivalent
  note exists. The coverage tool's collision report is attached to the ledger
  record.
- **A verification:** an A record without a mechanically-verified evidence
  quote is invalid (the ledger validator rejects it).
- **Destination selection (C):** prefer (i) a section inside an existing
  cluster-domain note, then (ii) a new cluster-domain note when the item
  anchors a group of related items, then (iii) a new standalone note in a
  domain area (01–16) only for concepts of vault-wide relevance.
  Project-specific variants (e.g. *Handle Availability Mask*) live in
  cluster-domain notes; shared fundamentals (e.g. *Scaled Dot-Product
  Attention*) live in domain notes with project applications linking in.
- **Anchoring:** when a cluster uses a shared concept, the domain note gains a
  short "Applied in" pointer (or the project hub links it) — the fundamental
  is explained once, applications link to it.

## 7. Architecture integration rules

- **Project hubs:** area `18 - Projects` gains one hub note per cluster
  (e.g. `18 - Projects/Applied Projects/SynPath — Protein-Based Molecular Generation.md`):
  what the project is (as documented in the list), its pipeline, the concept
  groups it used, and links into the domain notes and cluster notes. Hubs are
  the entry points; they do not duplicate concept explanations.
- **Cluster-domain notes:** concepts specific to a cluster become sections of
  new notes placed in the most fitting domain area (e.g. geometric deep
  learning → area 05/11; medical terminologies → area 09; NeRF/3DGS → area 11;
  MVS/camera geometry → area 06; time-series → area 07; associative memory →
  area 10). Exact placement is decided per item during planning with evidence.
- **MOC and link integrity:** every new note is registered in its area MOC and
  the Projects MOC; `vu check-links` 0 problems after every wave; no orphans.
- **Editorial conformance:** all new/expanded material follows
  `docs/EDITORIAL_STYLE_GUIDE.md` (numbered-heading consistency per note, prose
  sections not bullet-only, math/code conventions). New notes pass
  `vu lint-artifacts` with 0 errors.
- **Provenance markers:** every new/expanded section carries a campaign
  provenance line citing its inventory item id(s) (e.g.
  `*Integrated from the user's project taxonomy (INT-0142, SynPath).*`) so
  future audits can distinguish campaign material from source-synthesized
  material. The full-corpus audit's marker-retention check is
  destination-anchored and unaffected; heading-convention, link-integrity and
  prose checks DO scan new notes, which is intended.
- **Terminology:** American spelling per vault convention; new aliases are
  added to note frontmatter so future searches find both surface forms.

## 8. Session allocation (S31–S45) and adaptive rules

Workload-calibrated; each session is a bounded unit with its own gate.

| Session | Phase | Objective | Completion criteria |
| --- | --- | --- | --- |
| **S31** | Setup | Methodology (this doc), inventory parse, lexical coverage mechanism + first report, campaign tasks registered | inventory complete with documented exclusions; coverage report reproducible; tests green; committed & pushed |
| **S32** | Audit | Semantic coverage judgments — MEDNLP cluster (largest, 368 items) | every MEDNLP item has a judgment; ≥10% orchestrator re-review; evidence quotes verified; ledger rows valid |
| **S33** | Audit | Semantic judgments — 2D3D (291 items) | same gate |
| **S34** | Audit | Semantic judgments — SYNPATH + VAULT-X (209 + 28 items; 235 unique after F-0049 union accounting — INT-0052/INT-0202 belong to both clusters) | same gate |
| **S35** | Audit | Semantic judgments — MAPDIG + MATHSOLVER + WEATHER + NLME + MASTER-INDEX (81 + 91 + 78 + 97 + 35 items; 374 unique after union accounting, 345 fresh after the 29 F-0048 carry-overs) | same gate |
| **S36** | Planning | Decision ledger complete (A/B/C/D + destination for every item); integration plan (waves, note-level placement); coverage report v1 (per-item rows) | 100% of items have decisions; B/C/D work items enumerated with destinations; plan committed |
| **S37–S43** | Execution | 7 integration waves, cluster-ordered (largest first: SYNPATH, 2D3D, MEDNLP, then MAPDIG/WEATHER/NLME/MATHSOLVER/MASTER-INDEX); each wave = author/expand + connect + full mutation battery | per-wave: all wave items completed at depth; lint/links/audit/dup-scan/tests green; battery evidence committed; running coverage ledger updated |
| **S44** | Verification | Independent second-pass item-by-item verification against the ORIGINAL list (fresh subagents, no memory of S32–S35 judgments); duplication + terminology consistency audits | 100% re-verified; every defect repaired or ledgered; coverage report v2 |
| **S45** | Close | Final gates, final coverage report (100% demonstration), README/AGENTS/handoff updates, campaign close | all release gates green; coverage formula = 100%; handoff written |

**Adaptive reallocation rules (evidence-driven, never arbitrary):**

- If the decision ledger (end S36) shows < 500 B/C/D work items, execution
  compresses to 5 sessions; S44 verification moves earlier and one session is
  returned to the reserve.
- If > 1,100 work items, execution extends into S44's slot; verification and
  close merge into the final session (verification is never dropped, only
  compressed with wider subagent parallelism under the same evidence rules).
- Audit sessions may absorb the next cluster when throughput allows (the gate
  is per-item judgments, not calendar time), pulling the planning session
  earlier.
- A session that cannot complete its objective records a `failed_session`
  flag honestly, and the plan re-balances; the verification and close sessions
  are never sacrificed to recover time.

## 9. Verification criteria and completion gates

**Per-mutation battery (every execution wave, after the last mutation):**

1. `vu lint-artifacts` — 0 errors (new warnings classified; verbatim-source
   convention documented).
2. `vu check-links` — 0 problems.
3. `vu audit-output` full-corpus — valid=true, 0 findings (27,536 KU markers
   untouched; new notes scanned by link/heading/prose checks).
4. `vu dup-scan` — 0 findings (new material must not introduce duplication).
5. Full pytest suite green.
6. `vu verify-manifest` ×2 — sources byte-identical.

**Per-session gates:** deliverable metric moved (judgments produced / items
integrated — bookkeeping-only sessions are failed sessions per ADR-0012 §2);
state records schema-valid; continuous commit-and-push with remote-ref
verification (AGENTS.md §13); checkpoint + handoff updated.

**Campaign gates (close, S45):**

1. Coverage formula = 100% with per-item rows in the final coverage report
   (item, original coverage status, decision, resulting knowledge unit,
   verification evidence).
2. Independent second-pass verification (S44) re-confirmed ≥100% of items
   (every defect repaired and re-verified).
3. No unaccounted inventory item; ledger cross-joins the inventory exactly
   (validator-enforced).
4. Full mutation battery green on the final vault.
5. Duplication audit: no competing explanations for any integrated concept
   (dup-scan + targeted cross-section review of consolidated concepts).
6. Architecture audit: every new note reachable from an MOC; every
   B/C/D-integrated concept linked from its cluster hub.

## 10. Campaign state and records

- Task queue: `INTEG-001…` entries (schema-valid, status tracked).
- `state/integration/inventory-v1.jsonl` — the item inventory (this session).
- `state/integration/coverage-lexical-v1.jsonl` — lexical evidence per item.
- `state/integration/decisions-v1.jsonl` — the decision ledger (S32+).
- `reports/integration/sNN-*.json` — per-session machine-readable reports.
- Findings ledger: campaign findings continue F-0048+.
- Checkpoints: `state/checkpoints/checkpoint-*-sessionNN.json` with the
  `accelerated_mode` block (budget = 15 sessions from S31).
- Handoff: `docs/agent-handoff/next-agent.md` rewritten each session.

## 11. Risks

| Risk | Mitigation |
| --- | --- |
| Terminology mismatch hides existing coverage (false "missing") | semantic judgments required for C decisions; equivalence search in judging prompts; ADR "K-Nearest Neighbour" precedent |
| Integration creates competing explanations (duplication) | D-before-C rule; collision report mandatory for C; dup-scan + S44 cross-section review |
| Invented project detail (hallucination) | project-context authority rule (§2); provenance markers; S44 verification checks claims against the list |
| Scale overrun (1,209 items × depth) | cluster waves; sections-in-notes over new notes; adaptive reallocation (§8) |
| Vault coherence drift (orphan notes, MOC rot) | architecture gate in every wave; final architecture audit |
| Corpus-level regression | full battery after every mutation; sources verified every session |

## 12. Binding status

This plan is binding for sessions 31–45. Deviations require a findings-ledger
entry with rationale and an updated plan section — never a silent change. The
preservation contract (AGENTS.md §3, §7) and the verification floor remain
inviolate; the accelerated-completion policy (ADR-0012) applies with the
campaign budget substituted (15 sessions, S31–S45).
