---
title: Proximal Policy Optimization
type: concept
aliases:
  - PPO
  - PPO Deep Treatment
  - Clipped Surrogate Objective
tags:
  - reinforcement-learning
  - ppo
  - rlhf
  - clipped-surrogate-objective
  - trust-region-methods
  - policy-gradient
  - actor-critic
sources:
  - "10 - PPO Deep Treatment"
created_index: 20
---

Proximal Policy Optimization (Schulman et al. 2017) is the most-used policy gradient algorithm in modern RL, and its key innovation is simple to state: clip the policy update to prevent destructively large steps. PPO is the algorithm behind RLHF — the alignment method that produced ChatGPT — and it is the endpoint of a chain of ideas that runs through [[Markov Decision Processes and Bellman Equations]], [[Q-Learning and Deep Q Networks]], and especially [[Policy Gradients and Actor Critic]], whose advantage estimates PPO consumes directly. This note covers the clipped surrogate objective in detail, the full loss, the algorithm, and PPO's central role in LLM alignment.

## The problem PPO solves

Vanilla policy gradients and earlier trust-region methods each have issues:

- **REINFORCE / actor-critic**: high variance, and no constraint on how much the policy can change — a single bad update can collapse the policy entirely.
- **TRPO** (Trust Region Policy Optimization, Schulman et al. 2015): constrains the KL divergence between the old and new policy. Stable, but the constraint requires solving a constrained (second-order) optimization — slow and complex.

PPO's idea: **clip the policy ratio** to keep updates small, without the expensive second-order machinery of TRPO. The result is much simpler, almost as stable, and much faster.

## The policy ratio

The probability ratio between the new and old policy:

$$
r_t(\theta) = \frac{\pi_\theta(a_t \mid s_t)}{\pi_{\theta_{\text{old}}}(a_t \mid s_t)}
$$

The standard policy gradient can be written as $\nabla J = \mathbb{E}[r_t(\theta) \hat{A}_t]$. If we update $\theta$ too aggressively, $r_t$ can blow up, and the new policy diverges from the old one — precisely the failure mode PPO is designed to prevent.

## The clipped surrogate objective

PPO replaces the standard policy gradient objective with a **clipped** version:

$$
L^{\text{CLIP}}(\theta) = \mathbb{E}_t \left[ \min\left( r_t(\theta) \hat{A}_t, \, \text{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon) \hat{A}_t \right) \right]
$$

Where:

- $\hat{A}_t$ is the estimated advantage (typically GAE — see [[Policy Gradients and Actor Critic]]).
- $\epsilon$ is the clip range (typically 0.1–0.2).
- $\min$ picks the more conservative (pessimistic) of the two terms.

### What the clipping does

Case 1: $\hat{A}_t > 0$ (the action was better than expected):

- We want to increase $\pi_\theta(a_t \mid s_t)$ — push $r_t$ up.
- Clipping at $1 + \epsilon$ caps the ratio. Past the cap, the gradient is 0 — no further incentive to increase the probability.

Case 2: $\hat{A}_t < 0$ (the action was worse than expected):

- We want to decrease $\pi_\theta(a_t \mid s_t)$ — push $r_t$ down.
- Clipping at $1 - \epsilon$ caps the decrease.

The $\min$ ensures the surrogate is a **lower bound** on the true objective. PPO is pessimistic — it never overestimates the improvement an update will bring, which is exactly the conservatism that keeps training stable.

## The full PPO loss

PPO combines three terms:

$$
L^{\text{PPO}}(\theta) = L^{\text{CLIP}}(\theta) - c_1 L^{\text{VF}}(\theta) + c_2 S[\pi_\theta](s_t)
$$

1. **Clipped policy loss** $L^{\text{CLIP}}$ (maximize).
2. **Value function loss** $L^{\text{VF}} = (V_\theta(s_t) - G_t)^2$ (minimize). This is the critic.
3. **Entropy bonus** $S[\pi_\theta]$ (maximize). Encourages exploration.

Here $c_1 \approx 0.5$ and $c_2 \approx 0.01$ are typical. The equation is written as a maximization: the clipped policy loss and the entropy bonus enter positively (both are to be maximized), while the value-function loss — the critic regressing toward the observed returns — is subtracted, so maximizing $L^{\text{PPO}}$ drives it down. In implementations the whole expression is negated and handed to a minimizer, as the algorithm below shows.

## The PPO algorithm

The overall loop collects trajectories with the current policy, computes GAE advantages, then runs several epochs of minibatch SGD over the collected data with the clipped objective:

```python
# Pseudo-code
for iteration in range(num_iterations):
    # 1. Collect trajectories with current policy
    trajectories = []
    for _ in range(num_rollout_steps):
        s = env.reset()
        for t in range(horizon):
            a, log_prob, v = policy.act(s)
            s_next, r, done = env.step(a)
            trajectories.append((s, a, r, s_next, done, log_prob, v))
            s = s_next
    
    # 2. Compute advantages (GAE)
    advantages = compute_gae(trajectories, gamma=0.99, lam=0.95)
    returns = advantages + values  # for value loss target
    
    # 3. Multiple epochs of SGD on the collected data
    for epoch in range(num_epochs):  # typically 4-10
        for minibatch in make_minibatches(trajectories, batch_size=64):
            # New policy's log prob and value
            new_log_prob = policy.log_prob(minibatch.states, minibatch.actions)
            new_value = policy.value(minibatch.states)
            
            # Ratio
            ratio = exp(new_log_prob - minibatch.old_log_prob)
            
            # Clipped surrogate
            surr1 = ratio * minibatch.advantages
            surr2 = clamp(ratio, 1-eps, 1+eps) * minibatch.advantages
            policy_loss = -min(surr1, surr2).mean()
            
            # Value loss
            value_loss = mse(new_value, minibatch.returns)
            
            # Entropy bonus
            entropy = policy.entropy(minibatch.states).mean()
            
            loss = policy_loss + 0.5 * value_loss - 0.01 * entropy
            
            opt.zero_grad()
            loss.backward()
            clip_grad_norm_(policy.parameters(), max_norm=0.5)
            opt.step()
```

