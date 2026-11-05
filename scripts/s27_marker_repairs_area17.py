#!/usr/bin/env python3
"""S27/SYNTH-001: anchored marker repairs for area 17 (Papers).

Root-caused from reports/synthesis/s25-area17-audit.json (40 findings: 12
term markers + 28 code fingerprints). Classes:

- bare-fence equations -> $$ LaTeX: the notes converted the sources' unicode
  pseudocode fences (DPO, Bahdanau, Luong, GPT-1, Vaswani, InstructGPT) into
  display math. Restored as ```text fences carrying the SOURCE-VERBATIM
  content (s24 '19 bare-fence equations' precedent). Multi-equation source
  fences are restored as ONE fence (s24 'L(p)/log L(p) one fence' precedent).
- mermaid quoted subgraph labels: the notes quoted labels like
  subgraph "Standard Attention O(N^2)"; the sources' bare form passes the
  mermaid grammar check (verified on fixtures) — restored verbatim
  (s24 mermaid-whitespace precedent).
- chapter-NN references dropped in See-also paraphrase: restored
  (s23 note-ID / s24 filename-series precedent: source numbering is
  historical context).
- the source's own typo'd link path '2024-2024' (H3's See-also) kept as
  inline-code historical context, sic.
- the source's own hyphenation 'communityfine-tunes' (LoRA) carried
  alongside the readable form (keep-both).
- the source's self-reference '(cross-link)' (RAG 2020) restored.

The term markers '_sft' (pi_SFT) and 'head_1/head_h/head_i' are satisfied by
the corresponding fence restorations (tokens live inside the fences).

Probe-based idempotency; entries with expected_count>1 replace every
occurrence after asserting the count. A second run is a complete no-op.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VAULT = REPO / "output" / "Unified-Vault"

DPO = "17 - Papers/Alignment and RLHF/DPO.md"
INSTR = "17 - Papers/Alignment and RLHF/InstructGPT.md"
BAHDAU = "17 - Papers/Attention and Transformers/Bahdanau Attention.md"
LUONG = "17 - Papers/Attention and Transformers/Luong Attention.md"
VASWANI = "17 - Papers/Attention and Transformers/Attention Is All You Need.md"
GPT1 = "17 - Papers/Attention and Transformers/GPT-1.md"
LINF = "17 - Papers/Efficiency/Linformer.md"
PERF = "17 - Papers/Efficiency/Performer.md"
LONGF = "17 - Papers/Efficiency/Longformer.md"
GQA = "17 - Papers/Efficiency/GQA.md"
H3 = "17 - Papers/State Space Models and Linear Attention/H3.md"
JAMBA = "17 - Papers/State Space Models and Linear Attention/Jamba.md"
MINIMAX = "17 - Papers/State Space Models and Linear Attention/MiniMax-01.md"
SCALING = "17 - Papers/Scaling and Training/Scaling Laws (Kaplan and Chinchilla).md"
LORA = "17 - Papers/Scaling and Training/LoRA.md"
GOT = "17 - Papers/Reasoning/Graph of Thoughts.md"
RAGP = "17 - Papers/Agents and RAG/RAG.md"

REPAIRS: list[dict] = [
    # ---- DPO: five bare-fence equations ----
    dict(id="A17-R01", file=DPO, why="AF-023 code (src 26 - Papers/Alignment/09 - DPO L33-35)",
         bad="$$max_π E_{x ~ D, y ~ π(·|x)} [r(x, y)] - β · KL(π || π_ref)$$",
         good="```text\nmax_π E_{x ~ D, y ~ π(·|x)} [r(x, y)] - β · KL(π || π_ref)\n```"),
    dict(id="A17-R02", file=DPO, why="AF-009 code (src L47-49)",
         bad="$$π*(y|x) = π_ref(y|x) · exp(r(x, y) / β) / Z(x)$$",
         good="```text\nπ*(y|x) = π_ref(y|x) · exp(r(x, y) / β) / Z(x)\n```"),
    dict(id="A17-R03", file=DPO, why="AF-007 code (src L58-60)",
         bad="$$r(x, y) = β · log(π(y|x) / π_ref(y|x)) + β · log Z(x)$$",
         good="```text\nr(x, y) = β · log(π(y|x) / π_ref(y|x)) + β · log Z(x)\n```"),
    dict(id="A17-R04", file=DPO, why="AF-010 code (src L67-69)",
         bad="$$L_BT = -log σ(r(x, y_w) - r(x, y_l))$$",
         good="```text\nL_BT = -log σ(r(x, y_w) - r(x, y_l))\n```"),
    dict(id="A17-R05", file=DPO, why="AF-004 code (src L73-75)",
         bad="$$L_DPO = -log σ( β · log(π(y_w|x) / π_ref(y_w|x)) - β · log(π(y_l|x) / π_ref(y_l|x)) )$$",
         good="```text\nL_DPO = -log σ( β · log(π(y_w|x) / π_ref(y_w|x)) - β · log(π(y_l|x) / π_ref(y_l|x)) )\n```"),
    # ---- InstructGPT: two fences ----
    dict(id="A17-R06", file=INSTR, why="AF-014 code (src 26 - Papers/Alignment/07 - InstructGPT L54-56)",
         bad="$$\\text{loss} = -\\log \\sigma(r(x, y_w) - r(x, y_l))$$",
         good="```text\nloss = -log σ(r(x, y_w) - r(x, y_l))\n```"),
    dict(id="A17-R07", file=INSTR, why="AF-030 code + AF-029 '_sft' (src L71-73, pi_SFT token)",
         bad="$$\\text{objective} = E[r(x, y)] - \\beta \\cdot KL(\\pi \\| \\pi_{SFT})$$",
         good="```text\nobjective = E[r(x, y)] - β · KL(π || π_SFT)\n```"),
    # ---- Bahdanau: six fences (one triple consolidated) ----
    dict(id="A17-R08", file=BAHDAU, why="AF-038 code (src 26 - Papers/Attention Origins/01 - Bahdanau L43-45)",
         bad="$$e_{t,j} = a(s_{t-1}, h_j)$$",
         good="```text\ne_{t,j} = a(s_{t-1}, h_j)\n```"),
    dict(id="A17-R09", file=BAHDAU, why="AF-005 code (src L49-51)",
         bad="$$a(s_{t-1}, h_j) = v_a^T \\cdot \\tanh(W_a \\cdot s_{t-1} + U_a \\cdot h_j)$$",
         good="```text\na(s_{t-1}, h_j) = v_a^T · tanh(W_a · s_{t-1} + U_a · h_j)\n```"),
    dict(id="A17-R10", file=BAHDAU, why="AF-040 code (src L58-60)",
         bad="$$\\alpha_{t,j} = softmax_j(e_{t,j}) = exp(e_{t,j}) / \\sum_k exp(e_{t,k})$$",
         good="```text\nα_{t,j} = softmax_j(e_{t,j}) = exp(e_{t,j}) / Σ_k exp(e_{t,k})\n```"),
    dict(id="A17-R11", file=BAHDAU, why="AF-021 code (src L67-69)",
         bad="$$c_t = \\sum_j \\alpha_{t,j} \\cdot h_j$$",
         good="```text\nc_t = Σ_j α_{t,j} · h_j\n```"),
    dict(id="A17-R12", file=BAHDAU, why="AF-032 code (src L107-109)",
         bad="$$p(y_t | y_{<t}, x) = softmax(g(s_t, y_{t-1}, c_t))$$",
         good="```text\np(y_t | y_<t, x) = softmax(g(s_t, y_{t-1}, c_t))\n```"),
    dict(id="A17-R13", file=BAHDAU, why="AF-017 code (src L113-117: ONE three-line fence)",
         bad=("$$s_t = RNN(s_{t-1}, [y_{t-1}; c_t])$$\n\n"
              "$$c_t = \\sum_j \\alpha_{t,j} h_j$$\n\n"
              "$$\\alpha_{t,j} = softmax_j(a(s_{t-1}, h_j))$$"),
         good=("```text\ns_t = RNN(s_{t-1}, [y_{t-1}; c_t])\n"
               "c_t = Σ_j α_{t,j} h_j\n"
               "α_{t,j} = softmax_j(a(s_{t-1}, h_j))\n```")),
    # ---- Luong: seven fences (two duplicated forms replace-all) ----
    dict(id="A17-R14", file=LUONG, why="AF-033 + AF-025 code (src L29-31 and L61-63: same W_a form twice)",
         bad="$$score(s_t, h_j) = s_t^T \\cdot W_a \\cdot h_j$$",
         good="```text\nscore(s_t, h_j) = s_t^T · W_a · h_j\n```", expected_count=2),
    dict(id="A17-R15", file=LUONG, why="AF-024 + AF-011 code (src L35-37 and L55-57: same dot form twice)",
         bad="$$score(s_t, h_j) = s_t^T \\cdot h_j$$",
         good="```text\nscore(s_t, h_j) = s_t^T · h_j\n```", expected_count=2),
    dict(id="A17-R16", file=LUONG, why="AF-012 code (src L43-46: ONE two-line fence)",
         bad=("$$\\alpha_{t,j} = softmax_j(score(s_t, h_j))$$\n\n"
              "$$c_t = \\sum_j \\alpha_{t,j} \\cdot h_j$$"),
         good=("```text\nα_{t,j} = softmax_j(score(s_t, h_j))\n"
               "c_t = Σ_j α_{t,j} · h_j\n```")),
    dict(id="A17-R17", file=LUONG, why="AF-039 code (src L67-69)",
         bad="$$score(s_t, h_j) = v_a^T \\cdot \\tanh(W_a \\cdot [s_t; h_j])$$",
         good="```text\nscore(s_t, h_j) = v_a^T · tanh(W_a · [s_t; h_j])\n```"),
    dict(id="A17-R18", file=LUONG, why="AF-028 code (src L73-75)",
         bad="$$score(s_t, h_j) = w_a^T \\cdot \\tanh(W_a \\cdot s_t + U_a \\cdot h_j + b_a)$$",
         good="```text\nscore(s_t, h_j) = w_a^T · tanh(W_a · s_t + U_a · h_j + b_a)\n```"),
    # ---- Vaswani: three fences (triple consolidated, plus standalone) ----
    dict(id="A17-R19", file=VASWANI, why="AF-037 code + AF-034/035/036 head_1/head_h/head_i (src L45-49: ONE three-line fence)",
         bad=("$$\\text{MultiHead}(Q, K, V) = \\text{Concat}(\\text{head}_1, ..., \\text{head}_h) W^O$$\n\n"
              "$$\\text{head}_i = \\text{Attention}(Q W_i^Q, K W_i^K, V W_i^V)$$\n\n"
              "$$\\text{Attention}(Q, K, V) = \\text{softmax}(Q K^T / \\sqrt{d_k}) V$$"),
         good=("```text\nMultiHead(Q, K, V) = Concat(head_1, ..., head_h) W^O\n"
               "head_i = Attention(Q W_i^Q, K W_i^K, V W_i^V)\n"
               "Attention(Q, K, V) = softmax(Q K^T / sqrt(d_k)) V\n```")),
    dict(id="A17-R20", file=VASWANI, why="AF-027 code (src L56-58)",
         bad="$$\\text{Attention}(Q, K, V) = \\text{softmax}(Q K^T / \\sqrt{d_k}) V$$",
         good="```text\nAttention(Q, K, V) = softmax(Q K^T / sqrt(d_k)) V\n```"),
    dict(id="A17-R21", file=VASWANI, why="AF-008 code (src L65-68: ONE two-line aligned fence)",
         bad=("$$PE(pos, 2i) = \\sin(pos / 10000^{2i/d_{model}})$$\n\n"
              "$$PE(pos, 2i+1) = \\cos(pos / 10000^{2i/d_{model}})$$"),
         good=("```text\nPE(pos, 2i)   = sin(pos / 10000^{2i/d_model})\n"
               "PE(pos, 2i+1) = cos(pos / 10000^{2i/d_model})\n```")),
    # ---- GPT-1 ----
    dict(id="A17-R22", file=GPT1, why="AF-006 code (src 26 - Papers/Transformers/14 - GPT-1 L49-51; source writes L1 not L_1)",
         bad="$$L_1(\\theta) = \\sum_{i} \\log P(u_i | u_{i-k}, ..., u_{i-1}; \\theta)$$",
         good="```text\nL1(θ) = Σ_{i} log P(u_i | u_{i-k}, ..., u_{i-1}; θ)\n```"),
    # ---- Mermaid subgraph labels restored to bare source form ----
    dict(id="A17-R23", file=LINF, why="AF-003 code (src 19 - Linformer L47-67 bare subgraph labels)",
         bad='  subgraph "Standard Attention O(N²)"', good="  subgraph Standard Attention O(N²)"),
    dict(id="A17-R24", file=LINF, why="AF-003 code (src L47-67)",
         bad='  subgraph "Linformer Attention O(N·k)"', good="  subgraph Linformer Attention O(N·k)"),
    dict(id="A17-R25", file=PERF, why="AF-013 code (src 22 - Performer L61-76 bare subgraph labels)",
         bad='  subgraph "Standard Attention O(N²)"', good="  subgraph Standard Attention O(N²)"),
    dict(id="A17-R26", file=PERF, why="AF-013 code (src L61-76)",
         bad='  subgraph "Performer Attention O(N·r)"', good="  subgraph Performer Attention O(N·r)"),
    dict(id="A17-R27", file=LONGF, why="AF-022 code (src 18 - Longformer L42-56 bare subgraph labels)",
         bad='  subgraph "Standard Attention O(N²)"', good="  subgraph Standard Attention O(N²)"),
    dict(id="A17-R28", file=LONGF, why="AF-022 code (src L42-56)",
         bad='  subgraph "Longformer Attention O(N)"', good="  subgraph Longformer Attention O(N)"),
    dict(id="A17-R29", file=GQA, why="AF-031 code (src 29 - GQA L43-63 bare subgraph labels)",
         bad='  subgraph "GQA-2 (4 query heads, 2 KV groups)"',
         good="  subgraph GQA-2 (4 query heads, 2 KV groups)"),
    dict(id="A17-R30", file=GQA, why="AF-031 code (src L43-63)",
         bad='  subgraph "MQA (4 query heads, 1 KV)"', good="  subgraph MQA (4 query heads, 1 KV)"),
    # ---- Term markers: chapter references, source forms, cross-link ----
    dict(id="A17-R31", file=H3, why="AF-001 '2024-2024' (src 44 - H3 L83: the source's own typo'd link path, kept sic)",
         bad="- [[Jamba]] — the production-scale H3-style hybrid.",
         good="- [[Jamba]] — the production-scale H3-style hybrid (the source's own link form: `26 - Papers/2024-2024/41 - Jamba 2024`, sic)."),
    dict(id="A17-R32", file=SCALING, why="AF-002 'chapter-11' (src 42 - Scaling Laws L192-198 'the chapter-11 deep dive')",
         bad="- [[Pretraining Objectives and Scaling Laws]] — the training-side deep dive.",
         good="- [[Pretraining Objectives and Scaling Laws]] — the chapter-11 deep dive."),
    dict(id="A17-R33", file=JAMBA, why="AF-015 'chapter-24' (src 41 - Jamba L181-187 'the chapter-24 overview')",
         bad="- [[SSMs Mamba and Frontiers]] — the research-frontier overview of this model family.",
         good="- [[SSMs Mamba and Frontiers]] — the chapter-24 overview of this model family."),
    dict(id="A17-R34", file=GOT, why="AF-016 'chapter-15' (src 39 - Graph of Thoughts L198-203 'the chapter-15 deep dive')",
         bad="- [[Tree of Thoughts and Self Consistency]] — the agent-side deep dive on this reasoning family.",
         good="- [[Tree of Thoughts and Self Consistency]] — the chapter-15 deep dive on this reasoning family."),
    dict(id="A17-R35", file=LORA, why="AF-018 'communityfine-tunes' (src 06 - LoRA L132: the source's own hyphenation, keep-both)",
         bad="The community fine-tunes ecosystem of Stable Diffusion — where users trade LoRA files for specific art styles, characters, and concepts — is the most visible consumer-facing application of the technique.",
         good=("The community fine-tunes ecosystem of Stable Diffusion — where users trade LoRA files for "
               "specific art styles, characters, and concepts — is the most visible consumer-facing "
               "application of the technique (the source writes this as 'communityfine-tunes').")),
    dict(id="A17-R36", file=MINIMAX, why="AF-019 'chapter-06' (src 43 - MiniMax-01 L195-202 'the chapter-06 deep dive')",
         bad="- [[Linear Attention]] — the topical deep dive on linear attention.",
         good="- [[Linear Attention]] — the chapter-06 deep dive on linear attention."),
    dict(id="A17-R37", file=MINIMAX, why="AF-020 'chapter-24' (src L195-202 'the chapter-24 overview')",
         bad="- [[SSMs Mamba and Frontiers]] — the research-frontier overview of this model family.",
         good="- [[SSMs Mamba and Frontiers]] — the chapter-24 overview of this model family."),
    dict(id="A17-R38", file=RAGP, why="AF-026 'cross-link' (src 35 - RAG L194-201 'this paper (cross-link)')",
         bad="- [[Papers MOC]] — the area hub for paper notes.",
         good=("- [[Papers MOC]] — the area hub for paper notes.\n"
               "- The source's See-also also self-references this paper — `35 - RAG 2020 — this paper "
               "(cross-link)` — a cross-link marker this note fulfills."),
         insertion=True, probe="a cross-link marker this note fulfills"),
]


def main() -> int:
    applied = skipped = failed = 0
    for r in REPAIRS:
        path = VAULT / r["file"]
        if not path.is_file():
            print(f"FAILED: missing file {r['file']}"); failed += 1; continue
        text = path.read_text(encoding="utf-8")
        bad, good = r["bad"], r["good"]
        expected = r.get("expected_count", 1)
        if r.get("insertion"):
            marker = r["probe"]
            if marker in text:
                print(f"OK (already repaired): {r['id']}"); skipped += 1; continue
            n = text.count(bad)
            if n != 1:
                print(f"FAILED: {r['id']} anchor count {n} != 1"); failed += 1; continue
            path.write_text(text.replace(bad, good, 1), encoding="utf-8")
            post = path.read_text(encoding="utf-8")
            assert marker in post and post.count(marker) == 1
            print(f"APPLIED: {r['id']} {r['file'].split('/')[-1]} (insertion)"); applied += 1
            continue
        n = text.count(bad)
        if n == 0:
            if good in text:
                print(f"OK (already repaired): {r['id']}"); skipped += 1; continue
            print(f"FAILED: probe not found and repair not present: {r['id']} {r['file']}"); failed += 1; continue
        if n != expected:
            print(f"FAILED: probe found {n} times (expected {expected}), refusing: {r['id']}"); failed += 1; continue
        new_text = text.replace(bad, good) if expected > 1 else text.replace(bad, good, 1)
        if new_text == text:
            print(f"FAILED: no change: {r['id']}"); failed += 1; continue
        path.write_text(new_text, encoding="utf-8")
        post = path.read_text(encoding="utf-8")
        assert bad not in post, f"{r['id']}: probe still present"
        assert post.count(good) >= expected, f"{r['id']}: repaired form missing"
        print(f"APPLIED: {r['id']} {r['file'].split('/')[-1]} — {r['why'][:64]}")
        applied += 1
    print(f"\nsummary: applied={applied} skipped={skipped} failed={failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
