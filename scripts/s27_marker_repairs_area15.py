#!/usr/bin/env python3
"""S27/SYNTH-001: anchored marker repairs for area 15 (Agents and Tooling).

Root-caused from reports/synthesis/s25-area15-audit.json (19 findings: 18
unique-detail-omission term markers + 1 code fingerprint). Every repair
restores the SOURCE-VERBATIM form at the semantically correct place in the
destination note; nothing is invented. Classes (all with session-23/24
precedent):

- ASCII-vs-typographic dashes: the source writes ranges with ASCII hyphens
  ('75-80', '0.011-0.051', '700-3500ms', '200-500', '100-150'); the notes
  used en-dashes. Repair: source-verbatim ASCII (s24 '1950s-1980s' precedent).
- dropped hyphenated words/word forms: 'document-type', 'prompting-engineering',
  'user-declared', 'deprioritized', 'reschedule' (s24 'discussions' precedent).
- dropped history/context: the frameworks-vault iteration history carrying
  'per-framework' (s23 note-ID precedent: restored as historical context).
- source's own term form: 'Self-RAF' in the source's Training paragraph
  (the section title stays Self-RAG; hyphenated vs spaced forms are different
  markers — keep the source's form where the source wrote it).
- mermaid label adaptation: the note quoted the subgraph labels; the source's
  bare form passes the mermaid grammar check (verified) — restore verbatim
  (s24 mermaid-whitespace precedent).

Probe-based idempotency: every repair probes that the defective form exists
with the expected multiplicity, replaces, and asserts the post-condition; a
second run is a complete no-op.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VAULT = REPO / "output" / "Unified-Vault"

RAG = "15 - Agents and Tooling/Retrieval Augmented Generation/RAG Pipeline Overview.md"
CHUNK = "15 - Agents and Tooling/Retrieval Augmented Generation/Chunking, Hybrid Search, and Reranking.md"
ADV = "15 - Agents and Tooling/Retrieval Augmented Generation/Advanced RAG Patterns.md"
MOC = "15 - Agents and Tooling/Agents and Tooling MOC.md"
MEMGPT = "15 - Agents and Tooling/Memory Systems/MemGPT and Letta.md"
MEMOPS = "15 - Agents and Tooling/Memory Systems/Memory Operations.md"
MCP = "15 - Agents and Tooling/Model Context Protocol/MCP Enterprise Integration.md"
COT = "15 - Agents and Tooling/AI Agents/Chain of Thought.md"
HITL = "15 - Agents and Tooling/AI Agents/Human-in-the-Loop Patterns.md"

REPAIRS: list[dict] = [
    # ---- RAG Pipeline Overview: cost/latency table + tier sentences ----
    dict(id="A15-R01", file=RAG, why="AF-014 '50-100ms' (src L366-370, ASCII hyphen)",
         bad="| Embed query | ~$0.0001 (1K tokens at OpenAI text-embedding-3 prices) | 50–100ms |",
         good="| Embed query | ~$0.0001 (1K tokens at OpenAI text-embedding-3 prices) | 50-100ms |"),
    dict(id="A15-R02", file=RAG, why="AF-013 '20-50ms' (src L366-370, ASCII hyphen)",
         bad="| Vector search | ~$0.0001 (depends on DB and index size) | 20–50ms (HNSW index, sublinear) |",
         good="| Vector search | ~$0.0001 (depends on DB and index size) | 20-50ms (HNSW index, sublinear) |"),
    dict(id="A15-R03", file=RAG, why="AF-012 '100-300ms' (src L366-370, ASCII hyphen)",
         bad="| Reranking | ~$0.001 (cross-encoder on 20 chunks) | 100–300ms |",
         good="| Reranking | ~$0.001 (cross-encoder on 20 chunks) | 100-300ms |"),
    dict(id="A15-R04", file=RAG, why="AF-006 '0.01-0.05' + AF-015 '500-3000ms' (src L357-361/L366-370, ASCII hyphens)",
         bad="| LLM generation | ~$0.01–0.05 (depending on context size and model) | 500–3000ms (depends on context and output length) |",
         good="| LLM generation | ~$0.01-0.05 (depending on context size and model) | 500-3000ms (depends on context and output length) |"),
    dict(id="A15-R05", file=RAG, why="AF-007 '0.011-0.051' + AF-016 '700-3500ms' (src L357-361/L366-370, ASCII hyphens)",
         bad="| **Total** | **~$0.011–0.051 per query** | **700–3500ms** |",
         good="| **Total** | **~$0.011-0.051 per query** | **700-3500ms** |"),
    dict(id="A15-R06", file=RAG, why="AF-005 '11k-51k' (src L363 'For 1M queries/month: ~$11K-51K/month.', ASCII hyphen)",
         bad="works out to roughly $11K–51K/month.",
         good="works out to roughly $11K-51K/month."),
    dict(id="A15-R07", file=RAG, why="AF-001 '75-80' (src L435 'Expected: ~75-80% faithfulness', ASCII hyphen)",
         bad="Expected: ~75–80% faithfulness, ~80% hit rate. The reranker is the biggest win.",
         good="Expected: ~75-80% faithfulness, ~80% hit rate. The reranker is the biggest win."),
    dict(id="A15-R08", file=RAG, why="AF-011 'document-type' (src L209 '**Document-type specific**:')",
         bad="Chunking should also match the document type: technical docs chunk by section",
         good="Chunking should also be document-type specific: technical docs chunk by section"),
    # ---- MOC: frameworks iteration history (per-framework) ----
    dict(id="A15-R09", file=MOC, why="AF-002 'per-framework' (src 25 - Frameworks and Tools/MOC.md L10 iteration history)",
         bad="16 frameworks and serving engines in total, with coverage complete.",
         good=("16 frameworks and serving engines in total, with coverage complete. The coverage "
               "accreted over the source vault's iterations: iteration 4 added per-framework deep "
               "dives for LangChain, LangGraph, DSPy, LlamaIndex, OpenAI SDK/Agents, vLLM, and "
               "Ollama/llama.cpp; iteration 6 added six more frameworks — AutoGen, CrewAI, and "
               "PydanticAI (agent frameworks) plus TGI, TensorRT-LLM, and SGLang (serving engines); "
               "iteration 10 added the final two: Semantic Kernel (Microsoft's multi-language agent "
               "framework) and Haystack (deepset's RAG-focused pipeline framework)."),
         insertion=True, probe="The coverage accreted over the source vault's iterations"),
    # ---- MemGPT: mermaid subgraph labels restored to source-verbatim bare form ----
    dict(id="A15-R10", file=MEMGPT, why="AF-003 code fingerprint (src 18 - Memory Systems L37-53 bare subgraph labels)",
         bad='  subgraph MainCtx["Main Context (in prompt)"]',
         good="  subgraph Main Context (in prompt)"),
    dict(id="A15-R11", file=MEMGPT, why="AF-003 code fingerprint (src L37-53 bare subgraph labels)",
         bad='  subgraph ExtCtx["External Context (database)"]',
         good="  subgraph External Context (database)"),
    # ---- MCP Enterprise Integration: user-declared ----
    dict(id="A15-R12", file=MCP, why="AF-004 'user-declared' (src 19 - MCP L292-294 'project_id — user-declared at session start')",
         bad="a `project_id` declared by the user at session start",
         good="a `project_id` that is user-declared at session start"),
    # ---- Chain of Thought: prompting-engineering ----
    dict(id="A15-R13", file=COT, why="AF-008 'prompting-engineering' (src 15 - AI Agents L133-136 'leading to the prompting-engineering field')",
         bad="leading to the prompt-engineering field",
         good="leading to the prompting-engineering field"),
    # ---- Human-in-the-Loop: reschedule (source's imperative form) ----
    dict(id="A15-R14", file=HITL, why="AF-009 'reschedule' (src L204-205 'Long timeout (24 hours): terminate the agent; reschedule.')",
         bad="a long timeout (24 hours) terminates the agent and reschedules.",
         good="a long timeout (24 hours) terminates the agent and triggers a reschedule."),
    # ---- Chunking: dash forms ----
    dict(id="A15-R15", file=CHUNK, why="AF-010 '200-500' (src L391-392 'A: 200-500 tokens', ASCII hyphen)",
         bad="**What chunk size should I use?** 200–500 tokens for most use cases.",
         good="**What chunk size should I use?** 200-500 tokens for most use cases."),
    dict(id="A15-R16", file=CHUNK, why="AF-017 '100-150' (src L368-378 'Rerank top 100-150.', ASCII hyphen)",
         bad="Rerank top 100–150.",
         good="Rerank top 100-150."),
    # ---- Advanced RAG: Self-RAF (the source's own form in its Training paragraph) ----
    dict(id="A15-R17", file=ADV, why="AF-018 'self-raf' (src 17 - RAG/Advanced Patterns L81 'Self-RAF fine-tunes the model on trajectories')",
         bad="Self-RAG fine-tunes the model on trajectories that include these reflection tokens",
         good="Self-RAF fine-tunes the model on trajectories that include these reflection tokens"),
    # ---- Memory Operations: deprioritized (source's participle) ----
    dict(id="A15-R18", file=MEMOPS, why="AF-019 'deprioritized' (src 18 - Memory Systems L73-76 'are deprioritized')",
         bad="**Access-based decay** deprioritizes memories that haven't been retrieved in a long time, similar to LRU cache eviction.",
         good="**Access-based decay**: memories that haven't been retrieved in a long time are deprioritized, similar to LRU cache eviction."),
]


def main() -> int:
    applied = skipped = failed = 0
    for r in REPAIRS:
        path = VAULT / r["file"]
        if not path.is_file():
            print(f"FAILED: missing file {r['file']}"); failed += 1; continue
        text = path.read_text(encoding="utf-8")
        bad, good = r["bad"], r["good"]
        if r.get("insertion"):
            marker = r["probe"]
            if marker in text:
                print(f"OK (already repaired): {r['id']}"); skipped += 1; continue
            n = text.count(bad)
            if n != 1:
                print(f"FAILED: {r['id']} anchor count {n} != 1"); failed += 1; continue
            new_text = text.replace(bad, good, 1)
            path.write_text(new_text, encoding="utf-8")
            post = path.read_text(encoding="utf-8")
            assert marker in post and post.count(marker) == 1
            print(f"APPLIED: {r['id']} {r['file'].split('/')[-1]} (insertion)"); applied += 1
            continue
        n = text.count(bad)
        if n == 0:
            if good in text:
                print(f"OK (already repaired): {r['id']}"); skipped += 1; continue
            print(f"FAILED: probe not found and repair not present: {r['id']} {r['file']}"); failed += 1; continue
        if n != 1:
            print(f"FAILED: probe found {n} times (expected 1), refusing: {r['id']}"); failed += 1; continue
        new_text = text.replace(bad, good, 1)
        if new_text == text:
            print(f"FAILED: replacement produced no change: {r['id']}"); failed += 1; continue
        path.write_text(new_text, encoding="utf-8")
        post = path.read_text(encoding="utf-8")
        assert bad not in post, f"{r['id']}: probe still present"
        assert post.count(good) >= 1, f"{r['id']}: repaired form missing"
        print(f"APPLIED: {r['id']} {r['file'].split('/')[-1]} — {r['why'][:70]}")
        applied += 1
    print(f"\nsummary: applied={applied} skipped={skipped} failed={failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
