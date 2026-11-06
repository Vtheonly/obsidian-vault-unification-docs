---
title: Remaining Work Log
type: reference
aliases: [Remaining Work, Prioritized Backlog]
tags: [vault-management, remaining-work, backlog, project-log]
sources:
  - "Remaining Work"
created_index: 14
---

This note is the archived open-work backlog of the vault build, ordered by priority and dated 2026-08-08 at the close of iteration 13. After that iteration tackled all 7 gaps deeply, the vault stood at ~100% effective completion with no systematic chapter-level gaps remaining, so the remaining items are future-iteration (14+) work that depends on external events (new model releases, new papers, etc.). Every backlog item, priority tier, and verification caveat from the original record is preserved here in its original order.

## Critical (iteration 14+ should monitor)

The critical tier is verification work gated on official sources that did not yet exist when iteration 13 closed:

- [ ] Verify chapter 10 model architecture notes when GPT-5, Claude 5/Opus 5, Gemini 3 official technical reports emerge.
- [ ] Verify Fable 5 and Mythos — these may be hypothetical 2026 models that never get official technical reports. If unverifiable indefinitely, leave the stub notes ([[Fable 5 Architecture]], [[Mythos Architecture]]) as documentation of the gap.
- [ ] Re-verify chapter 24 research frontier notes when new architectures ([[Titans]] scale-up, new hybrid attention variants) emerge in 2027.

## High priority (when new research emerges)

The high-priority tier collects additions that become possible only as new research appears, drawn from the future sections of the updated chapter MOCs.

### Papers (26) — future

From the updated chapter 26 papers MOC section "Planned for Iteration 14+" (see [[Papers MOC]]) — long-context work would extend [[Long-Context Architectures]], agent evaluation would build on [[LLM Benchmarks]], test-time learning on [[Titans]], and new linear attention on [[Linear Attention]] and [[Mamba-2 and Structured Attention]]:

- [ ] 2026 frontier model architectures (GPT-5, Claude 5, Gemini 3 — when technical reports emerge).
- [ ] Long-context breakthroughs (Ring Attention variants, new positional schemes).
- [ ] Multimodal reasoning papers (reasoning + vision + audio).
- [ ] Agent benchmarks and evaluation frameworks (when standardized benchmarks emerge).
- [ ] Test-time learning architectures (Titans scale-up, if production deployment occurs).
- [ ] New linear attention formulations (improvements over lightning attention, Mamba-2 SSD).

### Projects (27) — future

From the updated chapter 27 projects MOC section "Future Projects for Iteration 14+" (see [[Projects MOC]]) — the same five builds queued in the next-iteration handoff, where the MCP platform builds on [[MCP Overview]], the red-team pipeline on [[LLM Security and Prompt Injection]], and the routing system on [[Gateway and Router Patterns]]:

- [ ] Build a continuous pretraining pipeline (continued pretraining on a new domain).
- [ ] Build a multimodal reasoning model (vision + reasoning training).
- [ ] Build an MCP-based agent platform (multi-server, multi-tenant).
- [ ] Build an automated red-team pipeline (systematic prompt injection testing).
- [ ] Build a model routing system (cost-aware routing across multiple models).

### Interview prep (29) — future

Interview prep grows by extending its three question banks as new topics and techniques appear:

- [ ] Add conceptual interview questions for new topics that emerge in 2026–2027 — extending [[Conceptual Interview Questions]].
- [ ] Add coding questions for new techniques (test-time learning, new hybrid attention variants, etc.) — extending [[Coding Interview Questions]].
- [ ] Add system design questions for new architectures (multimodal reasoning deployment, agentic systems at scale) — extending [[System Design Interview Questions]].

## Medium priority — quality polish

### All chapters at "Strong" status — no systematic gaps

After iteration 13 (tackle ALL 7 gaps deeply), every chapter is comprehensively deepened. No chapter has remaining systematic shallow-note patterns; individual notes may benefit from future expansion, but no chapter-level work remains. The specific deepening completed in iteration 13 was:

- Chapter 01 (AI Foundations) — [[History and Evolution of AI|A Brief History of AI]] deepened (133 → 190 lines).
- Chapter 09 (Foundation Models) — [[Embedding Models for Retrieval]] deepened (122 → 247 lines).
- Chapter 10 (Model Architecture Research) — 8 new 2026 notes + synthesis added ([[Frontier Model Synthesis 2026]]).
- Chapter 24 (Research Frontiers) — 2026 Research Frontier Update added ([[Research Frontier Update 2026]]).
- Chapter 26 (Papers) — 5 new paper notes added (51–55).
- Chapter 27 (Projects) — 5 new capstones added (20–24).
- Chapter 29 (Interview Prep) — 2 new notes added (06 conceptual, 05 coding part 3).

All other chapters remain at "Strong" status from prior iterations.

## Wikilink audit (iteration 13 — final)

The final wikilink audit of iteration 13, run with `/home/z/my-project/scripts/audit_wikilinks_v3.py`, produced the following results:

- **Total wikilinks**: 5,183 (up from 4,814 in iteration 12).
- **Broken**: 3 (down from 289 — **99% reduction**).
- **Breakage rate**: 0.1% (down from 6.1%).
- **Remaining 3 broken**: all are documentation-example placeholders in the [[Architecture Decisions Log]] — the two placeholder forms, fenced below so the syntax shows literally — these are intentional examples of wikilink syntax and should not be fixed.

```text
[[Note Name]], [[folder/path/Note Name]]
```

## Coverage summary (iteration 13 final)

| Status | Count | Chapters |
| --- | --- | --- |
| **Complete/Strong** | 30 | 00, 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29 |
| (empty) | 1 | 99 (Archives) |

The vault is now comprehensively built out, comprehensively deepened, and comprehensively verified against 2026 sources. All 30 chapters are at "Strong" status with no systematic gaps. Iteration 14+ should focus on:

1. New papers/projects as they emerge in 2026–2027.
2. Verifying chapter 10 model architecture notes when new technical reports emerge.
3. Verifying chapter 24 research frontier notes for newest 2027 developments.
4. Adding any new techniques that emerge (test-time learning at scale, new attention variants).

## See also

- [[Master Roadmap]]
- [[Vault Status Log]]
- [[Next Iteration Log]]
- [[Coverage Audit Log]]
- [[Vault Management README]]
- [[Current Iteration Log]]
- [[Completed Work Log]]
