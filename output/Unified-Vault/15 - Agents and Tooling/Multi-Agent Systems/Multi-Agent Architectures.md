---
title: Multi-Agent Architectures
type: concept
aliases: [Multi-Agent Architectures, Multi-Agent Patterns, Multi-Agent System Design, Multi-Agent Coordination Patterns]
tags: [multi-agent, agent-architectures, coordination, langgraph, autogen, crewai, pydanticai, production]
sources: ["01 - Multi-Agent Architectures"]
created_index: 38
---

A multi-agent system coordinates multiple LLM-based agents to solve a task instead of relying on a single agent. The recurring coordination patterns are hierarchical (planner + workers), manager-worker, peer swarm, blackboard (shared state), and marketplace (bidding), and each trades capability against cost, latency, and debuggability. Frameworks such as [[LangGraph]], [[AutoGen]], [[CrewAI]], and [[PydanticAI]] package these patterns into deployable abstractions, which is why multi-agent underlies the most ambitious agent products — and why it costs more and is harder to debug than single-agent designs.

> [!info] TL;DR
> Multi-agent systems coordinate multiple LLM-based agents to solve tasks. Common patterns: hierarchical (planner + workers), swarm (peer agents), blackboard (shared state), marketplace (bidding). Frameworks: LangGraph, AutoGen, CrewAI, PydanticAI. Higher capability, higher cost, harder to debug.

## Why multi-agent

Single-agent systems hit limits on complex tasks. One agent cannot be expert at everything; context windows fill up, so the agent "forgets" earlier parts of the task; and sequential single-agent execution is slow. Multi-agent designs answer each of these limits directly:

- **Specialization** — each agent handles a sub-task it is good at.
- **Parallelism** — independent sub-tasks run in parallel.
- **Modularity** — individual agents are easier to debug and improve.
- **Discussion / verification** — agents can critique each other.

The benefit is not free. Multi-agent is more complex to build, harder to debug, and costs more, because every step may involve multiple LLM calls.

## Common patterns

### Hierarchical (planner-executor)

```text
[Planner Agent] → [Plan: step1, step2, step3]
                      ↓
[Executor Agent] → [Step 1 result]
                      ↓
[Executor Agent] → [Step 2 result]
                      ↓
[Executor Agent] → [Step 3 result]
```

The planner decomposes the task; the executor carries out each step. Optionally, a third "synthesizer" agent combines the results. This is the pattern used by ReWOO, Plan-and-Execute, and LangGraph's planner-executor template — see [[Planner-Executor Pattern]] for the single-agent version of the idea.

### Manager-worker

```text
[Manager Agent] ← task
   ↓ assigns to:
[Worker 1] [Worker 2] [Worker 3]
   ↓ results flow back:
[Manager Agent] → final answer
```

The manager delegates and synthesizes; the workers are specialists. Unlike the fixed planner-executor sequence, delegation here is dynamic — the manager decides who does what as work arrives.

### Peer swarm

```text
[Agent A]  [Agent B]  [Agent C]
              ↓
        [Discussion / consensus]
```

All agents are peers. They share information, debate, and converge on an answer. This style is used by AutoGen's group chat and CAMEL, and it connects naturally to the consensus mechanisms covered in [[Coordination and Consensus]].

### Blackboard

```text
[Shared Memory / Blackboard]
       ↑ ↓ ↑ ↓ ↑ ↓
[Agent A] [Agent B] [Agent C]
```

A shared state (the "blackboard") that agents read from and write to. There is no direct agent-to-agent communication — everything flows through the shared state. This is a classic AI pattern from the 1980s that is reviving for LLMs; [[Communication Patterns]] treats it as one of the four canonical communication styles.

### Marketplace / bidding

```text
[Task posted]
   ↓
[Agent 1: bid 0.8] [Agent 2: bid 0.6] [Agent 3: bid 0.9]
   ↓ highest bid wins:
[Agent 3] does the task
```

