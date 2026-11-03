---
title: LangGraph
type: concept
aliases: [LangGraph, Agent Orchestration]
tags: [framework, langgraph, agents, state-machine, orchestration]
sources: ["03 - LangGraph"]
created_index: 17
---

LangGraph is LangChain's agent orchestration framework, built on a graph-based model: agents are nodes, transitions are edges, and state flows through the graph. Unlike LangChain's `AgentExecutor`, which is a fixed loop, LangGraph gives you explicit control over the agent's execution path, supporting cycles, conditional routing, human-in-the-loop, and persistent state. It is the recommended approach for production agent applications in the LangChain ecosystem. This note covers the graph model and its core concepts, the key production features, common agent patterns expressed as graphs, strengths and weaknesses, and production guidance.

> [!info] TL;DR
> LangGraph is LangChain's agent orchestration framework, built on a graph-based model: agents are nodes, transitions are edges, and state flows through the graph. Unlike LangChain's `AgentExecutor` (which is a fixed loop), LangGraph gives you explicit control over the agent's execution path, supporting cycles, conditional routing, human-in-the-loop, and persistent state. LangGraph is the recommended approach for production agent applications in the LangChain ecosystem.

## Overview

LangGraph is developed by LangChain Inc. (2024). It is available in Python and JavaScript/TypeScript, under the MIT license. It is actively developed and is the recommended framework for LangChain agents.

## Why LangGraph exists

LangChain's original `AgentExecutor` was a black box: it ran an LLM in a loop, called tools, and returned when the LLM stopped calling tools. This worked for simple cases but failed for five classes of problem:

- **Complex workflows**: multi-step processes with branching logic.
- **Human-in-the-loop**: pausing for user approval mid-execution.
- **Persistent state**: resuming a conversation across sessions.
- **Multi-agent coordination**: orchestrating multiple agents with explicit roles.
- **Error recovery**: retrying specific steps, falling back to alternatives.

LangGraph was built to address these. The core idea: model the agent as a **graph** where you control every transition.

## Core concepts

### State

LangGraph agents operate on a shared state object — typically a TypedDict or Pydantic model:

```python
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]  # accumulates messages
    documents: list  # retrieved documents
    iteration: int
```

The state flows through the graph and is updated by each node. The `Annotated` types specify how updates merge (e.g., `add_messages` appends rather than replaces).

### Nodes

Nodes are functions that take the state and return updates:

```python
def call_model(state: AgentState) -> dict:
    response = llm.invoke(state["messages"])
    return {"messages": [response]}  # appends to messages

def call_tool(state: AgentState) -> dict:
    tool_result = execute_tool(state["messages"][-1].tool_calls)
    return {"messages": [tool_result]}
```

Each node reads from the state, does work, and returns a partial state update.

### Edges

Edges define transitions between nodes, and there are two kinds: a **direct edge** always goes from A to B, while a **conditional edge** goes to B or C based on a function.

```python
from langgraph.graph import StateGraph, END

graph = StateGraph(AgentState)
graph.add_node("agent", call_model)
graph.add_node("tools", call_tool)

graph.set_entry_point("agent")

# Conditional edge: after agent, either call tools or end
def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

graph.add_conditional_edges("agent", should_continue)
graph.add_edge("tools", "agent")  # after tools, back to agent

app = graph.compile()
```

### Cycles

The graph can have cycles (e.g., `agent → tools → agent → tools → ...`). This is how agent loops are implemented — but unlike `AgentExecutor`, you have explicit control over the cycle and can add conditions, limits, or interruptions.

```mermaid
graph LR
  Start([Start]) --> Agent[Agent node: LLM call]
  Agent -->|has tool calls| Tools[Tools node: execute]
  Tools --> Agent
  Agent -->|no tool calls| End([End])
```

## Key features

### Human-in-the-loop

LangGraph supports pausing execution for human approval:

```python
app = graph.compile(
    interrupt_before=["sensitive_tool"],
    checkpointer=memory_checkpointer,
)

# Run until the interrupt
result = app.invoke(input, config={"configurable": {"thread_id": "1"}})

# Human reviews, then continues
result = app.invoke(None, config={"configurable": {"thread_id": "1"}})
```

This is essential for high-stakes tool calls (sending emails, modifying production data) where human oversight is required.

### Persistent state

LangGraph supports checkpointer backends (in-memory, SQLite, Postgres) that save state after each node execution. This enables three capabilities. **Resuming across sessions**: a user can close the app and resume the conversation later. **Time travel**: revert to a previous state and explore a different path. **Concurrency**: multiple users can run agents simultaneously, each with isolated state.

### Streaming

LangGraph streams events as the graph executes, at three levels: **node updates** stream the output of each node as it completes, **token streaming** delivers LLM tokens as they're generated, and **state updates** stream the evolving state. This enables real-time UI updates in applications.

### Subgraphs

A node can be a subgraph — another LangGraph agent. This enables hierarchical multi-agent systems: a top-level orchestrator delegates to specialized sub-agents.

### Time travel and replay

Because state is checkpointed, you can replay execution from any point, modify state and re-run from that point, and debug by inspecting state at each node. This is invaluable for debugging complex agent behaviors.

