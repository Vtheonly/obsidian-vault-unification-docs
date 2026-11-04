---
title: Process Reward Models
type: concept
aliases: [Process Reward Models, PRM, PRM800K, OpenAI PRM, Let's Verify Step by Step, Lightman 2023]
tags: [paper, process-reward-model, prm, reasoning, math]
sources:
  - "50 - Process Reward Models 2023"
created_index: 7
---

Process Reward Models (PRMs), introduced by Lightman et al. at OpenAI in 2023 in *Let's Verify Step by Step*, are reward models that score each *step* of a reasoning chain rather than just the final answer. PRMs dramatically outperform Outcome Reward Models (ORMs) on math reasoning because they provide denser training signal and can identify exactly where a solution went wrong. The paper shipped with **PRM800K**, an 800k-step human-annotated dataset that became the standard for PRM training, and PRMs underpin modern reasoning models such as OpenAI o1 and DeepSeek-R1. This note covers the approach, the results, why the paper mattered, its limitations and open questions, and the variants that followed; [[Papers MOC]] indexes the surrounding papers area.

## Citation

Lightman, H., Kosaraju, V., Burda, Y., Edwards, H., Baker, B., Lee, T., Leike, J., Schulman, J., Sutskever, I., Cobbe, K. (OpenAI). (2023). *Let's Verify Step by Step*. arXiv:2305.20050.

## The problem being solved

Standard Reinforcement Learning from Human Feedback (RLHF) uses an **Outcome Reward Model (ORM)**: the reward is a single scalar for the entire response — the outcome-based setup established by [[InstructGPT]] and covered in [[RLHF with PPO]]. For math reasoning, this has four problems:

1. **Sparse signal**: a 10-step math solution gets one reward. If the answer is wrong, which step was the bug?
2. **Credit assignment**: the ORM can't tell whether step 2 or step 8 caused the wrong answer.
3. **Reward hacking**: the model learns to produce plausible-looking steps that lead to the right answer by luck (or wrong steps that happen to produce right answers).
4. **Hard to debug**: when an RL-trained model fails, you can't trace the failure to a specific step.

The paper's question: **what if we had a reward for each step, not just the final answer?** A Process Reward Model (PRM) scores each step independently, providing dense, localized signal.

## The approach: process reward models

### Step-level annotation

The authors collected **PRM800K** — 800,000 human-annotated reasoning steps across 75,000 math problems. Annotators labeled each step as:

- **Good**: step is correct and useful.
- **Bad**: step is incorrect or unhelpful.
- **Neutral**: step is correct but unnecessary (e.g., redundant).

### PRM architecture

The PRM is a transformer that takes the problem + solution-so-far + current-step and outputs a single scalar: P(step is good | problem, solution-so-far). It is trained on PRM800K with cross-entropy loss.

### Inference: best-of-N selection

At inference, generate N candidate solutions (e.g., N=64). Score each solution by **min over steps** (the worst step determines the score — a chain is only as strong as its weakest link) or by **product over steps**. Pick the highest-scoring solution.

This Best-of-N + PRM approach beats both Best-of-N + ORM and standard RLHF on math benchmarks.

## Key results

- **GSM8K (grade-school math)**: PRM Best-of-N (N=64) achieves 78% accuracy vs 70% for ORM Best-of-N — an 8-point improvement from better reward signal.
- **MATH (competition math)**: PRM Best-of-N achieves 33% vs 27% for ORM.
- **PRM vs ORM at scale**: PRMs scale better with more annotation — each step-level label provides more signal than a single outcome label.

### What made PRMs win

- **Dense supervision**: 800k step labels vs ~75k outcome labels — 10x more supervision signal.
- **Localized error detection**: the PRM identifies the exact step where a solution fails.
- **Step-level reward shaping**: when used in RL, the per-step reward provides gradient signal that helps the model learn each step correctly, not just the final answer.

## Why this paper matters

### Foundation for reasoning models

PRMs are a key ingredient in modern reasoning models. OpenAI o1 (2024) uses PRMs (or PRM-like reward shaping) for test-time search. DeepSeek-R1 (2025) uses verifiable rewards — a generalized PRM where the "step verifier" is a deterministic checker, not a learned model — for RL training. Anthropic Claude thinking (2024) uses step-level rewards for thinking supervision. The model category these systems belong to is covered in [[Reasoning Models]].

### Test-time search becomes practical

PRMs enable test-time best-of-N search: generate many candidate solutions, score each, pick the best. This is a form of **test-time compute scaling** — spend more compute at inference for better results. o1 takes this to the extreme with tree search + PRM. See [[Test-Time Compute Scaling]] for the broader pattern and [[Tree of Thoughts and Self Consistency]] for the search structures PRMs can guide.

### Shifted RLHF from outcomes to processes

The paper shifted the RLHF literature from outcome-based to process-based rewards. Subsequent work — RLAIF, Constitutional AI, DPO variants — increasingly considers step-level signals.

### Open dataset (PRM800K)

The PRM800K dataset is open. Researchers can train their own PRMs without the expensive annotation. This democratized PRM research and enabled many follow-up papers (Math-Shepherd, Skywork-PRM, Qwen-Math-PRM).

## Limitations

- **Annotation cost**: 800k human step labels cost ~$1M+ at OpenAI's annotation rates. Hard to replicate without significant budget.
- **Domain restriction**: PRM800K is math-only. PRMs for code, science, and general reasoning are still maturing.
- **PRM != verifier**: a learned PRM can be wrong; it's not a ground-truth verifier. Adversarial solutions can fool the PRM (e.g., plausible-looking steps that are actually wrong).
- **Verifiable rewards are better when possible**: for domains where step correctness can be checked deterministically (code execution, math proof verification), verifiable rewards >> learned PRMs. DeepSeek-R1 uses this approach.

## Variants and extensions

### Math-Shepherd (2024)

Automatic PRM training data generation: use a stronger model to label steps as good/bad. Eliminates the need for human annotation. Quality is lower but scales better.

### Skywork-PRM (2024)

Open-source PRM trained on a mix of human and synthetic data. Comparable quality to OpenAI's PRM but fully reproducible.

### Process-supervised DPO (2024)

Extends DPO to step-level preferences. Instead of preferring one full response over another, prefer one step over another. Combines PRM-style supervision with DPO's simplicity.

### Verifiable rewards (DeepSeek-R1, 2025)

Replace the learned PRM with a deterministic verifier (e.g., for math, check the final answer; for code, run tests). Eliminates PRM training entirely and is immune to reward hacking. The current (2025–2026) state of the art for math/code reasoning.

## Comparison with related approaches

| Method                       | Reward Granularity | Annotation Cost | Quality on MATH | Notes                                  |
|------------------------------|---------------------|-----------------|-----------------|----------------------------------------|
| ORM (outcome RM)             | 1 per response      | Low             | 27% (Best-of-64) | Sparse signal; reward hacking         |
| PRM (Lightman 2023)          | 1 per step          | High (~$1M)     | 33% (Best-of-64) | Dense signal; requires PRM800K-style data |
| Math-Shepherd PRM (2024)     | 1 per step          | Low (automatic) | 31%             | Synthetic labels; slightly lower quality |
| Verifiable Rewards (R1 2025) | 1 per response      | None (deterministic) | 35%+ | Best for math/code; immune to hacking |

## Reception and follow-ups

Process Reward Models (PRMs) became foundational for the 2024–2025 reasoning model wave. OpenAI o1 (2024) uses PRMs (or PRM-like reward shaping) for test-time search during reasoning. DeepSeek-R1 (2025) uses **verifiable rewards** — a generalization where the "PRM" is a deterministic checker (math verifier, code executor), not a learned model — eliminating reward hacking. Open-source PRMs (Math-Shepherd, Skywork-PRM, Qwen-Math-PRM, all 2024) are open-weights, trained on synthetic or partially-human-labeled data. Process-supervised DPO (2024) extends DPO to step-level preferences, and the PRM800K dataset became the standard for PRM training (~800k human-annotated steps).

By 2025, the trend shifted from learned PRMs to verifiable rewards (for math/code) and LLM-as-judge rewards (for open-ended tasks). PRMs remain influential but are no longer the state-of-the-art for verifiable domains — the trade-offs are analyzed in [[Verifiable Rewards vs PRMs]].

## Limitations and open questions

The limitations above bear repeating with their failure modes and the questions they open. Annotation cost remains the gating constraint: 800k human step labels cost ~$1M+ at OpenAI's annotation rates, hard to replicate without significant budget. PRM800K is math-only, and PRMs for code, science, and general reasoning are still maturing. A learned PRM can be wrong — it is not a ground-truth verifier, and adversarial solutions can fool it with plausible-looking steps that are actually wrong. Where step correctness can be checked deterministically (code execution, math proof verification), verifiable rewards beat learned PRMs, which is the approach DeepSeek-R1 takes. Learned PRMs can also be hacked: the model learns to produce steps that look good to the PRM but are actually wrong, and verifiable rewards eliminate this.

Two questions remain open:

- **Adversarial robustness**: can PRMs be made adversarially robust? Current approaches (ensemble PRMs, adversarial training) help but don't fully solve it.
- **Optimal granularity**: what's the optimal granularity for step-level rewards? Per-token? Per-sentence? Per-reasoning-step? PRM800K uses per-step (human-defined), but automatic step segmentation is an open problem.

## Interview questions

**What's the key difference between a PRM and an ORM?**
An **ORM (Outcome Reward Model)** scores the entire response with one scalar — sparse signal, hard to debug. A **PRM (Process Reward Model)** scores each reasoning step independently — dense signal, localized error detection. For a 10-step math solution, the ORM gives 1 reward; the PRM gives 10. The PRM can identify exactly which step went wrong; the ORM cannot. This denser signal makes PRMs dramatically better for math reasoning (Lightman 2023 showed an 8-point improvement on GSM8K).

**Why have verifiable rewards (DeepSeek-R1) largely replaced learned PRMs?**
Three reasons. (1) **No reward hacking**: a deterministic math checker can't be tricked; a learned PRM can be fooled by plausible-looking but wrong reasoning. (2) **No annotation cost**: verifiers are code, not human-labeled data. (3) **Perfect calibration**: verifier reward = ground truth quality; PRM rewards are noisy. Learned PRMs are still useful for non-verifiable domains (writing, helpfulness) but for math/code, verifiable rewards win. DeepSeek-R1 (2025) demonstrated this conclusively.

**How are PRMs used at inference time (not just training)?**
PRMs enable **test-time search**: generate N candidate solutions, score each with the PRM, pick the highest-scoring. This is "Best-of-N with PRM" — a form of test-time compute scaling. OpenAI o1 takes this further with tree search + PRM, exploring reasoning branches and pruning low-PRM-score paths. The PRM acts as a search heuristic, guiding the model toward correct reasoning. This is why o1 can solve problems the base model can't — it's not just generating; it's searching with PRM guidance.

## See also

- [[Papers MOC]] — the papers index.
- [[Verifiable Rewards vs PRMs]] — the head-to-head comparison with RLVR and the post-R1 convergence.
- [[InstructGPT]] — the outcome-based RLHF setup PRMs improve upon.
- [[DPO]] — the preference-optimization loss that process-supervised DPO extends to steps.
- [[RLHF with PPO]] — the RL framework PRMs plug into.
- [[DeepSeek-R1]] — verifiable-reward reasoning training, the PRM generalization.
- [[Reasoning Models]] — the model category PRMs enable.
- [[Chain of Thought]] — the step-by-step reasoning traces PRMs score.
- [[Tree of Thoughts and Self Consistency]] — the search structures PRMs guide.
- [[Test-Time Compute Scaling]] — the inference-compute paradigm PRMs unlock.
- [[Build a Reasoning Model Fine-Tune]] — practical implementation.