Agents bid on tasks based on self-assessed capability, and the highest bidder executes. This is useful for load balancing and specialization across a pool of heterogeneous agents.

## Comparing the patterns

| Pattern | Strengths | Weaknesses | Best For |
|---|---|---|---|
| Hierarchical (Planner-Executor) | Clear division of labor, predictable flow | Rigid, planner errors cascade | Multi-step workflows with clear sub-tasks |
| Manager-Worker | Dynamic delegation, parallel execution | Manager is a bottleneck; coordination overhead | Specialized sub-tasks (research, coding) |
| Peer Swarm | Robust via discussion, no single point of failure | Unbounded conversation, hard to converge | Brainstorming, exploration, verification |
| Blackboard | Decoupled agents, shared state | Coordination complexity, race conditions | Long-running complex tasks with shared context |
| Marketplace / Bidding | Self-organizing, load balancing | Bidding strategies are hard to design | Heterogeneous agent pools |

The table makes the central tradeoff visible: the more dynamic and decentralized the pattern (swarm, marketplace), the more adaptive the system and the harder its coordination and debugging become.

## When to use multi-agent vs single-agent

The decision to use multi-agent should be deliberate, not default. Most LLM applications are better served by a single well-prompted LLM with good tools.

Use multi-agent when the task naturally decomposes into specialist roles (researcher + writer + reviewer); when a single LLM's context window cannot hold all the needed information; when different sub-tasks benefit from different models (for example a reasoning model for planning and a fast model for execution); when you need verification, with one agent producing and another critiquing; or when the task is long-running and benefits from parallelism.

Use single-agent when the task is short and well-defined; when one LLM with good tools can do it; when latency and cost matter (multi-agent is 5-50× more expensive); or when you need determinism, since multi-agent systems are more variable.

The rule of thumb: start single-agent. Move to multi-agent only when you have hit a clear ceiling with single-agent and the multi-agent structure addresses that specific ceiling. This is the same deliberate-capability argument that separates agents from fixed workflows — see [[Agent vs Workflow vs LLM Application]].

## Frameworks

### LangGraph

LangGraph (part of the LangChain ecosystem) provides stateful, cyclic graphs of agents with durable execution that resumes after crashes, a strong production story, and the most popularity for serious multi-agent deployments. The core API is small:

```python
from langgraph.graph import StateGraph

graph = StateGraph(State)
graph.add_node("planner", planner_agent)
graph.add_node("executor", executor_agent)
graph.add_node("synthesizer", synth_agent)
graph.add_edge("planner", "executor")
graph.add_edge("executor", "synthesizer")
app = graph.compile()
```

### AutoGen

AutoGen (Microsoft) implements the conversational multi-agent pattern: agents talk to each other in group chats. AutoGen 0.4+ (2025) is a major rewrite with a better architecture.

### CrewAI

CrewAI provides role-based agents ("researcher", "writer", "reviewer"). Its API is simpler than LangGraph's but less flexible, which makes it good for straightforward workflows.

### PydanticAI

PydanticAI offers type-safe agents built on Pydantic schemas, with strong Python type hints throughout. It is a good fit for structured output and tool use.

### OpenAI Agents SDK

The OpenAI Agents SDK (2024+) is OpenAI's first-party agent framework, with tight integration with OpenAI models and APIs. It is useful if you are committed to the OpenAI stack.

### Framework selection matrix (2026)

| Framework | Best For | Strengths | Weaknesses |
|---|---|---|---|
| LangGraph | Production multi-agent | Durable, observable, mature | Steep learning curve, LangChain tie-in |
| OpenAI Agents SDK | OpenAI-only stacks | First-party, simple API | OpenAI lock-in, less flexible |
| AutoGen | Research, conversational agents | Flexible, multi-pattern | Less production-ready, v0.4 rewrite |
| CrewAI | Simple role-based workflows | Easy API, readable | Less flexible, less observable |
| PydanticAI | Type-safe structured agents | Excellent type hints, validation | Newer ecosystem, less battle-tested |
| Custom (no framework) | Maximum control, simple workflows | No lock-in, full control | You build everything |

