---
title: Build a Multi-Agent System
type: tutorial
aliases: [Multi-Agent System, Planner Executor, Build a Multi-Agent]
tags: [project, multi-agent, planner-executor, implementation]
sources: ["06 - Build a Multi-Agent System"]
created_index: 7
---

A multi-agent system splits one hard request across several cooperating LLM agents instead of asking a single agent to do everything. This capstone builds the hierarchical pattern — a planner agent that decomposes tasks into subtasks, specialized executor agents (research, code, write) that carry them out, and a synthesizer that combines the results — in roughly 200 lines of Python. The architecture and its alternatives are covered in [[Multi-Agent Architectures]]; this note is the hands-on build, indexed alongside the other capstones in [[Projects MOC]].

> [!info] TL;DR
> Build a multi-agent system with a planner agent (decomposes tasks) and executor agents (specialized workers) in ~200 lines of Python. The planner creates a step-by-step plan, dispatches subtasks to specialized executors (research, code, write), and synthesizes results. This is the hierarchical multi-agent pattern used in production systems.

## Project goals

By the end of this project, you will have built:

1. A planner agent that decomposes tasks into subtasks.
2. Specialized executor agents (research, code, write).
3. A task queue and dispatch system.
4. Result synthesis (the planner combines executor outputs).
5. Tracing and observability for the multi-agent flow — extend it with the [[Build an Agent Observability Platform]] capstone.

The implementation uses OpenAI's API (or any OpenAI-compatible endpoint) and demonstrates the hierarchical pattern from [[Enterprise Multi-Agent Architectures]].

## Architecture

The user request flows to the planner, which produces a step-by-step plan; the dispatcher routes each subtask to the matching executor; results accumulate and flow back through the planner's synthesis step into a final response:

```mermaid
graph TD
  User[User request] --> Planner[Planner Agent]
  Planner --> Plan[Step-by-step plan]
  Plan --> Dispatcher[Task dispatcher]
  Dispatcher --> R[Research executor]
  Dispatcher --> C[Code executor]
  Dispatcher --> W[Writer executor]
  R --> Results[Task results]
  C --> Results
  W --> Results
  Results --> Synthesizer[Planner: synthesize]
  Synthesizer --> Final[Final response]
  Final --> User
```

## Prerequisites

```bash
pip install openai pydantic
```

## Define the agent and task types

Everything starts with typed data. Pydantic models define the three objects that flow through the system — a `SubTask` (with an ID, description, executor type, and dependencies), a `Plan` (the subtasks plus synthesis instructions), and a `TaskResult` (the outcome of executing one subtask, with success status and an optional error):

```python
import openai
import json
from pydantic import BaseModel, Field
from typing import Optional

class SubTask(BaseModel):
    """A subtask in a multi-step plan."""
    id: str = Field(description="Unique task ID, e.g., 'task_1'")
    description: str = Field(description="What the subtask should accomplish")
    agent_type: str = Field(description="Which executor: 'research', 'code', or 'write'")
    dependencies: list[str] = Field(default=[], description="IDs of tasks that must complete first")

class Plan(BaseModel):
    """A plan decomposed into subtasks."""
    subtasks: list[SubTask]
    synthesis_instructions: str = Field(description="How to combine subtask results into the final answer")

class TaskResult(BaseModel):
    """The result of executing a subtask."""
    task_id: str
    success: bool
    output: str
    error: Optional[str] = None
```

## The planner agent

The planner decomposes the user's request into subtasks. Its system prompt enumerates the available executor types and constrains the plan shape (2–5 subtasks, each with a clear description, an executor type, and explicit dependencies); structured output parsing turns the response directly into a `Plan` object. This is the decomposition half of the [[Planner-Executor Pattern]].

