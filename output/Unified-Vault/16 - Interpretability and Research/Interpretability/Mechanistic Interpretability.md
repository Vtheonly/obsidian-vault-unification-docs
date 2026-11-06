---
title: Mechanistic Interpretability
type: concept
aliases: ["Mechanistic Interpretability", "Circuits", "Induction Heads"]
tags: [interpretability, mechanistic, circuits, induction-heads]
sources: ["01 - Mechanistic Interpretability"]
created_index: 4
---

Mechanistic interpretability reverse-engineers neural networks into understandable circuits: it aims to identify, in the weights and activations, the algorithms the network is actually computing. Its landmark findings include attention head specialization (previous-token, induction, and syntactic heads), the residual stream understood as a memory bus, and feature decomposition via sparse autoencoders. The field was pioneered by Anthropic (the Circuits and Transformer Circuits threads) and by open-source work such as Neel Nanda's. This note walks through the mathematical framework, the key circuits and head types, the main analysis tools (logit lens, activation patching, SAEs), and what the findings mean for safety and production.

## The goal

Neural networks are black boxes: they work, but we don't know **how**. Mechanistic interpretability aims to reverse-engineer them — to identify, in the weights and activations, the algorithms the network is actually computing.

This matters for several reasons. **Safety**: if we can identify "deceptive behavior" in weights, we can prevent it. **Debugging**: understand why a model makes a specific error. **Trust**: high-stakes applications need explainability. **Science**: understand what these models actually learn.

## The residual stream as memory bus

Anthropic's "Mathematical Framework for Transformer Circuits" (Elhage et al. 2021) reframes the Transformer in a way that makes reverse-engineering tractable. The key insight: the Transformer can be decomposed into a sum of independent "heads" (attention + MLP) that read from and write to a shared residual stream. In this view:

- The **residual stream** is a shared memory bus.
- Each **attention head** reads from the stream (via Q, K, V) and writes to it (via output projection).
- Each **FFN** reads and writes.
- The model's computation is a sequence of read-modify-write operations on this shared memory.

This perspective makes Transformer behavior much easier to reason about.

Formally, let $\mathbf{x}_t \in \mathbb{R}^d$ be the residual stream at position $t$ after layer $\ell$. Initially $\mathbf{x}_t^{(0)} = \text{embed}(w_t) + \text{pos}(t)$. At each layer:

$$
\mathbf{x}_t^{(\ell+1)} = \mathbf{x}_t^{(\ell)} + \sum_{h \in \text{heads at }\ell} \text{Attn}_h^{(\ell)}(\mathbf{x}^{(\ell)})_t + \text{MLP}^{(\ell)}(\mathbf{x}_t^{(\ell)})
$$

The residual stream is **additive** — every head and MLP writes by *adding* to it. This means you can decompose the final representation as:

$$
\mathbf{x}_t^{(L)} = \text{embed}(w_t) + \text{pos}(t) + \sum_{\ell, h} \text{Attn}_h^{(\ell)}(\mathbf{x}^{(\ell)})_t + \sum_\ell \text{MLP}^{(\ell)}(\mathbf{x}_t^{(\ell)})
$$

Each term is an independent "contribution" to the final representation. The unembedding $W_U$ then maps $\mathbf{x}_t^{(L)}$ to logits:

$$
\text{logits}_t = W_U \mathbf{x}_t^{(L)} = W_U \text{embed}(w_t) + W_U \text{pos}(t) + \sum_{\ell, h} W_U \text{Attn}_h^{(\ell)} + \sum_\ell W_U \text{MLP}^{(\ell)}
$$

Each term is a "direct path" from a component to the output logits. By zeroing out all but one term, you can see that component's direct contribution to the prediction. This is the foundation of circuit analysis.

## QK and OV circuits

Each attention head can be decomposed into two circuits:

- **QK circuit** (which tokens attend to which): $W_Q^T W_K$ — a bilinear form on the residual stream that determines attention weights.
- **OV circuit** (what information is moved): $W_V W_O$ — a linear map applied to the source token's residual stream and added to the destination token's.

This decomposition lets you analyze attention heads independently. For example, an "induction head" has a QK circuit that matches `[A][B] ... [A]` patterns (the destination `[A]` attends to the token after the previous `[A]`), and an OV circuit that copies `[B]`.