The production recommendation follows directly: LangGraph for serious deployments, PydanticAI if type safety is critical, and custom (no framework) if the workflow is simple enough to not need one. [[Framework Selection Guide]] covers the broader decision.

## Worked examples

### A minimal planner-executor graph

A complete LangGraph planner-executor-synthesizer pipeline threads a typed state through three nodes:

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, List

class State(TypedDict):
    task: str
    plan: List[str]
    results: List[str]
    final: str

def planner(state):
    plan = llm.generate(f"Break down: {state['task']}").split('\n')
    return {"plan": plan}

def executor(state):
    results = []
    for step in state['plan']:
        result = llm.generate(f"Execute: {step}")
        results.append(result)
    return {"results": results}

def synthesizer(state):
    final = llm.generate(f"Synthesize: {state['results']}")
    return {"final": final}

graph = StateGraph(State)
graph.add_node("planner", planner)
graph.add_node("executor", executor)
graph.add_node("synthesizer", synthesizer)
graph.set_entry_point("planner")
graph.add_edge("planner", "executor")
graph.add_edge("executor", "synthesizer")
graph.add_edge("synthesizer", END)
app = graph.compile()
```

The `State` TypedDict carries `task` → `plan` → `results` → `final`; each node reads what it needs and returns the fields it updates, and the graph edges encode the control flow explicitly.

### A hierarchical code review system

A more realistic example shows the full planner-coder-reviewer-fix cycle with conditional routing and a loop cap:

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional

class CodeReviewState(TypedDict):
    task: str                              # the coding task
    plan: List[str]                         # steps from the planner
    code: str                               # the code from the coder
    review: Optional[str]                   # the reviewer's feedback
    final_code: Optional[str]              # the fixed code
    iterations: int                         # how many review cycles

def planner(state):
    """Decompose the task into coding steps."""
    prompt = f"""You are a software architect. Decompose this task into 3-5 steps:
    Task: {state['task']}
    Output one step per line, no numbering."""
    plan = llm.invoke(prompt).split('\n')
    return {"plan": [s.strip() for s in plan if s.strip()]}

def coder(state):
    """Implement the plan as code."""
    prompt = f"""You are a senior engineer. Implement this plan as Python code:
    Plan: {chr(10).join(state['plan'])}
    Output only the code, no explanation."""
    code = llm.invoke(prompt)
    return {"code": code, "iterations": state.get("iterations", 0) + 1}

def reviewer(state):
    """Review the code for bugs and issues."""
    prompt = f"""You are a code reviewer. Find bugs, edge cases, and improvements.
    Code: {state['code']}
    If the code is acceptable, respond 'APPROVED'. Otherwise, list issues."""
    review = llm.invoke(prompt)
    return {"review": review}

def fixer(state):
    """Fix the issues found by the reviewer."""
    if "APPROVED" in state["review"]:
        return {"final_code": state["code"]}
    prompt = f"""Fix the issues in this code:
    Code: {state['code']}
    Issues: {state['review']}
    Output the corrected code."""
    fixed = llm.invoke(prompt)
    return {"code": fixed, "review": None}

def should_fix_or_finish(state):
    if state.get("final_code"):
        return END
    if state.get("iterations", 0) >= 3:  # cap at 3 review cycles
        return END
    if state.get("review") and "APPROVED" in state["review"]:
        return "fixer"
    return "coder"  # re-code if not approved

graph = StateGraph(CodeReviewState)
graph.add_node("planner", planner)
graph.add_node("coder", coder)
graph.add_node("reviewer", reviewer)
graph.add_node("fixer", fixer)
graph.set_entry_point("planner")
graph.add_edge("planner", "coder")
graph.add_edge("coder", "reviewer")
graph.add_conditional_edges("reviewer", should_fix_or_finish, {
    "fixer": "fixer",
    "coder": "coder",
    END: END,
})
graph.add_edge("fixer", END)
app = graph.compile()

result = app.invoke({"task": "Write a function to compute the Fibonacci sequence with memoization."})
print(result["final_code"] or result["code"])
```

