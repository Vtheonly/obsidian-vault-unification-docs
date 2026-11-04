---
title: InstructGPT
type: concept
aliases: [InstructGPT 2022, Ouyang 2022, Training language models to follow instructions]
tags: [paper, rlhf, instructgpt, alignment, reward-model, ppo]
sources:
  - "07 - InstructGPT 2022"
created_index: 6
---

InstructGPT took a GPT-3 base model and aligned it to follow human instructions using a three-stage pipeline: supervised fine-tuning (SFT) on human-written demonstrations, reward model (RM) training on human preference comparisons, and reinforcement learning (PPO) optimizing against that reward model. The resulting model — the InstructGPT or `gpt-3.5-turbo` lineage — was dramatically more useful than the base GPT-3, and this SFT → RM → PPO recipe became known as RLHF (Reinforcement Learning from Human Feedback), the standard for aligning all subsequent LLMs. This note covers the misalignment problem it solved, the three training stages, its results and failure modes, and the alignment work it enabled — see [[Papers MOC]] for the surrounding paper collection and [[RLHF with PPO]] for the pipeline in production form.

## Citation

Ouyang, L., Wu, J., Jiang, X., Almeida, D., Wainwright, C., Mishkin, P., Zhang, C., Agarwal, S., Slama, K., Ray, A., et al. (2022). *Training language models to follow instructions with human feedback*. NeurIPS 2022. arXiv:2203.02155.

## The problem being solved

GPT-3 (2020) was powerful but unhelpful in conversation. It would continue prompts rather than answer them, refuse benign requests, ramble, or produce low-quality completions. Users had to engineer elaborate prompts to get useful output. The fundamental issue was a **misalignment between the pretraining objective (predict the next token on web text) and the user objective (follow instructions helpfully)**.

The standard fix would be supervised fine-tuning on instruction-response pairs, but high-quality labeled data is expensive. Worse, judging *quality* is subjective — different labelers may disagree on which response is better.

The InstructGPT paper proposed a clever workaround: use humans to **rank** pairs of model outputs (which is easier than writing ideal responses), train a reward model on these rankings, and then optimize the language model with RL to maximize the reward. This recipe — SFT → RM → PPO — became known as **RLHF** (Reinforcement Learning from Human Feedback).

## The three-stage pipeline

```mermaid
graph TD
  Base[GPT-3 Base Model] --> SFT
  Labelers1[Human Demonstrators] -->|Write ideal responses| SFT[SFT: Supervised Fine-Tune]
  SFT --> SFTModel[SFT Model]
  SFTModel --> Gen[Generate K responses per prompt]
  Prompt[Prompt] --> Gen
  Gen --> Labelers2[Human Raters: rank responses]
  Labelers2 --> RM[Reward Model training]
  RM --> Reward[Trained Reward Model]
  SFTModel --> PPO[PPO: RL on SFT model]
  Reward --> PPO
  PPO --> Final[InstructGPT: aligned model]
```

### Stage 1: supervised fine-tuning (SFT)

OpenAI hired roughly 40 human labelers, gave them a set of prompts (from real OpenAI API users, anonymized) and asked them to write the ideal response. GPT-3 was then fine-tuned on these prompt→response pairs for 1–2 epochs.

This stage alone dramatically improves usability — the model now follows instructions instead of just continuing text. But human-written responses are expensive, so the dataset is small (~13K prompts). The model still has plenty of failure modes that more data would fix.

### Stage 2: reward model (RM) training

For each prompt, sample K responses (typically K=4 to 9) from the SFT model. Have human labelers rank them from best to worst. Convert each ranking into pairwise comparisons: for K=4, you get 6 pairwise comparisons.

Train a reward model to predict which response a human would prefer. The RM is initialized from the SFT model (with the unembedding head replaced by a scalar output). The loss is the Bradley-Terry cross-entropy:

$$\text{loss} = -\log \sigma(r(x, y_w) - r(x, y_l))$$

where $r(x, y)$ is the RM's scalar reward for response $y$ to prompt $x$, and $y_w$, $y_l$ are the preferred and dispreferred responses.

The final RM training set was ~33K prompts with rankings.

### Stage 3: PPO reinforcement learning

Initialize the policy from the SFT model. For each prompt:

1. Sample a response from the policy.
2. Score it with the RM.
3. Use PPO to update the policy to increase the reward.

A **KL penalty** term keeps the policy close to the SFT model, preventing reward hacking:

$$\text{objective} = E[r(x, y)] - \beta \cdot KL(\pi \| \pi_{SFT})$$

The KL coefficient $\beta$ is typically 0.01–0.1. Without it, the policy exploits the RM (e.g., produces sycophantic or repetitive text that scores high but is useless).

PPO here is the policy-gradient algorithm covered in [[Proximal Policy Optimization]] and [[Policy Gradients and Actor Critic]].

## Key results

### Human preference

On the OpenAI API prompt distribution, labelers preferred InstructGPT outputs over GPT-3 outputs **85% of the time**. The 175B InstructGPT model also beat the 175B GPT-3 prompted with few-shot examples 71% of the time — meaning the RLHF alignment was more effective than careful prompt engineering.

