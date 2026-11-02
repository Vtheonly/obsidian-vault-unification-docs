---
title: Constrained Decoding
type: concept
aliases: [Constrained Decoding, CFG, Grammar Constrained Decoding, JSON Mode]
tags: [inference, decoding, constrained-decoding, cfg, grammar, json-schema, structured-output]
sources: ["07 — Constrained Decoding and CFG"]
created_index: 7
---

Constrained decoding forces an LLM's output to conform to a specified format — a JSON schema, a regex, a context-free grammar, or a choice list. Instead of hoping the model produces valid JSON and retrying when it doesn't, the engine masks the logits at each step so that only format-valid tokens can be sampled. The output is guaranteed valid by construction, with zero retries and usually no quality cost. This note covers the logit-masking core idea, the four constraint types, implementation techniques from naive masking to compiled state machines, performance characteristics, pitfalls, and production patterns.

> [!info] TL;DR
> Constrained decoding masks the logits at each step so that only format-valid tokens can be sampled. This guarantees valid output with zero retries, often at no quality cost. The two main techniques are **token-level masking** (mask out invalid next tokens) and **CFG-based parsing** (track the parser state and only allow tokens that keep the parse alive). It is essential for production agents that depend on JSON tool calls, structured output, and code generation.

## Why constrained decoding

LLMs by default generate free-form text. But production systems usually need structured output:

- **Tool calls**: the LLM must emit a JSON object with `name` and `arguments` fields.
- **Data extraction**: extract entities into a schema (`{"name": str, "age": int, "address": str}`).
- **Code generation**: emit syntactically valid code (parseable Python, JSON, etc.).
- **Choice selection**: pick one of N options ("yes", "no", "maybe").

Without constrained decoding, the workflow is: prompt the LLM to produce JSON, parse the output, and if parsing fails, retry (often with the error in context), repeating until success or budget exhausted. This is slow, expensive, and unreliable. Models produce invalid JSON 5-20% of the time even with strong prompts, and retries multiply cost. Constrained decoding eliminates this: the output is guaranteed valid by construction — the model literally cannot emit an invalid token.

## The core idea: logit masking

At each decoding step, the model produces a probability distribution over the vocabulary (via softmax on logits). Constrained decoding modifies this distribution:

1. Compute the set of "valid" next tokens — those that keep the output conformant to the constraint.
2. Mask the logits of invalid tokens to `-inf`.
3. Apply softmax to get the constrained distribution.
4. Sample from the constrained distribution.

```python
def constrained_sample(logits, valid_token_ids, temperature=1.0):
    """logits: (vocab,) tensor, valid_token_ids: set of allowed token IDs."""
    mask = torch.full_like(logits, float('-inf'))
    mask[torch.tensor(list(valid_token_ids))] = 0
    constrained_logits = logits + mask
    probs = torch.softmax(constrained_logits / temperature, dim=-1)
    return torch.multinomial(probs, num_samples=1)
```

The challenge is computing `valid_token_ids` efficiently at each step. This depends on the constraint type.

## Constraint types

### JSON schema constrained

For JSON output conforming to a schema, the engine tracks the parser state:

- "We're inside the object, expecting a key."
- "We're expecting the value of `age` (an integer)."
- "We've finished the object; only `<end>` is valid now."

At each step, the engine computes which tokens could appear next while keeping the JSON parseable and conforming to the schema. Invalid tokens are masked to $-\infty$ before softmax.

```python
# Example schema
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"},
        "email": {"type": "string", "format": "email"},
    },
    "required": ["name", "age"],
}

# The constrained decoder guarantees output like:
# {"name": "Alice", "age": 30, "email": "alice@example.com"}
# It cannot produce:
# {"name": "Alice"}  (missing required field "age")
# {"name": "Alice", "age": "thirty"}  (age must be integer)
```

This is implemented by libraries like `outlines`, `lm-format-enforcer`, and `xgrammar`. The engine compiles the schema into a state machine and steps through it token by token.

### Regex constrained

For output matching a regex, the engine tracks the regex's deterministic finite automaton (DFA) state:

