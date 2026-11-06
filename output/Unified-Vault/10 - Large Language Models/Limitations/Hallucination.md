---
title: Hallucination
type: concept
aliases:
  - LLM Hallucination
  - Fabrication
  - Confabulation
tags:
  - llm
  - limitations
  - hallucination
  - faithfulness
  - grounding
sources:
  - "05 - Hallucination"
created_index: 6
---

Hallucination is when an LLM produces confident but false information — invented facts, citations, API calls, or events delivered with the same fluency as verified knowledge. The fundamental cause is structural: LLMs generate plausible text, not verified truth, so nothing in the training objective guarantees correctness. This note covers the forms hallucination takes, its root causes, the taxonomy used to classify it (intrinsic versus extrinsic, factuality versus faithfulness, severity levels), mitigation strategies (RAG, prompting, fine-tuning, verification, calibration, tool use), detection methods, agent-specific concerns, production patterns, and the open research questions that remain. No complete solution exists — the goal is mitigation, not elimination.

> [!info] TL;DR
> Hallucination is when an LLM produces confident but false information. The fundamental cause: LLMs generate plausible text, not verified truth. Mitigations — RAG, prompting, fine-tuning, verification, calibration — reduce the rate but never eliminate it. No complete solution exists; the goal is mitigation, not elimination.

## What hallucination is

Hallucination takes many forms, and the distinctions matter because each form calls for a different detection and mitigation strategy. The recurring pattern is content that is fluent, confident, and unverifiable or outright false:

| Form | Example | What goes wrong |
|------|---------|-----------------|
| Factual | "The Eiffel Tower is in Berlin." | Confidently wrong about a fact. |
| Source | "According to a 2023 study by Smith et al..." | No such study exists. |
| Capability | "I've verified this code compiles." | It doesn't. |
| Self-knowledge | "I don't have personal experiences." | Sometimes followed by a personal anecdote. |
| Citation | "See [Smith 2020]" | Fabricated reference. |
| Date/time | "Today is March 15, 2025." | It's not; the model has no clock. |
| API | "The `numpy.calculate_mean()` function..." | No such function exists. |
| Logical | "Since A > B and B > C, therefore C > A." | Wrong logical conclusion. |

### Hallucination versus other failure modes

Hallucination is distinct from neighboring failure modes, and conflating them leads to wrong countermeasures. An **error** is a wrong answer due to lack of knowledge — the model "knows" it doesn't know, but guesses wrong anyway. **Bias** is systematic skew in outputs, such as always assuming doctors are male. **Toxicity** is harmful or offensive content. **Inconsistency** means different answers to the same question asked differently. Hallucination specifically is **confident fabrication** — the model produces wrong content as if it were true, without signaling uncertainty.

## Why LLMs hallucinate

Hallucination is not a bug in any single component; it follows from how LLMs are trained and how they generate. Eight root causes combine to produce it.

### Trained on next-token prediction, not truth

The training objective is "predict the next token given context", not "produce true statements." The model learns statistical patterns of text, not facts. Plausibility is the goal, not truth. The objective $\mathcal{L} = -\sum_t \log p(x_t | x_{<t})$ maximizes the likelihood of training text. If the training text contains errors (and it does), the model learns those errors. If the training text is silent on a topic, the model learns the *pattern* of plausible-sounding text on that topic, even without facts.

### No awareness of not knowing

An LLM has no internal "I don't know" signal. It will produce a confident-sounding answer regardless of whether it actually knows, and calibrated uncertainty is rare and hard to elicit. The model's probability distribution over tokens doesn't distinguish "high confidence because I know" from "high confidence because the pattern is common." Both produce fluent, confident output.

### Errors in the training data

If the training corpus has wrong facts, the model learns them. Wikipedia has errors; web text is full of misinformation; even authoritative sources disagree. The model has no way to distinguish reliable from unreliable sources. Four data issues recur in practice:

- Wikipedia "citation needed" tags get stripped during training.
- Satire (The Onion) is indistinguishable from news.
- Old information persists even after corrections.
- Multiple sources repeat the same error (echo chamber effect).

### Generalization invents new patterns

The model doesn't just memorize — it generalizes. Sometimes generalization creates patterns that look right but are wrong, such as plausible-sounding but nonexistent book titles. For example, if the model has seen many book titles like "The [Adjective] [Noun]: A [Topic] Journey", it can generate "The Crimson Path: A Mathematical Journey" — a plausible title for a book that doesn't exist. The pattern is right; the specific instance is fabricated.

