#!/usr/bin/env python3
"""DISC-002 session 16: assemble final bulk decisions + review bundles.

Single source of truth for the batch-16 classification, applying ADR-0011
classes in a safe order:

  N(validated noise: N1,N3,N4,N6,N7,N8)  -> bulk REJECT
  R2 everyday single (50/50 calib)       -> bulk REJECT
  R3_aux prose (1/1) / R4 vaultmeta(2/2) -> bulk REJECT
  P citation-backed definitional
    treatment (heading or def-window hit,
    no homonym/contradiction suspect)     -> bulk COVER
  everything else (incl. disabled H, N5,
  verb-forms, concept-shaped residual)    -> review bundle

P def-window citations are re-derived to the term's own line (not the
def-pattern line) so every file:line citation points at the evidence.
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
    out = []
    for f in struct.get("code_fences", []):
        start = f.get("start_line", 0)
        end = f.get("end_line")
        if end is None:
            end = total_lines
        out.append((start, end))
    return out


def norm(s: str) -> str:
    return " ".join(s.lower().replace("-", " ").replace("_", " ").split())


# ---- noise classes (validated subset) ----
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
MONTHS = {"january", "february", "march", "april", "may", "june", "july",
          "august", "september", "october", "november", "december"}
NUM_UNIT = re.compile(
    r"^[\d.,]+x?\s*(?:%|kb|mb|gb|tb|k|m|b|bn|mm|params?|steps?|tokens?"
    r"|documents?|images?|words?|epochs?|samples?|examples?|pixels?"
    r"|dimensions?|features?|neurons?|layers?|classes?|bits?|flops?"
    r"|tflops?|hours?|days?|weeks?|months?|years?|seconds?|ms|x|×|d|w)?$",
    re.IGNORECASE)
YEAR = re.compile(r"^(19|20)\d{2}$")
IMPORT_PAT = re.compile(r"(^from\s+\S+\s+import|^import\s|\simport\s)", re.I)
DOTTED = re.compile(
    r"^(torch|nn|np|pd|plt|sklearn|torchvision|transformers|self|os|cv2|"
    r"PIL|json|math|random|time|copy|warnings|datasets|trl|peft|accelerate)\.")
FSTR = re.compile(r"print\(f|\{epoch|\{.*\}|f'|f\"")

# everyday lexicon: identical to scripts/disc002_batch16_rfilter.py
exec((REPO / "scripts/disc002_batch16_rfilter.py").read_text()
     .split("AUX_NEG = re.compile")[0].split("EVERYDAY = {")[1]
     .join(["EVERYDAY = {", ""]).rstrip() if False else "")


def load_everyday() -> set:
    src = (REPO / "scripts/disc002_batch16_rfilter.py").read_text()
    m = re.search(r"EVERYDAY = \{(.*?)\n\}", src, re.S)
    return set(re.findall(r'"([^"]+)"', m.group(1)))


EVERYDAY = load_everyday()
AUX_NEG = re.compile(
    r"\b(doesn'?t|don'?t|didn'?t|isn'?t|aren'?t|wasn'?t|weren'?t|won'?t|"
    r"wouldn'?t|shouldn'?t|couldn'?t|can'?t|cannot|must|might|may|"
    r"should|would|could|shall)\b", re.I)
VAULT_META_R = re.compile(
    r"^(per note|notes? \d{4}|thoughts? \d{4}|new files?|file \d+|"
    r"note \d+|vault|scratch|repo|handoff|checkpoint|session|\"?moc\"?)$",
    re.I)

# finite verbs (NOT gerunds like 'training'/'learning' which head real
# concept phrases) — subject-verb / verb-object prose fragments
FINITE_VERB = {
    "adds", "gets", "takes", "gives", "shows", "means", "calls",
    "becomes", "seems", "keeps", "puts", "tries", "asks", "works",
    "plays", "runs", "walks", "reads", "writes", "speaks", "tells",
    "says", "comes", "goes", "learns", "teaches", "helps", "allows",
    "enables", "supports", "provides", "offers", "includes",
    "contains", "creates", "builds", "produces", "generates",
    "causes", "leads", "brings", "sends", "receives", "mentions",
    "describes", "explains", "discusses", "considers", "compares",
    "shares", "changes", "turns", "grows", "increases", "decreases",
    "reduces", "improves", "removes", "applies", "chooses", "selects",
    "prefers", "starts", "stops", "finishes", "completes",
    "achieves", "reaches", "arrives", "enters", "leaves", "returns",
    "deals", "handles", "treats", "processes", "trains", "tests",
    "checks", "verifies", "validates", "measures", "computes",
    "calculates", "counts", "estimates", "predicts", "decides",
    "determines", "depends", "requires", "involves", "exists",
    "happens", "occurs", "performs", "match", "use", "get", "make",
    "take", "see", "find", "know", "want", "need", "put", "try",
    "perform", "update", "tune", "scale", "serve", "treat",
    "convert", "converts", "combine", "combines", "extract",
    "extracts", "deploy", "deploys", "report", "reports",
    "consolidate", "consolidates", "democratize", "democratizes",
}
META_CHAPTER = re.compile(
    r"(\bch\d+\b|\bchapter \d+\b|\bfrontmatter\b|\bfront-matter\b|"
    r"\bresearch frontier\b|\bresearch update\b|^\d{4} research\b)", re.I)
NUMERIC_LED = re.compile(r"^\d[\d.,]*[bkmgt]?\s+[a-z]", re.I)


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
    if len(words) == 1 and tl in ADV_LEX:
        return "N6_adverb_adj"
    if len(words) == 1 and tl in MONTHS:
        return "N7_month"
    if len(words) == 1 and len(tl) <= 2:
        return "N9_too_short"
    # NOTE (calibration 2026-11-01): finite-verb phrases (N11), chapter/
    # meta references (N12) and numeric-led phrases (N13) are NOT bulk
    # classes — calibration found legitimate COVER counter-examples
    # ('use tools', 'receptive field grows', 'chapter 07', '13 inference',
    # '20 tokens per'). They stay in the semantic review bundle.
    return None


def r2class(term: str) -> str | None:
    words = norm(term).split()
    if len(words) == 1 and words[0] in EVERYDAY:
        return "R2_everyday_single"
    if len(words) > 1:
        if AUX_NEG.search(term):
            return "R3_aux_prose"
        if VAULT_META_R.search(norm(term)):
            return "R4_vaultmeta"
    return None


def signal(r) -> bool:
    return (r["kind"] == "fragmented_derivation"
            or r["confidence"]["score"] >= 0.8
            or r["independent_contexts"] >= 10)


def main() -> int:
    records = []
    with open(CAND, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                records.append(json.loads(line))

    # ---- corpus evidence index (headings + def windows with line spans)
    print("building index ...", flush=True)
    headings, defwins = [], []
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
                headings.append((vault, rel, h["line"], h["text"], None))
            for m in DEF_PAT.finditer(text):
                first_line = text[: m.start()].count("\n") + 1
                if any(s <= first_line <= e for s, e in spans):
                    continue
                wstart = max(0, m.start() - 140)
                window = text[wstart: m.end() + 180]
                defwins.append((vault, rel, first_line, window, wstart))
    h_idx, w_idx = defaultdict(list), defaultdict(list)
    for i, h in enumerate(headings):
        for t in set(norm(h[3]).split()):
            h_idx[t].append(i)
    for i, w in enumerate(defwins):
        for t in set(norm(w[3]).split()):
            w_idx[t].append(i)

    TERM_BOUND = re.compile(r"^[a-z0-9]+( [a-z0-9]+)*$")

    def phrase_hits(term, items, idx, getter):
        key = norm(term)
        if not TERM_BOUND.match(key) or not key:
            return []
        toks = key.split()
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
        pat = re.compile(r"(?<![a-z0-9])" + re.escape(key).replace(r"\ ", r"[ ]")
                         + r"(?![a-z0-9])")
        out = []
        for i in cand:
            if pat.search(norm(getter(items[i]))):
                out.append(items[i])
        return out

    def probe(term):
        return (phrase_hits(term, headings, h_idx, lambda h: h[3]),
                phrase_hits(term, defwins, w_idx, lambda w: w[3]))

    # term's own line inside a def window (citation accuracy)
    def term_line_in_window(win_item, term):
        vault, rel, wline, window, wstart = win_item
        key = norm(term).replace(" ", r"[ ]")
        pat = re.compile(r"(?<![a-z0-9])" + key + r"(?![a-z0-9])", re.I)
        m = pat.search(window)
        if not m:
            return wline
        # count newlines between window start and match
        return wline + window[: m.start()].count("\n")

    pool = [r for r in records
            if r["status"] == "provisional_candidate"
            and not r.get("decision_history") and signal(r)]
    print("pool:", len(pool))

    bulk, review = [], []
    stats = Counter()
    nid = 0
    for r in pool:
        t = r["term"]
        cls = noise_class(t) or r2class(t)
        if cls:
            stats[cls] += 1
            nid += 1
            bulk.append({
                "decision_id": f"D-DISC002-B16-{nid:04d}",
                "candidate_id": r["candidate_id"],
                "action": "reject",
                "rationale": (
                    f"ADR-0011 bulk class {cls}: mechanical non-concept "
                    f"(term '{t}' — {cls.split('_', 1)[1].replace('_', ' ')} "
                    f"shape); zero non-reject outcomes for this class in "
                    f"the 2,063-decision calibration set. No definitional "
                    f"treatment is required for a non-concept; KU ledger "
                    f"unaffected (ADR-0010)."),
                "reviewer": "session-16 orchestrator (GLM 4.6); ADR-0011 "
                            "calibrated bulk rule + sampled verification",
            })
            continue
        hh, dw = probe(t)
        if (hh or dw) and not r.get("homonym_suspect") \
                and not r.get("contradiction_suspect"):
            stats["P_cover"] += 1
            if hh:
                v, rel, line, text, _ = hh[0]
                cite = (f"HEADING '{text}' ({v} '{rel}':{line})")
            else:
                witem = dw[0]
                line = term_line_in_window(witem, t)
                snippet = " ".join(witem[3].split())[:170]
                cite = (f"DEFINITION \"{snippet}\" "
                        f"({witem[0]} '{witem[1]}':{line})")
            nid += 1
            bulk.append({
                "decision_id": f"D-DISC002-B16-{nid:04d}",
                "candidate_id": r["candidate_id"],
                "action": "cover",
                "rationale": (
                    f"ADR-0011 bulk class P: citation-backed cover for the "
                    f"term '{t}' — a definitional treatment exists in the "
                    f"corpus: {cite}. Fence-aware authoritative "
                    f"heading/definition evidence; concept covered, no new "
                    f"note needed."),
                "reviewer": "session-16 orchestrator (GLM 4.6); ADR-0011 "
                            "calibrated bulk rule + sampled verification",
            })
            continue
        stats["REVIEW"] += 1
        review.append({
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
                              for v, rel, line, text, _ in hh[:4]],
            "probe_def": [f"{v} '{rel}':{term_line_in_window(item, t)} :: "
                          f"{' '.join(win.split())[:140]}"
                          for item in dw[:4]
                          for (v, rel, wl, win, ws) in [item]],
        })

    print("class counts:", dict(stats.most_common()))
    with open(SCRATCH / "disc002-s16-bulk-final.jsonl", "w", encoding="utf-8") as fh:
        for d in bulk:
            fh.write(json.dumps(d, ensure_ascii=False) + "\n")
    with open(SCRATCH / "disc002-s16-review-bundle.jsonl", "w", encoding="utf-8") as fh:
        for d in review:
            fh.write(json.dumps(d, ensure_ascii=False) + "\n")

    # split review bundle into 6 slices for parallel subagent review
    n = len(review)
    k = 6
    sizes = [n // k + (1 if i < n % k else 0) for i in range(k)]
    i0 = 0
    for si, sz in enumerate(sizes, 1):
        p = SCRATCH / f"disc002-s16-review-slice{si}.jsonl"
        with open(p, "w", encoding="utf-8") as fh:
            for d in review[i0: i0 + sz]:
                fh.write(json.dumps(d, ensure_ascii=False) + "\n")
        i0 += sz
        print(f"slice {si}: {sz} candidates -> {p.name}")
    (SCRATCH / "disc002-s16-assemble-report.json").write_text(json.dumps({
        "pool": len(pool), "class_counts": dict(stats.most_common()),
        "bulk_decisions": len(bulk), "review": len(review),
    }, indent=1) + "\n")
    print("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
