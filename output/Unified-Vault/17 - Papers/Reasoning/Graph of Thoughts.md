---
title: Graph of Thoughts
type: concept
aliases: [Graph of Thoughts, GoT, Besta 2023]
tags: [paper, graph-of-thoughts, reasoning, search, dag, planning]
sources:
  - "39 - Graph of Thoughts 2023"
created_index: 44
---

Graph of Thoughts (GoT) generalizes [[Tree of Thoughts]] from a tree to a **general directed graph** of reasoning steps. Nodes are thoughts; edges can merge (combine multiple thoughts into one) or branch (one thought spawns several). This enables operations ToT can't express: aggregating partial solutions, refining thoughts via feedback loops, and reusing successful sub-recipes across branches. GoT achieves state-of-the-art on sorting, set intersection, and keyword counting — tasks where combining partial results beats exploring independent branches. The generalization comes at the cost of more complex orchestration and harder-to-tune search hyperparameters.

## Citation

Besta, M., Blach, N., Kubicek, A., Gerstenberger, R., Podstawk, M., Gianinazzi, L., Gajda, J., Lehmann, T., Niewiadomski, H., Nyczyk, P., & Hoefler, T. (2023). *Graph of Thoughts: Solving Elaborate Problems with Large Language Models*. AAAI 2024. arXiv:2308.09687.

## The problem being solved

Tree of Thoughts generalized linear [[Chain of Thought|chain-of-thought]] to a tree: each thought can branch into multiple children. But a tree enforces a strict parent-child structure — there's no way to:

- **Merge** two thoughts from different branches into one (e.g., combine partial solutions from two approaches).
- **Refine** a thought by feeding back its own critique (cycles in the graph).
- **Reuse** a successful sub-reasoning across multiple branches (DAG structure, not tree).

For tasks like sorting a long list (where you can split into halves, sort each, then merge) or set intersection (where you process subsets and combine), the natural reasoning structure is a DAG, not a tree. GoT was built to express these structures.

## The key idea: general graph reasoning

GoT frames LLM reasoning as operations on a graph of thoughts:

- **Node**: a thought (a reasoning step, partial solution).
- **Edge**: a transformation — one thought produces another.
- **Aggregation**: multiple input edges to one node (merge $n$ thoughts into 1).
- **Branching**: multiple output edges from one node (1 thought spawns $n$).
- **Refinement**: a self-loop or cycle (refine a thought based on its own critique).

The graph can be any DAG (or even cyclic, if you allow refinement loops with a step budget). The user (or an LLM planner) specifies the graph structure for the task; the GoT runtime executes it.

## The four operations

GoT defines four primitive operations on the graph.

### Aggregation (merge)

Combine $k$ thoughts into 1:

$$
\text{aggregate}(t_1, \ldots, t_k) \to t'
$$

Example: in sorting, merge two sorted halves into one sorted list. In set intersection, intersect two partial intersection results.

### Branching (split)

Generate $k$ children from 1 thought:

$$
\text{branch}(t) \to (t_1, \ldots, t_k)
$$

This is what ToT does. Example: in 24-game, branch on each possible first operation.

### Refinement (improve)

Improve a thought in place:

$$
\text{refine}(t) \to t'
$$

The thought is replaced with a better version (e.g., fix errors, add detail). This is a self-loop in the graph.

### Ranking (score)

Score thoughts to decide which to keep:

$$
\text{rank}(t_1, \ldots, t_k) \to \text{scores}
$$

Used to prune low-quality thoughts and bound the graph size.

## Worked example: sorting with GoT

To sort a list of 32 numbers:

```text
1. Branch: split [32 numbers] into [first 16] and [last 16].
2. Recursively sort each half:
   a. Branch: split [16] into [8] and [8].
   b. Recursively sort each 8:
      i. Branch: split [8] into [4] and [4].
      ii. Recursively sort each 4 (base case: small enough to sort directly).
      iii. Aggregate: merge two sorted 4s into a sorted 8.
   c. Aggregate: merge two sorted 8s into a sorted 16.
3. Aggregate: merge two sorted 16s into a sorted 32.
```

This is a classic merge sort — and it's a DAG, not a tree. The aggregate step has two parents; in ToT's tree structure, this is impossible. GoT expresses it naturally.

The LLM is invoked for each branch (split the list) and each aggregate (merge two sorted lists). The final result is the single sorted list at the root of the DAG.

## Comparison with CoT and ToT