```python
PLANNER_SYSTEM_PROMPT = """You are a planner agent. Your job is to decompose complex tasks into subtasks 
that can be executed by specialized agents.

Available executor types:
- research: for finding information, web search, fact-checking
- code: for writing, running, or debugging code
- write: for writing prose, summaries, explanations

Create a plan with 2-5 subtasks. Each subtask should:
1. Have a clear, specific description
2. Specify which executor type should handle it
3. List any dependencies (other subtasks that must complete first)

After the subtasks, provide synthesis instructions explaining how to combine 
the subtask results into a final answer.
"""

def plan_task(user_request: str, model: str = "gpt-4o-mini") -> Plan:
    """Use the planner to decompose the user's request."""
    response = openai.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {"role": "user", "content": f"Decompose this task: {user_request}"},
        ],
        response_format=Plan,
        temperature=0.2,
    )
    return response.choices[0].message.parsed
```

## The executor agents

Each executor type has its own system prompt and capabilities. The `execute_subtask` function routes by `agent_type`, builds context from the subtask's completed dependencies, and wraps the API call in error handling so one failed executor doesn't crash the run:

```python
RESEARCH_PROMPT = """You are a research agent. Your job is to find information and answer factual questions.
- Provide accurate, well-sourced information
- If you're unsure, say so rather than guessing
- Cite sources when possible
- Be concise but complete
"""

CODE_PROMPT = """You are a code agent. Your job is to write, analyze, or debug code.
- Write clean, working code
- Include brief comments for non-obvious parts
- If debugging, explain the issue and the fix
- Use the appropriate language for the task
"""

WRITER_PROMPT = """You are a writing agent. Your job is to write clear, engaging prose.
- Adapt your style to the audience and purpose
- Be concise but complete
- Use structure (headings, lists) when helpful
- Proofread for clarity and grammar
"""

EXECUTORS = {
    "research": RESEARCH_PROMPT,
    "code": CODE_PROMPT,
    "write": WRITER_PROMPT,
}

def execute_subtask(subtask: SubTask, context: dict, model: str = "gpt-4o-mini") -> TaskResult:
    """Execute a subtask using the appropriate executor."""
    if subtask.agent_type not in EXECUTORS:
        return TaskResult(
            task_id=subtask.id,
            success=False,
            output="",
            error=f"Unknown agent type: {subtask.agent_type}"
        )
    
    # Build context from dependencies
    context_str = ""
    for dep_id in subtask.dependencies:
        if dep_id in context:
            context_str += f"\n\nResult from {dep_id}:\n{context[dep_id]}"
    
    user_message = f"""Task: {subtask.description}

Context from previous tasks:{context_str}

Please complete this task."""

    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": EXECUTORS[subtask.agent_type]},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,
            max_tokens=1000,
        )
        
        return TaskResult(
            task_id=subtask.id,
            success=True,
            output=response.choices[0].message.content,
        )
    except Exception as e:
        return TaskResult(
            task_id=subtask.id,
            success=False,
            output="",
            error=str(e),
        )
```

## The dispatcher

The dispatcher manages the task queue, respecting dependencies. Each iteration finds every pending task whose dependencies are all completed and executes it; failed tasks are marked completed with error context so downstream tasks still run; and a deadlock check plus safety limit protect against cyclic dependencies:

```python
def dispatch_plan(plan: Plan, model: str = "gpt-4o-mini") -> dict:
    """Execute all subtasks in dependency order."""
    context = {}  # task_id -> output
    results = {}  # task_id -> TaskResult
    
    # Build dependency graph
    pending = {t.id: t for t in plan.subtasks}
    completed = set()
    
    max_iterations = len(plan.subtasks) * 2  # safety limit
    iteration = 0
    
    while pending and iteration < max_iterations:
        iteration += 1
        # Find tasks whose dependencies are all completed
        ready = [
            t for t in pending.values()
            if all(dep in completed for dep in t.dependencies)
        ]
        
        if not ready:
            # Deadlock: no task can proceed
            print(f"Deadlock! Pending tasks: {list(pending.keys())}")
            break
        
        # Execute ready tasks (could parallelize here)
        for task in ready:
            print(f"  Executing {task.id} ({task.agent_type}): {task.description[:50]}...")
            result = execute_subtask(task, context, model)
            results[task.id] = result
            
            if result.success:
                context[task.id] = result.output
                completed.add(task.id)
            else:
                print(f"  Task {task.id} failed: {result.error}")
                # Mark as completed to avoid deadlock, but with error context
                context[task.id] = f"[Task failed: {result.error}]"
                completed.add(task.id)
            
            del pending[task.id]
    
    return context
```

