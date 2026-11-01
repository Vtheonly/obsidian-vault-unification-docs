---
title: Policy Gradients and Actor Critic
type: concept
aliases:
  - Policy Gradients and Actor-Critic
  - Actor Critic
  - Policy Gradient Methods
  - REINFORCE
tags:
  - reinforcement-learning
  - policy-gradient
  - actor-critic
  - reinforce
  - advantage-function
  - generalized-advantage-estimation
  - on-policy-learning
sources:
  - "09 - Policy Gradients and Actor Critic"
created_index: 19
---

Policy gradient methods directly optimize the policy $\pi_\theta$ via gradient ascent on expected return, rather than learning a value function first and deriving a policy from it. Actor-critic methods combine a policy (the "actor") with a value function (the "critic") to reduce the variance of the raw gradient estimate, which is what makes the approach practical. PPO, the algorithm behind RLHF, is an actor-critic method, which makes this note the direct prerequisite for [[Proximal Policy Optimization]]; it builds on the value functions of [[Markov Decision Processes and Bellman Equations]] and stands in contrast to the value-based route taken in [[Q-Learning and Deep Q Networks]].

## Why policy-based methods

Value-based methods such as DQN work well for discrete actions but struggle in three ways:

- Continuous action spaces — you can't `max` over a continuous set.
- Stochastic policies — necessary for some games, e.g., rock-paper-scissors, where any deterministic policy is exploitable.
- Indirect policy learning — Q-learning learns $Q$ and only then derives $\pi$, an extra step that can discard useful structure.

Policy-based methods sidestep all three limitations by parameterizing $\pi_\theta$ directly and optimizing $\theta$ on the expected return. The policy itself becomes the object of learning.

## The policy gradient theorem

The expected return under policy $\pi_\theta$:

$$
J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta} \left[ \sum_{t=0}^{T} \gamma^t r_t \right]
$$

The policy gradient theorem (Sutton et al. 2000) gives the gradient of this objective:

$$
\nabla_\theta J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta} \left[ \sum_{t=0}^{T} \nabla_\theta \log \pi_\theta(a_t \mid s_t) \, G_t \right]
$$

