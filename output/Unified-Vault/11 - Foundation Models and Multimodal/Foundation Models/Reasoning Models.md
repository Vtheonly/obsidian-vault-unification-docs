---
title: Reasoning Models
type: concept
aliases: ["Reasoning Models", "Reasoning Models (o1, R1)", "reasoning LLMs", "thinking models", "test-time compute models", "o1", "o3", "DeepSeek-R1", "R1"]
tags: [foundation-models, reasoning-models, test-time-compute, verifiable-rewards, grpo, agents]
sources: ["03 - Reasoning Models (o1, R1)"]
created_index: 5
---

> [!info] TL;DR
> Reasoning models (OpenAI o1/o3, DeepSeek-R1, Claude extended thinking, Gemini 2.5) are LLMs trained to produce a long internal chain-of-thought before answering. They spend more compute at inference ("test-time compute scaling") to solve harder problems, and they are SOTA on math, coding, and multi-step reasoning in 2025–2026.

Reasoning models are large language models that think before they answer: instead of emitting a response immediately, they generate a long internal chain-of-thought (CoT) and only then produce the final answer, converting extra inference-time compute into accuracy on hard problems. The architecture is an ordinary decoder-only Transformer — what changes is the training recipe (reinforcement learning on rewards that can be checked objectively) and the inference pattern (long thinking). This note covers the major released models, the training recipe in detail, the test-time compute scaling law, and the cost, latency, routing, and distillation patterns that decide where reasoning models belong in a production system. See [[Foundation Models and Multimodal MOC]] for the surrounding foundation-model family.

## What makes a reasoning model

A reasoning model is a standard LLM (decoder-only Transformer) plus three things:

1. **Training to produce long CoT**: RL on verifiable-reward signals (math, code) or process-reward models.
2. **Inference-time "thinking"**: the model generates a hidden chain-of-thought before the final answer.
3. **Higher test-time compute**: more tokens generated = more compute = better answers (for hard problems).

The architecture is unchanged from a regular LLM. The training and inference pattern differ — and those two differences explain everything else in this note.

## The major reasoning models

### OpenAI o1 / o3 (Sep 2024 – 2025)

o1 (Sep 2024) was the first major reasoning model: an internal chain-of-thought hidden from the user, and SOTA on math, coding, and science. o1-pro is the variant with a higher compute budget per query. o3 (Dec 2024 / Jan 2025) is significantly stronger — frontier on ARC-AGI, math olympiad, and competitive programming — while o3-mini is smaller, cheaper, and near-o1 quality.

The training recipe behind the family: RL with verifiable rewards (math correctness, code passing tests) plus a process reward model that rewards correct intermediate steps. The CoT is hidden from users (only a summary is shown) — OpenAI cites safety and competitive reasons.

### DeepSeek-R1 (Jan 2025)

DeepSeek-R1 is the open-source reasoning model from DeepSeek, based on DeepSeek-V3 (a mixture-of-experts model; see [[Mixture of Experts]]). Its training recipe runs in two steps:

1. **R1-Zero**: pure RL on verifiable rewards, no SFT first. The model spontaneously learns to produce long CoT.
2. **R1**: add SFT on cold-start data, then RL. Better readability, formatting, and safety.

R1's full training details and weights are open. This was a major moment — it showed that the reasoning-model recipe was reproducible without OpenAI's full pipeline.

### Claude extended thinking (Anthropic, Feb 2025)

