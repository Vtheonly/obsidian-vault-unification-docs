---
title: LLM Benchmarks
type: reference
aliases: ["LLM Benchmarks", "06 - LLM Benchmarks", "MMLU", "GPQA", "HumanEval", "MATH", "BBH"]
tags: [llm, evaluation, benchmarks, mmlu, gpqa, humaneval, contamination, saturation, llm-as-judge]
sources: ["06 - LLM Benchmarks (MMLU, GPQA, HumanEval, MATH, BBH)"]
created_index: 4
---

> [!info] TL;DR
> LLM benchmarks are standardized tests for measuring model capabilities. MMLU (general knowledge), GPQA (graduate-level Q&A), HumanEval (code), MATH (math), and BBH (reasoning) are the core 2024–2026 set. Contamination is a major concern — models can memorize benchmarks during training.

Large language models are general-purpose — hard to evaluate, because no single task sums up what a model can do. Benchmarks make evaluation tractable by providing comparable scores across models, capability tracking over time, and regression testing for new model versions. This note catalogs the core benchmark set, the specialized landscape by domain, how to run evaluations in practice, and the pitfalls — contamination, saturation, judge bias, and the gap to production — that determine how much a score should be trusted. Throughout, the guiding principle is that benchmarks are a useful signal, not ground truth.

## Why benchmarks matter

LLMs are general-purpose, so there is no obvious single yardstick for quality. Benchmarks provide three things that ad-hoc testing cannot: comparable scores across models, capability tracking over time, and regression testing for new model versions. Comparable scores put different models on one axis; capability tracking turns progress into a trend line; regression testing catches silent quality drops when a new model version ships. But benchmarks have known issues (see "Limitations and pitfalls" below) — they're a useful signal, not ground truth.

## The core 2026 benchmark set

The benchmarks that dominate model cards and leaderboards form a core set covering knowledge, reasoning, code, math, instruction following, and chat quality. The table below is the quick lookup; the subsections give the details that make each score meaningful.

| Benchmark | Tests | Format |
|---|---|---|
| MMLU | Broad knowledge | Multiple-choice across 57 subjects (STEM, humanities, professional) |
| MMLU-Pro | Harder MMLU | 10 options instead of 4 |
| GPQA | Deep reasoning and expertise | PhD-level questions in biology, chemistry, physics |
| HumanEval | Coding ability | 164 hand-written Python problems, pass@1 |
| GSM8K | Grade-school math | ~8k word problems |
| MATH | Competition-level math | Hard problems |
| BBH | Reasoning, common sense, multi-step | 23 difficult tasks from the BIG-Bench suite |
| IFEval | Instruction following | Explicit constraints such as "respond in JSON" |
| MT-Bench / AlpacaEval | Chat quality | Multi-turn conversations judged by GPT-4 (LLM-as-judge) |
| Chatbot Arena | Chat quality | Blind human side-by-side comparison, Elo rating |

### MMLU (Massive Multitask Language Understanding)

MMLU is the standard answer to "is this model smart?" It covers 57 subjects spanning STEM, the humanities, and professional fields, all multiple-choice questions, and tests broad knowledge rather than deep skill in one area. Because it is broad and cheap to run, nearly every model card reports it. MMLU-Pro is a harder version with 10 options instead of 4, and it is the designated replacement as the original nears saturation.

### GPQA (Google-Proof Q&A)

GPQA asks PhD-level questions in biology, chemistry, and physics. The name — "Google-proof" — means the questions are hard even with web search, so scoring well requires deep reasoning and expertise rather than lookup. It is a frontier model benchmark: still active far below saturation, and one of the standard ways to separate top-tier models.

### HumanEval

HumanEval is the standard for coding ability. It consists of 164 hand-written Python programming problems, each providing a function signature + docstring, and the model must implement the function. The headline metric is Pass@1: does the model get it right on the first try? HumanEval+ / MBPP are extended versions with more tests.

### MATH and GSM8K

GSM8K is grade-school math word problems (~8k problems); MATH is competition-level math problems. Both test mathematical reasoning, but they sit at very different difficulty ceilings: frontier models now hit ~90%+ on GSM8K, while MATH is still hard.