## The synthesizer

The planner combines subtask results into the final answer. The synthesis prompt insists on integration — resolving contradictions and attributing contributions — rather than concatenation:

```python
SYNTHESIS_PROMPT = """You are a synthesis agent. Your job is to combine the results of multiple subtasks 
into a coherent final answer.

Guidelines:
- Integrate information from all subtask results
- Resolve any contradictions
- Present the answer clearly and completely
- Cite which subtask contributed which information
"""

def synthesize_results(user_request: str, plan: Plan, context: dict, 
                       model: str = "gpt-4o-mini") -> str:
    """Combine subtask results into the final answer."""
    context_str = ""
    for task in plan.subtasks:
        if task.id in context:
            context_str += f"\n\n--- {task.id} ({task.agent_type}) ---\n{context[task.id]}"
    
    user_message = f"""Original request: {user_request}

Synthesis instructions: {plan.synthesis_instructions}

Subtask results:{context_str}

Please synthesize these into a final answer."""

    response = openai.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYNTHESIS_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.3,
        max_tokens=1500,
    )
    
    return response.choices[0].message.content
```

## The orchestrator

Tie everything together with tracing. The orchestrator runs plan → execute → synthesize and records every step into a trace dictionary — the seed of the observability layer:

```python
def run_multi_agent(user_request: str, model: str = "gpt-4o-mini") -> dict:
    """Run the full multi-agent pipeline."""
    trace = {
        "request": user_request,
        "steps": [],
    }
    
    # Step 1: Plan
    print("Planning...")
    plan = plan_task(user_request, model)
    trace["steps"].append({
        "step": "plan",
        "subtasks": [t.model_dump() for t in plan.subtasks],
    })
    print(f"Created plan with {len(plan.subtasks)} subtasks")
    
    # Step 2: Execute
    print("Executing...")
    context = dispatch_plan(plan, model)
    trace["steps"].append({
        "step": "execute",
        "context": context,
    })
    
    # Step 3: Synthesize
    print("Synthesizing...")
    final_answer = synthesize_results(user_request, plan, context, model)
    trace["steps"].append({
        "step": "synthesize",
        "final_answer": final_answer,
    })
    
    return {
        "answer": final_answer,
        "plan": plan,
        "context": context,
        "trace": trace,
    }

# Usage:
# result = run_multi_agent("Write a Python function to compute fibonacci numbers, 
#   explain how it works, and create documentation for it.")
# print(result["answer"])
```

## Multi-agent in action

A request that naturally decomposes — research, code, documentation — shows the system end to end:

```python
# Example request that benefits from multi-agent decomposition
request = """
Build a simple REST API for a todo app:
1. Research best practices for REST API design
2. Write the Python code (using FastAPI)
3. Write API documentation
"""

result = run_multi_agent(request)
print("=== PLAN ===")
for task in result["plan"].subtasks:
    print(f"  {task.id} ({task.agent_type}): {task.description}")

print("\n=== FINAL ANSWER ===")
print(result["answer"])
```

## Extensions

Once the basic multi-agent system works, try:

1. **Parallel execution**: execute independent subtasks concurrently (using `asyncio` or `concurrent.futures`).
2. **Human-in-the-loop**: add approval steps for high-risk subtasks (see [[Human-in-the-Loop Patterns]]).
3. **Reflection**: let executors critique and revise their own outputs (see [[Reflection]]).
4. **Dynamic replanning**: if a subtask fails, let the planner create a new plan.
5. **Memory**: persist context across multiple user requests (see [[Memory Types]]).
6. **Tool use**: give executors access to tools (web search, code execution) via [[Function Calling]].
7. **Visualization**: render the plan and execution as a graph.
8. **Streaming**: stream the synthesizer's output to the user as it's generated.

## Common pitfalls

Six failure patterns account for most broken multi-agent builds.

### Plans too granular or too coarse

If plans have too many subtasks, coordination overhead dominates. If too few, the multi-agent approach adds no value. Aim for 2–5 subtasks per plan.

### Dependency deadlocks

If subtask A depends on B, and B depends on A, the dispatcher deadlocks. The planner should produce acyclic dependencies. The dispatcher includes a deadlock check.

