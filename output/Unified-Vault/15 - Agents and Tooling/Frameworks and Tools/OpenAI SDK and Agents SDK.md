---
title: OpenAI SDK and Agents SDK
type: concept
aliases: [OpenAI SDK, OpenAI Agents SDK, OpenAI Python SDK]
tags: [framework, openai, sdk, agents-sdk]
sources: ["06 - OpenAI SDK and Agents SDK"]
created_index: 20
---

The OpenAI Python SDK is the official client for the OpenAI API: a thin, type-safe wrapper that doubles as the reference implementation for LLM API clients. On top of it sits the OpenAI Agents SDK (released 2024), a lightweight agent framework built around four primitives — agents, handoffs, guardrails, and tracing. Together they form the "official" OpenAI stack: minimal abstractions, close to the API, with production-grade tooling. This note covers the base SDK's usage and trade-offs, the Agents SDK's primitives, when the stack fits, and the production patterns for using it well.

> [!info] TL;DR
> The OpenAI Python SDK is the official client for the OpenAI API — simple, well-documented, and the reference implementation for LLM API clients. The OpenAI Agents SDK (released 2024) is a lightweight agent framework built on top of the SDK, providing primitives for agents, handoffs, guardrails, and tracing. Together, they represent the "official" OpenAI stack: minimal abstractions, close to the API, with production-grade tooling.

## The OpenAI Python SDK

### Overview

The SDK is developed by OpenAI. Its primary language is Python, with implementations in JavaScript, .NET, Go, and others as well. It is MIT-licensed and actively developed, and it is the reference LLM API client.

### Design philosophy

The OpenAI SDK is deliberately minimal. It is a thin wrapper over the HTTP API, and the base SDK ships no abstractions for prompts, chains, or agents. It is type-safe, well-documented, and supports streaming. It is also effectively provider-agnostic: many other providers ([[15 - Agents and Tooling/Frameworks and Tools/vLLM|vLLM]], Together, Anyscale) implement OpenAI-compatible APIs, so the SDK works with them too.

### Core usage

Chat completions, streaming, and function calling all flow through one client object:

```python
from openai import OpenAI

client = OpenAI(api_key="sk-...")

# Basic chat completion
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"},
    ],
    temperature=0.7,
)
print(response.choices[0].message.content)

# Streaming
stream = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Write a poem"}],
    stream=True,
)
for chunk in stream:
    print(chunk.choices[0].delta.content or "", end="")

# Function calling
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get weather for a location",
        "parameters": {
            "type": "object",
            "properties": {"location": {"type": "string"}},
            "required": ["location"],
        },
    },
}]

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "What's the weather in NYC?"}],
    tools=tools,
)

if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    # Execute the tool, then continue the conversation
```

### Embeddings

Embeddings use the same client and return fixed-size vectors:

```python
response = client.embeddings.create(
    model="text-embedding-3-small",
    input="Text to embed",
)
embedding = response.data[0].embedding  # 1536-dim vector
```

### Structured outputs

The SDK can parse responses directly into Pydantic models:

```python
from pydantic import BaseModel

class Person(BaseModel):
    name: str
    age: int

response = client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Extract: John is 30 years old"}],
    response_format=Person,
)
person = response.choices[0].message.parsed  # Person(name="John", age=30)
```

Structured outputs use JSON Schema to constrain the model's output, guaranteeing valid JSON that matches your schema.

### Strengths

**Simplicity.** The SDK is a thin wrapper. No magic, no heavy abstractions. You can read the source and understand exactly what's happening.

**Documentation.** OpenAI's documentation is excellent, with examples for every feature. The SDK follows the API closely, so API docs apply directly.

**Provider compatibility.** Because many providers implement OpenAI-compatible APIs, you can use the same SDK with vLLM, Together, Anyscale, Groq, and others by changing the `base_url` and `api_key`.

**Structured outputs.** The `response_format` parameter with Pydantic models guarantees valid structured output. This is one of the most valuable features for production applications.

**Streaming.** A well-designed streaming API covers both chat completions and assistants.

### Weaknesses

**OpenAI-specific features.** Some features (Assistants API, file uploads, batch API) are OpenAI-specific and don't work with other providers.

**No abstractions.** If you need agents, chains, or memory, you build them yourself or use a framework. The SDK is just a client.

**Frequent API changes.** OpenAI adds features regularly, and the SDK changes to match. Pin versions in production.

## The OpenAI Agents SDK

### Overview

The Agents SDK is developed by OpenAI (2024). It is Python-only and MIT-licensed, was released in 2024, and is actively developed.

### Why it exists

OpenAI previously released the "Swarm" framework (experimental, lightweight agents). The Agents SDK is the production version — a minimalist agent framework that's closer to the API than LangChain or LangGraph, but with enough structure for production agents. The design philosophy: provide the minimal primitives needed for agents, without the heavy abstractions of other frameworks.

### Agents

An Agent is a configured LLM with instructions and tools:

```python
from agents import Agent, Runner

agent = Agent(
    name="Math Tutor",
    instructions="You explain math concepts clearly. Use the calculator tool for computations.",
    tools=[calculator_tool],
)

result = Runner.run_sync(agent, "What is 17 * 23?")
print(result.final_output)
```

### Handoffs

Handoffs let one agent transfer to another:

```python
billing_agent = Agent(name="Billing", instructions="Handle billing questions.")
tech_agent = Agent(name="Tech Support", instructions="Handle technical issues.")

triage_agent = Agent(
    name="Triage",
    instructions="Route users to the right department.",
    handoffs=[billing_agent, tech_agent],
)

result = Runner.run_sync(triage_agent, "I was overcharged")
# Triage hands off to billing_agent
```

