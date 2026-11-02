#!/usr/bin/env python3
"""S22/SYNTH-001: anchored marker-retention repairs for area 08 (39 findings).

Findings AF-001..AF-039 (reports/synthesis/s22-area08-audit.json): rare source
terms and source-verbatim equation forms dropped or altered during synthesis.
Root-cause classes (session-21 pattern):
- verbatim-form equation gaps: content present but re-notated (frac vs slash,
  split math spans, K= folded inside $...$), so the whole-span fingerprint
  check fails -> restore the source-exact form alongside the note's variant;
- source-voice sentences and glosses: transitional sentences / See-also
  glosses paraphrased away -> restore the source wording;
- source note-ID cross-references (08.1.01 etc.): dropped parentheticals ->
  restored as historical context (session-21 standing precedent);
- hyphenation / dash variants (word-alignments, cat-vs-dog, RMSNorm-like,
  2018-2026) and en-dash->hyphen normalizations.
Every repair cites its source KU's locator; anchored, asserted, idempotent.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VAULT = REPO / "output/Unified-Vault"
A08 = VAULT / "08 - Attention and Transformers"

REPAIRS: list[dict] = [
    # ---- T5 and BART: AF-001 '2018-2026'; AF-008 'rmsnorm-like' (x2) ----
    {
        "id": "AF-001",
        "file": A08 / "Transformer Architecture/T5 and BART.md",
        "old": "The trend from 2018 onward has been toward decoder-only, for five reasons:",
        "new": "The trend 2018-2026 has been toward decoder-only, for five reasons:",
    },
    {
        "id": "AF-008a",
        "file": A08 / "Transformer Architecture/T5 and BART.md",
        "old": "RMSNorm-style normalization in place of the original LayerNorm — see [[Pre-Norm vs Post-Norm]] for that design axis.",
        "new": "RMSNorm-like normalization in place of the original LayerNorm — see [[Pre-Norm vs Post-Norm]] for that design axis.",
    },
    {
        "id": "AF-008b",
        "file": A08 / "Transformer Architecture/T5 and BART.md",
        "old": "- [[Pre-Norm vs Post-Norm]] — T5's later variants adopt simplified RMSNorm-style normalization",
        "new": "- [[Pre-Norm vs Post-Norm]] — T5's later variants adopt simplified RMSNorm-like normalization",
    },
    # ---- ALiBi: AF-003 'kv-cache-friendly'; AF-004 'locality-based' ----
    {
        "id": "AF-003",
        "file": A08 / "Attention Mechanism/ALiBi.md",
        "old": "Because the bias is added at query time, ALiBi is friendly to the KV cache — the cached keys and values carry no positional modification.",
        "new": "Because the bias is added at query time, ALiBi is KV-cache-friendly — the cached keys and values carry no positional modification.",
    },
    {
        "id": "AF-004",
        "file": A08 / "Attention Mechanism/ALiBi.md",
        "old": "- [[Sliding Window Attention]]\n- [[Scaled Dot-Product Attention]]",
        "new": "- [[Sliding Window Attention]] — another locality-based approach\n- [[Scaled Dot-Product Attention]]",
    },
    # ---- ViT Architecture: AF-007 'justify'; AF-020 'vision-language' + AF-031 'co-train' ----
    {
        "id": "AF-007",
        "file": A08 / "Vision Transformers/ViT Architecture.md",
        "old": "Each component of the ViT is a deliberate choice, often different from the original NLP Transformer. The major ones:",
        "new": "Each component of the ViT is a deliberate choice, often different from the original NLP Transformer. Let's justify the major ones:",
    },
    {
        "id": "AF-020+AF-031",
        "file": A08 / "Vision Transformers/ViT Architecture.md",
        "old": "**CLIP** (Radford et al. 2021) co-trains an image encoder (a ViT) and a text encoder (a Transformer) on 400M image-text pairs, producing image features aligned with language — the backbone of modern multimodal AI.",
        "new": "**CLIP** (Radford et al. 2021) applies the co-train recipe — an image encoder (a ViT) and a text encoder (a Transformer) trained together on 400M image-text pairs — producing image features aligned with language: the most common use of a ViT as one tower of a vision-language contrastive model, and the backbone of modern multimodal AI.",
    },
    # ---- BERT: AF-021 'bert-like' ----
    {
        "id": "AF-021",
        "file": A08 / "Transformer Architecture/BERT.md",
        "old": "Many modern embedding models are BERT-family models fine-tuned with contrastive loss: **BGE** (BAAI), **E5** (Microsoft), **GTE** (Alibaba), and **sentence-transformers** (SBERT), the original.",
        "new": "Many modern embedding models are BERT-like models fine-tuned for retrieval with contrastive loss: **BGE** (BAAI), **E5** (Microsoft), **GTE** (Alibaba), and **sentence-transformers** (SBERT), the original.",
    },
    # ---- FlashAttention: AF-024 'enablement' ----
    {
        "id": "AF-024",
        "file": A08 / "Efficient Attention/FlashAttention.md",
        "old": "and is a **long-context enabler**: without FlashAttention, 32k+ context is impractical; with it, 128k is routine.",
        "new": "and provides **long-context enablement**: without FlashAttention, 32k+ context is impractical; with it, 128k is routine.",
    },
    # ---- Sinusoidal: AF-025 'hypothesized'; AF-028 equation spaces ----
    {
        "id": "AF-025",
        "file": A08 / "Attention Mechanism/Sinusoidal and Learned Positional Encodings.md",
        "old": "The authors hoped sinusoidal encoding would **extrapolate** to longer sequences than seen in training, because",
        "new": "The original Transformer paper hypothesized that sinusoidal encoding would **extrapolate** to longer sequences than seen in training, because",
    },
    {
        "id": "AF-028",
        "file": A08 / "Attention Mechanism/Sinusoidal and Learned Positional Encodings.md",
        "old": "\\sin(i + \\delta) = \\sin(i) \\cos(\\delta) + \\cos(i) \\sin(\\delta)",
        "new": "\\sin(i + \\delta) = \\sin(i)\\cos(\\delta) + \\cos(i)\\sin(\\delta)",
    },
    # ---- Origins of Attention: AF-026 'word-alignments'; AF-038 'cross-sequence';
    #      AF-006 single-span alphas; AF-009 bold display equation ----
    {
        "id": "AF-026",
        "file": A08 / "Attention Mechanism/Origins of Attention.md",
        "old": "for translation they often recover word alignments that match linguistic intuition.",
        "new": "for translation they often recover word-alignments that match linguistic intuition.",
    },
    {
        "id": "AF-038",
        "file": A08 / "Attention Mechanism/Origins of Attention.md",
        "old": "**Self-attention**: attend within the same sequence (not cross-attention to another sequence).",
        "new": "**Self-attention**: attend within the same sequence, not cross-sequence attention to another sequence.",
    },
    {
        "id": "AF-006",
        "file": A08 / "Attention Mechanism/Origins of Attention.md",
        "old": "The attention weights come out as $\\alpha_{1,1} = 0.9$, $\\alpha_{1,2} = 0.05$, $\\alpha_{1,3} = 0.05$, so the context is",
        "new": "The attention weights come out as $\\alpha_{1,1} = 0.9, \\alpha_{1,2} = 0.05, \\alpha_{1,3} = 0.05$, so the context is",
    },
    {
        "id": "AF-009",
        "file": A08 / "Attention Mechanism/Origins of Attention.md",
        "old": "or in the more compact vector notation, $\\mathbf{c}_t = \\sum_{i=1}^n \\alpha_{ti} \\mathbf{h}_i$, where $\\alpha_{ti}$ are the attention weights",
        "new": "or, in the bold-vector notation of the original formulation, as a sum over the $T$ source positions:\n\n$$\\mathbf{c}_t = \\sum_{i=1}^{T} \\alpha_{ti} \\mathbf{h}_i^{enc}$$\n\nThe compact inline form $\\mathbf{c}_t = \\sum_{i=1}^n \\alpha_{ti} \\mathbf{h}_i$ says the same thing; $\\alpha_{ti}$ are the attention weights",
    },
    # ---- Linear Attention: AF-005 inline form; AF-010/AF-023 Linformer forms ----
    {
        "id": "AF-005",
        "file": A08 / "Efficient Attention/Linear Attention.md",
        "old": "Standard attention:\n\n$$\n\\text{Attn}(Q, K, V) = \\text{softmax}\\left(\\frac{Q K^T}{\\sqrt{d}}\\right) V\n$$",
        "new": "Standard attention, in its inline form $\\text{Attn}(Q, K, V) = \\text{softmax}(QK^T / \\sqrt{d}) V$:\n\n$$\n\\text{Attn}(Q, K, V) = \\text{softmax}\\left(\\frac{Q K^T}{\\sqrt{d}}\\right) V\n$$",
    },
    {
        "id": "AF-010+AF-023",
        "file": A08 / "Efficient Attention/Linear Attention.md",
        "old": "$$\n\\tilde{K} = E K \\quad \\text{where } E \\in \\mathbb{R}^{k \\times n}\n$$\n\n$$\n\\tilde{V} = F V \\quad \\text{where } F \\in \\mathbb{R}^{k \\times n}\n$$\n\nNow $Q \\tilde{K}^T$ is $n \\times k$ instead of $n \\times n$.",
        "new": "$$\n\\tilde{K} = E K, \\quad \\tilde{V} = F V\n$$\n\nwhere $E, F \\in \\mathbb{R}^{k \\times n}$. Now $Q \\tilde{K}^T$ is $n \\times k$ instead of $n \\times n$.",
    },
    # ---- Bahdanau: AF-022 single-span softmax values ----
    {
        "id": "AF-022",
        "file": A08 / "Attention Mechanism/Bahdanau Attention.md",
        "old": "The softmax gives $\\alpha_{11} \\approx 0.92$, $\\alpha_{12} \\approx 0.05$, $\\alpha_{13} \\approx 0.03$, so",
        "new": "Softmax: $\\alpha_{11} \\approx 0.92, \\alpha_{12} \\approx 0.05, \\alpha_{13} \\approx 0.03$. So",
    },
    # ---- GQA MQA and MLA: AF-032/AF-033 K=/V= outside math; AF-027 K= outside ----
    {
        "id": "AF-032+AF-033",
        "file": A08 / "Efficient Attention/GQA MQA and MLA.md",
        "old": "At inference, we need $K = \\mathbf{W}_{UK} \\mathbf{c}_t$ and $V = \\mathbf{W}_{UV} \\mathbf{c}_t$ — but computing K from $\\mathbf{c}_t$ at every step is expensive.",
        "new": "At inference, we need K = $\\mathbf{W}_{UK} \\mathbf{c}_t$ and V = $\\mathbf{W}_{UV} \\mathbf{c}_t$ — but computing K from $\\mathbf{c}_t$ at every step is expensive.",
    },
    {
        "id": "AF-027",
        "file": A08 / "Efficient Attention/GQA MQA and MLA.md",
        "old": "So instead of computing $K = \\mathbf{W}_{UK} \\mathbf{c}_j$ and then dotting with Q,",
        "new": "So instead of computing K = $\\mathbf{W}_{UK} \\mathbf{c}_j$ and then dotting with Q,",
    },
    # ---- Mixture of Experts: AF-029 single-span (E=8, k=2) ----
    {
        "id": "AF-029",
        "file": A08 / "Transformer Architecture/Mixture of Experts.md",
        "old": "For Mixtral 8x7B ($E=8$, $k=2$): parameters are ~47B",
        "new": "For Mixtral 8x7B ($E=8, k=2$): parameters are ~47B",
    },
    # ---- MOC: AF-011..AF-019 learning-path note-IDs; AF-034/AF-035 leaves-out IDs ----
    {
        "id": "AF-011..AF-019",
        "file": A08 / "Attention and Transformers MOC.md",
        "old": (
            '- why attention is a "soft lookup";\n'
            "- why Q, K, V are three different projections of the same input;\n"
            "- why we divide by $\\sqrt{d_k}$;\n"
            "- why we need multiple heads;\n"
            "- why self-attention kills the RNN;\n"
            "- why positional encoding is necessary;\n"
            "- how a ViT turns an image into a sequence;\n"
            "- why ViTs need more data than CNNs;\n"
            "- why BERT and GPT make opposite design choices;"
        ),
        "new": (
            '- why attention is a "soft lookup" (08.1.01);\n'
            "- why Q, K, V are three different projections of the same input (08.1.02);\n"
            "- why we divide by $\\sqrt{d_k}$ (08.1.03);\n"
            "- why we need multiple heads (08.1.04);\n"
            "- why self-attention kills the RNN (08.2.01);\n"
            "- why positional encoding is necessary (08.2.02);\n"
            "- how a ViT turns an image into a sequence (08.3.01);\n"
            "- why ViTs need more data than CNNs (08.3.03);\n"
            "- why BERT and GPT make opposite design choices (08.4.01);"
        ),
    },
    {
        "id": "AF-034",
        "file": A08 / "Attention and Transformers MOC.md",
        "old": "they surface in [[The Transformer]] as a research direction and are collected here as a second-layer subfamily rather than part of the core path.",
        "new": "they are mentioned in [[The Transformer]] (course note 08.2.05) as a research direction and are collected here as a second-layer subfamily rather than part of the core path.",
    },
    {
        "id": "AF-035",
        "file": A08 / "Attention and Transformers MOC.md",
        "old": "a definitive treatment would be premature — [[Choosing the Right Architecture]] is where they get weighed.",
        "new": "a definitive treatment would be premature (they are mentioned in 08.4.04) — [[Choosing the Right Architecture]] is where they get weighed.",
    },
    # ---- Choosing the Right Architecture: AF-030 'actionable'; AF-002 'concludes' ----
    {
        "id": "AF-030",
        "file": A08 / "Encoder Decoder Design Space/Choosing the Right Architecture.md",
        "old": "This note turns those questions into a decision tree, task-by-task recommendations, and per-configuration guidance, then closes with the modern reality:",
        "new": "This note ties the design space together into actionable guidance — a decision tree, task-by-task recommendations, and per-configuration guidance — then closes with the modern reality:",
    },
    {
        "id": "AF-002",
        "file": A08 / "Encoder Decoder Design Space/Choosing the Right Architecture.md",
        "old": "Taken together with the Transformer architecture itself and its application to vision, this completes the picture of the encoder/decoder design space.",
        "new": "This concludes the picture: you now understand the Transformer architecture, its application to vision (ViT), and the encoder/decoder design space.",
    },
    # ---- CLS Token: AF-036/AF-037 hyphenated task names ----
    {
        "id": "AF-036+AF-037",
        "file": A08 / "Vision Transformers/CLS Token.md",
        "old": 'If you switch from "cat vs dog" to "is there a person in this image?", the GAP summary is the same — only the final linear classifier changes. The CLS token, by contrast, is a learned parameter that adapts to the task: for "cat vs dog" it learns to attend to animal-related patches; for "is there a person?" it learns to attend to person-related patches.',
        "new": "If you switch from cat-vs-dog to person-detection, the GAP summary is the same — only the final linear classifier changes. The CLS token, by contrast, is a learned parameter that adapts to the task: for cat-vs-dog it learns to attend to animal-related patches; for person-detection it learns to attend to person-related patches.",
    },
    # ---- Multi-Head Attention: AF-039 'referents' ----
    {
        "id": "AF-039",
        "file": A08 / "Attention Mechanism/Multi-Head Attention.md",
        "old": '- **Coreference:** "it" should attend to "cat" (its referent).',
        "new": '- **Coreference:** attention from pronouns to their referents — "it" should attend to "cat".',
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
