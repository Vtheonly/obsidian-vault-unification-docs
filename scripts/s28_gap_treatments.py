#!/usr/bin/env python3
"""S28/SYNTH-001 gap treatments, phase B: treat the three confirmed gaps.

The three confirmed_gap candidates from DISC-002 (index
state/concept-candidates/002-disc002-full-corpus.index.jsonl) each receive a
DEDICATED treatment: a coherent explanatory section in the single most
load-bearing canonical note for that concept (the 544-note structure is
unchanged; the gap KUs' content is already preserved and audited in their
ledger destinations — what the gaps lack is the connective explanation the
discovery records flagged as missing).

Treatments (candidate -> section):
  CG-fe05f71fc6ba "Second Moment"  -> "## First and second moments" in
      04 - Machine Learning/Optimization Algorithms/Optimizers and Learning
      Rate Schedulers.md (5 gap KUs destined here; the Adam treatment is the
      heaviest user of the moment vocabulary)
  CG-c8f6e1408dc2 "Bradley-Terry"  -> "### MLE for preferences is the
      Bradley-Terry model" in 02 - Mathematics/Probability/Probability
      Essentials.md (the probability home; MLE section already teaches the
      classification/regression cases) + a cross-link from DPO Derivation.md
  CG-00366e34ee82 "Async Def"      -> "## Asynchronous functions (async def)"
      in 03 - Python and Data Tooling/Python Programming/Functions and Lambda
      Expressions.md (def is taught here; every area-15 async use is an
      I/O-bound client/server pattern that presumes this vocabulary)

Then, through the sanctioned machinery:
  1. note insertions (anchored, probe-idempotent; same discipline as the
     s28 marker repairs);
  2. batch17 accept decisions (confirmed_gap -> accepted) applied via
     `vu discovery-decide` to the replayed post-batch16 state (phase A);
  3. `vu discovery-index` -> the committed index is updated;
  4. `vu discovery-validate` -> green;
  5. union provenance (note -> ku_ids for all 544 notes, from the committed
     ledger) written for the corpus-wide drift re-audit;
  6. treatment record state/synthesis/gap-treatments-v1.json.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRATCH = REPO / "scratch" / "s28-gap"
VAULT = REPO / "output/Unified-Vault"

OPT = VAULT / "04 - Machine Learning/Optimization Algorithms/Optimizers and Learning Rate Schedulers.md"
PE = VAULT / "02 - Mathematics/Probability/Probability Essentials.md"
FN = VAULT / "03 - Python and Data Tooling/Python Programming/Functions and Lambda Expressions.md"
DPO = VAULT / "13 - Training and Adaptation/Fine-Tuning/DPO Derivation.md"

MOMENTS_SECTION = """## First and second moments

The vocabulary of *moments* recurs throughout the optimizer and loss-function literature, and the adaptive optimizers below depend on it directly, so it is worth making precise first. The **first moment** of a random variable is its expectation, $E[X]$ — the mean. The **second moment** is the expectation of its square, $E[X^2]$. The **second central moment** subtracts the mean before squaring, $E[(X - E[X])^2]$ — this is the variance, and its square root is the standard deviation. The raw and central second moments coincide exactly when the mean is zero; in general they differ by the square of the mean, $E[X^2] = \\mathrm{Var}[X] + (E[X])^2$.

Adam's naming follows this vocabulary exactly. Its $m_t$ is a running estimate of the *first* moment of the gradient distribution — the mean direction in which the parameter has been moving — and its $v_t$ is a running estimate of the *second* moment of the gradient, deliberately **uncentered**: it averages $g_t^2$, not $(g_t - E[g_t])^2$. The uncentered choice is what makes the per-parameter scaling meaningful. A parameter whose gradients hover around a consistent nonzero value (say $g \\approx 1.0$) has almost zero variance but a second moment near 1; the step size must be scaled by that raw magnitude, and a centered estimate would lose it entirely — dividing by the square root of a near-zero variance would explode the update. Conversely, for a parameter whose gradients oscillate around zero (say $\\pm 0.1$), the mean nearly cancels while the second moment correctly captures the magnitude that should govern the step. Because $m_0$ and $v_0$ start at zero, both running averages are biased toward zero in the first steps; Adam's bias correction divides out this initialization bias, which matters most early in training.