- "We're at the start; only `[0-9]` is valid (the regex starts with `\d`)."
- "We've matched `\d{3}`; `-` is valid next (the regex is `\d{3}-\d{3}-\d{4}`)."
- "We've matched `\d{3}-\d{3}`; only `[0-9]` is valid for the last 4 digits."

```python
regex = r"\d{3}-\d{3}-\d{4}"  # US phone number format
# The constrained decoder guarantees output like:
# 555-123-4567
# It cannot produce:
# 555-12-4567 (wrong format)
# 555-1234-4567 (wrong format)
```

Regex constraints are simpler than JSON schema constraints because regexes compile to well-understood DFAs. The `interegular` library compiles Python regexes to DFAs suitable for constrained decoding.

### Context-free grammar (CFG) constrained

For output matching a CFG, the engine tracks the parser state. CFGs are more expressive than regexes (they can handle nested structures like balanced parentheses, recursive grammars like programming languages).

```python
# A CFG for simple arithmetic expressions
grammar = """
expr    := term (("+" | "-") term)*
term    := factor (("*" | "/") factor)*
factor  := number | "(" expr ")"
number  := [0-9]+
"""
# The constrained decoder guarantees output like:
# (3 + 4) * 5
# It cannot produce:
# (3 + 4 * 5  (unbalanced paren)
# 3 + * 4     (missing operand)
```

CFG constraints are used for code generation (force syntactically valid Python/SQL/etc.), structured DSLs, and complex output formats. The `outlines` library supports CFG constraints via `Lark` grammars.

### Choice constrained

For output that must be one of N choices, the engine masks all tokens that aren't a prefix of any choice:

```python
choices = ["positive", "negative", "neutral"]
# After generating 'p', only 'o' is valid (only "positive" starts with 'p').
# After generating 'po', only 's' is valid.
# And so on until "positive" is complete.
```

This is simpler than JSON/regex/CFG constraints because the choices are finite. It's commonly used for classification, routing, and binary decisions.

## Implementation techniques

### Naive token-level masking

The simplest implementation: at each step, enumerate all tokens in the vocabulary, check which ones keep the output conformant, mask the rest.

```python
for token_id in range(vocab_size):
    if is_valid(token_id, current_state):
        mask[token_id] = 0
    else:
        mask[token_id] = -inf
```

This is $O(V)$ per step (where $V$ is vocabulary size, typically 50K-200K). For each of 50K tokens, we need to check validity. This is too slow for production.

### Trie-based validity

For string-based constraints (regex, JSON), precompute a trie of all valid continuations:

1. Build a trie where each node represents a state in the constraint automaton.
2. At each step, walk the trie based on the current state.
3. The trie's children at the current node are the valid next characters.

For token-level decoding, this is trickier because tokens span multiple characters. The engine must compute which tokens are valid as the first token of a valid continuation. This is implemented in `xgrammar` and `outlines`.

### Compiled state machines

For JSON schemas, compile the schema into a state machine. Each state represents "what we're expecting next" (key, value, comma, end-of-object). Transitions are triggered by token patterns. This is the approach used by `lm-format-enforcer` and `outlines`.

The compiled state machine enables $O(1)$ validity checks per token. This is the production-grade approach.

### xgrammar

`xgrammar` (XGBoost-adjacent, by the MLC team) is a state-of-the-art constrained decoding library that compiles JSON schemas and grammars into highly efficient state machines. It's used in production by SGLang, MLC-LLM, and others. Its key innovation: precomputing the per-token validity mask offline, so the runtime cost is just a lookup — not a state machine step. `outlines` computes validity at runtime, which is why xgrammar is faster and more memory-efficient.

## Performance characteristics

### Overhead

Constrained decoding adds overhead per token:

- **Token-level masking**: ~1-5% overhead (logit masking is cheap).
- **State machine stepping**: ~5-10% overhead (more complex constraints).
- **Schema compilation**: one-time cost at request start (~1-50ms depending on schema complexity).

For most workloads, the overhead is negligible compared to the cost of retries without constrained decoding.

### Quality impact

Constrained decoding can affect output quality in two ways:

- **Truncation effects**: if the model wants to generate a long string but the schema constrains it to a short one, the model may produce a worse answer because it can't say what it wanted.
- **Forced structure**: forcing JSON when the model would naturally produce prose may degrade quality. The model is fighting the constraint.