### Output quality

InstructGPT outputs were:

- More truthful (less hallucination) on TruthfulQA.
- Less toxic (using the RealToxicityPrompts benchmark).
- Better at following constraints (e.g., "write in 3 sentences").
- More helpful for coding and reasoning tasks.

### Generalization

The model generalized to instructions not seen in the training set — including following instructions in languages other than English, despite the labelers being primarily English speakers.

## Why it worked

### Preference rankings are easier than demonstrations

Writing an ideal response is hard and labelers vary in skill. Ranking two responses is much easier — most people can reliably say "this one is better" even when they could not have written the better one themselves. This made it economically feasible to collect enough data to train a reward model.

### The reward model scales

Once trained, the RM can score unlimited responses. The expensive human step is bounded; the RL step is bounded only by compute. This decoupling is the key economic insight.

### KL penalty prevents drift

Without the KL constraint, PPO drifts toward reward-hacking behaviors that score high on the RM but lose general capability. The KL penalty keeps the policy anchored to the SFT model's distribution, so the RL phase *edits* rather than *overwrites* the model.

### RLHF generalizes better than SFT alone

Empirically, RLHF improves generalization to unseen instructions even though the SFT data was English. This is because the RM is trained on a broad distribution of prompts, and PPO optimizes the policy to produce high-reward responses on a similar distribution.

## Limitations

- **Reward hacking**. The RM has biases and blind spots. The policy exploits them. The KL penalty mitigates but does not eliminate this.
- **Labeler disagreement**. Different labelers rank differently; the RM averages over their preferences, which may not match any single user.
- **Sycophancy**. The model learns to agree with the user even when the user is wrong, because agreeable responses tend to be rated higher.
- **Cost**. The full pipeline (SFT + RM + PPO) is expensive: ~3× the compute of just SFT, plus the human-labeling cost.
- **Deceptive alignment**. RLHF does not align the model's *internal* objective — only its *output* behavior. This is a concern for safety research but not a practical problem for current chatbot use cases.

## What came after

InstructGPT established the RLHF recipe that nearly every frontier lab adopted:

- **Anthropic Claude**: RLHF + Constitutional AI (RLAIF — replace human feedback with AI feedback). See [[Constitutional AI]].
- **Llama 2 Chat**: open-weights RLHF, with detailed documentation of the recipe. See [[LLaMA]].
- **Mistral Instruct / Mixtral Instruct**: RLHF on top of the Mistral base. See [[Mistral 7B]].
- **DeepSeek-R1**: replaced PPO with GRPO (a simpler RL algorithm) and used verifiable rewards (math/code execution) instead of human feedback. See [[DeepSeek-R1]].

A parallel line of work replaced the RM+PPO pipeline entirely:

- **DPO** (Rafailov et al., 2023) — directly optimize the policy on preference data, no RM needed. See [[DPO]] and [[DPO Derivation]].
- **IPO, KTO, SimPO** — variants of direct preference optimization.

## Impact and legacy

InstructGPT is arguably the most important applied paper of the LLM era because:

1. **It defined "alignment" as a concrete engineering problem**. Before InstructGPT, alignment was a philosophical concern. After, it was a three-stage pipeline that any team with enough labels and compute could implement.
2. **It launched ChatGPT**. The `gpt-3.5-turbo` model that powered ChatGPT at launch was a descendant of InstructGPT. The product's explosive adoption was a direct consequence of this paper's recipe.
3. **It made RL commercially relevant again**. PPO had been used in games (Atari, Go) but was seen as a niche technique. InstructGPT demonstrated RL at scale on a real product, reinvigorating RL research in industry.
4. **It created the preference-data industry**. Companies like Scale AI, Surge, and Argilla now provide human preference data as a product — a market that exists because of this paper.

For an AI engineer in 2024–2026, understanding RLHF is essential. Even if you use DPO (the simpler modern default), the InstructGPT framing — collect preferences, optimize for them — is the conceptual backbone of all alignment work.

## Further reading

- Original paper: arXiv:2203.02155
- Christiano et al. (2017), *Deep RL from Human Preferences* — the foundational RLHF paper for general RL, predating InstructGPT.
- Stiennon et al. (2020), *Learning to Summarize from Human Feedback* — applied RLHF to summarization, the immediate predecessor to InstructGPT.
- DPO (Rafailov et al., 2023): arXiv:2305.18290 — direct preference optimization.

## See also

- [[Papers MOC]] — the paper index for this area.
- [[RLHF with PPO]] — the pipeline as practiced for fine-tuning.
- [[Instruction Tuning and Chat Templates]] — the SFT stage in modern form.
- [[DPO]] and [[DPO Derivation]] — the direct-optimization successor to RM+PPO.
- [[Constitutional AI]] — RLAIF: replacing human feedback with AI feedback.
- [[DeepSeek-R1]] — GRPO plus verifiable rewards.
- [[GPT-3]] — the base model being aligned.
- [[Proximal Policy Optimization]] and [[Policy Gradients and Actor Critic]] — the underlying RL algorithms.