### BBH (BIG-Bench Hard)

BBH collects 23 difficult tasks from the BIG-Bench suite and tests reasoning, common sense, and multi-step problem solving. It has become the standard shorthand for "reasoning ability."

### IFEval (Instruction Following Evaluation)

IFEval tests whether the model follows explicit instructions (e.g., "respond in JSON", "use at most 3 sentences"). It is surprisingly hard for many models and important for production use, where prompts carry exactly this kind of constraint.

### MT-Bench and AlpacaEval

MT-Bench and AlpacaEval are multi-turn conversation benchmarks judged by GPT-4 (LLM-as-judge). They test chat quality, not just knowledge, and because they rely on an LLM judge they inherit the judge biases described below.

### Chatbot Arena (LMSYS)

Chatbot Arena takes a different approach: humans compare two anonymous models side-by-side and pick the better response, and an Elo rating is computed from the results. It is the most trusted "vibe check" for chat quality — real human preferences, not synthetic ones.

## Specialized benchmark landscape

Beyond the core set, each capability axis has its own benchmarks. The map below is the quick reference for finding the right benchmark once you know which capability matters:

| Domain        | Benchmarks                                    |
|---------------|-----------------------------------------------|
| Code          | HumanEval, MBPP, LiveCodeBench, BigCodeBench  |
| Math          | MATH, GSM8K, AIME                             |
| Reasoning     | BBH, ARC, HellaSwag, Winogrande               |
| Long context  | Needle in a Haystack, RULER, LongBench        |
| Multilingual  | MGSM, multilingual MMLU                       |
| Tool use      | ToolBench, API-Bank, BFCL                     |
| Agents        | AgentBench, WebArena, SWE-Bench               |
| Safety        | TruthfulQA, ToxiGen, AdvBench                 |
| Alignment     | HH-RLHF, MT-Bench, AlpacaEval                 |

The core set reappears here deliberately: HumanEval and MBPP carry the code column, MATH, GSM8K, and AIME the math column, and MT-Bench and AlpacaEval the alignment column. Note also the agentic tier — AgentBench, WebArena, and SWE-Bench — which evaluates multi-step tool-using behavior, and the safety tier of TruthfulQA, ToxiGen, and AdvBench.

## Benchmark saturation

Benchmarks have a lifecycle: they're created, models improve on them, and eventually they saturate (most models hit 90%+). Saturated benchmarks stop being informative — when most models score 90%+ on a benchmark, it can no longer distinguish between them. MMLU is near-saturated (~88%); GSM8K is saturated (~95%+). The field responds by creating harder benchmarks: MMLU-Pro, GPQA, SWE-bench, ARC-AGI. The current state of the major benchmarks:

| Benchmark | Year | Current SOTA | Saturation Level | Replacement |
|-----------|------|-------------|-----------------|-------------|
| MMLU | 2021 | ~88% | Near-saturated | MMLU-Pro |
| GSM8K | 2021 | ~95%+ | Saturated | MATH, AIME |
| HumanEval | 2021 | ~90%+ | Saturated | LiveCodeBench, BigCodeBench |
| HellaSwag | 2019 | ~95%+ | Saturated | — |
| BBH | 2022 | ~85% | Near-saturated | GPQA, ARC-AGI |
| GPQA | 2023 | ~65% | Active | — |
| MMLU-Pro | 2024 | ~75% | Active | — |
| SWE-bench | 2024 | ~50% | Active | — |
| ARC-AGI | 2024 | ~20% | Active | — |

The pattern: every 2-3 years, the field needs new benchmarks as old ones saturate. This is a sign of progress, not a problem — but it means benchmark comparisons across years are not meaningful.

## Chatbot Arena as the gold standard