## Attention head specialization

Empirically, attention heads specialize — a mechanistic finding about [[Multi-Head Attention]]. Several recurring types have been catalogued.

**Previous-token heads** attend to position $t-1$ from position $t$. Useful for bigram statistics.

**Induction heads** are the key finding: a two-head circuit that enables in-context learning. At position $t$, the induction head finds previous occurrences of token $x_{t-1}$ in the context, then attends to the token **after** that occurrence. This effectively implements "if you saw $A \to B$ before, and you see $A$ again, predict $B$." Induction heads are necessary for in-context learning (ICL). They emerge spontaneously during training, around the same training step across model families.

**Syntactic heads** attend to syntactic dependents (subject → verb, head noun → modifier).

**Copy heads** copy a specific token from the context to the output.

**Suppression heads** attend to a token and **subtract** it from the output (for unigram suppression, anti-repetition).

## The induction head circuit in detail

The induction head is the most-studied Transformer circuit. It implements in-context learning (ICL) via a two-head composition:

```text
Sequence:  [A] [B] [C] ... [A] [?]
                              ↑ want to predict B
```

The induction circuit works in two steps:

1. **Previous-token head** (in an earlier layer): for each position $t$, attends to position $t-1$ and writes the previous token's identity into the residual stream at position $t$. So at position $t$ (where $w_t = A$), the residual stream now contains "previous was B" (from the first [A][B] pair).
2. **Induction head** (in a later layer): at position $t$ (where $w_t = A$), looks for previous positions where the *next* token was A's predecessor in the pattern. It uses the previous-token head's output (which says "I followed A with B before") to attend to those positions, then copies their successor token (B) to the output.

The composition is: `previous-token head → induction head` — information flows through the residual stream from one head to the other.

**Empirical signature**: induction heads emerge suddenly during training at a consistent point across model families (usually 1-3 billion training tokens). After emergence, the model's ICL capability jumps. This phase transition is one of the most striking findings in mechanistic interpretability.

## The logit lens

A simple technique: at each layer, project the residual stream through the unembedding matrix (the output projection) to get vocabulary logits. This shows "what the model is predicting at each layer."

Findings: early layers predict common words; middle layers start predicting context-relevant words; late layers refine. Some layers do "preparation" (not yet predicting the right word but setting up for later layers). See [[Logit Lens and Tuned Lens]] for the full treatment.

### Worked example: the logit lens on GPT-2

Applying the logit lens to [[GPT-2]] takes a few lines:

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("gpt2", output_hidden_states=True)
tokenizer = AutoTokenizer.from_pretrained("gpt2")

inputs = tokenizer("The capital of France is", return_tensors="pt")
outputs = model(**inputs)

# outputs.hidden_states is a tuple of (n_layers + 1) tensors
# Apply the unembedding matrix to each layer's hidden state
unembedding = model.lm_head.weight  # (vocab, d_model)

for layer, hidden in enumerate(outputs.hidden_states):
    last_token_hidden = hidden[0, -1]  # (d_model,)
    logits = last_token_hidden @ unembedding.T  # (vocab,)
    top_token = logits.argmax().item()
    print(f"Layer {layer}: {tokenizer.decode(top_token)!r}")
