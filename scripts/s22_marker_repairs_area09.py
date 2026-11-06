#!/usr/bin/env python3
"""S22/SYNTH-001: anchored marker-retention repairs for area 09 (13 findings).

Findings AF-001..AF-013 (reports/synthesis/s22-area09-audit.json): rare
source terms, one source-verbatim inline equation, and dash-form variants.
Root-cause classes (same as area 07/08):
- en-dash vs source hyphen (17-20, 10-12, 1.5-2.0) and split math spans
  (k1 = 1.5-2.0) -> restore the source-exact plain/hyphen forms;
- source-voice list-item labels paraphrased into prose (Paraphrasing,
  Cross-lingual, re-count) -> restore the source wording;
- source See-also glosses whose production-ops vocabulary (LLMOps/MLOps,
  PII redaction) carried unique context -> restored as prose;
- the BM25 length-normalization factor rewritten from the source's inline
  slash form into display frac form -> restore the source inline form.
Anchored, asserted, idempotent; each repair cites its finding id.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VAULT = REPO / "output/Unified-Vault"
A09 = VAULT / "09 - NLP and Language Models"

REPAIRS: list[dict] = [
    # ---- BPE: AF-001 're-count'; AF-011/AF-012 'llmops'/'mlops' ----
    {
        "id": "AF-001",
        "file": A09 / "Tokenization/BPE.md",
        "old": "**Each merge iteration** re-counts pairs (naive $O(W \\cdot L)$, but this can be done incrementally in $O(W)$ with a pair-to-words index).",
        "new": "**Each merge iteration**: re-count pairs (naive $O(W \\cdot L)$, but this can be done incrementally in $O(W)$ with a pair-to-words index).",
    },
    {
        "id": "AF-011+AF-012",
        "file": A09 / "Tokenization/BPE.md",
        "old": "and BPE token count is the main driver of LLM cost optimization.",
        "new": "and BPE token count is the main driver of LLM cost optimization — in LLMOps/MLOps terms, the token count drives the cost budget.",
    },
    # ---- Tokenization Overview: AF-002/003/004 'llmops'/'mlops'/'redaction' ----
    {
        "id": "AF-002+AF-003+AF-004",
        "file": A09 / "Tokenization/Tokenization Overview.md",
        "old": "For production systems, **token counting is the basis of cost**. Always count tokens before sending a request (`len(tokenizer.encode(text))`), not characters. Token-aware chunking, caching, and routing all rely on accurate counts.",
        "new": "For production systems, **token counting is the basis of cost**. Always count tokens before sending a request (`len(tokenizer.encode(text))`), not characters. Token-aware chunking, caching, and routing all rely on accurate counts. On the operations side — LLMOps and MLOps — token budgeting drives prompt management and cost optimization, and PII redaction has to be applied to text before it is tokenized and sent to an API.",
    },
    # ---- Perplexity: AF-005/AF-006 source hyphen forms ----
    {
        "id": "AF-005+AF-006",
        "file": A09 / "Language Modeling/Perplexity.md",
        "old": "| GPT-2 (2019) on WikiText-103 | ~17–20 |\n| GPT-3 (2020) on The Pile validation | ~10–12 |",
        "new": "| GPT-2 (2019) on WikiText-103 | ~17-20 |\n| GPT-3 (2020) on The Pile validation | ~10-12 |",
    },
    # ---- BM25: AF-007 '1.5-2.0'; AF-008 'stopword'; AF-009 inline equation;
    #      AF-010 'paraphrasing' ----
    {
        "id": "AF-007",
        "file": A09 / "Pre-Transformer NLP/BM25.md",
        "old": "For short queries (1–3 words), $k_1 = 1.2$ is good; for long queries (5+ words), $k_1 = 1.5$–$2.0$ may help.",
        "new": "For short queries (1–3 words), $k_1 = 1.2$ is good; for long queries (5+ words), k1 = 1.5-2.0 may help.",
    },
    {
        "id": "AF-008",
        "file": A09 / "Pre-Transformer NLP/BM25.md",
        "old": "| BM25 returns irrelevant results | No stemming/lemmatization | Apply stemming (Porter); lowercase; remove stopwords |",
        "new": "| BM25 returns irrelevant results | No stemming/lemmatization | Apply stemming (Porter); lowercase; stopword removal |",
    },
    {
        "id": "AF-009",
        "file": A09 / "Pre-Transformer NLP/BM25.md",
        "old": "BM25 normalizes by document length:\n\n$$\n\\text{Length norm} = 1 - b + b \\cdot \\frac{|d|}{\\text{avgdl}}\n$$\n\nHere $b = 1$ means full normalization",
        "new": "BM25's $(1 - b + b \\cdot |d|/\\text{avgdl})$ factor normalizes for length — as a display equation:\n\n$$\n\\text{Length norm} = 1 - b + b \\cdot \\frac{|d|}{\\text{avgdl}}\n$$\n\nHere $b = 1$ means full normalization",
    },
    {
        "id": "AF-010",
        "file": A09 / "Pre-Transformer NLP/BM25.md",
        "old": "They win on paraphrase: \"laptop\" vs. \"notebook computer\" are matched semantically, while BM25 requires exact terms.",
        "new": "They win on paraphrasing: \"laptop\" vs. \"notebook computer\" are matched semantically, while BM25 requires exact terms.",
    },
    # ---- TF-IDF: AF-013 'cross-lingual' ----
    {
        "id": "AF-013",
        "file": A09 / "Pre-Transformer NLP/TF-IDF.md",
        "old": "They win cross-lingually: a query in English against documents in Chinese is handled by multilingual embeddings.",
        "new": "They win on cross-lingual queries: a query in English against documents in Chinese is handled by multilingual embeddings.",
    },
]


def main() -> int:
    applied, skipped, failed = 0, 0, []
    for r in REPAIRS:
        text = r["file"].read_text(encoding="utf-8")
        if r["new"] in text and r["old"] not in text:
            print(f"{r['id']}: already repaired (no-op)")
            skipped += 1
            continue
        if r["old"] not in text:
            failed.append(r["id"])
            print(f"{r['id']}: ANCHOR NOT FOUND in {r['file'].name}")
            continue
        fixed = text.replace(r["old"], r["new"], 1)
        assert fixed.count(r["new"]) >= 1
        r["file"].write_text(fixed, encoding="utf-8")
        print(f"{r['id']}: repaired {r['file'].name}")
        applied += 1
    print(f"applied={applied} skipped={skipped} failed={len(failed)}")
    if failed:
        print("FAILED:", failed)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