For most well-designed schemas, quality impact is minimal. The model adapts to the constraint and produces constrained-but-good output. For production, the reliability gain (100% valid vs 80-95% with prompts) far outweighs the quality cost.

### Output length

Constrained outputs are often shorter than unconstrained outputs. This is because the constraint eliminates "filler" tokens and structured output is more information-dense than prose. This is usually a feature, not a bug — shorter outputs are cheaper to generate and parse.

## Common pitfalls

### Token boundary issues

Tokens don't align with characters or schema boundaries. A single token might be `{"name":` (the start of a JSON object). The constraint engine must handle multi-character tokens correctly. This is the trickiest implementation detail. Most engines handle it via "token healing" — adjusting the previous token if the next token would split a logical unit.

### Vocabulary mismatch

Some tokens in the vocabulary may not be valid in any constrained context (e.g., control characters, special tokens). The engine must exclude these from consideration.

### Schema complexity

Complex JSON schemas (oneOf, allOf, recursive references) can be slow to compile. For production, simplify schemas where possible.

### Whitespace handling

JSON allows arbitrary whitespace. The engine must decide whether to allow it (more flexible, slightly slower) or forbid it (faster, more compact output). Most engines allow whitespace for compatibility with the LLM's natural style.

### Stop tokens

The engine must handle stop tokens correctly. If the schema expects more fields, the engine should prevent early stop tokens. If the schema is complete, the engine should encourage stop tokens.

## Production patterns

### Use JSON mode for tool calls

For tool calls, always use JSON schema constrained decoding. Don't rely on prompts to produce valid JSON — even with strong prompts, models produce invalid JSON 5-20% of the time. With constrained decoding, it's 0%.

### Combine with function calling

Constrained decoding complements function calling. The model decides *whether* to call a tool (via a tool-use prompt); constrained decoding ensures the tool call is *valid* (via schema masking).

### Use outlines or xgrammar

For new projects, use `outlines` (Python) or `xgrammar` (faster, more memory-efficient). Both integrate with vLLM, SGLang, TGI, and other serving engines. SGLang additionally offers its own DSL for structured generation.

### Pre-compile schemas

For schemas used repeatedly, pre-compile them at startup. Avoid compiling on every request — the compilation cost (10-50ms) is significant at high QPS.

### Test edge cases

Test the constrained decoder with edge cases:

- Empty strings (valid for some schemas, invalid for others).
- Unicode characters (some engines mishandle non-ASCII).
- Very long outputs (some engines have performance cliffs).
- Deeply nested structures (some engines hit recursion limits).

## Comparison to alternatives

| Technique                  | Reliability | Quality Impact | Overhead |
|----------------------------|-------------|----------------|----------|
| Prompt engineering         | Low (80-95%) | None           | None     |
| Prompt + retry             | Medium (95-99%) | None       | 1-3× cost |
| JSON Mode (OpenAI)         | High (~100%) | Low         | Low      |
| Outlines / xgrammar        | High (~100%) | Low         | Low      |
| CFG constrained            | High (~100%) | Low         | Medium   |

Constrained decoding is strictly better than prompt engineering + retries for production use. The reliability gain (100% vs. 95%) eliminates entire classes of bugs.

Which constraint type to pick: JSON schema for structured data output (tool calls, data extraction); regex for simple patterns (phone numbers, IDs, dates); CFG for complex nested structures (code, DSLs, mathematical expressions). JSON schema is the most common (via `outlines` or `xgrammar`); CFG is for code generation; regex is for simple patterns. All use the same underlying logit-masking approach.

## See also

- [[Inference and Production MOC]] — orientation for the inference and production area.
- [[Sampling Strategies]] — what constrained decoding modifies.
- [[Continuous Batching]] — how per-request constraints fit into the scheduler.
- [[14 - Inference and Production/Inference/vLLM|vLLM]] — serving engine integration for outlines and xgrammar.
- [[14 - Inference and Production/Inference/TensorRT-LLM|TensorRT-LLM]] — production engine with constrained decoding support.
- [[Speculative Decoding]] — another decoding-time optimization.
- [[Guardrails]] — constrained decoding as a safety tool.