The same terminology appears on the loss side, where variance is the second central moment of the error distribution — see [[Loss Functions]] — and in the hyperparameter guidance for tuning $\\beta_1$ and $\\beta_2$, which control the decay rates of the two moment estimates (the path-form link [[05 - Neural Network Foundations/Training Dynamics and Stability/Hyperparameters and Network Configuration|Hyperparameters and Network Configuration]] treats them; the mathematical background is in [[Optimization Essentials]]).

"""

BT_SECTION = """### MLE for preferences is the Bradley-Terry model

Maximum likelihood also covers a different kind of data: instead of numeric targets, you observe *comparisons* — which of two items won. The **Bradley-Terry model** assigns each item $i$ a strength parameter $s_i$ and says

$$
p(i \\succ j) = \\frac{e^{s_i}}{e^{s_i} + e^{s_j}} = \\sigma(s_i - s_j),
$$

so the probability that $i$ beats $j$ depends only on the strength difference through a sigmoid. Fitting the strengths by maximum likelihood on observed pairwise outcomes maximizes $\\sum \\log \\sigma(s_w - s_l)$ — the winner $w$ playing the role of the positive class, this is exactly the logistic-regression objective. The model is classical (Bradley and Terry, 1952) and is the standard statistical foundation for ranking from comparisons; Elo-style ratings are its online-update cousin.

This is the probability model behind preference-based reward modeling in modern alignment. A reward $r(x, y)$ plays the role of the strength, human preference labels are the comparisons, and the reward model is trained by MLE on exactly this likelihood — see [[RLHF with PPO]]. [[DPO Derivation]] then substitutes its closed-form reward into the same sigmoid, eliminating the reward model entirely. What happens to the estimate when the preference data itself is biased (for example, labelers systematically preferring verbose answers) is treated in [[Estimators and Bias]]; the original alignment application is [[InstructGPT]].

"""

ASYNC_SECTION = """## Asynchronous functions (async def)

The `def` keyword has an asynchronous variant: `async def` defines a *coroutine function*. Calling it does not run the body — it returns a coroutine object, a description of the computation that has not started yet. The body runs only when the coroutine is awaited or handed to a scheduler, which is what makes the pattern useful: many coroutines can be pending at once, each suspended wherever it is waiting.

The second half of the pattern is `await`, usable only inside `async def` functions: it suspends the enclosing coroutine until its operand completes, and while one coroutine is suspended, the *event loop* — a single-threaded scheduler — runs whichever other coroutines have work ready. No threads are created; the concurrency comes from interleaving the waiting. This is the natural model for I/O-bound programs such as clients and servers: while one request waits on a network read, the loop serves the others. The typical shape, using the collection's own vocabulary from the agent and retrieval notes:

```text
async def fetch_documents(query):
    results = await search(query)              # suspend until search returns
    docs = [await load(r.id) for r in results]  # await each load in turn
    return docs
```

The rest of the function-related syntax generalizes the same way: `async for` iterates an async iterator (one whose items arrive via `await`), and `async with` acquires and releases an async context manager. One caveat worth internalizing early: awaiting inside a loop runs the awaits one after another, which serializes I/O that could overlap — `asyncio.gather` exists to run awaitables concurrently.

This vocabulary is load-bearing across the serving- and agent-side notes: every tool handler in an MCP server (see [[MCP Overview]]) is an `async def`, PydanticAI tools are async callables (see [[PydanticAI]]), and vector-store clients expose async APIs (see [[Vector Memory Backends]]). Plain generators — the non-async counterpart of this machinery — are covered in [[Iterators and Generators]].