### Prompting can induce hallucination

Leading questions ("Why did the US invade Canada in 1812?") presuppose false premises, and the model often plays along rather than correcting the premise. This is sometimes called **sycophancy** — the model agrees with the user's framing, even when wrong.

### No ground truth at inference time

At inference, the model has only its parameters and the prompt. There's no mechanism to "look up" facts; everything comes from memory. If the memory is wrong or incomplete, the output is wrong.

### Sampling introduces randomness

At temperature > 0, sampling can produce low-probability tokens that lead the model into unfamiliar territory, where it hallucinates. Lower temperature reduces this effect but doesn't eliminate it. The interaction between decoding randomness and hallucination is covered in [[Sampling Strategies]].

### Long-form generation drifts

As the model generates longer outputs, early hallucinations propagate: the model conditions on its own fabricated content, producing more hallucinations consistent with the first. This "snowball" effect is why long-form generation is more hallucination-prone than short-form.

## Types of hallucination

Beyond the surface forms above, hallucinations are classified along three axes that determine how detectable they are, plus a severity scale for production tracking.

### Intrinsic versus extrinsic

**Intrinsic** hallucinations contradict the source: the output contradicts it — in a RAG setting, the retrieved context. They are easier to detect because you can simply compare the output to the context. **Extrinsic** hallucinations produce content not supported by the source; it might be true, might be false — you can't verify from context alone. Extrinsic hallucinations are harder to detect and require external verification.

### Open-domain versus closed-domain

**Open-domain** hallucination concerns any fact in the world, and is hard to verify. **Closed-domain** hallucination concerns facts about a specific document — the RAG setting — and is easier to detect via faithfulness metrics.

### Factuality versus faithfulness

**Factuality** means the output is true in the real world; verifying it requires external checks. **Faithfulness** means the output is supported by the provided context; verifying it requires only comparing output to context. A model can be faithful but not factual (the context is wrong), or factual but not faithful (the model adds correct facts not in the context). RAG evaluation focuses on faithfulness; broader evaluation focuses on factuality.

### Severity levels

Hallucination isn't binary — it's a spectrum, and production systems should track hallucination rates by severity, not just count:

| Level | Name | What it looks like |
|-------|------|--------------------|
| L1 | Minor inaccuracy | A small factual error that doesn't change the answer's utility ("The Eiffel Tower was built in 1887" — actually 1889). |
| L2 | Misleading | An error that could lead to wrong conclusions ("Aspirin cures cancer" — wrong and harmful). |
| L3 | Fabricated source | An invented citation, study, or quote ("According to Smith 2020..." — no such study). |
| L4 | Complete fabrication | Entirely made-up content presented as fact ("The 1947 Treaty of Lisbon established the European Space Agency." — totally false). |
| L5 | Dangerous fabrication | False content in a high-stakes domain (medical, legal, financial) that could cause harm. |

## Mitigation strategies

No single technique eliminates hallucination, so real systems layer several of the following, trading cost and latency against residual risk.

### Retrieval-augmented generation

Retrieve relevant documents and condition generation on them. RAG **helps** by grounding the model in real data and providing source attribution. It **doesn't fully solve** the problem: the model can still hallucinate from the retrieved context, especially if the context is ambiguous or the model misreads it. **Best practice**: prompt explicitly to "answer only from the context; say 'I don't know' if the context doesn't contain the answer", use reranking to ensure relevant context, and validate citations.

### Prompt engineering

Prompting tactics each help partially and each carries a caveat:

- "If you don't know, say 'I don't know'." — helps but is not perfectly reliable; the model's threshold for "knowing" is unclear.
- "Cite your sources." — produces citations, but they may be hallucinated; always validate citations programmatically.
- Chain-of-thought — helps the model reason but can also rationalize false answers; use with caution.
- "Verify each claim against the context before including it." — encourages step-by-step checking.
- Few-shot examples of refusing unanswerable questions — teaches the "I don't know" behavior (see [[In-Context Learning]]).

### Fine-tuning

- RLHF/DPO with "I don't know" as a valid response for unanswerable questions — the model learns to refuse rather than fabricate (see [[RLHF with PPO]] and [[DPO Derivation]]).
- Constitutional AI / RLAIF: a critic model flags hallucinations; the policy learns to avoid them.
- Factuality fine-tuning: train on (question, verified answer) pairs to reinforce factual recall.
- RAG-specific fine-tuning: train on (context, question, grounded answer) triples to teach grounded generation.

