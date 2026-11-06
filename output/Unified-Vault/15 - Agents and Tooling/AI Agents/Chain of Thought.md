---
title: Chain of Thought
type: concept
aliases: ["Chain-of-Thought", "CoT", "chain-of-thought prompting", "CoT prompting", "step-by-step reasoning"]
tags: [agents, reasoning, chain-of-thought, cot, prompting]
sources: ["02 - Chain-of-Thought"]
created_index: 3
---

Chain-of-Thought (CoT) prompting asks the model to "think step by step" before answering instead of going straight to a final answer. This simple change dramatically improves performance on multi-step reasoning tasks such as math, logic, and code, and it is the foundation of all modern agent reasoning patterns. This note covers the technique and its variants, the theories for why it works, when it helps and when it does not, and how it evolved into the trained reasoning models of 2024–2025.

## The idea

Standard prompting asks for a direct answer:

> Q: A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost?
> A: $0.10

(Wrong — but this is what most people, and un-CoT'd models, say.)

Chain-of-Thought prompting asks for reasoning first:

> Q: A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost?
> A: Let me think step by step. The bat costs $1.00 more than the ball, so if the ball costs $x$, the bat costs $x + 1.00$. Together they cost $x + (x + 1.00) = 2x + 1.00 = 1.10$. So $2x = 0.10$, $x = 0.05$. The ball costs $0.05$.

(Now correct.)

Wei et al. (2022) showed this simple trick dramatically improves performance on math, logic, and multi-step reasoning benchmarks. On GSM8K (grade-school math), PaLM 540B jumped from 18% to 57% with CoT.

## Variants

### Zero-shot CoT

Just append "Let's think step by step." to the prompt. Surprisingly effective:

```python
prompt = f"{question}\n\nLet's think step by step."
```

### Few-shot CoT

Provide examples that include reasoning, not just answers:

```text
Q: Roger has 5 tennis balls. He buys 2 cans of 3 balls each. How many balls does he have?
A: Roger starts with 5. He buys 2 cans × 3 balls = 6. Total: 5 + 6 = 11.

Q: <new question>
A:
```

### Self-consistency

Sample multiple CoT chains (with temperature > 0), take the majority answer. Reduces variance and improves accuracy — see [[Tree of Thoughts and Self Consistency]] for the full treatment:

```python
chains = [llm(cot_prompt, temperature=0.7) for _ in range(5)]
answers = [extract_final_answer(c) for c in chains]
final = majority_vote(answers)
```

### Auto-CoT

Automatically construct few-shot CoT examples by clustering questions and sampling zero-shot CoT outputs. Avoids hand-crafting examples.

## Why CoT works

Several theories attempt to explain why eliciting step-by-step reasoning helps so much, and all four likely contribute.

The first is **more compute per token**: CoT generates more tokens, which means more forward passes through the model, and more compute leads to better reasoning. This is the "test-time compute" view (see [[Test-Time Compute Scaling]]).

The second is **decomposition**: CoT breaks a hard problem into easier sub-problems, so each step is simpler than the full problem. This is also the basis of the [[Planner-Executor Pattern]].

The third is **attention over intermediate results**: the model attends to its own intermediate reasoning when producing the final answer, which effectively gives it a "scratchpad" to work in.

The fourth is **training data bias**: models are trained on text that includes reasoning (math solutions, code, explanations), and CoT elicits this learned behavior.

All four likely contribute. The first (more compute) is supported by the observation that CoT's benefit scales with model size — small models don't benefit, because they can't reason well enough even with CoT.

## Limitations

CoT has four important failure modes. It doesn't fix fundamental capability gaps — if a model can't do arithmetic, CoT won't make it able to. It can amplify errors — if the first step is wrong, the rest of the chain is built on a false premise. It can be unfaithful — the model's stated reasoning may not match its actual computation, so the model can produce a correct answer with wrong reasoning, or vice versa (see [[Probing]]). And it carries a token cost — CoT produces longer outputs, which cost more.

## When CoT helps most

CoT earns its keep on multi-step arithmetic and math, logical reasoning (syllogisms, conditional reasoning), code understanding and debugging, and planning problems. As a rule of thumb, use it for any task where intermediate results would help a human too.

## When CoT does not help (or hurts)

The mirror image also holds. CoT adds nothing on simple factual recall or single-step tasks, on tasks where the model already has strong pattern-matching (no reasoning is needed), and on tasks where the reasoning would be longer than the answer — there it is pure overhead.

## Implementation

```python
def cot_prompt(question, examples=None):
    prompt = ""
    if examples:
        for q, a in examples:
            prompt += f"Q: {q}\nA: {a}\n\n"
    prompt += f"Q: {question}\nA: Let's think step by step. "
    return prompt

# Use
response = llm.chat(cot_prompt(question, examples=cot_examples))
```

For tool use, CoT pairs naturally with [[ReAct Pattern]] — the model reasons (Thought), then acts (Action), then observes (Observation), then repeats.

## Reasoning models: the modern evolution

In 2024–2025, models like OpenAI o1/o3, DeepSeek-R1, and Claude "extended thinking" are trained specifically to produce long CoT chains. These chains can be thousands of tokens and involve trying multiple approaches, catching and correcting mistakes mid-chain, backtracking when a path doesn't work, and verifying the final answer. This is "test-time compute scaling" — using more inference-time compute for harder problems. See [[Test-Time Compute Scaling]] and [[Reasoning Models]].

## Why this matters

CoT is the single most impactful prompting technique — almost every production LLM feature uses CoT in some form. The discovery of CoT (Wei et al. 2022) was a turning point: it showed that prompting alone could unlock new capabilities, leading to the prompting-engineering field. Reasoning models (o1, R1) are essentially CoT at training time — they learn to produce CoT chains as part of training, not just from prompting. And for agents, CoT is the foundation: every agent reasoning pattern (ReAct, ToT, GoT, reflection) builds on CoT.

## Production implications

Five practices dominate real deployments:

- **Default to CoT for reasoning tasks**. Always prompt with "Let's think step by step." or similar for multi-step problems.
- **Hide CoT from end users** unless they want it. CoT chains are verbose and can confuse non-technical users. Show only the final answer in the UI; log the full chain for debugging.
- **Use self-consistency for high-stakes answers**. Sample 3–5 chains and majority-vote. Cuts error rate substantially.
- **For reasoning models** (o1, R1), don't prompt with CoT — they do it themselves. Just ask the question directly.
- **Cost**: CoT produces more tokens, which costs more. For high-volume low-difficulty tasks, skip CoT.

## Common pitfalls

The five recurring mistakes:

- **Forgetting CoT for math/logic** — the single biggest prompting mistake. Always CoT for multi-step.
- **CoT for trivial tasks** — wastes tokens. Use CoT only when the task has multiple steps.
- **Trusting CoT as explanation** — CoT is the model's *stated* reasoning, which may not match its actual computation. See the "unfaithful CoT" literature.
- **Forcing CoT into a fixed format** — let the model produce natural language reasoning. Strict formats (like "Step 1: ... Step 2: ...") can hurt quality.
- **Not using CoT in agents** — agents without CoT are essentially random. CoT (or ReAct) is the minimum viable reasoning for agents.

## Relationship to other concepts

[[ReAct Pattern]] combines CoT with tool use. [[Tree of Thoughts and Self Consistency]] extends CoT into search and voting — the papers behind them are [[Tree of Thoughts]] and [[Self-Consistency]]. [[Reflection]] layers self-critique on top of CoT, and [[Graph of Thoughts]] generalizes CoT into graph-structured reasoning. Few-shot CoT is an application of [[In-Context Learning]]. CoT also has an information-theoretic reading: reasoning step by step reduces the entropy of the output distribution (see [[Entropy Cross-Entropy and KL Divergence]]).

## Interview questions

**Why does CoT work? What are the theories?** Four theories: (1) more compute per token — more forward passes lead to better reasoning; (2) decomposition — CoT breaks hard problems into easier sub-problems; (3) attention over intermediate results — the model attends to its own reasoning as a "scratchpad"; (4) training data bias — models are trained on text with reasoning, and CoT elicits this. All four likely contribute. The first is supported by CoT's benefit scaling with model size.

**When does CoT NOT help?** (1) Simple factual recall — no reasoning needed. (2) Single-step tasks — decomposition is unnecessary. (3) Tasks where the model already has strong pattern-matching. (4) Tasks where reasoning is longer than the answer (pure overhead). (5) Small models (<1B) — they can't reason well enough even with CoT. CoT's benefit is an emergent property that appears above ~10B parameters.

**What is unfaithful CoT and why does it matter?** The model's stated reasoning (the CoT chain) may not match its actual computation. The model can produce correct answers with wrong reasoning, or wrong answers with plausible reasoning. This matters for trust (you can't rely on CoT as an explanation), debugging (you can't fix reasoning by fixing the CoT), and safety (the model might hide its true reasoning process). See Turpin et al. (2023).

**How do reasoning models (o1, R1) differ from CoT prompting?** CoT prompting: you prompt a standard LLM to "think step by step," and the model produces CoT as a response to the prompt. Reasoning models: the model is trained (via RL) to produce long CoT chains internally. The chains can be thousands of tokens and involve trying multiple approaches, catching errors, and backtracking. The model learns to reason during training, not just from prompting.

**What is self-consistency and when should you use it?** Sample N CoT chains at temperature > 0 and take the majority answer. It works because different chains have independent failure modes — majority voting cancels errors. Cost: N× more LLM calls. Use it for high-stakes answers (math, code, factual queries) where accuracy matters more than cost; typical N is 5–10. Not worth it for chat or creative tasks.

**How does CoT interact with tool use (ReAct)?** CoT pairs naturally with ReAct: the model reasons (Thought), then acts (Action), then observes (Observation), then repeats. The CoT is the "Thought" step — it helps the model decide what action to take. Without CoT, agents are essentially random; CoT (or ReAct) is the minimum viable reasoning for agents.

## Further reading

- Wei et al. (2022), *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models*.
- Kojima et al. (2022), *Large Language Models are Zero-Shot Reasoners* (zero-shot CoT).
- Wang et al. (2022), *Self-Consistency Improves Chain of Thought Reasoning in Language Models*.
- Turpin et al. (2023), *Language Models Don't Always Say What They Think: Unfaithful Explanations in Chain-of-Thought Prompting*.

## See also

- [[Agents and Tooling MOC]] — the area orientation for agents and tooling.
- [[ReAct Pattern]] — CoT plus tool use.
- [[Tree of Thoughts and Self Consistency]] — search and voting extensions of CoT.
- [[Reflection]] — CoT plus self-critique.
- [[Function Calling]] — acting on CoT decisions in the real world.
- [[Planner-Executor Pattern]] — decomposition as an agent architecture.
- [[Agent vs Workflow vs LLM Application]] — where reasoning-heavy agents fit.
- [[Reasoning Models]] — trained CoT.
- [[Test-Time Compute Scaling]] — CoT as test-time compute.
- [[In-Context Learning]] — the mechanism behind few-shot CoT.
- [[Probing]] — checking whether stated reasoning matches computation.
- [[Self-Consistency]] — the self-consistency paper.
- [[Tree of Thoughts]] — search over CoT.
- [[Graph of Thoughts]] — graph-structured generalization.
- [[Entropy Cross-Entropy and KL Divergence]] — CoT reduces output entropy.