| Aspect              | CoT            | ToT                          | GoT                              |
|---------------------|----------------|------------------------------|----------------------------------|
| Structure           | Linear path    | Tree (branching only)        | General DAG (branch + merge + refine) |
| Operations          | Single chain   | Branch + rank                | Branch + aggregate + refine + rank |
| Merge partial results | No          | No                           | Yes (aggregation)                |
| Refinement loops    | No             | No                           | Yes (self-loops)                 |
| Sub-reasoning reuse | No             | No                           | Yes (DAG sharing)                |
| Cost (vs CoT)       | 1×             | 10–100×                      | 10–1000×                         |
| Best for            | Single-path reasoning | Planning, search    | Tasks with natural DAG structure |

## Empirical results

On sorting 64 elements (LLaMA-2 70B):

| Method                  | Accuracy |
|-------------------------|----------|
| CoT                     | 52%      |
| ToT                     | 71%      |
| **GoT**                 | **92%**  |

On set intersection (intersection of 2 sets of 64 elements each):

| Method                  | Accuracy |
|-------------------------|----------|
| CoT                     | 61%      |
| ToT                     | 78%      |
| **GoT**                 | **96%**  |

On keyword counting (count occurrences of a keyword in a long text):

| Method                  | Accuracy |
|-------------------------|----------|
| CoT                     | 72%      |
| ToT                     | 84%      |
| **GoT**                 | **94%**  |

The pattern is consistent: GoT beats ToT by 10–20% on tasks with natural DAG structure. On tasks without DAG structure (e.g., 24-game, where the reasoning is tree-like), GoT ≈ ToT.

## When GoT helps

- **Tasks with natural merge structure**: sorting, set operations, distributed computation, divide-and-conquer algorithms.
- **Tasks with refinement loops**: writing (draft → critique → revise → critique → ...), code (write → test → fix → test → ...).
- **Tasks with reusable sub-reasoning**: multi-step planning where the same sub-procedure is needed in multiple branches.

## When GoT doesn't help

- **Single-path reasoning**: arithmetic, simple deductions. CoT is enough; GoT's overhead is wasted.
- **Pure search problems**: 24-game, crosswords. ToT's tree search is sufficient; GoT's merge operations aren't useful.
- **Latency-critical applications**: GoT's 10–1000× cost over CoT makes it impractical for user-facing apps.

## Cost analysis

GoT's cost is bounded by the number of LLM calls, which is the number of nodes in the graph. For a balanced binary tree of depth $d$, that's $2^d - 1$ nodes. For a DAG with aggregation, it can be more (each aggregate is an extra call).