Handoffs are the key abstraction — they enable multi-agent orchestration without complex state machines.

### Guardrails

Guardrails are input and output validators that run before/after the agent:

```python
from agents import GuardrailFunctionOutput, AgentInputGuardrail

async def check_toxicity(ctx, agent, input):
    is_toxic = await toxicity_classifier(input)
    return GuardrailFunctionOutput(output_info={"toxic": is_toxic}, tripwire_triggered=is_toxic)

agent = Agent(
    name="Assistant",
    instructions="...",
    input_guardrails=[AgentInputGuardrail(guardrail_function=check_toxicity)],
)
```

If a guardrail triggers, the agent doesn't run (input guardrail) or its output isn't returned (output guardrail).

### Tracing

The SDK has built-in tracing for observability:

```python
from agents import trace

with trace("Customer support conversation"):
    result = Runner.run_sync(triage_agent, user_message)
    # All agent calls, tool calls, and handoffs are traced
```

Traces are viewable in the OpenAI dashboard or exported to external observability platforms.

### Sessions

Sessions provide session state for multi-turn conversations:

```python
from agents import Runner, SQLiteSession

session = SQLiteSession("conversation_123")
result1 = Runner.run_sync(agent, "Hi, I'm John", session=session)
result2 = Runner.run_sync(agent, "What's my name?", session=session)
# Agent remembers "John" from the previous turn
```

### Strengths

**Minimal abstractions.** Agent, Handoff, Guardrail, Trace. Four concepts cover most agent use cases. No state machines, no graph definitions, no complex composition.

**Close to the API.** The SDK builds directly on the OpenAI Python SDK. If you know the API, you know the Agents SDK.

**Handoffs are intuitive.** The handoff pattern is simpler than graph-based orchestration. For many agent applications (customer support routing, specialist delegation), handoffs are sufficient.

**Built-in tracing.** No need for external observability setup. Traces work out of the box.

**Guardrails as first-class.** Input/output validation is built into the framework, not an afterthought.

### Weaknesses

**OpenAI-only.** The Agents SDK is designed for OpenAI models. While it can work with OpenAI-compatible providers, some features (tracing, specific tool formats) are OpenAI-specific.

**Less control than LangGraph.** Handoffs are simpler than graphs, but also less flexible. Complex workflows with conditional routing, cycles, and state management are harder.

**Newer, less battle-tested.** Released in 2024, the Agents SDK has less production track record than LangChain or LangGraph.

**Limited multi-agent patterns.** Handoffs cover sequential delegation. Parallel agents, debate, and other patterns require custom implementation.

## When to use the OpenAI stack

### Good fit

The stack is a strong fit for OpenAI-centric applications: if you're committed to OpenAI models, the official SDK is the natural choice. It also suits simple agents, where handoffs are perfect for routing-style designs; structured output applications, where the SDK's Pydantic integration is excellent; and multi-provider setups via OpenAI compatibility, where you reach vLLM, Together, and similar providers through their OpenAI-compatible APIs.

### Poor fit

It is a poor fit for complex agent orchestration — use [[LangGraph]] for graph-based control — and for multi-model optimization, where routing between OpenAI, Anthropic, and others calls for LiteLLM or a gateway. It is also a poor fit for research and experimentation: frameworks with more abstractions ([[DSPy]], [[LangChain]]) are better for trying many approaches.

## Comparison to alternatives

| Framework       | Approach                    | Strengths                          | Weaknesses                       |
|-----------------|-----------------------------|------------------------------------|----------------------------------|
| OpenAI SDK      | Thin API wrapper            | Simple, well-documented, compatible| No abstractions                  |
| OpenAI Agents   | Minimal agent primitives    | Simple, handoffs, tracing          | OpenAI-only, less control        |
| LangChain       | General framework           | Breadth, integrations              | Heavy, breaking changes          |
| LangGraph       | Graph-based orchestration   | Control, persistence, HiTL         | Verbose, learning curve          |
| DSPy            | Declarative compilation     | Systematic optimization            | Learning curve, compilation cost |

## Production patterns

### Use structured outputs for reliability

Structured outputs (Pydantic models) guarantee valid JSON. Use them whenever you need the model's output in a specific format — it eliminates parsing failures.

### Pin SDK versions

OpenAI releases SDK updates frequently. Pin exact versions in production; test before upgrading.

### Use tracing from day one

The Agents SDK's built-in tracing is valuable. Enable it from the start — adding tracing later is painful.

### Combine with LiteLLM for multi-provider

If you need multi-provider support, use LiteLLM as a proxy in front of the OpenAI SDK. Your code uses the OpenAI SDK; LiteLLM translates to other providers.

### Don't overuse agents

For simple API calls, use the base SDK. The Agents SDK adds structure that's only worth it for genuine agent use cases.

## See also

- [[Agents and Tooling MOC]] — orientation for the agents and tooling area.
- [[Function Calling]] — the tool-calling capability the SDK exposes and agents wrap.
- [[LangGraph]] — graph-based orchestration when you need more control than handoffs.
- [[LangChain]] — the general-purpose framework alternative.
- [[LlamaIndex]] — the RAG-focused alternative.
- [[DSPy]] — declarative prompt optimization for experimentation-heavy work.
- [[PydanticAI]] — a type-safe, provider-agnostic alternative for agents.
- [[Framework Selection Guide]] — overall decision guidance across frameworks.
- [[15 - Agents and Tooling/Frameworks and Tools/vLLM|vLLM]] — an OpenAI-compatible serving engine the SDK can target.
