#!/usr/bin/env python3
"""S27/SYNTH-001: anchored marker repairs for area 19 (Reference and Practice).

Root-caused from reports/synthesis/s25-area19-audit.json (18 findings: 6 term
markers + 10 math spans + 2 code fingerprints). Classes:

- bare-fence equations -> $$ LaTeX (Coding Interview Questions: the attention
  formula and the RoPE rotation pair): restored as ```text fences carrying
  the SOURCE-VERBATIM content (s24 bare-fence precedent).
- math-span pairing: the audit's inline-math spans pair $-signs PER LINE; the
  source's sentences put the routing economics on their own line so the
  '$0.30 ... $0.10' span forms. The note merged the sentences onto one line
  with an odd $-count, dissolving the span. Repair: restore the source's
  sentence/line structure (s24 math-span-granularity precedent).
- punctuation-joins inside math spans: the note rewrote '(Llama-3.1-8B, ~5s,
  $0.001). Hard queries ... (~60-300s,' as 'model: Llama-3.1-8B, ~5s,
  $0.001. Hard ... model: ~60–300s,' — the span text changed. Repair:
  source-verbatim punctuation (s24 dropped-word precedent).
- ASCII-vs-typographic dashes inside dollar spans: '0.01-0.02', '5-30s',
  '300K-', '1M-', '500K-', '3M-', '10-50K', '500-1000' (s24 dash precedent).
- underscore token: 'avg_50_pages' (the source's arithmetic token) vs the
  note's 'avg 50 pages'.

Probe-based idempotency; a second run is a complete no-op.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VAULT = REPO / "output" / "Unified-Vault"

CODING = "19 - Reference and Practice/Interview Prep/Coding Interview Questions.md"
SYSDES = "19 - Reference and Practice/Interview Prep/System Design Interview Questions.md"
CONCEPT = "19 - Reference and Practice/Interview Prep/Conceptual Interview Questions.md"

REPAIRS: list[dict] = [
    # ---- Coding Interview Questions: two bare-fence equations ----
    dict(id="A19-R01", file=CODING, why="AF-001 code (src 29 - Interview Prep/Coding/03 L41-43)",
         bad="$$\\mathrm{Attention}(Q, K, V) = \\mathrm{softmax}(Q K^T / \\sqrt{d_k}) V$$",
         good="```text\nAttention(Q, K, V) = softmax(Q K^T / sqrt(d_k)) V\n```"),
    dict(id="A19-R02", file=CODING, why="AF-015 'q_2i' + AF-016 code (src L336-339: ONE two-line aligned fence)",
         bad=("$$q'_{2i} = q_{2i} \\cos(m \\theta_i) - q_{2i+1} \\sin(m \\theta_i)$$\n\n"
              "$$q'_{2i+1} = q_{2i} \\sin(m \\theta_i) + q_{2i+1} \\cos(m \\theta_i)$$"),
         good=("```text\nq'_2i   = q_2i * cos(m * θ_i) - q_2i+1 * sin(m * θ_i)\n"
               "q'_2i+1 = q_2i * sin(m * θ_i) + q_2i+1 * cos(m * θ_i)\n```")),
    # ---- System Design: query-routing paragraph (line structure + punctuation) ----
    dict(id="A19-R03", file=SYSDES,
         why="AF-006 span '0.001). Hard queries...(~60-300s,' + AF-005 span '0.30 average...cost to' (src L68/L70: two lines, source punctuation)",
         bad=("**Query routing**: classify queries by difficulty. Easy queries (factual lookups, simple Q&A) "
              "go to a fast, cheap model: Llama-3.1-8B, ~5s, $0.001. Hard queries (math, code, multi-step "
              "reasoning) go to the reasoning model: ~60–300s, $0.10–$0.60. Routing runs via a small "
              "classifier or the 8B model itself with a \"can you answer this in 5 seconds?\" prompt. "
              "This is critical: sending every query to the reasoning model would cost $0.30 average "
              "(10× the budget). Routing 70% to the fast model and 30% to the reasoning model brings "
              "average cost to $0.10."),
         good=("**Query routing**: classify queries by difficulty. Easy queries (factual lookups, simple Q&A) "
               "go to a fast, cheap model (Llama-3.1-8B, ~5s, $0.001). Hard queries (math, code, multi-step "
               "reasoning) go to the reasoning model (~60-300s, $0.10-$0.60). Routing runs via a small "
               "classifier or the 8B model itself with a \"can you answer this in 5 seconds?\" prompt.\n\n"
               "This is critical: sending every query to the reasoning model would cost $0.30 average "
               "(10× the budget). Routing 70% to the fast model and 30% to the reasoning model brings "
               "average cost to $0.10.")),
    # ---- System Design: modality routing paragraph ----
    dict(id="A19-R04", file=SYSDES,
         why="AF-009 '5-30s' + AF-010 span '0.001/page, 1s). Complex...(~' (src L151, source punctuation + ASCII hyphen)",
         bad=("Simple documents (receipts, IDs, single-field forms) go to OCR + regex extraction "
              "(~$0.001/page, 1s); complex documents (contracts, multi-column tables, handwritten notes) "
              "go to the VLM (~$0.05/page, 5–30s)."),
         good=("Simple documents (receipts, IDs, single-field forms) go to OCR + regex extraction "
               "(~$0.001/page, 1s). Complex documents (contracts, multi-column tables, handwritten notes) "
               "go to the VLM (~$0.05/page, 5-30s).")),
    dict(id="A19-R05", file=SYSDES,
         why="AF-011 'avg_50_pages' + AF-012 span '0.05 × 20K × avg_50_pages =' (src L153: the source's arithmetic token)",
         bad="sending every document to the VLM would cost $0.05 × 20K × avg 50 pages = $50K/day.",
         good="sending every document to the VLM would cost $0.05 × 20K × avg_50_pages = $50K/day."),
    dict(id="A19-R06", file=SYSDES,
         why="AF-003 '0.01-0.02' + AF-004 span '0.01-0.02/page at scale vs.' (src L155, ASCII hyphen)",
         bad="This also gives better cost control ($0.01–0.02/page at scale vs. $0.05 for GPT-4V).",
         good="This also gives better cost control ($0.01-0.02/page at scale vs. $0.05 for GPT-4V)."),
    # ---- System Design: capacity tiers (dollar spans) ----
    dict(id="A19-R07", file=SYSDES, why="AF-008 span '500K-' (src L97-100 users tier, ASCII hyphen)",
         bad="- **100K users/day**: dedicated GPU cluster (32+ GPUs), model distillation (train a smaller model to mimic the reasoning model's outputs on common query types). $500K–$1M/month.",
         good="- **100K users/day**: dedicated GPU cluster (32+ GPUs), model distillation (train a smaller model to mimic the reasoning model's outputs on common query types). $500K-$1M/month."),
    dict(id="A19-R08", file=SYSDES, why="AF-007 span '500K-' (src L427-430 tasks tier, ASCII hyphen)",
         bad="- **50K tasks/day**: requires significant infrastructure, model distillation, and specialized agents. $500K–$1M/month.",
         good="- **50K tasks/day**: requires significant infrastructure, model distillation, and specialized agents. $500K-$1M/month."),
    dict(id="A19-R09", file=SYSDES, why="AF-013/AF-014 spans '300K-'/'1M-' (src L183-186 documents tier, ASCII hyphens)",
         bad="fine-tune LLaVA on your specific document types for better accuracy and lower cost). $300K–$500K/month.",
         good="fine-tune LLaVA on your specific document types for better accuracy and lower cost). $300K-$500K/month."),
    dict(id="A19-R10", file=SYSDES, why="AF-013/AF-014 spans (src L183-186: the 1M-documents tier)",
         bad="or specialized models (e.g., LayoutLM for forms). $1M–$3M/month.",
         good="or specialized models (e.g., LayoutLM for forms). $1M-$3M/month."),
    dict(id="A19-R11", file=SYSDES, why="AF-002 span '3M-' (src L309-312 agents tier, ASCII hyphen)",
         bad="- **50K agents, 1M runs/day**: requires significant infrastructure (100+ GPUs), custom tool gateway, advanced caching. $3M–$5M/month.",
         good="- **50K agents, 1M runs/day**: requires significant infrastructure (100+ GPUs), custom tool gateway, advanced caching. $3M-$5M/month."),
    # ---- Conceptual Interview Questions: dash forms ----
    dict(id="A19-R12", file=CONCEPT, why="AF-017 '10-50k' (src 29 - Interview Prep/Conceptual/01 L154 '10-50K thinking tokens', ASCII hyphen)",
         bad="Because they generate 10–50K thinking tokens per query.",
         good="Because they generate 10-50K thinking tokens per query."),
    dict(id="A19-R13", file=CONCEPT, why="AF-018 '500-1000' (src L154 'Standard LLMs generate 500-1000 output tokens', ASCII hyphen)",
         bad="Standard LLMs generate 500–1000 output tokens.",
         good="Standard LLMs generate 500-1000 output tokens."),
]


def main() -> int:
    applied = skipped = failed = 0
    for r in REPAIRS:
        path = VAULT / r["file"]
        if not path.is_file():
            print(f"FAILED: missing file {r['file']}"); failed += 1; continue
        text = path.read_text(encoding="utf-8")
        bad, good = r["bad"], r["good"]
        n = text.count(bad)
        if n == 0:
            if good in text:
                print(f"OK (already repaired): {r['id']}"); skipped += 1; continue
            print(f"FAILED: probe not found and repair not present: {r['id']} {r['file']}"); failed += 1; continue
        if n != 1:
            print(f"FAILED: probe found {n} times (expected 1), refusing: {r['id']}"); failed += 1; continue
        new_text = text.replace(bad, good, 1)
        if new_text == text:
            print(f"FAILED: no change: {r['id']}"); failed += 1; continue
        path.write_text(new_text, encoding="utf-8")
        post = path.read_text(encoding="utf-8")
        assert bad not in post, f"{r['id']}: probe still present"
        assert post.count(good) >= 1, f"{r['id']}: repaired form missing"
        print(f"APPLIED: {r['id']} {r['file'].split('/')[-1]} — {r['why'][:64]}")
        applied += 1
    print(f"\nsummary: applied={applied} skipped={skipped} failed={failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