Four design choices are worth noticing. The cycle cap of 3 iterations prevents infinite loops. Conditional routing lets the reviewer's output determine the next step. State threading means the code persists across iterations so the coder can incrementally fix it. And there are two terminal conditions — APPROVED or the iteration cap — so the graph always terminates.

This pattern (plan → execute → review → fix → repeat) is the canonical multi-agent code-generation workflow, used by Devin, Cursor's agent mode, and SWE-Agent internally.

## Cost and latency

Multi-agent systems multiply cost. A 4-agent pipeline where each agent makes 3 LLM calls costs 12× a single-agent call. Concretely (2026 pricing, Llama 3 70B self-hosted at $0.50/1M tokens):

- Single agent: 1 call, ~500 tokens output = ~$0.00025.
- 4-agent pipeline, 3 calls each, 500 tokens output each = $0.003 — 12× cost.
- 4-agent pipeline with reasoning model (o3-mini, 15K CoT per call): $0.18 — 720× cost.

Latency behaves the same way. Sequential multi-agent pays the sum of agent latencies (4 agents × 3s = 12s). Parallel multi-agent pays the max of agent latencies (~3s if all run in parallel). A pipeline with a reasoning model pays 4 × 30s = 120s — unacceptable for real-time use.

The production guidance that follows from these numbers: budget per request, and route to multi-agent only when the marginal capability justifies the marginal cost. Most production systems use multi-agent for batch or async tasks, not real-time chat.

## Production implications

Start single-agent, and move to multi-agent only when single-agent hits limits. LangGraph is the production standard for serious multi-agent — durable, observable, well-supported. Cost management is critical because multi-agent systems can burn 10-100x more tokens than single-agent, so budget per request. Observability is non-negotiable: trace every agent's actions, because without traces multi-agent is impossible to debug. And failure modes compound — if each agent has a 95% success rate, a 5-agent pipeline has 77% success — so plan for retries and fallbacks.

## Observability for multi-agent systems

Multi-agent systems need richer observability than single-agent ones. The five essentials are per-agent traces (which agent did what, when), token accounting per agent (cost attribution), state transitions (how the shared state evolved), failure attribution (which agent caused the failure), and cycle detection (alert on agents stuck in loops). The tooling landscape covers all of them: LangSmith (best for LangGraph), Langfuse (open-source), Arize Phoenix, and OpenTelemetry with LLM semconv.

## Coordination failure modes

Multi-agent systems have unique failure modes beyond single-agent issues, each with a standard remedy:

- **Echo chamber** — peer agents agree too quickly, missing errors. Fix: assign one agent as "devil's advocate" by default.
- **Deadlock** — two agents disagree indefinitely. Fix: timeout + arbitration (a third agent decides).
- **Livelock** — agents keep revising without converging. Fix: iteration cap + "declare done after N rounds."
- **Cascade errors** — a planner error corrupts all downstream agents. Fix: planner verification (a separate agent checks the plan before execution).
- **Context bloat** — shared state grows unboundedly. Fix: state summarization (compress old entries).
- **Token budget exhaustion** — agents run out of context. Fix: per-agent token budget + handoff (a new agent takes over with a summary).

## Common pitfalls

The recurring mistakes are architectural. Too many agents means coordination overhead exceeds the benefit. No clear roles means agents step on each other and do redundant work. Unbounded conversation means peer-swarm agents can talk forever — always set turn limits. No global state means agents repeat each other's work without shared memory. And forgetting that LLMs are stochastic — same input, different outputs — matters more here, because multi-agent systems amplify this variance.