### No context passing

If executors don't receive context from dependencies, they produce disconnected outputs. Always pass dependency results as context.

### Synthesizer just concatenates

The synthesizer should integrate, not just concatenate. Emphasize this in the synthesis prompt.

### No error handling

If a subtask fails and the system doesn't handle it, subsequent tasks may receive garbage context. Mark failed tasks and proceed with error context.

### No tracing

Without traces, multi-agent bugs are impossible to debug. Log every step, every subtask, every result.

## Production considerations

This minimal implementation is for learning. Production multi-agent systems add:

- **Async execution**: concurrent subtask execution for speed.
- **State persistence**: resume across sessions.
- **Observability**: distributed tracing (OpenTelemetry), metrics, audit logs.
- **Cost tracking**: per-subtask cost attribution.
- **Guardrails**: input/output validation for each agent.
- **Policy enforcement**: restrict which agents can call which tools.
- **Multi-tenancy**: isolate tenants' agents and context.

For production, use frameworks like [[LangGraph]] or the [[OpenAI SDK and Agents SDK]].

## Production hardening checklist

The upgrades that make the 200-line demo survivable in production:

1. **Typed messages**: use Pydantic models for inter-agent messages; reject untyped messages.
2. **Dead-letter queue**: failed messages go to a DLQ for inspection; don't silently drop.
3. **Idempotency keys**: every task carries an idempotency key; executors dedupe on it.
4. **Per-agent timeouts**: cap every executor at 60s; abort and re-plan on timeout.
5. **Concurrency limit**: cap parallel executors at 4–8; too many parallel calls overwhelm downstream tools.
6. **Result validation**: every executor result validated against a schema; reject and re-execute on mismatch.
7. **Tracing**: every agent message carries a `trace_id`; visualize in LangSmith / Langfuse.
8. **Cost tracking**: per-agent token cost; alert if total cost >\$X per task.
9. **Checkpointing**: persist plan + completed subtasks; resume on failure.
10. **Replanning on failure**: if an executor fails 3x, the planner re-plans around the failed subtask.
11. **Human-in-the-loop**: for sensitive subtasks (e.g., code deployment), require human approval before executor runs.
12. **Observability dashboard**: per-agent task queue depth, latency, error rate, cost.

## Modern developments (2024–2026)

Multi-agent practice consolidated between 2024 and 2026; these shifts matter for any system built today.

### LangGraph becomes the standard