### Post-hoc verification

Check the output after generation rather than trusting it. Use another LLM (or the same one) to fact-check the response: the verifier reads the answer and the sources and flags unsupported claims. Cross-reference with search results, retrieving fresh sources for each claim. Use structured output (JSON with citation fields) and validate citations programmatically — each citation must point to a real chunk ID with matching content; [[Constrained Decoding]] can enforce such structure at generation time. For math and data questions, use code execution: if the model claims "2+2=5", execute the calculation.

### Calibration

- Temperature scaling to make the model's confidence match empirical accuracy — a calibrated model that says "90% confident" is right 90% of the time.
- Reject low-confidence outputs: set a threshold (e.g., if top-1 probability < 0.3, refuse).
- Ask for confidence explicitly ("On a scale of 1-10, how confident?") — models are surprisingly good at self-assessment when asked directly.
- Verbalized uncertainty: ask the model to express uncertainty in language ("I'm not sure, but I think..."). Studies show this correlates with actual accuracy.

### Tool use

Give the model a way to check itself instead of guessing. Let it use a search tool when unsure — the model decides "I don't know, let me search" and invokes a tool. Use function calling for fact-checking APIs (e.g., a Wikipedia API, a fact-check database). Use code execution for math and data questions — don't trust the model to do arithmetic; execute it. Use database queries for structured data — don't trust the model to recall numbers; query the database.

### Architectural mitigations

- **Retrieval-augmented training**: during training, the model retrieves from a memory and conditions on it — different from inference-time RAG.
- **Faithfulness training**: train the model to produce only content supported by retrieved context; Self-RAG and Corrective RAG are examples.
- **Verifier models**: train a separate model to verify factual claims and use it as a post-hoc filter.

## Detection methods

Detection asks a different question than mitigation: given an output, was it hallucinated? Six approaches are used in practice, ordered roughly from cheapest to most expensive.

### Self-consistency

Sample multiple responses (e.g., 5 samples at temperature 0.7); if they disagree, the model is uncertain and possibly hallucinating. The disagreement rate correlates with the hallucination rate. Implementation: run the model N times, compare outputs semantically (not just string match), and flag queries with high disagreement for review.

### Perplexity-based detection

High perplexity on the model's own output suggests it's "off distribution" — possibly hallucinated. The model is less sure of fabricated content than factual content. Implementation: compute the model's perplexity on its own output; high perplexity means flag for review.

### External fact-checking

Use a search engine or knowledge base to verify claims: for each claim in the output, search for evidence and flag claims with no supporting evidence. Common tools include the Google Fact Check API; Snopes and Politifact for political claims; and custom knowledge bases for domain-specific fact-checking.

### Faithfulness metrics for RAG

**RAGAS faithfulness** measures the fraction of claims in the answer that are supported by the retrieved context — it decomposes the answer into atomic claims and checks each against the context. **TruLens** offers similar metrics with production monitoring, and **DeepEval** integrates with pytest for CI/CD. As an example, the answer "Llama 3 has 70B parameters and was released in 2024" decomposes into two claims — (1) Llama 3 has 70B parameters, (2) Llama 3 was released in 2024 — each checked against the retrieved context.

### LLM-as-judge

Use a strong LLM (GPT-4, Claude) to evaluate the output for hallucination. The judge reads the output and the sources and flags unsupported claims. It is cheaper than human review and more accurate than automated metrics; see [[LLM-as-Judge Evaluation]] for the judging methodology and its own failure modes.

### Human review

The gold standard. Sample outputs and have human reviewers flag hallucinations. Use human review to calibrate the automated metrics and to catch systematic issues the metrics miss.

## Why hallucination matters

Hallucination is **the** biggest blocker to LLM adoption in high-stakes domains (medicine, law, finance). Every LLM feature needs a hallucination strategy — pretending the model "is usually right" is not a strategy. For agents, hallucination compounds: hallucinated tool arguments, hallucinated observations, hallucinated final answers; each step can fail, and the failure propagates. The lack of a complete solution is why RAG is so widely adopted — it's the best mitigation we have, even though it's not perfect. Hallucination rate is also a key metric for LLM evaluation: models are compared on TruthfulQA, HaluEval, and other hallucination benchmarks (see [[LLM Benchmarks]]). Finally, hallucination erodes user trust — a single confident wrong answer can destroy a user's confidence in the system, even if 99 prior answers were correct.

## Hallucination in agent systems

