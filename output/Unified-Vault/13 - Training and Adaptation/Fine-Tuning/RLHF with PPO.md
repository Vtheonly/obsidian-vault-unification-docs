---
title: RLHF with PPO
type: concept
aliases: [RLHF with PPO, RLHF, Reinforcement Learning from Human Feedback]
tags: [fine-tuning, rlhf, ppo, reward-model]
sources: [05 - RLHF with PPO]
created_index: 6
---

RLHF (Reinforcement Learning from Human Feedback) aligns LLMs to human preferences through a three-stage pipeline: supervised fine-tuning, reward model training on preference data, and PPO optimization of the policy under a KL penalty that keeps it close to the SFT model. This note walks through that pipeline and its practical costs — four models in memory, sequential rollouts, reward hacking — along with hyperparameters, failure modes, and when to prefer the simpler modern alternative. It is the original ChatGPT-era alignment recipe and still the choice at frontier labs; see [[Training and Adaptation MOC]] for the surrounding area.

> [!info] TL;DR
> RLHF (Reinforcement Learning from Human Feedback) aligns LLMs to human preferences via three steps: train a reward model on preference data, then use PPO to optimize the policy to maximize the reward (with a KL penalty to stay close to the SFT model). DPO ([[DPO Derivation]]) is the simpler modern alternative.

## The three-stage pipeline

```mermaid
graph LR
  Base[Base LLM] --> SFT[SFT on Instructions]
  SFT --> PrefData[Collect Preference Data]
  PrefData --> RM[Train Reward Model]
  RM --> PPO[PPO Optimization]
  SFT --> Ref[Frozen Reference Policy]
  Ref --> PPO
  PPO --> Aligned[Aligned LLM]
```

### SFT

Supervised fine-tuning on instruction-response pairs. Produces a chat-capable model. See [[Instruction Tuning and Chat Templates]].

### Reward model training

Train a model $r_\phi(x, y)$ that scores how good a response $y$ is for a prompt $x$, based on human preferences.

**Preference data format**: $(x, y_w, y_l)$ — for prompt $x$, response $y_w$ is preferred over $y_l$.

**Training objective** (Bradley-Terry model):

$$
\mathcal{L}_{\text{RM}} = -\log \sigma(r_\phi(x, y_w) - r_\phi(x, y_l))
$$

The reward model is usually the SFT model with a scalar head replacing the language modeling head.

### PPO optimization

Use PPO to optimize the policy $\pi_\theta$ to maximize rewards while staying close to the SFT model:

$$
\max_\theta \mathbb{E}_{x \sim \mathcal{D}, y \sim \pi_\theta(\cdot \mid x)} \left[ r_\phi(x, y) - \beta \log \frac{\pi_\theta(y \mid x)}{\pi_{\text{ref}}(y \mid x)} \right]
$$

The KL penalty $\beta \log(\pi_\theta / \pi_{\text{ref}})$ prevents reward hacking — the model drifting to outputs that score high on the reward model but are degenerate.

See [[Proximal Policy Optimization]] for the PPO mechanics.

## Practical setup

### Models in memory

PPO for RLHF requires 4 models in memory simultaneously:

1. **Policy** $\pi_\theta$ (being trained).
2. **Reference** $\pi_{\text{ref}}$ (frozen, for KL penalty).
3. **Reward model** $r_\phi$ (frozen).
4. **Value model** $V_\psi$ (the critic, being trained).

For a 7B SFT model: 4 × 7B = 28B params in fp16 = 56 GB, plus optimizer state and activations. Needs multiple H100s.

### Generating rollouts

Each PPO step:

1. Sample prompts from the preference dataset.
2. Generate responses with the current policy (this is the expensive part).
3. Score responses with the reward model.
4. Compute per-token KL penalty against the reference.
5. PPO update.

### Hyperparameters (typical)

The KL coefficient $\beta$ runs 0.01–0.5 and is critical — too low → reward hacking; too high → no learning. The learning rate sits at 1e-5 to 5e-5, the PPO clip range at 0.1–0.2, the rollout batch size at 32–512 prompts, and PPO epochs per batch at 1–4.

## Reward hacking

The classic RLHF failure mode: the policy finds inputs to the reward model that score high but are degenerate. Examples include repetitive outputs (the reward model gives high scores to repeated phrases it saw in positive training data), gibberish that exploits reward model biases, and overly long responses (if length correlates with positive examples).

Mitigations: the **KL penalty** is the main defense and keeps the policy close to SFT; **reward model ensembles** average multiple reward models; **length normalization** penalizes long responses; and **active reward model retraining** updates the reward model with newly collected preferences.

## Why RLHF lost ground to DPO

PPO-based RLHF is finicky and expensive: it holds 4 models in memory, is tuning-sensitive (KL coefficient, clip range, LR all matter), is slow (rollout generation is sequential), and is hard to debug.

[[DPO Derivation|DPO]] replaced PPO for most open-source work with 2 models (policy + reference), no reward model training, no PPO, and standard supervised learning on preference pairs. PPO survives at frontier labs (where every bit of quality matters) but is rare in open-source RLHF as of 2026.

