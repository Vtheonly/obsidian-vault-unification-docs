---
title: Tree of Thoughts and Self Consistency
type: concept
aliases: ["Tree of Thoughts", "Tree-of-Thoughts", "ToT", "Graph of Thoughts", "Graph-of-Thoughts", "GoT", "Self-Consistency", "self-consistency"]
tags: [agents, reasoning, tot, got, self-consistency, tree-of-thoughts, graph-of-thoughts]
sources: ["06 - Tree of Thoughts and Self Consistency"]
created_index: 9
---

Beyond single-chain [[Chain of Thought]] and ReAct lies a family of advanced reasoning patterns: self-consistency samples multiple CoT chains and majority-votes the answers, Tree-of-Thoughts (ToT) explores multiple reasoning branches and prunes them by evaluation, and Graph-of-Thoughts (GoT) generalizes the tree to an arbitrary graph of reasoning steps. They buy higher answer quality at much higher cost, and they are all forms of test-time compute. This note covers each pattern, its variants, when it helps, and the engineering trade-offs.

## Self-consistency

The simplest enhancement to CoT (Wang et al. 2022) has three steps:

1. Sample $N$ CoT chains at temperature > 0 (e.g., $N=5$).
2. Extract the final answer from each.
3. Take the majority answer.

```python
chains = [llm.generate(prompt, temperature=0.7) for _ in range(5)]
answers = [extract_answer(c) for c in chains]
final = Counter(answers).most_common(1)[0][0]
```

**Why it works**: different reasoning chains have independent failure modes. Majority voting cancels out errors.

**Cost**: $N$x the LLM calls. Worth it for high-stakes answers (math, code, factual queries).

**Quality gain**: typically 5–15% absolute improvement on math/reasoning benchmarks.

## Tree of Thoughts

CoT is a linear chain: $A \to B \to C \to \text{answer}$. ToT (Yao et al. 2023) explores a tree instead:

```text
              [Problem]
            /     |     \
        [A1]   [A2]   [A3]      ← generate multiple first steps
        / \    /  \    / \
      [B1][B2][B3][B4][B5][B6]  ← for each, generate multiple next steps
      ...                       ← evaluate and prune; expand promising branches
```

### The algorithm

1. **Thought generation**: at each step, generate $k$ candidate next thoughts.
2. **Evaluation**: have the LLM (or a heuristic) score each candidate.
3. **Search**: BFS or DFS over the tree, expanding high-scoring branches and pruning low-scoring ones.

### When ToT helps

ToT earns its cost on problems with multiple intermediate steps where backtracking is useful, and on problems where partial progress can be evaluated (puzzles, math, planning).

### When ToT is overkill

Most chatbot use cases, problems where CoT already works well, and cost-sensitive applications (ToT can be 10–100x CoT cost) don't justify the machinery.

## Graph of Thoughts

GoT (Besta et al. 2023) generalizes ToT to arbitrary graphs:

```text
              [Start]
            /         \
        [A]            [B]
        | \          / |
        |  [C]------   |
        | /            |
        [D]            [E]
         \            /
          [Combine]
              |
           [Answer]
```

Different reasoning paths can **merge** (e.g., combine insights from two branches). More flexible than ToT but more complex to implement.

## Other variants

### Self-Refine

The model generates an answer, then critiques and refines it iteratively (Madaan et al. 2023):

```text
answer → critique → refined answer → critique → refined answer → ...
```

See [[Reflection]].

### Plan-and-Solve

Decompose a problem into sub-problems, solve each. Variant of CoT with an explicit planning step.

### Reasoning via Planning (RAP)

Use an MDP framework: states = reasoning steps, actions = next-step proposals, rewards = LLM-evaluated progress. Combine LLMs with classical planning (Monte Carlo Tree Search).

## Worked example: self-consistency

```python
def self_consistent_answer(question, n=5):
    prompt = f"Q: {question}\nA: Let's think step by step. "
    chains = [llm.generate(prompt, temperature=0.7, max_tokens=500) for _ in range(n)]

    # Extract final numeric answers (assuming math question)
    answers = []
    for chain in chains:
        match = re.search(r'answer is (\d+)', chain)
        if match:
            answers.append(int(match.group(1)))

    if not answers:
        return None
    return Counter(answers).most_common(1)[0][0]
```

The prompt asks for step-by-step reasoning, the $n$ sampled chains run at temperature 0.7 for diversity, and the majority numeric answer wins; if no chain yields a parseable answer, the function gives up and returns `None`.

## Why this matters

These techniques extend LLM reasoning beyond single-shot CoT, and for hard problems they can dramatically improve quality. Self-consistency is the most practical — easy to implement, robust improvement, modest cost increase. ToT and GoT are research-grade; mostly relevant for benchmark chasing and specialized reasoning tasks. For agents, these patterns are sometimes combined with tool use — e.g., an agent that explores multiple plans before acting.