In agent systems, hallucination manifests in additional ways beyond wrong prose answers:

- **Hallucinated tool arguments**: the model calls `search(query="...")` with arguments that don't match the tool's schema, causing tool errors or wrong results.
- **Hallucinated observations**: the model "remembers" a tool result that didn't happen ("I searched for X and found Y..." — but no search was run).
- **Hallucinated plan**: the model produces a plan that includes impossible steps (e.g., "Step 3: Access the user's bank account" without any such tool).
- **Hallucinated state**: the model believes it has completed a step it hasn't, or vice versa.
- **Hallucinated final answer**: the final answer references steps that didn't happen or results that weren't obtained.

The mitigations for agent hallucination all replace model memory with external, verifiable state. Validate tool arguments against the schema before execution and reject and ask the model to retry on mismatch. Log all tool results and include them in subsequent prompts so the model doesn't need to "remember". Verify the plan against available tools before execution and reject impossible steps. Use structured state tracking (e.g., LangGraph's `AgentState`) rather than relying on the model to track state. Verify the final answer against the tool log — each claim should trace to a tool result.

## Production implications

Production deployment means assuming hallucination will happen and designing around it:

- **Always assume hallucination is possible.** Design features that are robust to wrong answers (cite sources, allow user correction, fall back to human review for critical paths).
- **For fact-grounded features**, use RAG with explicit "answer only from context" prompts, and validate citations.
- **For high-stakes features** (medical, legal, financial), add human review for any critical output; don't auto-approve.
- **Monitor hallucination in production** — sample responses, have human reviewers flag hallucinations, track the rate over time, and alert on rate increases (see [[Production Monitoring]]).
- **Citations**: if you cite sources, validate that the citations exist. Hallucinated citations are worse than no citations — they erode trust faster.
- **User feedback**: let users flag wrong answers, and use this signal to improve prompts, fine-tune, or update RAG indexes.
- **Calibration**: monitor the model's confidence vs. its accuracy. If confident answers are often wrong, the model is miscalibrated.
- **Model versioning**: hallucination rates change between model versions; re-evaluate on every upgrade.
- **Domain-specific mitigation**: for medical, legal, or financial domains, fine-tune on verified data and use domain-specific fact-checkers.
- **User expectations**: set expectations clearly — "This AI provides information, not authoritative advice. Verify important facts."
- **Refusal rates**: track how often the model says "I don't know". Too low means it is hallucinating; too high means it is not useful. Find the right balance.

Output filtering layers such as [[Guardrails]] complement these practices by blocking or rewriting unsafe or unsupported outputs before they reach the user.

## Common pitfalls

Ten mistakes recur in teams building on LLMs:

- **Trusting the model's confidence** — confident wrong answers are common; confidence is not calibration.
- **Forgetting that RAG doesn't fully solve it** — RAG reduces hallucination but doesn't eliminate it; the model can still misread context or hallucinate from ambiguous context.
- **Prompting once and assuming it works** — "say I don't know" prompts help but leak; test the failure rate empirically.
- **Treating hallucination as a binary** — it's a spectrum; some answers are partly right, partly wrong. Track severity.
- **Blaming the model only** — bad prompts, missing context, and ambiguous questions all contribute. Fix the system, not just the model.
- **Ignoring the user's role** — leading questions, vague prompts, and unrealistic expectations all increase hallucination.
- **Assuming fine-tuning fixes it** — fine-tuning on factual data helps but doesn't generalize to unseen facts; RAG is still needed.
- **Not validating citations** — a citation to a non-existent source is worse than no citation; always validate.
- **Confusing factuality with faithfulness** — a faithful answer (supported by context) can still be wrong if the context is wrong. Track both.
- **Not testing for hallucination** — without measuring hallucination rate, you can't tell if mitigations work. Build hallucination eval into your test suite.

## Worked example: mitigating hallucination in a customer support bot

Suppose you're building an LLM-based customer support bot for a SaaS product. The bot answers questions about pricing, features, and troubleshooting. Stacking mitigations drives the hallucination rate down step by step.

### Baseline (high hallucination)

Use GPT-4o directly, with no RAG, and the prompt "Answer the user's question about our product." The hallucination rate lands around 15-20% — the model invents features, prices, and troubleshooting steps.

### Add RAG (medium hallucination)

Index the product docs, pricing page, and FAQ; retrieve the top 5 chunks per query; and prompt "Answer based on the context. Cite sources." The rate drops to roughly 5-10% — the model still adds details not in the context.