where $G_t = \sum_{t'=t}^{T} \gamma^{t'-t} r_{t'}$ is the return from step $t$.

### Intuition

Each factor in the sum has a distinct role:

- $\nabla_\theta \log \pi_\theta(a_t \mid s_t)$ is the direction that increases the probability of taking action $a_t$ in state $s_t$.
- $G_t$ weights this direction by how good the outcome was.
- The gradient pushes up the probability of actions that led to high returns, and down for low returns.

The $\log$ comes from the **score function estimator** — a general trick for differentiating through an expectation. The resulting algorithm is equivalent to REINFORCE (Williams, 1992).

## REINFORCE: the vanilla policy gradient

The simplest policy gradient algorithm is a three-step loop:

1. Run policy $\pi_\theta$ in the environment to collect a trajectory $\tau = (s_0, a_0, r_0, s_1, \ldots)$.
2. Compute returns $G_t$.
3. Update: $\theta \leftarrow \theta + \alpha \sum_t \nabla_\theta \log \pi_\theta(a_t \mid s_t) \, G_t$.

### Problems with REINFORCE

The algorithm is correct but barely usable:

- **Huge variance**: $G_t$ is the sum of many noisy rewards, so gradient estimates are extremely noisy.
- **Sample inefficient**: data is thrown away after one update.
- **No credit assignment**: it is hard to tell which actions in a trajectory actually caused the eventual return.

Everything that follows — baselines, the advantage function, actor-critic, GAE — is an attempt to fix these problems without breaking the estimator's correctness.

## Reducing variance: baselines

Subtract a baseline $b(s_t)$ from the return:

$$
\nabla_\theta J(\theta) = \mathbb{E} \left[ \sum_t \nabla_\theta \log \pi_\theta(a_t \mid s_t) (G_t - b(s_t)) \right]
$$

The baseline doesn't bias the gradient — this is a mathematical identity, not an approximation — but it can dramatically reduce variance. The intuition is that the baseline removes the "how good is this state on average" component from the return, leaving only the action's marginal contribution. The most common baseline is $V^\pi(s_t)$, the value of the state. Subtracting the state's value from the action's value yields the **advantage** $A^\pi(s_t, a_t) = Q^\pi(s_t, a_t) - V^\pi(s_t)$.

## The advantage function

$$
A^\pi(s, a) = Q^\pi(s, a) - V^\pi(s)
$$

The advantage has a clean interpretation:

- $A > 0$: action $a$ is better than average in state $s$ → push its probability up.
- $A < 0$: action $a$ is worse than average → push its probability down.

Using $A$ instead of $G$ is the key variance reduction that makes policy gradients practical. It converts the question from "was the outcome good?" (noisy, state-dependent) to "was this action better than what the policy usually does here?" (much tighter around zero).

## Actor-critic

Actor-critic methods maintain **two** models simultaneously:

- **Actor**: the policy $\pi_\theta$.
- **Critic**: a value estimator $V_\phi$ (or $Q_\phi$).

The critic provides the baseline for the actor's gradient, and both are trained at the same time. This is the fundamental architecture of modern policy-gradient systems: the actor learns what to do, the critic learns how good things are, and each stabilizes the other.

### A2C and A3C

**Advantage Actor-Critic** pairs the two networks in the simplest possible way: the critic learns $V_\phi$ via TD learning, and the actor updates with the advantage estimate $\hat{A}_t = r_t + \gamma V_\phi(s_{t+1}) - V_\phi(s_t)$ — the TD error used directly as the advantage.

**A3C** (Asynchronous Advantage Actor-Critic, Mnih et al. 2016) runs multiple workers in parallel, asynchronously updating shared actor and critic parameters. It was the first major actor-critic success.

**A2C** is the synchronous version; it is often as good as A3C and simpler, which is why many practitioners prefer it.

### Generalized advantage estimation

GAE (Generalized Advantage Estimation) is a more sophisticated advantage estimate that interpolates between one-step TD and Monte Carlo returns:

$$
\hat{A}_t^{(1)} = \delta_t
$$
$$
\hat{A}_t^{(2)} = \delta_t + \gamma \lambda \delta_{t+1}
$$
$$
\hat{A}_t^{(\infty)} = \sum_{l=0}^{\infty} (\gamma \lambda)^l \delta_{t+l}
$$

where $\delta_t = r_t + \gamma V_\phi(s_{t+1}) - V_\phi(s_t)$ is the TD error. The hyperparameter $\lambda \in [0, 1]$ trades off bias (low $\lambda$) and variance (high $\lambda$) — the same tension that pervades machine learning, discussed in [[Bias Variance Tradeoff]] — and $\lambda = 0.95$ is a common default. GAE is standard in modern actor-critic methods, including PPO.

## On-policy versus off-policy learning

- **On-policy**: train on data collected by the current policy. Old data must be discarded after each update. PPO is on-policy.
- **Off-policy**: train on data from any policy (e.g., via a replay buffer). More sample-efficient but harder to stabilize. DQN and SAC are off-policy.

On-policy methods are simpler and more stable but sample-inefficient. The RLHF use case is on-policy because we want to improve the current LLM, not old versions of it — collecting fresh trajectories from the model being trained is exactly what the on-policy setting assumes.

## Worked example: REINFORCE with a baseline

The following PyTorch sketch implements the full actor-critic pattern in miniature: a policy network with a softmax head, a value network, and an update that computes advantages as returns minus detached values, takes a policy-gradient step, and regresses the critic toward the returns.

```python
class Policy(nn.Module):
    def __init__(self, state_dim, n_actions):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, 64), nn.ReLU(),
            nn.Linear(64, n_actions),
        )
    def forward(self, s):
        return F.softmax(self.net(s), dim=-1)

class Value(nn.Module):
    def __init__(self, state_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, 64), nn.ReLU(),
            nn.Linear(64, 1),
        )
    def forward(self, s):
        return self.net(s).squeeze(-1)

policy = Policy(state_dim, n_actions)
value = Value(state_dim)
opt_pi = torch.optim.Adam(policy.parameters(), lr=1e-3)
opt_v = torch.optim.Adam(value.parameters(), lr=1e-3)

def update(states, actions, returns):
    # Advantage
    v = value(states)
    advantages = returns - v.detach()
    
    # Policy gradient
    log_probs = torch.log(policy(states).gather(1, actions.unsqueeze(1)).squeeze(1))
    pi_loss = -(log_probs * advantages).mean()
    opt_pi.zero_grad(); pi_loss.backward(); opt_pi.step()
    
    # Value update
    v_loss = F.mse_loss(v, returns)
    opt_v.zero_grad(); v_loss.backward(); opt_v.step()
```

Two details deserve attention. The advantages are computed against `v.detach()`, so the policy gradient does not flow into the critic — the critic is a pure baseline here. And the policy loss is the negative of $(\log \pi) \cdot A$ averaged over the batch, because optimizers minimize while policy gradients ascend.

## Why this matters for modern AI

- **PPO is an actor-critic method.** Without understanding policy gradients and advantage, you can't understand PPO — and without PPO, you can't understand RLHF.
- The **advantage function** is a central concept that recurs in modern alignment (e.g., DPO uses log-ratio advantages).
- The on-policy setting is what makes LLM alignment tractable — we can collect fresh trajectories from the current model and improve it.

## Production implications

- Pure policy gradient methods (REINFORCE) are too high-variance for production. Always use actor-critic with GAE.
- For LLMs, the actor-critic machinery culminates in [[Proximal Policy Optimization]] and its use in RLHF.
- For game-playing and robotics, more advanced methods (PPO, SAC, MuZero) are standard.

## Common pitfalls

- **No baseline** — REINFORCE without a baseline is too noisy to be useful.
- **Wrong advantage sign** — flipping the sign makes the model worse instead of better.
- **Off-policy data with an on-policy algorithm** — PPO can use a small amount of stale data (via importance sampling), but going too far off-policy breaks it.
- **Critic learning too fast or too slow** — the critic must be reasonably accurate for the actor's gradients to be meaningful. Tune the critic's learning rate separately.

## Further reading

- Sutton et al. (2000), *Policy Gradient Methods for Reinforcement Learning with Function Approximation*.
- Williams (1992), *Simple Statistical Gradient-Following Algorithms for Connectionist Reinforcement Learning* (REINFORCE).
- Schulman et al. (2016), *High-Dimensional Continuous Control Using Generalized Advantage Estimation* (GAE).
- Mnih et al. (2016), *Asynchronous Methods for Deep Reinforcement Learning* (A3C).

## See also

- [[Markov Decision Processes and Bellman Equations]]
- [[Q-Learning and Deep Q Networks]]
- [[Proximal Policy Optimization]]
- [[Machine Learning MOC]]