## Common patterns

### The ReAct loop

The standard ReAct pattern ([[ReAct Pattern]]) is a simple LangGraph. The `agent` node has the LLM decide the action, the `tools` node executes the tool, a conditional edge routes to `tools` if there are tool calls and to the end otherwise, and an edge runs from `tools` back to `agent`.

### Plan-and-execute

A planner node generates a multi-step plan and an executor node executes each step, in the shape of the [[Planner-Executor Pattern]]. The `planner` node has the LLM produce a list of steps, the `executor` node executes the current step, and a conditional edge continues if more steps remain and ends otherwise.

### Multi-agent with routing

A router node classifies the query and specialized agent nodes handle different query types. The `router` node classifies the query type, a conditional edge routes to `billing_agent`, `tech_agent`, or `general_agent`, and each agent has its own subgraph.

### Reflection

After generating an answer, a reflection node critiques it; if the critique is negative, the answer is regenerated — the [[Reflection]] pattern in graph form. The `generator` node produces the answer, the `critic` node evaluates it, and a conditional edge ends if the critique is positive or loops back to the generator otherwise.

## Comparison to alternatives

| Framework     | Approach                          | Strengths                          | Weaknesses                       |
|---------------|-----------------------------------|------------------------------------|----------------------------------|
| LangGraph     | Graph-based, explicit state       | Control, persistence, HiTL         | More verbose than AgentExecutor  |
| AgentExecutor | Black-box loop                    | Simple for basic cases             | Limited control, no HiTL         |
| CrewAI        | Role-based                        | Intuitive for team metaphors       | Less flexible than graph-based   |
| AutoGen       | Conversational                    | Multi-agent conversations          | Less structured state            |
| OpenAI Swarm  | Lightweight handoffs              | Simple                             | Limited features, experimental   |

LangGraph is the most feature-complete agent framework for production use. Its verbosity is the trade-off for explicit control.

## Strengths

### Explicit control

Every transition is visible in the graph definition. No magic, no surprising defaults. This makes debugging and auditing much easier than black-box agent executors.

### Persistence and resumability

Checkpointing enables long-running agents that span sessions, which is essential for production applications.

### Human-in-the-loop

First-class support for pausing execution, getting human input, and resuming. This is hard to build correctly from scratch; LangGraph handles it.

### Observability

LangGraph integrates with LangSmith for detailed traces of every node execution, state transition, and LLM call.

### Multi-agent support

Subgraphs enable hierarchical multi-agent systems with clean separation of concerns.

## Weaknesses

### Verbose

Even simple agents require significant boilerplate (state definition, node functions, edges, compilation). For very simple use cases, this is overkill.

### Learning curve

The graph-based model requires understanding state management, conditional edges, and checkpointing. Developers familiar with imperative agent loops may find it unintuitive.

### Performance overhead

State checkpointing and serialization add overhead. For high-throughput applications, a simpler loop may be faster.

### LangChain ecosystem dependency

LangGraph is part of the LangChain ecosystem. While it can be used standalone, it works best with LangChain's model wrappers, tool definitions, and LangSmith observability.

## When to use LangGraph

### Good fit

LangGraph is a good fit for **production agents**, where explicit control and persistence are essential; **human-in-the-loop workflows**, where pausing for approval is a first-class feature; **multi-agent systems**, where subgraphs enable clean orchestration; **long-running workflows**, where checkpointing enables resumption across sessions; and **complex state**, when the agent's state is more than just a message list.

### Poor fit

It is a poor fit for **simple chatbots**, where a basic LLM call with history is enough; **high-throughput applications**, where the overhead matters; and **non-Python ecosystems**, since LangGraph is Python-first and the JS version lags.

## Production patterns

### Use persistent checkpointing

For any agent that users interact with, use Postgres-backed checkpointing. This enables session resumption and crash recovery.

### Set iteration limits

Even with explicit control, cycles can loop forever. Add a maximum iteration count and a timeout.

### Stream aggressively

Stream node updates and tokens to the UI. LangGraph's streaming is well-designed and improves perceived performance dramatically.

### Trace everything

Integrate with LangSmith (or OpenTelemetry) for detailed traces. Without traces, debugging multi-step agents is nearly impossible.

### Test with eval sets

Build a test set of (input, expected behavior) pairs. Run them against the graph after every change. LangSmith's eval features help here.

## See also

- [[Agents and Tooling MOC]] — orientation for the agents and tooling area.
- [[LangChain]] — the umbrella framework LangGraph grew out of.
- [[ReAct Pattern]] — the standard agent loop, expressible as a two-node graph.
- [[Planner-Executor Pattern]] — plan-and-execute as a LangGraph pattern.
- [[Reflection]] — generator-critic cycles in graph form.
- [[Human-in-the-Loop Patterns]] — the approval workflows that interrupt points enable.
- [[OpenAI SDK and Agents SDK]] — the handoff-based alternative with less control.
- [[LlamaIndex]] — the RAG-focused framework with a similar workflow system.
- [[DSPy]] — declarative prompt optimization.
- [[Framework Selection Guide]] — overall decision guidance across frameworks.
