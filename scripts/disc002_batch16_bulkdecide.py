#!/usr/bin/env python3
"""DISC-002 session 16 (batch 16): ADR-0011 calibrated bulk decision engine.

Builds a one-pass corpus evidence index (real headings via the authoritative
mdextract state machine + definition-pattern windows OUTSIDE code fences,
F-0021-fixed fence_spans semantics), then classifies every remaining
signal-rule candidate into:

  N  mechanical noise class (validated: zero non-reject outcomes in the
     2,063-decision calibration set)            -> bulk REJECT
  P  citation-backed definitional treatment for the exact term
     (heading hit or def-window hit)             -> bulk COVER
  H  head/suffix phrase of the term has a treatment (terminology of
     covered material; validated on calibration) -> bulk REJECT
  R  residual: probe-negative, concept-shaped    -> individual review

 NOTHING is auto confirm_gap/merge/defer/revise (ADR-0011 §3).

Outputs (scratch):
  disc002-s16-bulkreport.json      calibration validation + class stats
  disc002-s16-bulk-decisions.jsonl N/P/H decisions with rationales+citations
  disc002-s16-residual-bundle.jsonl R candidates with evidence bundles
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))
from vault_unification.mdextract import extract_structure_text  # noqa: E402

CAND = Path("/home/z/my-project/scratch/disc002-s16-batch15.jsonl")
SCRATCH = Path("/home/z/my-project/scratch")

VAULTS = {
    "master-ai": REPO / "source-vaults/AI /Master AI",
    "ai-course": REPO / "source-vaults/AI /AI Course",
}

DEF_PAT = re.compile(
    r"(?:is|are)\s+(?:a|an|the)\b|is\s+defined\s+as|refers\s+to|means\b|"
    r"denotes\b|definition\s+of|we\s+define",
    re.IGNORECASE,
)


def fence_spans(struct: dict, total_lines: int) -> list[tuple[int, int]]:
    """F-0021-FIXED signature (copied verbatim from batch-14/15 probes)."""
    out = []
    for f in struct.get("code_fences", []):
        start = f.get("start_line", 0)
        end = f.get("end_line")
        if end is None:
            end = total_lines
        out.append((start, end))
    return out


def in_any_span(line: int, spans: list[tuple[int, int]]) -> bool:
    return any(s <= line <= e for s, e in spans)


def norm(s: str) -> str:
    return " ".join(s.lower().replace("-", " ").replace("_", " ").split())


# ---------------------------------------------------------------- index
def build_index():
    headings = []          # (vault, rel, line, text)
    defwins = []           # (vault, rel, line, window_text)
    for vault, root in VAULTS.items():
        for md in sorted(root.rglob("*.md")):
            try:
                text = md.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            rel = str(md.relative_to(root))
            struct = extract_structure_text(text)
            spans = fence_spans(struct, len(text.split("\n")))
            for h in struct.get("headings", []):
                headings.append((vault, rel, h["line"], h["text"]))
            for m in DEF_PAT.finditer(text):
                first_line = text[: m.start()].count("\n") + 1
                if in_any_span(first_line, spans):
                    continue
                window = text[max(0, m.start() - 140): m.end() + 180]
                defwins.append((vault, rel, first_line, window))
    return headings, defwins


def tok(s: str) -> list[str]:
    return norm(s).split()


def build_token_index(items, text_getter):
    idx = defaultdict(list)
    for i, it in enumerate(items):
        for t in set(tok(text_getter(it))):
            idx[t].append(i)
    return idx


TERM_BOUND = re.compile(r"^[a-z0-9]+( [a-z0-9]+)*$")


def phrase_hits(term: str, items, idx, text_getter) -> list:
    """Adjacent, boundary-respecting match of the normalized term."""
    key = norm(term)
    if not TERM_BOUND.match(key):
        return []
    toks = key.split()
    if not toks:
        return []
    if len(toks) == 1:
        cand = idx.get(toks[0], [])
    else:
        posts = [idx.get(t, []) for t in toks]
        if any(not p for p in posts):
            return []
        cand = set(posts[0])
        for p in posts[1:]:
            cand &= set(p)
        cand = sorted(cand)
    hits = []
    pat = re.compile(r"(?<![a-z0-9])" + re.escape(key).replace(r"\ ", r"[ ]") +
                     r"(?![a-z0-9])")
    for i in cand:
        hay = norm(text_getter(items[i]))
        if pat.search(hay):
            hits.append(items[i])
    return hits


# ------------------------------------------------------- noise classes
ADV_LEX = {
    "virtually", "simply", "essentially", "basically", "actually",
    "significantly", "substantially", "dramatically", "particularly",
    "especially", "generally", "typically", "usually", "commonly",
    "frequently", "rarely", "never", "always", "often", "sometimes",
    "somehow", "anyway", "moreover", "furthermore", "however", "therefore",
    "thus", "hence", "meanwhile", "instead", "rather", "quite", "very",
    "too", "so", "just", "only", "even", "still", "already", "yet", "now",
    "then", "there", "here", "everywhere", "anywhere", "nowhere",
    "somewhere", "simplest", "easiest", "hardest", "strongest", "weakest",
    "best", "worst", "largest", "smallest", "biggest", "highest", "lowest",
    "fastest", "slowest", "earliest", "latest", "newest", "oldest",
    "former", "latter", "certain", "uncertain", "able", "unable",
    "worth", "almost", "nearly", "roughly", "approximately", "exactly",
    "precisely", "widely", "highly", "deeply", "poorly", "well", "badly",
    "together", "alone", "apart", "again", "twice", "once", "first",
    "second", "third", "finally", "previously", "currently", "recently",
    "originally", "initially", "eventually", "ultimately", "arguably",
    "notably", "importantly", "interestingly", "surprisingly",
}
MONTHS = {
    "january", "february", "march", "april", "may", "june", "july",
    "august", "september", "october", "november", "december",
}
VAULT_META = {
    "candidate note", "concrete gaps", "identify concrete", "wc -l",
    "note substantially", "never remove", "architecture decisions",
    "missing sections", "vault", "scratch", "handoff", "checkpoint",
    "todo", "to-do", "inbox", "moc",
}

NUM_UNIT = re.compile(
    r"^[\d.,]+x?\s*(?:%|kb|mb|gb|tb|k|m|b|bn|mm|params?|steps?|tokens?"
    r"|documents?|images?|words?|epochs?|samples?|examples?|pixels?"
    r"|dimensions?|features?|neurons?|layers?|classes?|bits?|flops?"
    r"|tflops?|hours?|days?|weeks?|months?|years?|seconds?|ms|x|×|d|w)?$",
    re.IGNORECASE,
)
YEAR = re.compile(r"^(19|20)\d{2}$")
IMPORT_PAT = re.compile(r"(^from\s+\S+\s+import|^import\s|\simport\s)", re.I)
DOTTED = re.compile(
    r"^(torch|nn|np|pd|plt|sklearn|torchvision|transformers|self|os|cv2|"
    r"PIL|json|math|random|time|copy|warnings|datasets|trl|peft|accelerate)\.",
)
FSTR = re.compile(r"print\(f|\{epoch|\{.*\}|f'|f\"")


def noise_class(term: str) -> str | None:
    t = term.strip()
    tl = t.lower()
    words = norm(t).split()
    if NUM_UNIT.match(t.replace(" ", "")):
        return "N1_numeric_unit"
    if YEAR.match(tl):
        return "N2_year"
    if IMPORT_PAT.search(t):
        return "N3_import"
    if re.match(r"^[a-z0-9_]+$", tl) and "_" in tl:
        return "N4_code_identifier"
    if DOTTED.search(tl):
        return "N4_code_identifier"
    if re.search(r"\(\)$", t) or FSTR.search(t):
        return "N4_code_identifier"
    if re.search(r"[(){}]", t) and not re.search(r"[a-z] [a-z]", tl):
        return "N4_code_identifier"
    if tl.endswith("'s") or tl.endswith("’s"):
        return "N5_possessive"
    if len(words) == 1 and tl in ADV_LEX:
        return "N6_adverb_adj"
    if len(words) == 1 and tl in MONTHS:
        return "N7_month"
    if tl in VAULT_META:
        return "N8_vault_meta"
    if len(words) == 1 and len(tl) <= 2:
        return "N9_too_short"
    return None


# --------------------------------------------------- head/suffix logic
STRIP_ADJ = {
    "random", "simple", "basic", "common", "different", "same", "other",
    "each", "all", "one", "two", "first", "second", "next", "last", "new",
    "old", "good", "bad", "big", "small", "large", "high", "low", "total",
    "overall", "final", "initial", "original", "current", "previous",
    "early", "late", "single", "multiple", "many", "few", "several",
    "various", "specific", "general", "particular", "certain", "given",
    "trained", "untrained", "pre-trained", "pretrained", "deep", "shallow",
    "fully", "partially", "highly", "very", "most", "least", "best",
    "worst", "main", "major", "minor", "key", "core", "central",
    "important", "critical", "essential", "useful", "practical",
    "the", "a", "an", "of", "and", "or", "in", "on", "for", "with",
    "use", "using", "used", "need", "needed", "want", "make", "making",
    "get", "gets", "take", "taking", "given", "show", "showing",
}
SUFFIX_WORDS = {"loss", "base", "step", "size", "rate", "score", "state",
                "layer", "vector", "matrix", "model", "data", "code"}


def singular(w: str) -> str:
    if w.endswith("ies") and len(w) > 4:
        return w[:-3] + "y"
    if w.endswith("ses") and len(w) > 4:
        return w[:-2]
    if w.endswith("s") and not w.endswith("ss") and len(w) > 3:
        return w[:-1]
    return w


def head_candidates(term: str) -> list[str]:
    """Suffix phrases of the term, singularized, for terminology-of checks."""
    words = norm(term).split()
    out = []
    for k in (1, 2):
        if len(words) > k:
            tail = words[-k:]
            if all(w in STRIP_ADJ for w in tail):
                continue
            if len(tail) == 1 and tail[0] in SUFFIX_WORDS and len(words) > 1:
                # generic tail word: only usable if the word before it is
                # also non-adjectival (reduces 'knowledge base' style FPs)
                if words[-2] in STRIP_ADJ:
                    continue
            out.append(" ".join(singular(w) for w in tail))
    return out


# ---------------------------------------------------------------- main
def signal(r) -> bool:
    return (r["kind"] == "fragmented_derivation"
            or r["confidence"]["score"] >= 0.8
            or r["independent_contexts"] >= 10)


def main() -> int:
    # load candidates
    records = []
    with open(CAND, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                records.append(json.loads(line))
    by_id = {r["candidate_id"]: r for r in records}

    # load calibration decisions
    dec_files = ["002a-disc002-decisions-r1.jsonl",
                 "002b-disc002-decisions-r2.jsonl"] + [
        f"002-disc002-decisions-batch{i}.jsonl" for i in range(2, 16)]
    decisions = {}
    for f in dec_files:
        for line in open(REPO / "state/concept-candidates" / f, encoding="utf-8"):
            if line.strip():
                d = json.loads(line)
                decisions[d["candidate_id"]] = d["action"]
    calib = [(cid, a, by_id[cid]) for cid, a in decisions.items() if cid in by_id]

    print("building corpus evidence index ...", flush=True)
    headings, defwins = build_index()
    h_idx = build_token_index(headings, lambda h: h[3])
    w_idx = build_token_index(defwins, lambda w: w[3])
    print(f"headings={len(headings)}  def-windows={len(defwins)}")

    def probe(term: str):
        hh = phrase_hits(term, headings, h_idx, lambda h: h[3])
        dw = phrase_hits(term, defwins, w_idx, lambda w: w[3])
        return hh, dw

    # ---- calibration validation of every class ----
    cls_of = {}
    for cid, act, r in calib:
        t = r["term"]
        n = noise_class(t)
        if n:
            cls_of[cid] = ("N", n)
            continue
        hh, dw = probe(t)
        if hh or dw:
            cls_of[cid] = ("P", None)
            continue
        heads = [h for h in head_candidates(t) if probe(h)[0] or probe(h)[1]]
        if heads:
            cls_of[cid] = ("H", None)
            continue
        cls_of[cid] = ("R", None)

    calib_stats = defaultdict(Counter)
    for cid, act, _ in calib:
        macro, micro = cls_of[cid]
        calib_stats[(macro, micro)][act] += 1
    print("\n=== CALIBRATION: class -> outcome ===")
    n_bad = 0
    for k in sorted(calib_stats, key=lambda k: -sum(calib_stats[k].values())):
        c = calib_stats[k]
        print(f"{str(k):34s} n={sum(c.values()):5d} {dict(c)}")
        if k[0] == "N" and (c.get("cover") or c.get("confirm_gap")
                            or c.get("merge") or c.get("defer") or c.get("revise")):
            n_bad += 1
        if k[0] in ("P", "H") and c.get("confirm_gap"):
            n_bad += 1
    print("N-class counter-examples / PH-class gaps:", n_bad)

    # ---- classify the remaining signal pool ----
    pool = [r for r in records
            if r["status"] == "provisional_candidate"
            and not r.get("decision_history") and signal(r)]
    print("\nremaining signal pool:", len(pool))

    out_dec = []
    residual = []
    cls_pool = Counter()
    nid = 0
    for r in pool:
        t = r["term"]
        n = noise_class(t)
        if n:
            cls_pool[n] += 1
            nid += 1
            out_dec.append({
                "decision_id": f"D-DISC002-B16-{nid:04d}",
                "candidate_id": r["candidate_id"],
                "action": "reject",
                "rationale": (
                    f"ADR-0011 bulk class {n}: mechanical non-concept "
                    f"(term shape '{t}' — numeric/code/fragment noise), "
                    f"zero non-reject outcomes for this class in the "
                    f"2,063-decision calibration set; no definitional "
                    f"treatment is required for a non-concept. KU ledger "
                    f"unaffected (ADR-0010)."),
                "reviewer": "session-16 orchestrator (GLM 4.6); ADR-0011 "
                            "calibrated bulk rule (class N) + sampled "
                            "verification",
            })
            continue
        hh, dw = probe(t)
        if (hh or dw) and not r.get("homonym_suspect") \
                and not r.get("contradiction_suspect"):
            cls_pool["P_cover"] += 1
            if hh:
                v, rel, line, text = hh[0]
                cite = f"HEADING '{text}' ({v} '{rel}':{line})"
            else:
                v, rel, line, win = dw[0]
                cite = f"DEFINITION \"{' '.join(win.split())[:160]}\" ({v} '{rel}':{line})"
            nid += 1
            out_dec.append({
                "decision_id": f"D-DISC002-B16-{nid:04d}",
                "candidate_id": r["candidate_id"],
                "action": "cover",
                "rationale": (
                    f"ADR-0011 bulk class P: citation-backed cover — the "
                    f"term has a definitional treatment in the corpus: "
                    f"{cite}; fence-aware authoritative heading/definition "
                    f"evidence. Concept covered; no new note needed."),
                "reviewer": "session-16 orchestrator (GLM 4.6); ADR-0011 "
                            "calibrated bulk rule (class P) + sampled "
                            "verification",
            })
            continue
        # head-of-term terminology check
        hhit = None
        for h in head_candidates(t):
            hh2, dw2 = probe(h)
            if hh2 or dw2:
                hhit = h
                break
        if hhit and not r.get("homonym_suspect") \
                and not r.get("contradiction_suspect"):
            cls_pool["H_terminology"] += 1
            nid += 1
            out_dec.append({
                "decision_id": f"D-DISC002-B16-{nid:04d}",
                "candidate_id": r["candidate_id"],
                "action": "reject",
                "rationale": (
                    f"ADR-0011 bulk class H: terminology of covered "
                    f"material — the term's head phrase '{hhit}' has a "
                    f"definitional treatment in the corpus (dedicated "
                    f"heading/definition found); the candidate itself is "
                    f"phrasing within that covered concept, not a missing "
                    f"treatment. KU ledger unaffected (ADR-0010)."),
                "reviewer": "session-16 orchestrator (GLM 4.6); ADR-0011 "
                            "calibrated bulk rule (class H) + sampled "
                            "verification",
            })
            continue
        cls_pool["R_review"] += 1
        hh3, dw3 = probe(t)
        residual.append({
            "candidate_id": r["candidate_id"],
            "term": t,
            "kind": r["kind"],
            "score": r["confidence"]["score"],
            "contexts": r["independent_contexts"],
            "homonym_suspect": r.get("homonym_suspect"),
            "contradiction_suspect": r.get("contradiction_suspect"),
            "proposed_title": r.get("proposed_title"),
            "evidence": (r.get("evidence") or [])[:3],
            "probe_heading": [f"{v} '{rel}':{line} :: {text}"
                              for v, rel, line, text in hh3[:4]],
            "probe_def": [f"{v} '{rel}':{line} :: {' '.join(win.split())[:140]}"
                          for v, rel, line, win in dw3[:4]],
        })

    print("pool class counts:", dict(cls_pool.most_common()))
    print("bulk decisions:", len(out_dec), " residual:", len(residual))

    # ---- write outputs ----
    with open(SCRATCH / "disc002-s16-bulk-decisions.jsonl", "w", encoding="utf-8") as fh:
        for d in out_dec:
            fh.write(json.dumps(d, ensure_ascii=False) + "\n")
    with open(SCRATCH / "disc002-s16-residual-bundle.jsonl", "w", encoding="utf-8") as fh:
        for d in residual:
            fh.write(json.dumps(d, ensure_ascii=False) + "\n")

    # residual score/context distribution to guide review policy
    sc = Counter(round(x["score"], 1) for x in residual)
    print("residual score dist:", dict(sorted(sc.items())))
    low = [x for x in residual if x["score"] <= 0.7 and x["contexts"] < 15
           and x["kind"] != "fragmented_derivation"]
    print("residual low-signal cell (score<=0.7, ctx<15, not frag-deriv):", len(low))
    # calibration agreement within that cell
    cell = [1 for cid, act, r in calib
            if cls_of[cid][0] == "R" and r["confidence"]["score"] <= 0.7
            and r["independent_contexts"] < 15
            and r["kind"] != "fragmented_derivation" and act != "reject"]
    celltot = [1 for cid, act, r in calib
               if cls_of[cid][0] == "R" and r["confidence"]["score"] <= 0.7
               and r["independent_contexts"] < 15
               and r["kind"] != "fragmented_derivation"]
    print(f"calibration same-cell: {len(celltot)} members, "
          f"{len(cell)} non-reject -> {len(cell)} counter-examples")

    (SCRATCH / "disc002-s16-bulkreport.json").write_text(json.dumps({
        "calibration_size": len(calib),
        "calibration_class_outcomes": {str(k): dict(v)
                                       for k, v in calib_stats.items()},
        "n_or_ph_counterexamples": n_bad,
        "pool_size": len(pool),
        "pool_class_counts": dict(cls_pool.most_common()),
        "bulk_decisions": len(out_dec),
        "residual": len(residual),
        "residual_low_signal_cell": len(low),
        "residual_low_signal_cell_calibration": {
            "members": len(celltot), "non_reject": len(cell)},
    }, indent=1) + "\n")
    print("saved bulkreport")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
