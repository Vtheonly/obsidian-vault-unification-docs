#!/usr/bin/env python3
"""DISC-002 session 16: calibrate a deterministic decision rule.

Joins the 2,063 committed review decisions (r1, r2, batch2..batch15) with
the replayed candidate records (scratch/disc002-s16-batch15.jsonl) and
measures how well mechanical term-shape/kind/score classes predict the
human/orchestrator decision. Goal: find classes with ZERO non-reject
outcomes in the calibration set (safe bulk-reject classes under ADR-0011),
and quantify the size of the residual that needs individual review.

Output: scratch/disc002-s16-calibration.json + printed summary.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CAND = Path("/home/z/my-project/scratch/disc002-s16-batch15.jsonl")
OUT = Path("/home/z/my-project/scratch/disc002-s16-calibration.json")

# --- load decisions ---
dec_files = ["002a-disc002-decisions-r1.jsonl", "002b-disc002-decisions-r2.jsonl"] + [
    f"002-disc002-decisions-batch{i}.jsonl" for i in range(2, 16)
]
decisions = {}
for f in dec_files:
    for line in open(REPO / "state/concept-candidates" / f, encoding="utf-8"):
        if line.strip():
            d = json.loads(line)
            decisions[d["candidate_id"]] = d["action"]

# --- load candidates ---
records = []
with open(CAND, encoding="utf-8") as fh:
    for line in fh:
        if line.strip():
            records.append(json.loads(line))

by_id = {r["candidate_id"]: r for r in records}
reviewed = [(cid, act, by_id[cid]) for cid, act in decisions.items() if cid in by_id]
print("calibration set (joined):", len(reviewed), "of", len(decisions), "decisions")
print("actions:", Counter(a for _, a, _ in reviewed))

# --- signal rule (same as tranche scripts) ---
def signal(r):
    return (r["kind"] == "fragmented_derivation"
            or r["confidence"]["score"] >= 0.8
            or r["independent_contexts"] >= 10)

# --- mechanical term-shape classes ---
VERB_LEXICON = {
    "computes", "using", "used", "uses", "apply", "applied", "applying",
    "trained", "training", "converts", "converted", "containing", "contains",
    "including", "includes", "representing", "represents", "processing",
    "processed", "generating", "generated", "performs", "performing",
    "combining", "combined", "extracting", "extracted", "removing",
    "removed", "adding", "added", "producing", "produced", "creating",
    "created", "making", "makes", "gives", "given", "taking", "takes",
    "showing", "shows", "denotes", "denoting", "refers", "referring",
    "based", "called", "known", "defined", "defining", "learning",
    "predicting", "predicted", "predicts", "updating", "updates",
    "calculating", "calculated", "measuring", "measured", "ensuring",
    "ensures", "allowing", "allows", "enabling", "enables", "helping",
    "helps", "keeping", "keeps", "storing", "stores", "loading", "loads",
    "saving", "saves", "plotting", "plotted", "visualizing", "visualized",
    "implementing", "implemented", "initializing", "initialized",
    "returning", "returns", "printing", "prints", "running", "runs",
    "building", "builds", "choosing", "chosen", "selecting", "selected",
    "splitting", "split", "rescaling", "resized", "cropping", "cropped",
    "flipping", "flipped", "rotating", "rotated", "shuffling", "shuffled",
    "normalizing", "normalized", "standardizing", "standardized",
    "evaluating", "evaluated", "comparing", "compared", "improving",
    "improved", "reducing", "reduced", "increasing", "increased",
    "minimizing", "minimized", "maximizing", "maximized", "optimizing",
    "optimized", "tuning", "tuned", "overfitting", "underfitting",
    "converging", "converged", "diverging", "diverged", "passing",
    "passes", "multiplied", "multiplying", "summing", "summed",
    "averaging", "averaged", "stacking", "stacked", "feeding", "fed",
    "propagating", "propagated", "backpropagating", "backpropagated",
    "releasing", "released", "obtaining", "obtained", "yielding",
    "yielded", "resulting", "resulted", "leading", "leads", "suffering",
    "suffers", "avoiding", "avoids", "preventing", "prevents", "causing",
    "causes", "introducing", "introduced", "importing", "imported",
    "mapping", "mapped", "projecting", "projected", "encoding", "encoded",
    "decoding", "decoded", "sampling", "sampled", "masking", "masked",
    "weighting", "weighted", "clipping", "clipped", "freezing", "frozen",
    "accelerating", "accelerated", "decomposing", "decomposed",
    "expressing", "expressed", "expanding", "expanded", "solving",
    "solved", "substituting", "substituted", "differentiating",
    "differentiated", "integrating", "integrated", "deriving", "derived",
    "simplifying", "simplified", "canceling", "canceled", "dropping",
    "dropped", "appended", "appending", "modifying", "modified",
    "adjusting", "adjusted", "scaling", "scaled", "shifting", "shifted",
}

def term_class(term: str, kind: str) -> str:
    t = term.strip()
    tl = t.lower()
    words = tl.replace("-", " ").replace("_", " ").split()
    # 1. verb fragments: single word in the verb lexicon
    if len(words) == 1 and tl in VERB_LEXICON:
        return "verb_single"
    # 2. verb-led phrases: first word is a verb in gerund/past form + more words
    if len(words) > 1 and words[0] in VERB_LEXICON:
        return "verb_led_phrase"
    # 3. code-ish: snake_case, camelCase, def/param-like, dotted attrs
    if "_" in t and not t.lower() == t and re.match(r"^[a-z]+[A-Z]", t):
        return "code_identifier"
    if re.search(r"_[a-z]", t) and tl == t:
        return "code_identifier"
    if re.search(r"^(def |class |import |self\.|torch\.|nn\.|np\.|pd\.|plt\.|sklearn\.)", t):
        return "code_identifier"
    if re.match(r"^[a-zA-Z_]+\(\)$", t):
        return "code_identifier"
    # 4. possessive/fragment shapes
    if re.search(r"'s$", tl) or re.match(r"^[a-z]+(ing|ed)\b", tl) and len(words) == 1:
        return "fragment_shape"
    # 5. single common/stopword-ish short words
    STOPISH = {
        "the", "and", "or", "not", "with", "without", "for", "from", "into",
        "value", "values", "data", "model", "models", "note", "notes",
        "output", "outputs", "input", "inputs", "result", "results",
        "example", "examples", "code", "line", "lines", "file", "files",
        "size", "shape", "type", "types", "case", "cases", "step", "steps",
        "layer", "layers", "weight", "weights", "vector", "vectors",
        "matrix", "matrices", "number", "numbers", "function", "functions",
        "network", "networks", "learning", "deep", "simple", "basic",
        "common", "different", "same", "other", "each", "all", "one",
        "two", "first", "second", "next", "then", "when", "where", "how",
        "what", "why", "which", "that", "this", "these", "those", "there",
        "here", "also", "only", "just", "even", "still", "now", "new",
        "old", "good", "bad", "big", "small", "large", "high", "low",
        "left", "right", "up", "down", "out", "in", "on", "at", "by",
        "to", "of", "a", "an", "is", "are", "was", "were", "be", "been",
    }
    if len(words) == 1 and tl in STOPISH:
        return "stopword_single"
    return "other"


# --- classify the calibration set ---
cls_action = defaultdict(Counter)
mismatches = []
for cid, act, r in reviewed:
    tc = term_class(r["term"], r["kind"])
    cls_action[tc][act] += 1

print("\n=== term-class x action (calibration set) ===")
for tc in sorted(cls_action, key=lambda k: -sum(cls_action[k].values())):
    print(f"{tc:20s} {dict(cls_action[tc])}")

# --- how big is each class in the remaining signal pool? ---
prov_unreviewed_signal = [
    r for r in records
    if r["status"] == "provisional_candidate"
    and not r.get("decision_history")
    and signal(r)
]
print("\nremaining signal pool:", len(prov_unreviewed_signal))
pool_cls = Counter(term_class(r["term"], r["kind"]) for r in prov_unreviewed_signal)
print("pool term-classes:", dict(pool_cls.most_common()))

# non-reject outcome share per class in calibration
print("\n=== non-reject rates in calibration ===")
for tc in sorted(cls_action, key=lambda k: -sum(cls_action[k].values())):
    c = cls_action[tc]
    tot = sum(c.values())
    nonrej = tot - c.get("reject", 0)
    print(f"{tc:20s} n={tot:5d}  non-reject={nonrej:4d} ({100*nonrej/tot:.1f}%)  {dict(c)}")

# kind x action
print("\n=== kind x action ===")
ka = defaultdict(Counter)
for cid, act, r in reviewed:
    ka[r["kind"]][act] += 1
for k in ka:
    print(f"{k:28s} {dict(ka[k])}")
pool_kind = Counter(r["kind"] for r in prov_unreviewed_signal)
print("pool kinds:", dict(pool_kind.most_common()))

OUT.write_text(json.dumps({
    "calibration_size": len(reviewed),
    "actions": dict(Counter(a for _, a, _ in reviewed)),
    "term_class_x_action": {k: dict(v) for k, v in cls_action.items()},
    "remaining_signal_pool": len(prov_unreviewed_signal),
    "pool_term_classes": dict(pool_cls.most_common()),
    "pool_kinds": dict(pool_kind.most_common()),
}, indent=1) + "\n")
print("\nsaved:", OUT)
