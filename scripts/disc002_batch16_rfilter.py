#!/usr/bin/env python3
"""DISC-002 session 16: extended residual filtering (ADR-0011 R-classes).

Second deterministic layer for the 3,549-candidate residual, using curated
linguistic lexica (orchestrator knowledge, validated against the 2,063
calibration decisions — zero non-reject counter-examples required):

  R1  single verb-form word (3rd-person/-ing/-ed) not a corpus-heading
      token                                     -> prose/verb fragment
  R2  single everyday-English word (curated)    -> non-concept
  R3  multiword containing aux/modal/negation or ending in a verb form
      or everyday word                          -> prose fragment
  R4  vault-meta / datelike / file-list shapes  -> meta noise

Whatever survives is concept-shaped and goes to individual review
(orchestrator + subagent tiers per ADR-0011 §4).
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

# --- curated everyday-English lexicon (technical-prose noise) ---
EVERYDAY = {
    # function words
    "whether", "when", "where", "while", "because", "although", "though",
    "since", "until", "unless", "whereas", "however", "therefore", "thus",
    "hence", "moreover", "furthermore", "meanwhile", "instead", "rather",
    "although", "besides", "anyway", "somehow", "anywhere", "everywhere",
    "nothing", "something", "anything", "everything", "someone", "anyone",
    "everyone", "nobody", "somebody", "anybody", "everybody", "one",
    "ones", "thing", "things", "way", "ways", "part", "parts", "place",
    "places", "case", "cases", "point", "points", "side", "sides",
    "end", "ends", "start", "starts", "beginning", "middle", "top",
    "bottom", "front", "back", "left", "right", "inside", "outside",
    # everyday nouns that appear in ML prose
    "car", "cars", "dog", "dogs", "cat", "cats", "house", "houses",
    "person", "people", "human", "humans", "world", "life", "day", "days",
    "week", "weeks", "month", "months", "year", "years", "time", "times",
    "hour", "hours", "minute", "minutes", "second", "seconds", "money",
    "price", "prices", "cost", "costs", "purpose", "purposes", "reason",
    "reasons", "result", "results", "effect", "effects", "example",
    "examples", "idea", "ideas", "topic", "topics", "subject", "subjects",
    "question", "questions", "answer", "answers", "problem", "problems",
    "solution", "solutions", "trick", "tricks", "job", "jobs", "work",
    "works", "task", "tasks", "role", "roles", "team", "teams", "tool",
    "tools", "book", "books", "page", "pages", "word", "words", "letter",
    "letters", "name", "names", "number", "numbers", "amount", "amounts",
    "piece", "pieces", "bit", "bits", "kind", "kinds", "type", "types",
    "sort", "sorts", "form", "forms", "version", "versions", "edition",
    "guide", "guides", "list", "lists", "table", "tables", "row", "rows",
    "column", "columns", "cell", "cells", "box", "boxes", "line", "lines",
    "note", "notes", "draft", "drafts", "source", "sources", "thought",
    "thoughts", "opinion", "opinions", "fact", "facts", "detail",
    "details", "summary", "summaries", "review", "reviews", "chapter",
    "chapters", "section", "sections", "appendix", "index", "introduction",
    "conclusion", "conclusions", "overview", "background", "history",
    "future", "past", "present", "moment", "today", "tomorrow",
    "yesterday", "decade", "decades", "century", "millennium",
    # common verbs (base forms seen in prose)
    "use", "used", "uses", "using", "make", "makes", "made", "making",
    "get", "gets", "got", "getting", "take", "takes", "took", "taking",
    "give", "gives", "gave", "giving", "see", "sees", "saw", "seen",
    "look", "looks", "looked", "looking", "find", "finds", "found",
    "finding", "think", "thinks", "thought", "thinking", "know", "knows",
    "knew", "known", "knowing", "want", "wants", "wanted", "wanting",
    "need", "needs", "needed", "needing", "mean", "means", "meant",
    "meaning", "call", "calls", "called", "calling", "become", "becomes",
    "became", "becoming", "seem", "seems", "seemed", "seeming", "show",
    "shows", "showed", "shown", "showing", "appear", "appears",
    "appeared", "appearing", "feel", "feels", "felt", "keep", "keeps",
    "kept", "keeping", "let", "lets", "letting", "put", "puts", "putting",
    "try", "tries", "tried", "trying", "ask", "asks", "asked", "asking",
    "work", "worked", "working", "play", "plays", "played", "playing",
    "run", "runs", "ran", "running", "walk", "walks", "walked", "walking",
    "read", "reads", "reading", "write", "writes", "wrote", "written",
    "writing", "speak", "speaks", "spoke", "spoken", "speaking", "tell",
    "tells", "told", "telling", "say", "says", "said", "saying", "come",
    "comes", "came", "coming", "go", "goes", "went", "gone", "going",
    "learn", "learns", "learned", "learning", "teach", "teaches",
    "taught", "teaching", "help", "helps", "helped", "helping", "allow",
    "allows", "allowed", "allowing", "enable", "enables", "enabled",
    "enabling", "support", "supports", "supported", "supporting",
    "provide", "provides", "provided", "providing", "offer", "offers",
    "offered", "offering", "include", "includes", "included",
    "including", "contain", "contains", "contained", "containing",
    "create", "creates", "created", "creating", "build", "builds",
    "built", "building", "produce", "produces", "produced", "producing",
    "generate", "generates", "generated", "generating", "cause",
    "causes", "caused", "causing", "lead", "leads", "led", "leading",
    "bring", "brings", "brought", "bringing", "send", "sends", "sent",
    "sending", "receive", "receives", "received", "receiving",
    "mention", "mentions", "mentioned", "mentioning", "describe",
    "describes", "described", "describing", "explain", "explains",
    "explained", "explaining", "discuss", "discusses", "discussed",
    "discussing", "consider", "considers", "considered", "considering",
    "compare", "compares", "compared", "comparing", "share", "shares",
    "shared", "sharing", "change", "changes", "changed", "changing",
    "turn", "turns", "turned", "turning", "grow", "grows", "grew",
    "grown", "growing", "increase", "increases", "increased",
    "increasing", "decrease", "decreases", "decreased", "decreasing",
    "reduce", "reduces", "reduced", "reducing", "improve", "improves",
    "improved", "improving", "add", "adds", "added", "adding", "remove",
    "removes", "removed", "removing", "apply", "applies", "applied",
    "applying", "choose", "chooses", "chose", "chosen", "choosing",
    "select", "selects", "selected", "selecting", "prefer", "prefers",
    "preferred", "preferring", "start", "started", "starting", "stop",
    "stops", "stopped", "stopping", "finish", "finishes", "finished",
    "complete", "completes", "completed", "completing", "achieve",
    "achieves", "achieved", "achieving", "reach", "reaches", "reached",
    "reaching", "arrive", "arrives", "arrived", "arriving", "enter",
    "enters", "entered", "entering", "leave", "leaves", "left", "leaving",
    "return", "returns", "returned", "returning", "give", "deal",
    "deals", "dealt", "dealing", "handle", "handles", "handled",
    "handling", "treat", "treats", "treated", "treating", "process",
    "processes", "processed", "processing", "train", "trains", "trained",
    "training", "test", "tests", "tested", "testing", "check", "checks",
    "checked", "checking", "verify", "verifies", "verified", "verifying",
    "validate", "validates", "validated", "validating", "measure",
    "measures", "measured", "measuring", "compute", "computes",
    "computed", "computing", "calculate", "calculates", "calculated",
    "calculating", "count", "counts", "counted", "counting", "estimate",
    "estimates", "estimated", "estimating", "predict", "predicts",
    "predicted", "predicting", "decide", "decides", "decided",
    "deciding", "determine", "determines", "determined", "determining",
    "depend", "depends", "depended", "depending", "require", "requires",
    "required", "requiring", "involve", "involves", "involved",
    "involving", "exist", "exists", "existed", "existing", "happen",
    "happens", "happened", "happening", "occur", "occurs", "occurred",
    "occurring", "perform", "performs", "performed", "performing",
    # common adjectives/adverbs in prose
    "good", "bad", "big", "small", "large", "little", "long", "short",
    "high", "low", "fast", "slow", "cheap", "expensive", "easy", "hard",
    "difficult", "simple", "complex", "complicated", "clear", "unclear",
    "important", "unimportant", "possible", "impossible", "likely",
    "unlikely", "common", "rare", "normal", "strange", "new", "old",
    "young", "early", "late", "recent", "modern", "ancient", "classic",
    "standard", "typical", "special", "specific", "general", "particular",
    "certain", "uncertain", "sure", "ready", "available", "useful",
    "useless", "helpful", "practical", "theoretical", "technical",
    "basic", "advanced", "intermediate", "beginner", "expert",
    "successful", "failed", "failing", "correct", "incorrect", "right",
    "wrong", "true", "false", "real", "fake", "actual", "current",
    "present", "similar", "different", "same", "other", "another",
    "extra", "additional", "more", "less", "fewer", "most", "least",
    "many", "much", "few", "several", "some", "any", "all", "both",
    "each", "every", "either", "neither", "whole", "partial", "full",
    "empty", "open", "closed", "free", "busy", "rich", "poor", "strong",
    "weak", "heavy", "light", "dark", "bright", "quiet", "loud", "soft",
    "hard", "smooth", "rough", "sharp", "dull", "thin", "thick", "wide",
    "narrow", "deep", "shallow", "near", "far", "close", "distant",
    "inner", "outer", "internal", "external", "upper", "lower", "final",
    "initial", "original", "main", "major", "minor", "key", "primary",
    "secondary", "direct", "indirect", "explicit", "implicit",
    "mentioned", "deployed", "consolidated", "reported", "applicable",
    "democratized", "virtually", "mentioned", "many", "times", "slightly",
    "moderately", "extremely", "fairly", "pretty", "somewhat", "slightly",
    "tremendously", "enormously", "vastly", "widely", "narrowly",
}

AUX_NEG = re.compile(
    r"\b(doesn'?t|don'?t|didn'?t|isn'?t|aren'?t|wasn'?t|weren'?t|won'?t|"
    r"wouldn'?t|shouldn'?t|couldn'?t|can'?t|cannot|must|might|may|"
    r"should|would|could|shall)\b", re.I)

VAULT_META_R = re.compile(
    r"^(per note|notes? \d{4}|thoughts? \d{4}|new files?|file \d+|"
    r"note \d+|vault|scratch|repo|handoff|checkpoint|session|\"?moc\"?)$",
    re.I)
# (tightened 2026-11-01: the earlier greedy variant matched 'class index'
# — a confirmed COVER — via the token 'index'; calibration caught it)

VERB_SUFFIX = re.compile(r"(?:ies|es|s|ed|ing)$")


def norm(s: str) -> str:
    return " ".join(s.lower().replace("-", " ").replace("_", " ").split())


def load_heading_tokens() -> set:
    toks = set()
    for root in VAULTS.values():
        for md in sorted(root.rglob("*.md")):
            try:
                text = md.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            struct = extract_structure_text(text)
            for h in struct.get("headings", []):
                for t in norm(h["text"]).split():
                    toks.add(t)
    return toks


def main() -> int:
    heading_toks = load_heading_tokens()

    residual = [json.loads(l) for l in
                open(SCRATCH / "disc002-s16-residual-bundle.jsonl",
                     encoding="utf-8") if l.strip()]

    # calibration set (same join as bulkdecide)
    records = {}
    with open(CAND, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line)
                records[r["candidate_id"]] = r
    dec_files = ["002a-disc002-decisions-r1.jsonl",
                 "002b-disc002-decisions-r2.jsonl"] + [
        f"002-disc002-decisions-batch{i}.jsonl" for i in range(2, 16)]
    decisions = {}
    for f in dec_files:
        for line in open(REPO / "state/concept-candidates" / f, encoding="utf-8"):
            if line.strip():
                d = json.loads(line)
                decisions[d["candidate_id"]] = d["action"]

    def rclass(term: str) -> str | None:
        words = norm(term).split()
        if not words:
            return None
        if len(words) == 1:
            w = words[0]
            if w in EVERYDAY:
                return "R2_everyday_single"
            return None
        # multiword
        if AUX_NEG.search(term):
            return "R3_aux_prose"
        if VAULT_META_R.search(norm(term)):
            return "R4_vaultmeta"
        # NOTE: 'ends in everyday word' and 'ends in verb form' are NOT
        # applied as bulk classes: calibration showed 20 covers among
        # ends-everyday terms (e.g. 'masked language') — unsafe. Those
        # stay for individual review.
        return None

    # calibrate
    calib_out = defaultdict(Counter)
    for cid, act in decisions.items():
        r = records.get(cid)
        if not r:
            continue
        c = rclass(r["term"])
        if c:
            calib_out[c][act] += 1
    print("=== CALIBRATION (R-classes; counter-examples must be 0) ===")
    ok = True
    for k in sorted(calib_out, key=lambda k: -sum(calib_out[k].values())):
        c = calib_out[k]
        bad = c.get("cover", 0) + c.get("confirm_gap", 0) + \
            c.get("merge", 0) + c.get("defer", 0) + c.get("revise", 0)
        if bad:
            ok = False
        print(f"{k:24s} n={sum(c.values()):5d} {dict(c)}  {'** BAD **' if bad else ''}")
    if not ok:
        print("\nCounter-examples found — refusing to apply; adjust lexica.")
        return 1

    # apply to residual
    out = Counter()
    kept = []
    for x in residual:
        c = rclass(x["term"])
        if c:
            out[c] += 1
        else:
            out["KEEP_review"] += 1
            kept.append(x)
    print("\nresidual classification:", dict(out.most_common()))
    print("kept for individual review:", len(kept))

    with open(SCRATCH / "disc002-s16-residual2-review.jsonl", "w",
              encoding="utf-8") as fh:
        for x in kept:
            fh.write(json.dumps(x, ensure_ascii=False) + "\n")
    (SCRATCH / "disc002-s16-rclass-report.json").write_text(json.dumps({
        "calibration": {k: dict(v) for k, v in calib_out.items()},
        "residual_counts": dict(out.most_common()),
        "kept": len(kept),
    }, indent=1) + "\n")
    print("saved residual2-review + rclass-report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