```

## Activation patching

Activation patching (also called "causal tracing" or "interchange intervention") is the gold standard for causal interpretability claims. The basic technique:

1. Run the model on input A, save activations.
2. Run on input B, but **patch** a specific activation with A's value.
3. See if the output changes.

If patching layer $L$'s activation changes the output from B to A, then layer $L$ is causally responsible for the difference. It is used to localize: which layer/head/token position carries which information?

### The protocol

1. **Run on input A** (the "source"): save all activations $\mathbf{a}_A^{(\ell)}$.
2. **Run on input B** (the "destination"): the model produces output $y_B$.
3. **Patch**: at a chosen layer $\ell$ (or position, or head), replace B's activation with A's: $\mathbf{a}_B^{(\ell)} \leftarrow \mathbf{a}_A^{(\ell)}$.
4. **Observe**: does the output change from $y_B$ toward $y_A$?

### Variants

- **Direct patching**: replace the full activation. Blunt instrument.
- **Resample ablation**: replace with A's activation — useful for "where is the information stored?"
- **Zero ablation**: replace with zeros — useful for "what does this component do?"
- **Mean ablation**: replace with the mean activation over a dataset — better baseline than zero (preserves distribution).
- **Path patching**: patch only the contribution along a specific path (e.g., "head A's contribution to head B"). Most surgical, most informative.

The result of activation patching is a causal claim: "this component at this layer is causally responsible for the model's output difference between A and B." This is the strongest interpretability claim available. See [[Activation Patching and Causal Tracing]] for the full treatment.

## Sparse autoencoders

The frontier of interpretability (2023–2026). Problem: individual neurons are **polysemantic** (one neuron responds to "cats", "DNA", and "the French Revolution"). This happens because there are more concepts than neurons — the model uses **superposition** to pack many features into fewer dimensions. This makes individual neurons hard to interpret.

SAEs decompose activations into **monosemantic features**:

$$
\mathbf{a} \approx \sum_i f_i(\mathbf{a}) \cdot \mathbf{d}_i
$$

where $\mathbf{a} \in \mathbb{R}^d$ is the activation, $f_i(\mathbf{a}) = \text{ReLU}(\mathbf{w}_i^T \mathbf{a} + b_i)$ is a sparse feature activation (most are 0), and $\mathbf{d}_i \in \mathbb{R}^d$ is a learned feature direction. The source's summary is plainer: $f_i$ are sparse (most are 0) and $\mathbf{d}_i$ are learned "feature directions." Each feature tends to be monosemantic — it activates for one concept.

Training: minimize $\|\mathbf{a} - \text{decoder}(\text{encoder}(\mathbf{a}))\|^2 + \lambda \|\text{encoder}(\mathbf{a})\|_1$. The L1 penalty enforces sparsity.

Anthropic's "Scaling Monosemanticity" (2024) trained SAEs on Claude 3 Sonnet and found interpretable features at scale — features for "San Francisco", "deception", "code bugs", "sycophancy", etc. Crucially, the features are *causal* — activating the "deception" feature makes the model deceptive; suppressing it makes the model more honest. See [[Sparse Autoencoders]] for the full treatment.

## Why this matters for AI

Mechanistic interpretability is the **path to understanding** what LLMs actually do — without it, we're flying blind. For **safety**, interpretability is the only way to detect deceptive behavior, backdoors, or learned biases in weights. For **debugging**, it lets you pinpoint which layer/head is responsible for an error. For **model editing**, it's the foundation — you can only edit what you can locate. And the induction-heads finding explains **why in-context learning works** — a key mystery of LLMs.

## Production implications and applications (2026)

Mechanistic interpretability is mostly research in 2026 — not yet standard in production. The logit lens is cheap and useful for debugging — try it on your model. SAE-based monitoring is emerging for safety-critical applications (detect when "deception" features activate). For most engineering, simpler techniques (attention visualization, prompting the model to explain itself) are more practical.

That said, the field is moving from research to production along four patterns:

- **SAE-based monitoring**: deploy SAEs alongside the model in production. When "deception" or "harmful intent" features activate, flag the response for human review. Used by some AI safety startups.
- **Steering vectors in production**: train a probe for "is this response helpful vs. sycophantic", then subtract the sycophancy direction from the residual stream during inference. Cheap, effective, no model retraining.
- **Circuit-level debugging**: when a model makes a specific error, use activation patching to localize which head/layer is responsible. Then fine-tune to fix that specific component.
- **Red-teaming via SAEs**: find features that activate on adversarial inputs, then check production inputs for the same features — early warning system for jailbreaks.

Most of these are still research-grade in 2026, but the trajectory is toward production deployment.

## Common pitfalls

Four recurring mistakes:

- **Treating attention weights as explanations** — they're correlational, not causal. Use activation patching for causal claims.
- **Forgetting that polysemantic neurons exist** — a single neuron firing doesn't mean a single concept.
- **Reading too much into logit lens** — early-layer predictions are noise; only late layers matter.
- **Assuming features are interpretable by default** — SAE training is finicky; not all features are clean.

## Tooling and implementation

- **TransformerLens** (Neel Nanda): the standard library for mechanistic interpretability on small/medium open models. Supports hooks for every component, activation patching, SAEs.
- **Pyvene** (Princeton): framework for intervention-based interpretability on arbitrary models.
- **SAELens**: training and analyzing SAEs on TransformerLens models.
- **Anthropic's SAE viewer**: web UI for browsing Claude 3 features.
- **Custom hooks**: PyTorch forward hooks for ad-hoc interpretability — most production interpretability work uses this.

## Interview questions

**What is the residual stream, and why is the additive view important?** The residual stream is the sequence of vectors that flows through the Transformer, with each layer adding its contribution. The additive view ($\mathbf{x}^{(L)} = \text{embed} + \text{pos} + \sum \text{Attn} + \sum \text{MLP}$) lets you decompose the final representation into independent contributions from each component. This makes circuit analysis possible — you can zero out one component's contribution and see what changes.

**What is an induction head, and why is it important?** A two-head circuit that implements in-context learning: (1) a previous-token head writes "the previous token was X" into the residual stream, (2) the induction head finds previous occurrences of the current token's predecessor and copies its successor. Together, they implement "if you saw A→B before, predict B when you see A again." Induction heads emerge suddenly during training and are causally necessary for ICL — ablating them destroys ICL capability.

**What is the difference between attention weights and activations as explanations?** Attention weights are correlational — they show where the model looked, not what it used. Activations (via patching) are causal — they show what information, when changed, changes the output. Attention weights can be misleading: a head may attend to a token without using its information, or use information from a token it doesn't attend to (via the OV circuit). Always prefer causal interventions over attention visualization for interpretability claims.

**What is polysemanticity, and how do SAEs address it?** Polysemanticity: a single neuron fires for multiple unrelated concepts (e.g., "cat", "DNA", "French Revolution"). This happens because there are more concepts than neurons — the model uses superposition to pack many features into fewer dimensions. SAEs decompose activations into many sparse monosemantic features, where each feature fires for one concept. The SAE is trained with a reconstruction loss plus an L1 sparsity penalty.

**How would you use mechanistic interpretability in production?** Three concrete patterns. (1) SAE-based monitoring: deploy SAEs alongside the model; flag responses where "deception" or "harmful intent" features fire. (2) Steering vectors: train probes for properties (sycophancy, toxicity), then add/subtract the probe direction from the residual stream during inference to control behavior. (3) Circuit-level debugging: when the model makes a specific error, use activation patching to localize the responsible head, then fine-tune or mask that head. Most of this is research-grade in 2026 but moving toward production.

**Why do induction heads emerge suddenly during training?** The leading hypothesis (Olsson et al. 2022): induction heads require a two-head composition (previous-token + induction), which is a "phase transition" — small improvements in either head don't help until both are good enough, then the composition suddenly clicks. This is consistent with the sudden capability jump observed in ICL benchmarks. The exact mechanism is still being studied; the sudden emergence is one of the cleanest examples of "grokking"-like behavior in LLM training.

## Further reading

- Elhage et al. (2021), *A Mathematical Framework for Transformer Circuits* (Anthropic).
- Olsson et al. (2022), *In-context Learning and Induction Heads* (Anthropic).
- Nostalgebraist (2020), *Interpreting GPT: the Logit Lens* (blog).
- Anthropic (2024), *Scaling Monosemanticity* (SAEs on Claude 3).
- Neel Nanda's interpretability blog and ARENA tutorial.

## See also

- [[Interpretability and Research MOC]] — the area orientation for interpretability and research.
- [[Logit Lens and Tuned Lens]] — the simplest mechanistic tool.
- [[Activation Patching and Causal Tracing]] — causal analysis.
- [[Sparse Autoencoders]] — feature decomposition.
- [[Probing]] — the supervised counterpart.
- [[Multi-Head Attention]] — head specialization is a mechanistic finding.
- [[In-Context Learning]] — induction heads enable ICL.
- [[Guardrails]] — production application.
- [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]] — representation engineering can be seen as "LoRA for behavior".
- [[GPT-2]] — the model used in the logit lens worked example.
- [[Inference and Production MOC]]
