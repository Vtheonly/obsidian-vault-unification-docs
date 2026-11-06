---
title: In-Context Learning
type: concept
aliases: ["In-Context Learning", "ICL", "Few-Shot Learning"]
tags: [llm, capabilities, in-context-learning, few-shot, induction-heads]
sources: ["04 - In-Context Learning"]
created_index: 2
---

> [!info] TL;DR
> In-context learning (ICL) is the ability of an LLM to learn new tasks from examples in the prompt — without any weight updates. Discovered with GPT-3 (2020); the property that made LLMs "general purpose" rather than task-specific.

In-context learning is the defining emergent capability of large language models: show the model a handful of worked examples in the prompt and it performs the task, with no gradient updates anywhere in the loop. Its discovery with GPT-3 in 2020 shifted the field from many small task-specific models to one big model plus prompting, and it is the reason prompting — not retraining — is the default way to adapt a deployed model. This note covers the phenomenon, the zero-shot/one-shot/few-shot taxonomy from the GPT-3 paper, the induction-head mechanism that implements ICL under the hood, and the trade-offs against fine-tuning and retrieval, together with the production guidance, pitfalls, and failure modes that come with all of it.

## The phenomenon

Give an LLM a few examples in the prompt:

```text
Translate English to French:
cheese → fromage
bread → pain
wine →
```

The model outputs "vin". It learned the translation task from two examples, without any gradient updates.

This is **in-context learning** (ICL) — sometimes called **few-shot learning** (when examples are given) or **zero-shot** (when no examples, just instructions). Nothing about the model changed between requests; the examples alone reshape its behavior, which is what makes the same deployed weights usable for a new task the moment someone writes a prompt for it.

## How it differs from classical ML

Set beside the paradigms that came before it, ICL is the odd one out: it adapts without touching weights, which makes adaptation instant and shifts the cost from compute to tokens.

| Paradigm                | How it learns                          | Speed        | Cost           |
|-------------------------|----------------------------------------|--------------|----------------|
| Classical supervised    | Gradient updates on labeled data       | Slow         | Compute-bound  |
| Fine-tuning             | Gradient updates on a pretrained model | Medium       | Compute-bound  |
| **In-context learning** | Examples in the prompt, no updates     | Instant      | Token-cost     |

ICL is the defining property of modern LLMs. Without it, you'd need a fine-tuned model for every task — a return to pre-2020 NLP.

## Three levels of ICL

Following the GPT-3 paper's terminology: demonstrations come in three grades, distinguished only by how many examples accompany the task. The same translation task illustrates all three.

### Zero-shot

Just describe the task:

```text
Translate "cheese" to French:
```

The model must figure out the task from the instruction alone.

### One-shot

Give one example:

```text
Translate English to French:
cheese → fromage
Now translate "bread":
```

### Few-shot

Give multiple examples:

```text
Translate English to French:
cheese → fromage
bread → pain
water → eau
Now translate "wine":
```

More examples generally improve accuracy (up to a point — context limits). The GPT-3 paper showed diminishing returns past 5-10 examples for most tasks, so "few" really is the operating regime.

## How ICL works (mechanistically)

Mechanistic interpretability research has shown that ICL is implemented by **induction heads** — attention heads that:

1. Find previous occurrences of the current token.
2. Attend to the token that followed.
3. Copy that token (or a transformed version) to the output.

So when the model sees `wine →` and previously saw `cheese → fromage`, an induction head finds the `cheese →` pattern and copies `fromage`'s analog.

Induction heads emerge naturally during training and are necessary for ICL. They appear around the same training point across different model families.

## The induction head circuit — a deep dive

The **induction head** (Olsson et al., 2022) is the best-understood mechanistic circuit for ICL. It's a two-head composition:

1. **Previous-token head**: at position $t$, attends to position $t-1$ and copies that token's identity into the residual stream at position $t$.
2. **Induction head**: at position $t$, looks for previous occurrences of the token at $t-1$ (using the previous-token head's output), then attends to the token *after* that occurrence.

This creates a pattern: "if you saw `[A] [B]` earlier, and now you see `[A]`, predict `[B]`."

### Emergence during training

Induction heads emerge **suddenly** during training — there's a phase transition where the capability appears. This transition correlates strongly with the model's ICL ability. Before the transition, the model can't do ICL; after, it can. This is one of the strongest examples of **grokking** in LLM training.

### Model size and emergence

ICL is an emergent property — it appears only above a certain model size (~1B parameters for simple tasks, ~10B+ for complex tasks). Larger models have more induction heads, stronger circuits, and can handle more complex patterns. The relationship is not linear: there are phase transitions where new capabilities emerge. This is why GPT-3 (175B) showed dramatic ICL improvements over GPT-2 (1.5B).

### Why induction heads enable ICL

When you give the model few-shot examples like:

```text
cheese → fromage
bread → pain
wine →
```

The induction head finds the pattern `[word] → [translation]` and applies it to `wine`. The model isn't "learning" translation — it's doing pattern matching via the induction circuit.

This explains why:

- **Model size matters**: larger models have more induction heads and stronger circuits.
- **Example format matters**: consistent format (`A → B`) makes the pattern easy to detect.
- **Example order matters**: the most recent example has the strongest induction signal (recency bias in attention).

The format and order bullets are the mechanistic reason behind prompt advice that recurs later in this note: format examples consistently, and put the most important one last.

## ICL vs fine-tuning

Adapting through the prompt and adapting through gradient updates trade off along six axes:

| Property           | ICL                          | Fine-Tuning              |
|--------------------|------------------------------|--------------------------|
| Speed              | Instant                      | Minutes to hours         |
| Cost per task      | Token cost per request       | One-time training cost   |
| Quality ceiling    | Lower than fine-tuned        | Higher                   |
| Latency per request| Higher (longer prompts)      | Lower                    |
| Per-task storage   | None                         | Adapter or full model    |
| Update flexibility | Change prompt instantly      | Retrain to update        |

**Rule of thumb**: try ICL first. If it works, ship it. If it doesn't, consider fine-tuning.

## ICL vs fine-tuning vs RAG — a decision framework

Once retrieval enters the picture the comparison becomes three-way, and the right choice hinges on whether the model is missing knowledge or missing capability:

| Criterion | ICL | Fine-Tuning | RAG |
|-----------|-----|-------------|-----|
| Setup time | Instant | Hours | Minutes |
| Cost per request | High (long prompts) | Low | Medium |
| Quality ceiling | Medium | High | Medium-High |
| Task adaptation | Change prompt | Retrain | Update index |
| Best for | Prototyping, simple tasks | Production, domain-specific | Knowledge-intensive tasks |

**Rule of thumb**: ICL → RAG → Fine-Tuning. Start with ICL (cheapest). If ICL lacks knowledge, add RAG. If ICL lacks capability (can't do the task even with knowledge), fine-tune. Most production systems start with ICL and only move to fine-tuning when the quality gap justifies the engineering cost.

## The "lost in the middle" problem

Liu et al. (2023) found that LLMs have a **positional bias** in ICL: they attend more to examples at the beginning and end of the prompt, ignoring those in the middle.

```text
[Example 1] ← high attention
[Example 2] ← low attention (middle)
[Example 3] ← low attention (middle)
[Example 4] ← high attention (end)
[Query]
```

Implications:

- **Put the most relevant example last** (recency bias).
- **Put the most representative example first** (primacy bias).
- **Don't put critical examples in the middle**.
- **Keep prompts short** — fewer examples means less middle to get lost in.

And when a prompt grows long because it is carrying knowledge rather than task structure, the fix is retrieval rather than more examples: use RAG instead of long prompts for knowledge-intensive tasks.

## Worked examples

### Few-shot sentiment classification

```python
# Few-shot ICL
prompt = """Classify sentiment:
Text: I loved this movie!
Sentiment: positive

Text: The food was terrible.
Sentiment: negative

Text: It was okay, nothing special.
Sentiment:"""

response = llm.generate(prompt, max_tokens=5)
# Usually: "neutral"
```

Two demonstrations are enough to establish the input/output format and the label vocabulary, and the model completes the lukewarm query — usually with "neutral", a judgment it produces with no task-specific weight updates.

### Few-shot ICL with different example counts

```python
from openai import OpenAI
client = OpenAI()

def few_shot_icl(task_examples, query, model="gpt-4o"):
    """Run few-shot ICL with variable example counts."""
    prompt = "\n\n".join([f"Input: {ex['input']}\nOutput: {ex['output']}" for ex in task_examples])
    prompt += f"\n\nInput: {query}\nOutput:"

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=50,
    )
    return response.choices[0].message.content

# Test with different example counts
examples = [
    {"input": "The movie was great!", "output": "positive"},
    {"input": "Terrible experience.", "output": "negative"},
    {"input": "It was okay.", "output": "neutral"},
    {"input": "Best film ever!", "output": "positive"},
    {"input": "Waste of time.", "output": "negative"},
]

query = "I really enjoyed it."
for n in [0, 1, 3, 5]:
    result = few_shot_icl(examples[:n], query)
    print(f"n={n}: {result}")
```

The sweep turns "how many examples do I need?" into an experiment: n=0 is zero-shot, n=1 is one-shot, and n=3 and n=5 are few-shot, all run at temperature 0 so that any difference in the output comes from the demonstrations rather than sampling noise.

## Why this matters for AI

- ICL is **the** property that makes LLMs useful. Without it, every task would need a specialized model.
- The discovery of ICL (GPT-3, 2020) is what shifted the field from "many small models" to "one big model + prompting".
- For production AI features, ICL is the default — few-shot examples in the prompt are often enough.
- The induction-heads finding connects ICL to mechanistic interpretability, giving us a concrete understanding of how LLMs "think".

Two extensions round out the picture. In-context learning combines with chain-of-thought prompting: few-shot examples that include reasoning steps teach the model both the task and the reasoning style, which made "few-shot CoT" the most effective prompting strategy for reasoning tasks before dedicated reasoning models (o1, R1) existed. And in the taxonomy that separates an LLM application from a workflow and an agent, ICL is the LLM application level — the model doing the task straight from the prompt. In information-theoretic terms, ICL reduces output entropy, tying the phenomenon back to the entropy, cross-entropy, and KL divergence measures of information theory.

## Production implications

In production, the prompt is the adaptation surface, and the operating advice is short:

- **Default to ICL**. Start with 0–5 examples in the prompt. Only fine-tune if ICL is insufficient.
- **Token cost**: every example in the prompt costs tokens. For high-volume features, this adds up. Cache prompts where possible.
- **Example quality matters more than quantity**. 3 well-chosen examples beat 10 mediocre ones.
- **Example order matters** (recency bias). Put the most relevant example last.
- **Watch for prompt injection** in examples — if examples come from untrusted sources, they can manipulate the model.

> [!warning]
> Few-shot examples are prompt input like any other. If examples are assembled from untrusted sources, a malicious example can steer the model's behavior on every request that includes it — treat example text with the same suspicion as user input.

## Common pitfalls

The recurring mistakes are prompt-design errors:

- **Too many examples** — fills context, increases cost, can hurt quality (lost in the middle).
- **Inconsistent example format** — model gets confused if examples have different structures.
- **Examples that contradict the task** — model follows examples over instructions.
- **Forgetting that ICL is stochastic** — same prompt, different outputs. Use temperature 0 for deterministic tasks.

The stochasticity point deserves emphasis: ICL output is sampled, not looked up, so a deterministic application needs temperature 0 — see [[Sampling Strategies]] for how temperature shapes what the model emits.

## Common failure modes

Where pitfalls are design errors made while writing the prompt, failure modes are the runtime symptoms that surface anyway, each with a likely cause and a fix:

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Model ignores examples | Wrong chat template; or examples too far from query | Use apply_chat_template; put relevant examples last |
| Model copies example format instead of content | Examples too similar in structure | Vary example structure; use different inputs |
| Inconsistent outputs | Temperature > 0 | Set temperature=0 for deterministic tasks |
| Model "lost in the middle" | Too many examples; critical info in middle | Fewer examples; put most relevant last |
| Token cost too high | Many examples in every prompt | Cache prefix; or fine-tune to reduce examples |

The chat-template row is worth flagging: a prompt assembled without the model's expected template can render the examples invisible to the model. The template machinery itself is covered in [[Instruction Tuning and Chat Templates]].

## Further reading

Three papers anchor the literature:

- Brown et al. (2020), *Language Models are Few-Shot Learners* (GPT-3, the ICL paper).
- Olsson et al. (2022), *In-context Learning and Induction Heads* (mechanistic).
- Min et al. (2022), *Rethinking the Role of Demonstrations* (what makes ICL work).

## Interview questions

The distinctions interviewers probe about ICL compress into six questions.

1. **Q: What is an induction head and how does it enable ICL?**
   A: An induction head is a two-head attention circuit: (1) a previous-token head copies the token at position $t-1$ into the residual stream; (2) an induction head finds previous occurrences of the $t-1$ token and attends to the token after it. This creates pattern completion: if the model saw `[A] [B]` earlier and now sees `[A]`, it predicts `[B]`. Induction heads emerge suddenly during training and correlate strongly with ICL ability.

2. **Q: What is the "lost in the middle" problem and how do you mitigate it?**
   A: LLMs attend more to examples at the beginning and end of the prompt, ignoring those in the middle (Liu et al., 2023). Mitigations: (1) put the most relevant example last (recency bias); (2) put the most representative example first (primacy bias); (3) keep prompts short (fewer examples = less middle); (4) use RAG instead of long prompts for knowledge-intensive tasks.

3. **Q: When should you use ICL vs fine-tuning vs RAG?**
   A: Start with ICL (cheapest, instant). If ICL lacks knowledge (model doesn't know facts), add RAG. If ICL lacks capability (model can't do the task even with knowledge), fine-tune. The progression: ICL → RAG → Fine-Tuning. Most production systems start with ICL and only move to fine-tuning when the quality gap justifies the engineering cost.

4. **Q: How does model size affect ICL?**
   A: ICL is an emergent property — it appears only above a certain model size (~1B parameters for simple tasks, ~10B+ for complex tasks). Larger models have more induction heads, stronger circuits, and can handle more complex patterns. The relationship is not linear: there are phase transitions where new capabilities emerge. This is why GPT-3 (175B) showed dramatic ICL improvements over GPT-2 (1.5B).

5. **Q: What's the difference between zero-shot, one-shot, and few-shot ICL?**
   A: Zero-shot: just describe the task ("Translate to French: cheese"). One-shot: give one example. Few-shot: give multiple examples. More examples generally improve accuracy up to a point (context limits, lost-in-the-middle). The GPT-3 paper showed diminishing returns past 5-10 examples for most tasks.

6. **Q: How does ICL interact with chain-of-thought?**
   A: CoT + ICL is powerful: give few-shot examples that include reasoning steps, and the model learns to reason step-by-step for the new query. This is "few-shot CoT" — the most effective prompting strategy for reasoning tasks before reasoning models (o1, R1) existed. The examples teach both the task and the reasoning style.

## See also

- [[Large Language Models MOC]] — the area orientation, for where ICL sits among LLM capabilities.
- [[Sampling Strategies]] — temperature affects ICL consistency.
- [[LLM Benchmarks]] — ICL is tested in few-shot benchmarks.
- [[Decoder-Only Architecture]] — the architecture of the GPT line in which ICL was discovered.
- [[KV Cache Mechanics]] — the machinery that makes caching a shared few-shot prefix across requests worthwhile.
- [[Instruction Tuning and Chat Templates]] — SFT builds on ICL.
- [[DPO Derivation]] — preference learning refines ICL behavior.
- [[Mechanistic Interpretability]]
- [[Agent vs Workflow vs LLM Application]]
- [[Chain of Thought]]