LangGraph (LangChain's graph-based agent framework) is the 2025–2026 default for multi-agent systems in Python. It supports stateful agents, branching, parallel execution, human-in-the-loop, and persistent state. Alternatives: OpenAI Agents SDK (simpler, OpenAI-only), AutoGen (Microsoft, research-focused), CrewAI (role-based, simpler).

### Agent communication via structured messages

The early "free-form text between agents" pattern is dead. Modern multi-agent systems use **structured messages**: typed payloads (Pydantic models) with clear semantics. The planner emits `SubTask` objects; executors emit `SubTaskResult` objects. This eliminates parsing failures and enables schema validation.

### Swarm patterns (OpenAI Swarm, CrewAI)

An alternative to hierarchical planner-executor is the **swarm** pattern: agents hand off tasks to each other based on specialization. A `triage_agent` routes to `billing_agent` or `tech_support_agent` based on the query. Each agent can hand off back to triage or to another specialist. Simpler than hierarchical for customer service / routing use cases.

### Long-running multi-agent systems

Multi-day agent tasks (research, code migration) require: (1) **Checkpointing** — save state every N minutes; resume on crash. (2) **Async execution** — agents run as background jobs, not blocking the user. (3) **Human-in-the-loop checkpoints** — pause at key milestones for human review. (4) **Cost monitoring** — abort if cost exceeds budget. (5) **Audit log** — every agent decision logged for post-hoc review. [[Autonomous Agent Lifecycles]] covers the full lifecycle.

### Agent coordination via blackboard pattern

For complex tasks with shared state, the **blackboard** pattern (from classic AI) is back: a shared workspace where agents post findings, claims, and hypotheses. Other agents read and respond. The blackboard enforces consistency (no two agents can contradict without a resolution step). Useful for collaborative research, design, and analysis tasks.

## Interview questions

**When would you use a multi-agent system instead of a single agent?** Use multi-agent when: (1) the task decomposes into specialized roles (research, code, write) — specialization beats generalization. (2) Context limits matter — each agent has its own context window, avoiding the single-agent context overflow. (3) Parallelism helps — independent subtasks run concurrently. (4) Different models for different roles — cheap model for routing, expensive model for synthesis. Avoid multi-agent when: (1) the task is simple (a single agent handles it in one tool call). (2) Latency is critical (multi-agent has coordination overhead). (3) Debugging complexity is a concern (multi-agent traces are harder to follow).

**How do you prevent the planner from generating an unrealistic plan?** (1) **Plan schema validation** — require each subtask to have a clear objective, executor type, and success criteria. (2) **Plan critic** — a separate agent reviews the plan for feasibility before execution. (3) **Step-by-step execution with replanning** — execute one subtask, observe the result, then decide the next subtask (don't pre-commit to all subtasks). (4) **Cost estimation** — estimate per-subtask cost before execution; abort if total exceeds budget. (5) **Plan templates** — for common task types, use a pre-validated template; only free-form plan for novel tasks.

**How do you handle executor failures in a multi-agent system?** Layered strategy: (1) **Retry** — transient failures (network, rate limit) retry 3x with backoff. (2) **Alternative executor** — if `code_executor` fails, try `code_executor_v2` or a different model. (3) **Replanning** — if a subtask fails irrecoverably, return to planner with the failure context; planner generates a new plan around the failed subtask. (4) **Graceful degradation** — if all retries fail, return partial results with a clear "incomplete" flag. (5) **Dead-letter queue** — failed tasks go to DLQ for human review; don't silently lose them.

**How do you debug a multi-agent system?** (1) **Tracing** — every agent message carries a `trace_id`; visualize in LangSmith / Langfuse. (2) **Replay** — record all agent messages; replay offline to reproduce issues. (3) **Per-agent metrics** — latency, error rate, cost per agent; spot the bottleneck. (4) **Message inspection** — inspect every inter-agent message for correctness (was the planner's plan well-formed? was the executor's result valid?). (5) **A/B testing** — run the same task with different planner/executor configs; compare outcomes.

**How do you handle agent coordination (avoiding conflicts)?** Depends on the pattern: (1) **Hierarchical (planner-executor)** — no conflicts; planner sequences and dispatches. (2) **Parallel** — ensure subtasks are independent; if not, run sequentially or use a shared state mediator. (3) **Blackboard** — agents post claims; a consistency checker resolves conflicts before any agent acts on them. (4) **Negotiation** — for resource conflicts (two agents want the same tool), use a bidding protocol; highest-priority bid wins.

**How do you evaluate a multi-agent system?** Three layers: (1) **Per-agent metrics** — each agent has its own success criteria (planner: plan completeness; executor: task success rate). (2) **End-to-end metrics** — task completion rate, total cost, total latency, user satisfaction. (3) **Coordination metrics** — number of replans, number of conflicts, message overhead. Compare against a single-agent baseline to justify the multi-agent complexity.

## See also

- [[Projects MOC]] — the projects index.
- [[Build a Mini Agent]] — single-agent foundation.
- [[Build a Code Agent]] — a specialized executor in depth.
- [[Build an Agent Observability Platform]] — the tracing and observability layer.
- [[Build a Mini RAG Pipeline]] and [[Build a Mini MoE]] — sibling mini-projects.
- [[Multi-Agent Architectures]] — architecture patterns.
- [[Communication Patterns]] — message patterns.
- [[Coordination and Consensus]] — coordination protocols.
- [[Enterprise Multi-Agent Architectures]] — production patterns.
- [[Planner-Executor Pattern]] — the pattern implemented here.
- [[LangGraph]], [[AutoGen]], [[CrewAI]], and [[OpenAI SDK and Agents SDK]] — production frameworks.
- [[Autonomous Agent Lifecycles]] and [[Human-in-the-Loop Patterns]] — long-running and approval patterns.
- [[Build Attention and Transformer From Scratch]]