Note the reuse of data across epochs — this is the "slightly off-policy" wrinkle that the ratio and the clip make safe, and the gradient-norm clipping is an additional stabilization on top.

## Why PPO won

- **Simple to implement** — just SGD with a clipped objective. No second-order methods.
- **Stable** — the clip prevents the policy from changing too much per step.
- **Good performance** — not always SOTA, but reliably good across many domains.
- **Sample-efficient enough** — for RLHF, where each rollout is expensive, PPO's sample efficiency is acceptable.
- **Parallelizable** — collecting rollouts can be done in parallel across many workers.

OpenAI adopted PPO as their default RL algorithm in 2017, and it became the de facto standard for RLHF.

## PPO for RLHF

In RLHF, the setup is:

- **State**: the prompt + tokens generated so far.
- **Action**: the next token.
- **Policy**: the LLM $\pi_\theta(\text{next token} \mid \text{prompt, generated})$.
- **Reward**: from a trained reward model $r_\phi(\text{prompt, response})$ — typically computed at the end of the response.
- **Reference policy**: the SFT model $\pi_{\text{ref}}$, frozen. Used to compute a KL penalty.

### The RLHF-PPO objective

$$
\max_\theta \mathbb{E} \left[ r_\phi(x, y) - \beta \log \frac{\pi_\theta(y \mid x)}{\pi_{\text{ref}}(y \mid x)} \right]
$$

The KL term $\beta \log(\pi_\theta / \pi_{\text{ref}})$ prevents the policy from drifting too far from the SFT model, which would otherwise cause reward hacking — the model exploits bugs in the reward model rather than genuinely improving.

In practice:

- Per-token KL is computed and added to the reward: $r_t = -\beta (\log \pi_\theta(a_t \mid s_t) - \log \pi_{\text{ref}}(a_t \mid s_t))$, with a final reward of $r_\phi(x, y)$ at the last token.
- PPO then operates on this modified reward signal.

## Key hyperparameters

The knobs that most affect PPO training, with typical values and their effects:

| Hyperparameter        | Typical Value     | Effect                                       |
|-----------------------|-------------------|----------------------------------------------|
| $\epsilon$ (clip)     | 0.1 – 0.2         | Smaller = more conservative updates.         |
| $\gamma$ (discount)   | 0.99              | Lower = more myopic.                         |
| $\lambda$ (GAE)       | 0.95              | Trades bias/variance in advantage estimate.  |
| Epochs per batch      | 4 – 10            | More = more updates per rollout, but stale.  |
| Minibatch size        | 32 – 256          | Standard SGD consideration.                  |
| $\beta$ (KL in RLHF)  | 0.01 – 0.5        | Higher = stays closer to reference.          |
| Learning rate         | 1e-5 – 1e-4 (RLHF)| Much lower than pretraining.                 |
| Entropy coefficient   | 0.01              | Encourages exploration.                      |

The learning rate deserves special mention in the RLHF setting: it runs one to two orders of magnitude below pretraining rates, reflecting how fragile an already-competent language model is to aggressive policy updates. The general tuning considerations behind these knobs are covered in [[Optimizers and Learning Rate Schedulers]].

## Why this matters for modern AI

- **PPO is what made ChatGPT possible.** The InstructGPT paper (Ouyang et al. 2022) used PPO to align GPT-3 with human preferences. Every major aligned LLM (GPT-4, Claude, Gemini, Llama-Instruct) used PPO or its successor at some point.
- DPO was invented as a simpler alternative to PPO-based RLHF. As of 2026, both coexist — PPO at frontier labs, DPO in open-source.
- The clipped surrogate is a general technique — it appears in many algorithms beyond PPO.

## Production implications

- **PPO is expensive** for RLHF: you need 4 models in memory (policy, reference, reward, value). For a 7B model, that's ~28 GB just for weights (in fp16).
- **Sample efficiency is poor** — RLHF PPO needs millions of token generations. Cost adds up fast.
- **Stability is hard** — KL coefficients, learning rates, and clip ranges all need careful tuning.
- **For most teams, DPO is now preferred** — simpler, cheaper, comparable quality.
- **For frontier training**, PPO + reward model still gives the best results when you can afford the engineering.

## Common pitfalls

- **Clip range too large** — updates become unstable.
- **KL coefficient too low (RLHF)** — reward hacking; the model produces gibberish that scores high on the reward model.
- **KL coefficient too high (RLHF)** — no learning; the model stays at SFT.
- **Forgetting to detach the value target** — the value loss will backprop through itself, breaking training.
- **Old log probs not detached** — gradients flow through the ratio's denominator, which shouldn't happen.
- **Reward model not frozen** — the reward model should never update during PPO.
- **Wrong advantage normalization** — many implementations normalize advantages to mean 0, std 1 per batch. Don't forget.

## Further reading

- Schulman et al. (2017), *Proximal Policy Optimization Algorithms* — the PPO paper.
- Schulman et al. (2015), *Trust Region Policy Optimization* — PPO's predecessor.
- Ouyang et al. (2022), *Training language models to follow instructions with human feedback* (InstructGPT / RLHF).
- OpenAI Spinning Up's PPO implementation: https://spinningup.openai.com/

## See also

- [[Markov Decision Processes and Bellman Equations]]
- [[Q-Learning and Deep Q Networks]]
- [[Policy Gradients and Actor Critic]]
- [[Machine Learning MOC]]