### Add explicit refusal (lower hallucination)

Change the prompt to "Answer only from the context. If the context doesn't contain the answer, say 'I don't know.' Cite sources." and fine-tune on (context, question, refusal) examples for unanswerable questions. The rate falls to about 2-5%.

### Add citation validation (lower hallucination)

Use structured output so each claim must have a citation field. Programmatically validate citations: each citation must point to a real chunk with matching content. Reject answers with invalid citations and ask the model to retry. The rate drops to roughly 1-3%.

### Add post-hoc verification (lowest hallucination)

Use a second LLM to verify each claim against the context, flag and filter unsupported claims, and route flagged answers to human review. The rate drops below 1%.

| Stage | Intervention | Hallucination rate |
|-------|--------------|--------------------|
| Baseline | GPT-4o directly, no RAG | ~15-20% |
| Add RAG | Index docs, retrieve top 5 chunks, cite sources | ~5-10% |
| Add explicit refusal | "Answer only from the context" prompt + refusal fine-tuning | ~2-5% |
| Add citation validation | Structured citations, programmatic validation, retry on failure | ~1-3% |
| Add post-hoc verification | Second-LLM claim verification + human review of flagged answers | <1% |

Each step adds cost and latency but reduces hallucination. The right trade-off depends on the use case's risk tolerance.

## Interview questions

**Why do LLMs hallucinate, even when they "know" the right answer?** LLMs are trained on next-token prediction, not truth. They generate plausible text, which may be wrong even when the model has seen the correct information. The model has no mechanism to distinguish "high confidence because I know" from "high confidence because the pattern is common."

**How would you reduce hallucination in a RAG system?** Use explicit "answer only from context; say I don't know if not in context" prompts. Validate citations programmatically. Use reranking for relevant context. Fine-tune on (context, question, grounded answer) triples. Use post-hoc verification (LLM-as-judge) for high-stakes outputs.

**What's the difference between faithfulness and factuality?** Faithfulness = the output is supported by the provided context. Factuality = the output is true in the real world. A faithful answer can be unfactual (if the context is wrong); a factual answer can be unfaithful (if it adds correct facts not in the context). RAG evaluation focuses on faithfulness; broader evaluation focuses on factuality.

**How would you measure hallucination rate in production?** Sample outputs and have human reviewers flag hallucinations (gold standard). Use LLM-as-judge for cheaper evaluation. Track faithfulness metrics (RAGAS). Track user feedback (thumbs down, corrections). Track by severity (L1-L5). Alert on rate increases.

**Why does RAG not fully solve hallucination?** The model can still misread context, hallucinate from ambiguous context, or add details not in the context. RAG grounds the model but doesn't prevent fabrication. Explicit prompts ("answer only from context") and citation validation are needed.

**How does temperature affect hallucination?** Higher temperature → more randomness → more hallucination (the model explores low-probability tokens that may lead to unfamiliar territory). Lower temperature → more deterministic → less hallucination but also less diverse. For factual tasks, use temperature 0-0.3. For creative tasks, higher is fine.

## Further reading

- Ji et al. (2023), *Survey of Hallucination in Natural Language Generation*.
- Lewis et al. (2020), *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks* (RAG as hallucination mitigation).
- Lin et al. (2022), *TruthfulQA: Measuring How Models Mimic Human Falsehoods*.
- Asai et al. (2023), *Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection*.
- Kadavath et al. (2022), *Language Models (Mostly) Know What They Know* — on calibration.

## See also

- [[Large Language Models MOC]] — orientation for the LLM area.
- [[Sampling Strategies]] — temperature and randomness as a direct hallucination lever.
- [[In-Context Learning]] — few-shot demonstrations that teach refusal behavior.
- [[LLM Benchmarks]] — TruthfulQA and HaluEval measure hallucination.
- [[LLM-as-Judge Evaluation]] — automated judging used for hallucination detection.
- [[Guardrails]] — output filtering as a production safety net.
- [[Production Monitoring]] — tracking hallucination rates over time.
- [[RLHF with PPO]] — preference training that rewards honest refusals.
- [[DPO Derivation]] — direct preference optimization used for refusal training.
- [[Constrained Decoding]] — forcing structured output with validatable citation fields.
- Agent reflection — agents that self-critique their own outputs; this helps reduce hallucination.
- [[RAG Pipeline Overview]]
- [[Reflection]]
- [[Agents and Tooling MOC]]
- [[Inference and Production MOC]]