## Why this matters

Multi-agent is the frontier of agentic AI in 2026; most ambitious agent products (Devin, Cursor, Claude Code) use multi-agent internally. It enables tasks no single agent can do: complex software engineering, multi-source research, and content production pipelines. For production, the frameworks (LangGraph, AutoGen, PydanticAI) are mature enough for serious use, and the architectural patterns (hierarchical, swarm, blackboard) translate directly from classical AI to LLM agents.

## Further reading

Wu et al. (2023), *AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation*. Hong et al. (2023), *MetaGPT: Meta Programming for Multi-Agent Collaborative Framework*. LangGraph docs: https://langchain-ai.github.io/langgraph/

## Interview questions

These distinctions come up frequently in interviews; the short-form answers are worth knowing cold.

**When should you use a multi-agent system instead of a single agent?** Use multi-agent when (1) the task naturally decomposes into specialist roles, (2) a single LLM's context can't hold all needed information, (3) different sub-tasks need different models (reasoning for planning, fast for execution), (4) you need verification (one agent produces, another critiques), (5) the task is long-running and benefits from parallelism. Start single-agent; move to multi-agent only when you hit a clear ceiling.

**Compare hierarchical, peer swarm, and blackboard architectures.** Hierarchical (planner-executor): clear division of labor, predictable, rigid — best for multi-step workflows. Peer swarm: agents discuss as equals, robust via diversity, but unbounded conversation — best for brainstorming and verification. Blackboard: shared state that all agents read/write, decoupled but coordination-heavy — best for long-running complex tasks with shared context.

**How do you prevent multi-agent systems from looping forever?** Four safeguards: (1) iteration cap per agent and per workflow, (2) timeout per agent and per overall task, (3) convergence detection (state stops changing → terminate), (4) cycle detection in graph-based systems (LangGraph has built-in recursion limits). Combine all four; no single safeguard is sufficient.

**How do you attribute cost in a multi-agent system?** Per-agent token accounting. Each agent's LLM calls are logged with prompt/completion token counts and cost. Aggregate by agent role (planner, executor, reviewer) to see which roles dominate cost. Use this to decide where to optimize (e.g., if the planner is 50% of cost, consider a smaller planner model).

**What's the difference between a multi-agent system and a workflow with LLM calls?** A workflow has a fixed control flow — the LLM is called at specific points but doesn't decide the next step. A multi-agent system has LLMs deciding the next step — the control flow is dynamic. Workflows are predictable and debuggable; multi-agent systems are flexible and powerful. Most production systems are hybrids: a workflow with embedded agent decision points.

**Why is LangGraph the production standard for multi-agent in 2026?** Four reasons: (1) durable execution — survives crashes via checkpointing; (2) observable — LangSmith integration gives full traces; (3) graph-based — explicit state and edges make the control flow debuggable; (4) mature — battle-tested in production at scale. Alternatives (AutoGen, CrewAI) are improving but lag on durability and observability.

## See also

- [[Agents and Tooling MOC]] — orientation for the agents and tooling area.
- [[Communication Patterns]] — how agents exchange messages.
- [[Coordination and Consensus]] — task allocation, consensus, and negotiation mechanisms.
- [[Enterprise Multi-Agent Architectures]] — tenancy, audit, and governance for production deployments.
- [[Planner-Executor Pattern]] — the most common multi-agent pattern in detail.
- [[ReAct Pattern]] — the single-agent pattern that composes into multi-agent.
- [[Agent vs Workflow vs LLM Application]] — the foundational distinction.
- [[LangGraph]] — the production standard for multi-agent orchestration.
- [[AutoGen]] — conversational multi-agent framework.
- [[CrewAI]] — role-based multi-agent framework.
- [[Framework Selection Guide]] — choosing a framework.
- [[Build a Multi-Agent System]] — a project implementing these patterns.