Chatbot Arena (LMSYS) has emerged as the most trusted evaluation for chat quality because it measures real human preferences: humans compare two anonymous models side-by-side and pick the better response, and Elo ratings are computed from the results. Three reasons it is trusted: real human preferences — it measures what humans actually prefer, not a proxy; blind evaluation — humans don't know which model is which; and the Elo rating — it accounts for opponent difficulty. Its limitations are real too: it is subjective, chat-focused, expensive, and based on a small human sample. As of 2026, Chatbot Arena Elo is the metric that frontier labs optimize for. A 10-point Elo improvement is significant; 50+ points is a generational leap.

## Reasoning model benchmarks

Reasoning models (o1, R1) changed what benchmarks matter: AIME (competition math), Codeforces (competitive programming), GPQA Diamond (PhD science), ARC-AGI (abstract reasoning), and SWE-bench Verified (real software engineering). These are designed to be hard even for frontier models — current SOTA is 50-70%, not 90%+ — and they test multi-step reasoning, not memorization. Standard benchmarks (MMLU, GSM8K) saturate immediately for reasoning models.

## How to run benchmarks

### lm-evaluation-harness

lm-evaluation-harness is the standard open framework. A typical evaluation of an instruct model across three benchmarks:

```bash
pip install lm-eval
lm_eval --model hf --model_args pretrained=meta-llama/Meta-Llama-3-8B-Instruct \
        --tasks mmlu,gsm8k,humaneval \
        --batch_size auto
```

### lighteval

lighteval is HuggingFace's alternative, with good integration for their model hub. If your models and datasets already live on the hub, it is the smoother path.

### Vendor-reported numbers

OpenAI, Anthropic, and Google all publish their own benchmark numbers — be skeptical, as methodology varies. Treat vendor numbers as a first filter, not as directly comparable across vendors.

## Worked example: running MMLU

A concrete MMLU run with the harness, using five-shot prompting and remote code trust:

```bash
# Install
pip install lm-eval

# Evaluate a model on MMLU
lm_eval --model hf --model_args pretrained=meta-llama/Meta-Llama-3-8B-Instruct,trust_remote_code=True \
        --tasks mmlu --num_fewshot 5 --batch_size auto
```

Output: per-subject scores + overall average. The `--num_fewshot 5` flag makes this a five-shot evaluation — few-shot benchmark evaluation is a direct application of [[In-Context Learning]].

## Limitations and pitfalls

Benchmarks have known issues. Six matter in practice.

### Contamination

If a benchmark is in the training data, models can memorize it. Their score reflects memorization, not capability. MMLU has been heavily contaminated in many models. Newer benchmarks (GPQA, MMLU-Pro) try to avoid this with private test sets or recent questions. Always check if the model card reports decontaminated scores. Detection has four prongs: check whether the model card reports decontaminated scores; compare few-shot vs zero-shot performance, since contaminated models may score similarly in both regimes; use private or held-out test sets; and look for suspiciously high scores on specific subsets.

### Multiple-choice bias

Multiple-choice questions are easier than open-ended ones — the answer is in front of the model. Real-world tasks are open-ended, so a multiple-choice score is not an open-ended score.

### Benchmark gaming

Models can be fine-tuned on benchmark-style questions, inflating scores without real capability gain. The test set need not literally appear in the training data for the score to stop meaning capability.

### LLM-as-judge bias

LLM judges (used in MT-Bench, AlpacaEval) have biases: they prefer longer responses, prefer their own style, and show position bias (the first response wins more often). In full, four biases are documented: verbosity bias — judges prefer longer responses; self-preference — GPT-4 judges prefer GPT-4-style writing; position bias — judges prefer the first or last response; and calibration drift — different judges use different scales. Mitigations: use multiple judges, position-swap, calibrate against human labels, and use structured rubrics. Judge-based evaluation is treated in depth in [[LLM-as-Judge Evaluation]].

### Stale benchmarks

Once a benchmark is "solved" (most models hit 95%+), it stops being informative. MMLU is approaching this; see the saturation table above for the full picture of which benchmarks are still active.

### Real-world gap

Benchmark performance doesn't always translate to production. A model that scores well on HumanEval may still write bad code in your specific codebase. Relatedly, benchmarks don't capture [[Hallucination]] well — a model can benchmark cleanly and still hallucinate.

## Comparing scores safely