## When to use RLHF vs DPO

### Use RLHF (PPO)

When you have a frontier-scale compute budget, an active data collection pipeline (continuously updating the reward model), or DPO quality is insufficient and you've exhausted DPO variants.

### Use DPO

As the default choice for open-source alignment, with a smaller compute budget, or when you want simplicity and reproducibility.

### Use RLAIF / Constitutional AI

When you don't have human preference data: use a strong LLM (e.g., Claude) to label preferences.

## Why this matters for AI

RLHF (whether PPO or DPO) is what turned pretrained LLMs into useful chat assistants. Without it, ChatGPT wouldn't exist. The KL-penalized RL formulation is a general pattern — it appears in safety training, alignment, and agent training. Understanding RLHF also helps you read alignment papers and reason about model behavior (why does the model refuse? why does it have a particular style?).

## Production implications

**For most teams, use DPO** instead of PPO. Simpler, cheaper, comparable quality.

**For custom alignment**, start with DPO. Move to PPO only if DPO is insufficient.

**Reward model quality is the bottleneck.** Invest in preference data quality.

**Monitor KL** during training — if it grows past a threshold, the model is reward hacking.

**For agents**, "RLHF" can mean training with task-completion rewards (verifiable signals like code passing tests, agent reaching goals). This is closer to R1-style training.

## Common pitfalls

**KL coefficient too low** — reward hacking; model produces gibberish.

**KL coefficient too high** — no learning; model stays at SFT.

**Reward model trained on biased data** — propagates bias into the policy.

**Forgetting to freeze the reward model** during PPO — breaks the algorithm.

**Not enough rollout diversity** — PPO overfits to a narrow distribution.

**Forgetting to detach the value target** — gradient flows through itself.

## Further reading

The papers that defined the recipe:

- Ouyang et al. (2022), *Training language models to follow instructions with human feedback* (InstructGPT).
- Christiano et al. (2017), *Deep Reinforcement Learning from Human Preferences*.
- Bai et al. (2022), *Constitutional AI* (RLAIF).
- Rafailov et al. (2023), *DPO*.

## Interview-style questions

**What are the three stages of RLHF?** (1) SFT — supervised fine-tuning on instruction-response pairs. (2) Reward model training — train $r_\phi(x,y)$ on preference data $(x, y_w, y_l)$ using Bradley-Terry loss: $-\log \sigma(r(y_w) - r(y_l))$. (3) PPO optimization — train policy $\pi_\theta$ to maximize $r_\phi(x,y) - \beta KL(\pi_\theta || \pi_{ref})$, where $\pi_{ref}$ is the frozen SFT model.

**Why does PPO for RLHF need 4 models in memory?** (1) Policy $\pi_\theta$ (being trained). (2) Reference $\pi_{ref}$ (frozen, for KL penalty). (3) Reward model $r_\phi$ (frozen). (4) Value model $V_\psi$ (the critic, being trained). For a 7B SFT model: 4 × 7B = 28B params in fp16 = 56 GB. Plus optimizer state and activations. Needs multiple H100s. DPO reduces this to 2 models (policy + reference).

**What is reward hacking and how do you prevent it?** Reward hacking: the policy finds inputs to the reward model that score high but are degenerate (repetitive outputs, gibberish, overly long responses). Prevention: (1) KL penalty — keeps policy close to SFT; (2) reward model ensembles — average multiple RMs; (3) length normalization — penalize long responses; (4) active RM retraining — update RM with new preferences.

**How does the KL penalty work in RLHF?** The objective is $r(x,y) - \beta \log(\pi_\theta(y|x) / \pi_{ref}(y|x))$. The KL term $\beta \log(\pi_\theta / \pi_{ref})$ penalizes the policy for drifting from the reference. $\beta$ controls the strength: too low → reward hacking; too high → no learning. The KL is computed per-token, accumulated over the response.

**Why did DPO replace PPO for most open-source alignment?** PPO is finicky (4 models, tuning-sensitive, weeks to converge, hard to debug). DPO is simpler (2 models, stable, hours, standard supervised learning). DPO quality is comparable to PPO for most use cases. PPO survives at frontier labs where every bit of quality matters and they have the compute to tune it.

**What is RLAIF and how does it differ from RLHF?** RLAIF (Constitutional AI) replaces human preference labels with AI-generated labels. A strong LLM (e.g., Claude) evaluates which response is better, providing the preference signal. This removes the need for human labelers, making alignment scalable. The rest of the pipeline (reward model + PPO, or DPO) is the same.

## See also

Related notes across alignment and fine-tuning:

- [[Training and Adaptation MOC]] — orientation for training and adaptation
- [[DPO Derivation]] — the simpler alternative
- [[Proximal Policy Optimization]] — the PPO mechanics this pipeline relies on
- [[Instruction Tuning and Chat Templates]] — the SFT stage and the reference model
- [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]] — parameter-efficient fine-tuning usable within RLHF