In practice, GoT uses 10–1000× more LLM calls than CoT. This makes it suitable for batch eval (where latency doesn't matter) and unsuitable for user-facing apps (where 100× latency is unacceptable).

## Variants and successors

- **GoT-O** (GoT with oracle ranking) — uses an oracle scorer instead of LLM-based ranking. Useful for ablation studies.
- **LLM-based graph construction** — instead of pre-specifying the graph, an LLM planner dynamically decides which operations to apply. This is closer to agentic reasoning.
- **Algebraic GoT** — formalizes the graph operations as an algebra, enabling composition and analysis. Research direction, not yet productionized.

## Why this matters for AI

- **GoT completes the reasoning-structure taxonomy**: CoT (linear) → ToT (tree) → GoT (graph). This is the full generalization; there's no "Hypergraph of Thoughts" that's been useful in practice.
- **GoT formalizes operations** (aggregate, branch, refine, rank) that appear implicitly in many agent frameworks. Recognizing these operations helps you design better agent systems.
- **GoT is a research baseline** for reasoning eval. When benchmarking a new model or technique, compare against GoT on tasks with natural DAG structure.
- **GoT's cost makes it impractical for most production use**, but its ideas (especially refinement loops and merging partial results) appear in production agent systems — implemented as hand-coded workflows rather than GoT runtime calls.

## Production implications

- **Don't use GoT in production** — the cost is too high for most use cases. The ideas (merge, refine) are better implemented as hand-coded workflows in [[LangGraph]] or similar.
- **Use GoT-style thinking in workflow design** — even if you don't use the GoT runtime, recognizing when a task has natural merge or refinement structure helps you design better agent systems.
- **For batch eval**, GoT is a useful baseline — it represents the upper bound of what's achievable with explicit graph reasoning.
- **For agentic systems**, the refinement operation is the most production-relevant. Most agent loops are refinement cycles: act → observe → critique → act again. GoT formalizes this pattern.

## Common pitfalls

- **Overusing GoT** — most tasks don't have natural DAG structure. CoT or ToT is enough.
- **Specifying the wrong graph** — GoT requires the user to specify the graph structure. If the structure doesn't match the task, GoT performs worse than ToT.
- **Ignoring the cost** — GoT's 10–1000× cost is easy to underestimate. Always budget by graph size.
- **Treating GoT as agentic** — GoT is a graph execution runtime, not an agent. The graph is specified upfront; there's no dynamic decision-making beyond ranking.
- **Confusing GoT with graph neural networks** — they're unrelated. GoT is about LLM reasoning structure; GNNs are about neural network architecture.

## Further reading

- Besta et al. (2023), *Graph of Thoughts: Solving Elaborate Problems with Large Language Models*. arXiv:2308.09687.
- Yao et al. (2023), *Tree of Thoughts: Deliberate Problem Solving with Large Language Models*. (The predecessor.)
- Wei et al. (2022), *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models*. (The original CoT.)
- GoT GitHub: https://github.com/spcl/graph-of-thoughts

## Interview questions

**Q: What is the key generalization GoT makes over ToT?**

A: GoT allows the reasoning structure to be a general directed graph (DAG with possible cycles), whereas ToT is restricted to a tree. This enables three operations ToT can't express: (1) **aggregation** — merge multiple thoughts into one (e.g., merge two sorted halves in merge sort); (2) **refinement** — a self-loop that improves a thought based on its own critique; (3) **reuse** — a sub-graph can be referenced from multiple branches. The graph structure is specified upfront by the user or an LLM planner; the GoT runtime executes it.

**Q: Give an example of a task where GoT beats ToT.**

A: Sorting a list of 64 numbers. The natural reasoning structure is merge sort: split into halves, recursively sort each half, merge the sorted halves. The merge step has two parents — it aggregates two partial solutions. In ToT's tree structure, this is impossible (each node has one parent). In GoT, aggregation is a first-class operation. Empirically, GoT achieves 92% accuracy on sorting 64 elements with LLaMA-2 70B, vs 71% for ToT and 52% for CoT.

**Q: Why is GoT impractical for most production use?**

A: Cost. GoT uses 10–1000× more LLM calls than CoT, depending on graph size. For user-facing apps where 100× latency is unacceptable, GoT is unsuitable. The ideas — especially refinement loops and merging partial results — are better implemented as hand-coded workflows in LangGraph or similar, where you control the cost explicitly. GoT is most useful as a research baseline and as a conceptual framework for designing agent systems.

**Q: What are the four primitive operations in GoT?**

A: (1) **Aggregation** — merge $k$ thoughts into 1 (e.g., merge two sorted halves). (2) **Branching** — generate $k$ children from 1 thought (e.g., try $k$ different first moves). (3) **Refinement** — improve a thought in place via a self-loop (e.g., draft → critique → revise). (4) **Ranking** — score thoughts to prune low-quality ones and bound graph size. These four primitives can express any graph reasoning structure.

**Q: How does GoT relate to multi-agent systems?**

A: Multi-agent systems often have GoT-like graph structure: agents produce partial results, a coordinator aggregates them, agents refine based on feedback, etc. The difference is that multi-agent systems are dynamic (the graph emerges from agent interactions) while GoT is static (the graph is specified upfront). GoT's operations (aggregate, branch, refine, rank) are useful conceptual tools for designing multi-agent workflows, even if you don't use the GoT runtime.

**Q: When would you use GoT vs Self-Consistency?**

A: SC is for tasks with a unique correct answer that can be reached by many paths — sample N paths, vote. GoT is for tasks with natural graph structure (merge, refine) where you need to combine partial results. SC is much cheaper (N samples, no graph orchestration). GoT is more expressive but 10–100× more expensive. Rule of thumb: try SC first; if SC fails because the task needs merging or refinement, try GoT.

## See also

- [[Papers MOC]] — the papers hub for this note.
- [[Tree of Thoughts]] — the predecessor; GoT generalizes ToT.
- [[Self-Consistency]] — the sampling-based alternative to graph search.
- [[Chain of Thought]] — the foundation.
- [[Tree of Thoughts and Self Consistency]] — the chapter-15 deep dive on this reasoning family.
- [[Reflection]] — GoT's refinement operation is a reflection loop.
- [[Multi-Agent Architectures]] — multi-agent systems often have GoT-like graph structure.
- [[LangGraph]] — where GoT-style merge/refine workflows get hand-coded in production.