Most benchmark mistakes happen at the comparison step, not the measurement step. Five pitfalls account for most bad comparisons:

- **Comparing benchmarks across methodology** — few-shot vs zero-shot, different prompts, different eval frameworks. Numbers aren't comparable.
- **Trusting vendor-reported numbers** — always look for independent verification.
- **Forgetting benchmark drift** — a 70% MMLU score in 2023 meant something different than 70% in 2026.
- **Treating benchmarks as ground truth** — they're a proxy for capability, not the capability itself.
- **Overfitting to benchmarks** — fine-tuning on benchmark-style data improves benchmarks but may not improve real tasks.

## Common failure modes

The recurring failure modes, with likely causes and fixes:

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Benchmark scores don't match production quality | Benchmark is contaminated or doesn't match workload | Build custom eval set from production traffic |
| Sudden benchmark improvement | Contamination | Check decontamination; use private test sets |
| LLM-as-judge inconsistent | Judge bias (verbosity, style, position) | Use multiple judges; position-swap; human calibration |
| Benchmark is "solved" (95%+) | Saturation | Move to harder benchmarks (GPQA, MMLU-Pro, SWE-bench) |

Each fix points in the same direction: verify contamination, control judge bias, or move to harder benchmarks — and when the benchmark simply doesn't match your workload, build your own eval set, which is the next section.

## Benchmarks in production

Don't select models solely on benchmarks — run your own eval on your specific task. For internal eval, build a "golden set" of 50–200 examples representative of your production traffic, and use it for model selection and regression testing. Track benchmark scores over time: sudden improvements on a benchmark with no architectural change suggest contamination. For high-stakes features, combine benchmarks with human evaluation — LLM-as-judge is good for cheap iteration, humans for final validation. And watch the SOTA: capabilities are moving fast, and a model that's SOTA today is mediocre in 6 months.

### Building a custom evaluation set

The recipe: (1) sample 50-200 examples from real production traffic; (2) label each with expected output; (3) run the model at temperature=0, the standard benchmark setting (see [[Sampling Strategies]]); (4) compute accuracy, or use LLM-as-judge for open-ended tasks; (5) track the score over time and alert on regressions; (6) update quarterly. The eval set is your regression test for model changes. The same approach extends to custom eval implementations, such as building a RAG evaluation harness — the course treats that build as a capstone project. When comparing two models, the statistical significance of benchmark differences is what separates a real improvement from noise, and once a candidate wins offline, [[A-B Testing and Shadow Deployment]] is the production-grade way to confirm it on live traffic.

## Why this matters

Benchmarks are how we measure progress. Without them, we couldn't tell if a new model is actually better. For model selection, benchmarks are the starting point — but always validate on your own task. For research, benchmarks are the metric: new techniques are validated by benchmark improvements. Chatbot Arena has emerged as the most trusted signal for chat quality — real human preferences beat synthetic benchmarks. Benchmark scores also scale with compute, which ties leaderboard progress directly to the scaling-law literature (see [[Pretraining Objectives and Scaling Laws]]).

## Further reading

The foundational papers behind the benchmarks discussed here:

- Hendrycks et al. (2021), *Measuring Massive Multitask Language Understanding* (MMLU).
- Chen et al. (2021), *Evaluating Large Language Models Trained on Code* (HumanEval).
- Suzgun et al. (2022), *BIG-Bench Hard*.
- Chiang et al. (2023), *Chatbot Arena: An Open Platform for Evaluating LLMs by Human Preference*.

## See also

Related notes for the concepts this note touches:

- [[Large Language Models MOC]] — the area orientation for large language models.
- [[In-Context Learning]] — few-shot benchmark evaluation.
- [[Sampling Strategies]] — benchmarks use temperature=0.
- [[Hallucination]] — benchmarks don't capture hallucination well.
- [[LLM-as-Judge Evaluation]] — judge-based benchmarks and judge bias mitigation.
- [[A-B Testing and Shadow Deployment]] — production evaluation.
- [[Pretraining Objectives and Scaling Laws]] — benchmark scores scale with compute.