Claude 3.7+ supports an "extended thinking" mode: the model produces a visible CoT before answering. Users can see the thinking (unlike OpenAI's hidden CoT) and even guide it.

### Gemini thinking mode (Google, Mar 2025)

Gemini 2.5+ has a similar "thinking" mode. It is available in the API and in the consumer Gemini app.

## How to use reasoning models

### When to use

Reasoning models earn their cost when the task itself is hard or multi-step:

- **Math olympiad, competitive programming, scientific reasoning** — these models are dramatically better.
- **Multi-step planning** — agents that need to think through complex sequences.
- **Hard debugging** — code that requires deep understanding.
- **Research-style questions** — open-ended problems needing exploration.

### When not to use

The mirror image also holds, and overspending here is the most common mistake:

- **Simple Q&A** — overkill; a regular LLM is faster and cheaper.
- **High-volume / low-latency** — reasoning models are slow (30s+ per query) and expensive.
- **Tasks where standard LLMs are already SOTA** — translation, summarization, basic classification.

## The training recipe in detail

The reasoning-model recipe (o1, R1, o3) differs from standard instruction tuning in three key ways, and understanding the recipe clarifies why these models suddenly outperform much larger non-reasoning models on math and code. The policy-gradient machinery underneath is the one covered in [[RLHF with PPO]] and [[Proximal Policy Optimization]]; what changes is the reward signal and the length of the rollouts.

### Verifiable rewards (the key innovation)

Standard RLHF uses a learned reward model trained on human preference data. This works for "is response A better than response B" but is unreliable for math/code because human labelers often can't tell which math proof is correct, and reward models can be gamed (reward hacking) — they reward confident-sounding wrong answers.

Reasoning models use **verifiable rewards**: a function that checks correctness objectively:

- Math: does the final answer match the known answer?
- Code: do the unit tests pass?
- Logic puzzles: does the solution satisfy all constraints?

The reward is binary (1 if correct, 0 if wrong) or graded (partial credit for some tests passing). This gives a clean, unhackable signal.

### Process reward models (PRMs) — sometimes

For some reasoning models (especially o1, plausibly), an additional **process reward model** evaluates intermediate reasoning steps, not just the final answer. A PRM is trained on (step, correctness) labels from human annotators or from rollouts that lead to correct/incorrect final answers.

PRMs help when the model is "on the wrong track" early in a long CoT — the PRM can detect this and the policy can correct course. They are expensive to train (they need step-level labels) and not always used; R1 uses outcome-only rewards and still works.

### RL on long rollouts

The actual RL training samples long CoT trajectories (10K-100K tokens) from the model, scores them with the verifiable reward, and updates the policy. This is technically PPO or GRPO (Group Relative Policy Optimization, DeepSeek's variant).

GRPO simplifies PPO by:

- Sampling N completions per prompt (typically 4-16).
- Computing rewards for each.
- Using the **group baseline** (mean reward of the N samples) as the value estimate.
- No separate value model needed (PPO needs a value model; GRPO doesn't).

This makes GRPO cheaper than PPO and more stable for the binary-reward setting common in reasoning training.

### Cold start vs pure RL

R1-Zero showed that pure RL (no SFT first) on a base model can produce emergent CoT. But R1-Zero had readability issues — the CoT was sometimes incoherent or repeated. R1 (full) uses a **cold start**: a small amount of high-quality CoT data is used for SFT before RL, which produces a more polished final model.

The o1/o3 training recipe is not fully disclosed; the community consensus is that they use SFT on high-quality reasoning data + RL on verifiable rewards + (possibly) PRMs.

## Test-time compute scaling law

Snell et al. (2024) showed that test-time compute scales: more thinking → better answers, with diminishing returns. The relationship is approximately:

$$\text{Accuracy} \propto \log(\text{test-time tokens})$$

So doubling the thinking budget gives a roughly constant accuracy improvement. This means that for easy problems, a small thinking budget suffices; that for hard problems, the budget matters a lot — going from 1K to 100K thinking tokens can take accuracy from 30% to 80%; and that for problems where the user has a budget, you can trade cost for accuracy.

The practical implication: most production deployments of reasoning models use **adaptive thinking budgets** — a short budget for easy queries, a long budget for hard ones. This requires a classifier or the user to specify difficulty.

## Worked example: DeepSeek-R1 via the OpenAI-compatible API

DeepSeek exposes R1 through an OpenAI-compatible endpoint, so the standard client works with a different base URL and model name:

```python
from openai import OpenAI
client = OpenAI(api_key="your-key", base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-reasoner",  # R1
    messages=[{"role": "user", "content": "Prove that the sum of two odd numbers is even."}],
)

# The response has both reasoning_content (the CoT) and content (the answer)
print("Reasoning:")
print(response.choices[0].message.reasoning_content)
print("\nAnswer:")
print(response.choices[0].message.content)
```

The response object separates `reasoning_content` (the CoT) from `content` (the answer), which is the visible-thinking API design in action: you can inspect or log the reasoning rather than receiving only a summary.

## Why this matters

Reasoning models represent the **biggest capability jump of 2024–2025**. They open up tasks previously inaccessible to LLMs (competition math, complex code refactoring, scientific problem-solving). The recipe (RL on verifiable rewards) is **reproducible** — R1 proved this, and open-source reasoning models are now viable. Test-time compute scaling is a **new dimension** of capability: instead of just training bigger models, you can also let models think longer at inference. And for agents, reasoning models enable longer horizons and more reliable tool use.

## Production implications

Five implications dominate real deployments:

- **Cost**: reasoning models are 5–50x more expensive per query than standard LLMs (due to long CoTs).
- **Latency**: responses take 10s–2min. Not suitable for real-time chat; suitable for batch / async tasks.
- **Don't prompt with CoT** — reasoning models do their own CoT. Just ask the question directly.
- **For agents**, reasoning models improve planning but cost more. Use selectively for hard planning steps.
- **Hybrid systems**: route easy queries to a standard LLM, hard queries to a reasoning model. Cost optimization.

## When reasoning models fail

Reasoning models are not universally better. They fail on **tasks with no verifiable answer**: open-ended writing, brainstorming, emotional support — the long CoT adds nothing and may make the output more rigid. They fail on **tasks where the model's training data was already sufficient**: translation between common languages, simple factual Q&A, basic classification — the CoT overhead is pure cost. They fail on **tasks requiring multiple agent turns**: a single long CoT is not the same as a multi-step agent that observes intermediate results, and for tool-use with external state, agents beat reasoning models. And they fail on **tasks with tight latency budgets**: a 60-second response is unacceptable for real-time chat, autocomplete, or interactive UI.

The hybrid pattern (route easy queries to a fast model, hard queries to a reasoning model) is the dominant production pattern in 2026.

## Detailed cost analysis

Concrete cost comparison (2026 pricing, approximate):

| Model                | Input $/1M tokens | Output $/1M tokens | Avg CoT length | Cost per query (avg) |
|----------------------|-------------------|--------------------|----------------|----------------------|
| GPT-4o               | $2.50             | $10.00             | 0              | ~$0.005              |
| Claude 3.5 Sonnet    | $3.00             | $15.00             | 0              | ~$0.008              |
| Llama 3.1 70B (self) | ~$0.50            | ~$0.50             | 0              | ~$0.001              |
| o1-mini              | $3.00             | $12.00             | ~10K           | ~$0.12               |
| o1                   | $15.00            | $60.00             | ~30K           | ~$1.80               |
| o3-mini              | $3.00             | $12.00             | ~15K           | ~$0.18               |
| DeepSeek-R1          | $0.55             | $2.19              | ~20K           | ~$0.04               |

(Average query = 500 input tokens + CoT + 500 output tokens.)

Key observations:

- Reasoning models are 10-100× more expensive per query than standard LLMs.
- DeepSeek-R1 is dramatically cheaper than o1 because of (a) lower base prices and (b) MoE efficiency.
- The dominant cost is the CoT itself — 20K thinking tokens at $60/1M is $1.20 alone.
- For batch workloads, this is fine. For real-time chat, it's a non-starter for most use cases.

## Production patterns

### Pattern 1: router-based hybrid

```python
def route_query(query: str) -> str:
    if is_simple(query):  # classifier or rules
        return "gpt-4o"
    elif is_hard_reasoning(query):
        return "o3-mini"
    else:
        return "claude-3.5-sonnet"

model = route_query(user_query)
response = call_llm(model, user_query)
```

The router can be a small classifier, an LLM-as-judge, or rule-based on query length/keywords. This pattern typically reduces cost by 5-10× while preserving quality on hard queries.

### Pattern 2: caching verified answers

For math/code problems with verifiable answers, cache (query → answer) pairs. A user asking the same problem later gets the cached answer instantly, with no reasoning cost. This works well for educational platforms and coding tools.

### Pattern 3: reasoning model as planner

For agent systems, use a reasoning model only for the planning step (which is hard and benefits from long thinking), then execute the plan with a fast model. This combines the reasoning quality of o1 with the speed of Llama 3 for execution.

### Pattern 4: distillation to fast models

Train a smaller, faster model (Llama 3 8B) on the outputs of a reasoning model (R1). The distilled model learns to produce the answer directly, without the long CoT, but inherits some of the reasoning quality. This is the standard recipe for "reasoning-capable small models" in 2026.

## Common pitfalls

> [!warning]
> The four recurring mistakes: **forcing CoT in the prompt** (reasoning models do this themselves; extra CoT instructions can confuse them); **using reasoning models for everything** (10x cost for tasks where a standard LLM suffices); **trusting the CoT as explanation** (the CoT may not reflect actual computation — chain-of-thought unfaithfulness is a documented phenomenon, so treat visible reasoning as a clue, not an audit); and **forgetting that thinking is hidden in some APIs** (o1) — you can't see or guide the model's reasoning there.

## Relationship to other concepts

Reasoning models sit at the intersection of several threads. Test-time compute scaling is the formal scaling law behind the accuracy gains above. The underlying RL method is RLHF with PPO, and PPO itself is the policy gradient algorithm that GRPO simplifies. Chain-of-thought prompting is the technique that reasoning models internalize; tree-of-thoughts search with self-consistency is the non-RL approach to similar problems (sample several thoughts and vote). Reasoning models extend in-context learning with explicit thinking (see [[In-Context Learning]]). LoRA is used for distillation of reasoning models — the fine-tuning in pattern 4 is typically parameter-efficient — and DPO is a common follow-up when distilling (see [[DPO Derivation]] and [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]]).

## Interview questions

**What is a verifiable reward, and why is it critical for reasoning models?** A verifiable reward is a function that objectively checks answer correctness — math answer matches, code passes tests, logic puzzle satisfies constraints. It is critical because (1) human labelers can't reliably judge math/code correctness, (2) learned reward models can be gamed (reward hacking) by confident-sounding wrong answers, (3) the binary signal is unbiased, providing a clean gradient for RL.

**What is GRPO, and how does it differ from PPO?** Group Relative Policy Optimization (DeepSeek's variant) samples N completions per prompt, computes their rewards, and uses the group mean as the baseline. Unlike PPO, GRPO doesn't need a separate value model — the group statistics serve as the baseline. This is simpler, cheaper, and more stable for the binary-reward setting common in reasoning training. PPO is more general; GRPO is optimized for the reasoning case.

**Why does R1-Zero's emergent CoT matter?** It showed that you don't need supervised CoT data to train a reasoning model. Pure RL on verifiable rewards, starting from a base model, spontaneously produces long CoT. This was surprising — the field assumed you needed to teach the model to "think" with SFT first. R1-Zero proved the recipe was simpler than expected, opening the door to cheap replication.

**How do you choose between o1, o3-mini, and a standard LLM for a query?** Route by difficulty. Simple queries (translation, factual lookup, basic Q&A) → standard LLM (cheaper, faster). Hard reasoning (math competition, multi-step debugging, scientific proof) → o3-mini or R1 (cheaper than o1, near-o1 quality). Use o1 only for the hardest problems where the marginal quality justifies 10× cost. The router can be a small classifier or an LLM-as-judge.

**Why are reasoning models' CoTs sometimes hidden from users?** Three reasons cited by OpenAI: (1) competitive — disclosing the CoT helps competitors replicate, (2) safety — the CoT may reveal capabilities the model has but shouldn't expose, (3) user experience — long CoTs are hard to read and the user only needs the answer. Anthropic and DeepSeek show the CoT (or a summary), arguing that transparency helps debugging and trust. The trade-off is open.

**How would you distill a reasoning model into a smaller, faster model?** Generate (prompt, full CoT, answer) triples from the reasoning model on a large dataset. Fine-tune a smaller model (e.g., Llama 3 8B) on these triples with SFT. The distilled model learns to produce the answer with a much shorter CoT (or none), inheriting some reasoning quality. Optionally, follow with DPO on (correct, incorrect) pairs from the distilled model's own samples. This typically gives 80% of the reasoning model's quality at 1/10 the cost.

**Why is test-time compute scaling a "new dimension" of capability?** Pre-2024, capability came from (1) more parameters, (2) more training data, (3) more training compute. Test-time compute adds a fourth: more inference compute. The Snell et al. scaling law shows this dimension has its own scaling curve, and it can substitute for parameter scaling — a smaller model with more thinking can beat a larger model with less thinking, on hard problems. This opens a new design space for AI systems.

## Further reading

- OpenAI (2024), *Learning to Reason with LLMs* (o1 announcement).
- DeepSeek-AI (2025), *DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning*.
- Snell et al. (2024), *Scaling LLM Test-Time Compute Optimally Can Be More Effective Than Scaling Model Parameters*.

## See also

- [[Foundation Models and Multimodal MOC]] — the area orientation for this family.
- [[Code Models]] — sibling capability-specific foundation models.
- [[Multimodal Foundation Models]] — the multimodal branch of the family.
- [[In-Context Learning]] — reasoning models extend ICL with explicit thinking.
- [[RLHF with PPO]] — the underlying RL method.
- [[Proximal Policy Optimization]] — the policy gradient algorithm behind PPO and GRPO.
- [[DPO Derivation]] — preference optimization used after distillation.
- [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]] — parameter-efficient fine-tuning used for distillation of reasoning models.
- [[Cost Optimization]] — the routing and caching patterns in production context.
- [[LLM-as-Judge Evaluation]] — judge models double as query routers.
- [[Chain of Thought]]
- [[Test-Time Compute Scaling]]