## Production implications

Four practices dominate real deployments:

- **For high-stakes Q&A** (math, code, factual), use self-consistency with $n=3$–5. The cost is worth the accuracy gain.
- **For agents**, consider ToT-style planning for hard multi-step tasks. Cost can be 10x+, so use selectively.
- **Latency matters** — self-consistency adds latency (parallel sampling helps). ToT adds even more.
- **For chat**, these techniques are usually overkill. A single CoT response is fine.

## Common pitfalls

The four recurring mistakes:

- **Using ToT where CoT suffices** — 10x cost for marginal gain.
- **Forgetting self-consistency for math/factual** — easy win, often missed.
- **Wrong temperature for self-consistency** — temperature 0 gives identical chains (no diversity). Use 0.7+.
- **Bad evaluation function in ToT** — if the LLM can't reliably evaluate intermediate steps, ToT doesn't help.

## Relationship to other concepts

[[Chain of Thought]] is the foundation all of these patterns extend. [[ReAct Pattern]] combines reasoning with action, and [[Reflection]] is the self-critique pattern that Self-Refine builds on. Self-consistency depends on sampling mechanics, so temperature choice matters (see [[Sampling Strategies]]). The research papers are [[Self-Consistency]], [[Tree of Thoughts]], and [[Graph of Thoughts]], and all of these patterns are forms of test-time compute (see [[Test-Time Compute Scaling]]).

## Interview questions

**What is self-consistency and why does it work?** Sample N CoT chains at temperature > 0, take the majority answer. It works because different chains have independent failure modes — majority voting cancels errors. The right answer is unique (for closed-answer tasks) but there are many paths to it; wrong answers are scattered. Cost: N× more LLM calls. Typical: N=5-10. Quality gain: 5-15% absolute on math/reasoning benchmarks.

**How does ToT differ from CoT?** CoT explores a single reasoning path: A → B → C → answer. ToT explores a tree: at each step, generate k candidate thoughts, evaluate each, expand high-scoring branches and prune low-scoring ones. This allows backtracking — if a branch looks bad, the search explores alternatives. ToT is 10-100x more expensive than CoT but can solve problems CoT can't (planning, puzzles, crosswords).

**When is ToT overkill?** (1) Most chatbot use cases — CoT is sufficient. (2) Problems where CoT already works well — ToT adds cost without benefit. (3) Cost-sensitive applications — ToT can be 10-100x CoT cost. (4) Tasks where the right next step is obvious — no need to explore alternatives. ToT is for hard multi-step problems where backtracking matters.

**What is Graph-of-Thoughts and how does it generalize ToT?** GoT allows arbitrary graph structures (not just trees): branches can merge (combine insights from two paths), have cycles (refinement loops), and share sub-results. This is more expressive than ToT (which is strictly tree-structured). GoT achieves SOTA on sorting, set intersection, and keyword counting. Cost: 10-1000x CoT.

**How do you choose between CoT, self-consistency, ToT, and GoT?** CoT: default for most tasks (cheap, effective). Self-consistency: high-stakes closed-answer tasks (math, code) — N=5-10, majority vote. ToT: planning/puzzles where backtracking matters — 10-100x cost. GoT: tasks with natural merge structure (sorting, set operations) — 10-1000x cost. Start with CoT; add self-consistency if stakes are high; add ToT/GoT only for specialized tasks.

**What is Self-Refine and how does it differ from reflection?** Self-Refine: the model generates an answer, critiques it, refines it, repeats: answer → critique → refined → critique → refined → ... It's a linear refinement loop, not a tree search. Reflection (Reflexion): the agent attempts a task, evaluates, reflects on what went wrong, and retries with the reflection in context. Self-Refine is about improving a single output; Reflection is about improving across attempts.

## Further reading

- Wang et al. (2022), *Self-Consistency Improves Chain of Thought Reasoning*.
- Yao et al. (2023), *Tree of Thoughts: Deliberate Problem Solving with Large Language Models*.
- Besta et al. (2023), *Graph of Thoughts: Solving Elaborate Problems with Large Language Models*.
- Madaan et al. (2023), *Self-Refine*.

## See also

- [[Agents and Tooling MOC]] — the area orientation for agents and tooling.
- [[Chain of Thought]] — the foundation these patterns extend.
- [[ReAct Pattern]] — reasoning plus action.
- [[Reflection]] — the self-critique pattern (Self-Refine lives here).
- [[Planner-Executor Pattern]] — planning-first agent design.
- [[Sampling Strategies]] — self-consistency needs temperature > 0.
- [[Test-Time Compute Scaling]] — these patterns as test-time compute.
- [[Self-Consistency]] — the paper.
- [[Tree of Thoughts]] — the paper.
- [[Graph of Thoughts]] — the paper.