"""

INSERTIONS: list[tuple[Path, str, str, str]] = [
    # (path, anchor-before-which-to-insert, section, label)
    (OPT, "## Adaptive optimizers: RMSProp and Adam\n", MOMENTS_SECTION, "second moment"),
    (PE, "## MAP and Bayesian inference\n", BT_SECTION, "bradley-terry"),
    (FN, "## See also\n", ASYNC_SECTION, "async def"),
]

CROSSLINK = (
    DPO,
    "human preferences follow the Bradley-Terry model (a probability-theory staple; "
    "the KL divergence that appears throughout is the information-theoretic divergence)",
    "human preferences follow the Bradley-Terry model (a probability-theory staple, "
    "defined and derived under maximum likelihood in [[Probability Essentials]]; "
    "the KL divergence that appears throughout is the information-theoretic divergence)",
    "bradley-terry cross-link",
)

DECISIONS = [
    {
        "decision_id": "D-DISC002-B17-0001",
        "candidate_id": "CG-fe05f71fc6ba",
        "action": "accept",
        "rationale": (
            "Confirmed gap 'Second Moment' (score 1.0, unexplained_prerequisite, "
            "cross-vault, 12 KUs / 17 independent contexts) TREATED via the dedicated "
            "section '## First and second moments' in 04 - Machine Learning/"
            "Optimization Algorithms/Optimizers and Learning Rate Schedulers.md "
            "(s28, SYNTH-001 final phase): the section defines first moment, second "
            "moment, and second central moment, explains why Adam's v_t is the "
            "UNCENTERED second moment of the gradient, and links the loss-side and "
            "hyperparameter-side uses. The 12 gap KUs' content is already preserved "
            "and audited in their ledger destinations (Loss Functions, Optimizers, "
            "CNN training notes); the treatment adds the missing connective "
            "explanation. Record: state/synthesis/gap-treatments-v1.json."
        ),
        "reviewer": "s28 orchestrator (Z AI / GLM 5.3)",
    },
    {
        "decision_id": "D-DISC002-B17-0002",
        "candidate_id": "CG-c8f6e1408dc2",
        "action": "accept",
        "rationale": (
            "Confirmed gap 'Bradley-Terry' (score 0.9, fragmented_derivation, 12 KUs "
            "/ 17 independent contexts; batch-2 revise D-DISC002-B2-0070 already "
            "recorded the in-situ coverage evidence) TREATED via the dedicated "
            "subsection '### MLE for preferences is the Bradley-Terry model' in "
            "02 - Mathematics/Probability/Probability Essentials.md (s28): the "
            "model's paired-comparison form, its sigmoid rearrangement, its MLE = "
            "logistic-regression equivalence, and its role in reward modeling "
            "(RLHF/DPO/InstructGPT/Estimators-and-Bias links), plus a cross-link "
            "from the DPO Derivation preference-model step. The formula was already "
            "preserved in four notes; the treatment adds the standalone explanation "
            "the discovery record flagged as missing. Record: state/synthesis/"
            "gap-treatments-v1.json."
        ),
        "reviewer": "s28 orchestrator (Z AI / GLM 5.3)",
    },
    {
        "decision_id": "D-DISC002-B17-0003",
        "candidate_id": "CG-00366e34ee82",
        "action": "accept",
        "rationale": (
            "Confirmed gap 'Async Def' (score 0.75, fragmented_derivation, 12 KUs / "
            "29 independent contexts across the MCP, agent-framework, and "
            "vector-memory notes) TREATED via the dedicated section "
            "'## Asynchronous functions (async def)' in 03 - Python and Data "
            "Tooling/Python Programming/Functions and Lambda Expressions.md (s28): "
            "coroutine functions vs plain def, await and the event loop, async "
            "for / async with, the asyncio.gather concurrency caveat, and links to "
            "the MCP/PydanticAI/vector-backend notes whose code presumes this "
            "vocabulary. The async-def code fragments are already preserved and "
            "audited in their area-15 destinations; the treatment adds the missing "
            "language-level explanation. Record: state/synthesis/gap-treatments-v1.json."
        ),
        "reviewer": "s28 orchestrator (Z AI / GLM 5.3)",
    },
]


def run(cmd: list[str]) -> dict:
    print("+", " ".join(cmd), flush=True)
    proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    if proc.returncode != 0:
        print(proc.stdout[-2000:])
        print(proc.stderr[-2000:], file=sys.stderr)
        raise SystemExit(f"command failed: {cmd}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"raw": proc.stdout[:500]}


def apply_insertions(apply: bool) -> int:
    pending = 0
    for path, anchor, section, label in INSERTIONS + [CROSSLINK[:3] + (CROSSLINK[3],)]:  # type: ignore[misc]
        text = path.read_text(encoding="utf-8")
        if isinstance(label, str) and label.endswith("cross-link"):
            _, old, new, _lbl = CROSSLINK
        else:
            old, new = None, None
        # cross-link is a replacement; sections are insertions
        if path == CROSSLINK[0]:
            old, new = CROSSLINK[1], CROSSLINK[2]
            if new in text and old not in text:
                print(f"  already-applied: {label}")
                continue
            if old not in text:
                print(f"  !! ANCHOR NOT FOUND: {label}")
                return 1
            if apply:
                path.write_text(text.replace(old, new, 1), encoding="utf-8")
                print(f"  applied: {label}")
            else:
                print(f"  pending: {label}")
                pending += 1
            continue
        head = section.splitlines()[0]
        if section in text:
            print(f"  already-applied: {label} ({head})")
            continue
        if anchor not in text:
            print(f"  !! ANCHOR NOT FOUND for {label}: {anchor[:60]!r}")
            return 1
        if apply:
            path.write_text(text.replace(anchor, section + anchor, 1), encoding="utf-8")
            print(f"  applied: {label} ({head})")
        else:
            print(f"  pending: {label} ({head})")
            pending += 1
    if pending:
        print(f"probe: {pending} insertions pending; run with --apply")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="apply (default: probe)")
    args = ap.parse_args()

    print("== note insertions ==")
    rc = apply_insertions(args.apply)
    if rc or not args.apply:
        if rc:
            return rc

    if not args.apply:
        return 0

    # decisions file (committed)
    dec_path = REPO / "state/concept-candidates/002-disc002-decisions-batch17.jsonl"
    dec_path.write_text(
        "\n".join(json.dumps(d, ensure_ascii=False) for d in DECISIONS) + "\n",
        encoding="utf-8",
    )
    print(f"== batch17 decisions written: {dec_path.name} ==")

    # decide on the replayed post-batch16 state
    post17 = SCRATCH / "post-batch17.jsonl"
    res = run([
        "vu", "discovery-decide",
        "--candidates", str(SCRATCH / "post-batch16.jsonl"),
        "--decisions", str(dec_path),
        "--out", str(post17),
        "--candidate-schema", "schemas/concept-candidate.schema.json",
        "--decided-utc", "2026-11-06T00:00:00Z",
        "--report", "reports/discovery/s28-gap-batch17-decide.json",
    ])
    print(f"batch17 decide: {res.get('result', res).get('decisions_applied')} decisions applied")

    # re-index -> new committed index
    new_idx = SCRATCH / "post-batch17.index.jsonl"
    run([
        "vu", "discovery-index",
        "--candidates", str(post17),
        "--out", str(new_idx),
        "--max-ku-ids", "12",
        "--report", "reports/discovery/s28-gap-batch17-index.json",
    ])
    committed = REPO / "state/concept-candidates/002-disc002-full-corpus.index.jsonl"
    old = {}
    for line in committed.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            old[r["candidate_id"]] = r
    new = {}
    for line in new_idx.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            new[r["candidate_id"]] = r
    diffs = [k for k in set(old) | set(new) if old.get(k) != new.get(k)]
    print(f"index diff vs committed: {len(diffs)} records")
    for k in diffs:
        st_old = old.get(k, {}).get("status")
        st_new = new.get(k, {}).get("status")
        print(f"  {k}: {st_old} -> {st_new}")
    treated = {d["candidate_id"] for d in DECISIONS}
    committed_now_accepted = all(
        old.get(k, {}).get("status") == "accepted" and new.get(k, {}).get("status") == "accepted"
        for k in treated
    )
    if set(diffs) == treated:
        committed.write_bytes(new_idx.read_bytes())
        print("committed index updated")
    elif not diffs and committed_now_accepted:
        # treatments already committed by a previous --apply run (idempotent
        # re-entry after an interrupted run)
        print("committed index already carries the treatments (idempotent re-entry)")
    else:
        print("!! UNEXPECTED: index differs beyond the three treated candidates")
        return 1

    # validate
    res = run([
        "vu", "discovery-validate",
        "--candidates", str(post17),
        "--candidate-schema", "schemas/concept-candidate.schema.json",
        "--report", "reports/discovery/s28-gap-batch17-validate.json",
    ])
    ok = res.get("result", res).get("valid")
    print(f"discovery-validate valid: {ok}")
    if not ok:
        return 1

    # union provenance from the committed ledger (note -> ku_ids, all 544 notes)
    prov_path = SCRATCH / "union-provenance.jsonl"
    by_note: dict[str, list[str]] = {}
    with (REPO / "state/dispositions/001-disp001-rule-driven.jsonl").open(encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            for d in r.get("destinations", []):
                by_note.setdefault(d["path"], []).append(r["ku_id"])
    with prov_path.open("w", encoding="utf-8") as fh:
        for note in sorted(by_note):
            fh.write(json.dumps({"note": note, "ku_ids": by_note[note]}) + "\n")
    print(f"union provenance written: {len(by_note)} notes, "
          f"{sum(len(v) for v in by_note.values())} memberships -> {prov_path}")

    # treatment record
    record = {
        "version": "1",
        "date": "2026-11-06",
        "session": "28",
        "task": "SYNTH-001 final phase — confirmed-gap dedicated treatments",
        "treatments": [
            {
                "candidate_id": "CG-fe05f71fc6ba",
                "term": "second moment",
                "treatment": "dedicated section '## First and second moments'",
                "note": "04 - Machine Learning/Optimization Algorithms/Optimizers and Learning Rate Schedulers.md",
                "decision_id": "D-DISC002-B17-0001",
                "gap_kus_preserved_in": "ledger destinations (Loss Functions x5, Optimizers x5, Hyperparameters and Basic PyTorch Summary x3, Hyperparameters and Network Configuration x2, From Basic Convolution to Learned Weights, PyTorch Implementation Basics)",
            },
            {
                "candidate_id": "CG-c8f6e1408dc2",
                "term": "bradley-terry",
                "treatment": "dedicated subsection '### MLE for preferences is the Bradley-Terry model' + DPO Derivation cross-link",
                "note": "02 - Mathematics/Probability/Probability Essentials.md (+ 13 - Training and Adaptation/Fine-Tuning/DPO Derivation.md)",
                "decision_id": "D-DISC002-B17-0002",
                "gap_kus_preserved_in": "ledger destinations (DPO Derivation x4, Probability Essentials x3, Estimators and Bias x3, RLHF with PPO x2)",
            },
            {
                "candidate_id": "CG-00366e34ee82",
                "term": "async def",
                "treatment": "dedicated section '## Asynchronous functions (async def)'",
                "note": "03 - Python and Data Tooling/Python Programming/Functions and Lambda Expressions.md",
                "decision_id": "D-DISC002-B17-0003",
                "gap_kus_preserved_in": "ledger destinations (PydanticAI x3, Vector Memory Backends, MCP Overview, MCP Components, MCP Enterprise Integration, MCP Security, and the remaining area-15 uses)",
            },
        ],
        "machinery": [
            "phase A replay (scripts/s28_gap_replay.py): discover-gaps + 17 decision rounds, post-batch16 index byte-identical to the committed index",
            "phase B (this script): anchored probe-idempotent insertions + batch17 accepts via vu discovery-decide + vu discovery-index (committed index updated: exactly the 3 records change confirmed_gap -> accepted) + vu discovery-validate green",
        ],
        "reverification": "lint + audits + gates for areas 02/03/04/13 re-run after insertions (see s28 reports); corpus-wide drift re-audit uses the union provenance",
    }
    (REPO / "state/synthesis/gap-treatments-v1.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=1), encoding="utf-8")
    print("treatment record written: state/synthesis/gap-treatments-v1.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
