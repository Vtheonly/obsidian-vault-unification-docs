#!/usr/bin/env python3
"""S27/SYNTH-001: anchored marker repairs for area 16 (Interpretability and Research).

Root-caused from reports/synthesis/s25-area16-audit.json (11 findings: 4 term
markers + 1 math span + 6 code fingerprints). Classes:

- bare-fence equations -> $$ LaTeX (the note converted the sources' unicode
  pseudocode fences to display math): restored as ```text fences carrying the
  SOURCE-VERBATIM content (s24 '19 bare-fence equations' precedent; content
  byte-identical, only the fence form matches the source).
- ASCII-vs-typographic dashes: '128K-1M' (s24 precedent).
- dropped hyphenated word form: 'trade-able' (source's own hyphenation).
- dropped chapter reference: 'chapter-10' (source's numbering; s23 note-ID
  precedent — restored as historical context).
- dropped verification sentence: 're-check' (source L66 sentence restored).
- math-span granularity: the source's inline spans $f_i$ and $mathbf{d}_i$
  must appear as exact spans; the note folded them into longer spans
  (s24 '$y, z$ as one span' precedent — restore the source's granularity).

Probe-based idempotency throughout; a second run is a complete no-op.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VAULT = REPO / "output" / "Unified-Vault"

RWKV = "16 - Interpretability and Research/Research Frontiers/Hybrid Architectures/RWKV and RetNet.md"
HYENA = "16 - Interpretability and Research/Research Frontiers/Hybrid Architectures/Hyena and Long Convolutions.md"
LOGLIT = "16 - Interpretability and Research/Interpretability/Logit Lens and Tuned Lens.md"
MECH = "16 - Interpretability and Research/Interpretability/Mechanistic Interpretability.md"
SSMS = "16 - Interpretability and Research/Research Frontiers/State Space Models/SSMs Mamba and Frontiers.md"
TTC = "16 - Interpretability and Research/Research Frontiers/Reasoning/Test-Time Compute Scaling.md"
FABLE = "16 - Interpretability and Research/Model Architecture Research/Closed Source/Fable 5 Architecture.md"

REPAIRS: list[dict] = [
    # ---- RWKV and RetNet: four bare-fence equations restored as ```text ----
    dict(id="A16-R01", file=RWKV, why="AF-008 code (src 24 - Research Frontiers/Hybrid Architectures/03 L23-25)",
         bad="$$y_t = \\sum_j \\text{softmax}(q_t \\cdot k_j) \\cdot v_j$$",
         good="```text\ny_t = Σ_j softmax(q_t · k_j) · v_j\n```"),
    dict(id="A16-R02", file=RWKV, why="AF-006 code (src L28-30)",
         bad="$$y_t = \\sum_j w_{t,j} \\cdot k_j \\cdot v_j$$",
         good="```text\ny_t = Σ_j w_{t,j} · k_j · v_j\n```"),
    dict(id="A16-R03", file=RWKV, why="AF-001 code (src L34-37: two-line fence with # comments)",
         bad="$$h_t = a_t \\cdot h_{t-1} + k_t \\cdot v_t^T$$\n\n$$y_t = R_t \\cdot h_t$$",
         good=("```text\nh_t = a_t · h_{t-1} + k_t · v_t^T    # state update (like an RNN)\n"
               "y_t = R_t · h_t                       # output\n```")),
    dict(id="A16-R04", file=RWKV, why="AF-002 code (src L74-76)",
         bad="$$\\text{Retention}(Q, K, V) = (Q \\cdot D \\cdot K^T) \\cdot V$$",
         good="```text\nRetention(Q, K, V) = (Q · D · K^T) · V\n```"),
    # ---- Hyena ----
    dict(id="A16-R05", file=HYENA, why="AF-004 code (src 04 - Hyena and Long Convolutions L30-32)",
         bad="$$y = (x \\cdot h_1) \\cdot h_2 \\cdot h_3 \\cdot \\ldots$$",
         good="```text\ny = (x · h_1) · h_2 · h_3 · ...\n```"),
    # ---- Logit Lens: tuned-lens affine form (two-line source fence) ----
    dict(id="A16-R06", file=LOGLIT, why="AF-009 code (src 14 - Interpretability L80-83, two-line fence)",
         bad="$$\\text{logits}_l = W_U \\cdot (T_l(h_l)) = W_U \\cdot (A_l \\cdot h_l + b_l)$$",
         good="```text\nlogits_l = W_U · (T_l(h_l))\n         = W_U · (A_l · h_l + b_l)\n```"),
    # ---- Mechanistic Interpretability: source's inline-span granularity ----
    dict(id="A16-R07", file=MECH, why="AF-010 math spans 'f_i'/'\\\\mathbf{d}_i' (src 01 - Mechanistic Interpretability L85: source-verbatim sentence)",
         bad="is a learned feature direction. Each feature tends to be monosemantic — it activates for one concept.",
         good=("is a learned feature direction. The source's summary is plainer: $f_i$ are sparse (most are 0) "
               "and $\\mathbf{d}_i$ are learned \"feature directions.\" Each feature tends to be monosemantic — "
               "it activates for one concept.")),
    # ---- SSMs: dash form ----
    dict(id="A16-R08", file=SSMS, why="AF-003 '128k-1m' (src 01 - SSMs L232-234 '128K-1M: YaRN-extended RoPE', ASCII hyphen)",
         bad="- 128K–1M: YaRN-extended RoPE (Llama 3.1 extended, Qwen 2.5).",
         good="- 128K-1M: YaRN-extended RoPE (Llama 3.1 extended, Qwen 2.5)."),
    # ---- Test-Time Compute: the source's hyphenation ----
    dict(id="A16-R09", file=TTC, why="AF-005 'trade-able' (src 06 - Test-Time Compute L155 'a separate, trade-able dimension')",
         bad="now inference compute is a separate, tradeable dimension",
         good="now inference compute is a separate, trade-able dimension"),
    # ---- Fable 5: chapter reference + verification sentence ----
    dict(id="A16-R10", file=FABLE, why="AF-007 'chapter-10' (src 10 - Fable 5 L75 'the other chapter-10 architecture notes')",
         bad="it will be expanded with the same depth as the other per-model architecture notes",
         good="it will be expanded with the same depth as the other chapter-10 architecture notes"),
    dict(id="A16-R11", file=FABLE, why="AF-011 're-check' (src L66 'Future iterations should re-check the Research Queue entry')",
         bad="3. **Provide a verification target** so future work knows what to look for.",
         good=("3. **Provide a verification target** so future work knows what to look for: future iterations "
               "should re-check the Research Queue entry for \"Fable 5\" and update this note when a public "
               "source appears."),
         insertion=True, probe="future iterations should re-check the Research Queue entry"),
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
        if n != 1:
            print(f"FAILED: probe found {n} times (expected 1), refusing: {r['id']}"); failed += 1; continue
        new_text = text.replace(bad, good, 1)
        if new_text == text:
            print(f"FAILED: no change: {r['id']}"); failed += 1; continue
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
