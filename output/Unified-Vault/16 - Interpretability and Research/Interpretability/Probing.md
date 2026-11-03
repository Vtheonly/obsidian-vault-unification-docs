---
title: Probing
type: concept
aliases: ["Probing", "Linear Probes", "Representation Analysis", "probing classifiers"]
tags: [interpretability, probing, linear-probes, representations]
sources: ["05 - Probing"]
created_index: 5
---

Probing trains a small classifier (usually linear) on top of frozen model activations to predict a property of the input (part-of-speech, sentiment, entity type, truth value). If the probe performs well, the property is "linearly encoded" in the activations. Probing is the simplest interpretability technique — easy to implement, broadly applicable, but vulnerable to the "probing-the-probe" critique (a powerful probe might learn the property from the input, not from the model's representation). This note covers the method and its formal definition, control tasks and selectivity, what probing has revealed from the BERTology era to frontier models, and how it compares with the rest of the interpretability toolkit.

## The problem being solved

[[Logit Lens and Tuned Lens|The logit lens]] and [[Sparse Autoencoders|SAEs]] analyze what the model predicts. But we often want to know what the model *represents* — does it encode part-of-speech? Does it track entities? Does it distinguish true from false statements?

Probing answers this directly: train a classifier on the activations to predict the property of interest. If the classifier succeeds, the property is encoded (at least linearly) in the activations.

Probing was the dominant interpretability technique from 2016–2020 (the "BERTology" era). It has been partly superseded by [[Mechanistic Interpretability|mechanistic interpretability]] — the broader research program, in which probing is one tool in the toolkit — which asks *how* the model computes, not just *what* it encodes, and by SAEs, which discover features without supervision. But probing remains useful for targeted questions about specific properties.

## The method

### Setup

A probing experiment has five steps:

1. **Choose a property** to probe: part-of-speech, dependency parse, entity type, sentiment, factual truth, coreference, etc.
2. **Collect labeled data**: a dataset where each input has the property labeled. For POS tagging, this is a treebank; for sentiment, a sentiment corpus.
3. **Extract activations**: run the base model on each input, save the activation at the layer/position of interest.
4. **Train a probe**: a small classifier (typically linear or 1-hidden-layer MLP) that takes the activation as input and predicts the property.
5. **Evaluate**: measure the probe's accuracy on held-out data. High accuracy → the property is encoded in the activations.

### Linear versus nonlinear probes

A **linear probe**, `y = W · h + b`, tests whether the property is linearly encoded. Linear probes are preferred in modern interpretability — linear encoding is easier to interpret and more likely to reflect the model's actual computation. An **MLP probe**, `y = MLP(h)`, is more expressive; it can detect properties that are nonlinearly encoded. But it is harder to interpret — the probe might learn complex transformations that don't reflect the model's computation.

The convention in modern interpretability is to use linear probes. If a linear probe fails, the property is either not encoded or is encoded nonlinearly (which is harder to study).

### Layer-wise probing

Train separate probes for each layer. This reveals how the property emerges across layers: early layers show low accuracy (the property is not yet encoded), middle layers peak (the property is encoded), and late layers may drop (the property is no longer needed for the model's task).

The "peak layer" is often interpreted as where the property is most accessible, but this is an oversimplification — the property might be present at all layers but in different forms.

## Formal definition and probe accuracy

A probe is a function $g_\phi: \mathbb{R}^d \to \mathcal{Y}$ mapping an activation $\mathbf{h} \in \mathbb{R}^d$ to a label $y \in \mathcal{Y}$. The probe is trained on a labeled dataset $\{(\mathbf{h}^{(i)}, y^{(i)})\}$ where $\mathbf{h}^{(i)} = f_\theta(x^{(i)})_{\ell, p}$ is the activation of base model $f_\theta$ at layer $\ell$ and position $p$ for input $x^{(i)}$.

For a linear probe: $g_\phi(\mathbf{h}) = \text{softmax}(W \mathbf{h} + \mathbf{b})$, with $W \in \mathbb{R}^{|\mathcal{Y}| \times d}$. Train by minimizing cross-entropy on the labeled set.

Probe accuracy is an **upper bound on linear decodability**. If accuracy is high, the property is linearly decodable from the activations. If accuracy is low, either (a) the property isn't encoded, (b) it's encoded nonlinearly, or (c) the probe is poorly trained. You cannot distinguish these without further experiments.

## Control tasks and selectivity

Hewitt & Liang (2019) introduced **control tasks** to address the probing-the-probe critique. A control task is a fake task where the labels are random per-word (e.g., predict a random "control label" for each word). A good probe should achieve high accuracy on the real task (e.g., POS tagging) and low accuracy on the control task, because the control labels are random — there's nothing to learn.

**Selectivity** = accuracy on real task − accuracy on control task. A probe with high selectivity is genuinely extracting information from the activations, not just memorizing inputs.

| Probe type         | Real task acc | Control task acc | Selectivity | Verdict               |
|--------------------|---------------|------------------|-------------|-----------------------|
| Linear (rank 1)    | 92%           | 12%              | 80%         | Excellent             |
| Linear (rank 8)    | 95%           | 25%              | 70%         | Good                  |
| 1-hidden-layer MLP | 97%           | 55%              | 42%         | Suspicious            |
| 5-layer MLP        | 99%           | 88%              | 11%         | Bad — probe memorizes |

This shows why linear probes are the convention: they have the highest selectivity, meaning high accuracy genuinely reflects encoding rather than probe power.

## What probing has revealed

### BERT's internal representations (2018–2020)

The "BERTology" era used probing extensively to understand [[08 - Attention and Transformers/Transformer Architecture/BERT|BERT]], and a consistent layered picture emerged.

**Part-of-speech is encoded early.** Linear probes can predict POS with >95% accuracy from layer 4+ of BERT. Syntax is encoded before semantics.

**Dependencies are encoded in middle layers.** Probes for dependency labels (subject, object, modifier) peak at layers 6–10.

**Entity type is encoded in middle-to-late layers.** Probes for "is this a person / location / organization" peak at layers 8–11.

**Coreference is encoded in late layers.** Probes for coreference resolution improve through the final layers.

These findings shaped the understanding of how Transformers process language: syntax first, semantics later, with entity and coreference information built up through the layers.

### Truthfulness probing (Burns et al., 2022)

The "Discovering Latent Knowledge" paper showed that you can train a linear probe to distinguish true from false statements, even on topics the model was never explicitly trained on. The probe generalizes across domains, suggesting the model encodes a notion of truth.

This has implications for AI safety: if models encode truth, we might be able to extract it directly (rather than relying on the model's verbal output, which may be dishonest or sycophantic).

### Sentiment and stance probing

Linear probes can extract sentiment, political stance, and other high-level properties from LLM activations with high accuracy. This enables applications like monitoring model outputs for bias, steering model behavior by modifying the probed direction, and detecting when the model is "uncertain" (probes for confidence).

### Code property probing

Probes can detect whether a code model encodes properties like variable type, function signature, or bug presence. This helps understand what code models learn and how to steer them.

## Worked example: layer-wise POS probing

The following script trains logistic-regression probes on [[Llama Family Architecture|Llama 3 8B]] activations, aligning the first subword of each word to its POS tag, then sweeping across layers:

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from sklearn.linear_model import LogisticRegression
import numpy as np

model_id = "meta-llama/Llama-3-8B"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto",
                                             output_hidden_states=True)

# Collect (activation, POS label) pairs from a labeled corpus
def collect_activations(sentences_with_pos, layer=15):
    X, y = [], []
    for tokens, pos_tags in sentences_with_pos:
        ids = tokenizer(tokens, is_split_into_words=True, return_tensors="pt").to(model.device)
        with torch.no_grad():
            out = model(**ids)
        h = out.hidden_states[layer]  # (1, T, d)
        # Align subword activations to word POS tags (use first subword per word)
        word_ids = ids.word_ids()
        for w_idx, pos in enumerate(pos_tags):
            sub_idx = word_ids.index(w_idx)
            X.append(h[0, sub_idx].cpu().numpy())
            y.append(pos)
    return np.array(X), np.array(y)

X_train, y_train = collect_activations(train_data, layer=15)
X_test, y_test = collect_activations(test_data, layer=15)
probe = LogisticRegression(max_iter=1000).fit(X_train, y_train)
print(f"Layer 15 POS accuracy: {probe.score(X_test, y_test):.3f}")

# Sweep layers
for layer in [0, 4, 8, 12, 15, 20, 24, 31]:
    X_tr, y_tr = collect_activations(train_data, layer=layer)
    X_te, y_te = collect_activations(test_data, layer=layer)
    probe = LogisticRegression(max_iter=1000).fit(X_tr, y_tr)
    print(f"Layer {layer:2d}: {probe.score(X_te, y_te):.3f}")
```

Expected pattern (Llama 3 8B, Penn Treebank POS): layer 0 ~30%, layer 8 ~90%, layer 15 ~95%, layer 24 ~92%, layer 31 ~88%. POS peaks in the middle layers, then slightly degrades as the model focuses on next-token prediction.

## Probing frontier models (GPT-4, Claude)

Probing API-only models like [[GPT-4 Technical Report|GPT-4]] is harder because you can't directly access activations. Two workarounds exist.

**Logit-level probing** uses the model's output logits as a proxy for the final hidden state. It is limited — only the final layer is accessible.

**Embedding-level probing** uses the embeddings exposed by some APIs (OpenAI's `text-embedding-3-large`). These are typically the final-layer pooled representation — useful for high-level properties (sentiment, topic) but not for layer-wise analysis.

For full probing (all layers, all positions), you need open-weights models (Llama, DeepSeek, Mistral). This is why interpretability research is concentrated on open models.

## Limitations

### The probing-the-probe critique

The fundamental critique (Hewitt & Liang, 2019): if the probe is too powerful, it might learn the property from the input (via the activation), not from the model's encoding. A 5-layer MLP probe might learn to predict POS from any reasonable word embedding, even if the model didn't encode POS specifically.

Three solutions are used. **Control tasks** train the probe on a random baseline task (e.g., predicting random labels for the same inputs); if the probe achieves high accuracy on the control task, it's too powerful. **Minimum description length** prefers probes that achieve the task with fewer parameters. **Linear probes only** is the most common solution — linear probes are constrained enough that high accuracy implies linear encoding.

### Correlation, not causation

Probing tells you the property is *encoded*, not that the model *uses* it. A probe might detect that the model encodes POS, but the model might not use POS for its actual predictions. To establish use, you need intervention — [[Activation Patching and Causal Tracing|activation patching]] is the causal version of probing.

### Requires labeled data

Probing is supervised — you need labeled examples of the property. This limits probing to properties for which labeled data exists. Unsupervised methods (SAEs) can discover features without labels.

### Limited to predefined properties

You can only probe for properties you think to test. The model might encode many other properties you don't know to look for. SAEs and other unsupervised methods can discover these.

### Probe quality affects conclusions

A poorly-trained probe (e.g., trained on too little data, or on a biased subset) might fail to detect an encoded property, leading to the false conclusion that the property isn't encoded. Careful probe training (sufficient data, regularization, cross-validation) is essential.

## Comparison to other techniques

Probing answers a different question than the other core techniques:

| Technique           | What it reveals                       | Causal? | Unsupervised?          |
|---------------------|---------------------------------------|---------|------------------------|
| Probing             | Whether a property is encoded         | No      | No                     |
| Logit Lens          | What the model predicts at each layer | No      | Yes                    |
| SAEs                | What features the model represents    | No      | Yes                    |
| Activation Patching | What activations cause behavior       | Yes     | No (hypothesis-driven) |

Probing is the simplest and most broadly applicable, but it answers the weakest question (encoding, not causation). The logit lens can be viewed as a special case of probing where the "property" is the model's prediction. For rigorous interpretability, combine probing with intervention. A fuller comparison across the three main techniques:

| Aspect                  | Probing                      | SAEs                         | Activation Patching          |
|-------------------------|------------------------------|------------------------------|------------------------------|
| Question answered       | "Is X encoded?"              | "What features are present?" | "Does X causally affect Y?"  |
| Supervision             | Supervised (needs labels)    | Unsupervised                 | Hypothesis-driven            |
| Causality               | No (correlational)           | No (correlational)           | Yes (intervention)           |
| Discovers new features? | No (only tests predefined)   | Yes                          | No (tests hypotheses)        |
| Compute cost            | Low (linear probe)           | High (train SAE)             | Medium (many forward passes) |
| Interpretability        | Low (probe is opaque)        | High (monosemantic features) | Medium (causal, not semantic)|
| Best for                | Targeted questions           | Exploratory analysis         | Causal claims                |

For rigorous interpretability, **combine** all three: probe to verify a property is encoded, SAE to find the features encoding it, activation patching to confirm causality.

## Tooling

Four options cover most probing work:

- **TransformerLens** (Neel Nanda): includes probing utilities.
- **AllenNLP Interpret**: probing toolkit for NLP models.
- **adapters** (HuggingFace): can be used as probes (train a small adapter on top of frozen model).
- **Custom**: easy to implement — extract activations with forward hooks, train a scikit-learn classifier.

## Recent developments (2024–2026)

**Probing for deception**: probes trained to detect when a model is "lying" (saying something it knows is false). Burns et al. (2022) showed this works for simple true/false statements; extending to open-ended deception is active research.

**Probing for latent knowledge**: if a model knows something but won't say it (due to RLHF), can we extract the knowledge via probing? This is the "latent knowledge extraction" agenda (Anthropic, 2024–2026).

**Steering vectors**: once you have a probe for a property (sentiment, honesty, toxicity), you can use the probe direction to *steer* the model — add or subtract the direction from the residual stream to amplify or suppress the property. This is "representation engineering" (Zou et al., 2023).

**Probing for in-context learning**: what does the model encode during [[In-Context Learning|ICL]]? Probes show the model encodes the task implicitly (e.g., "this is a translation task, source language X, target language Y") in early layers.

**Probing multimodal models**: probes for vision-language models reveal where image and text representations are aligned (typically in middle layers, after the projector).

## Future directions

**Probing at scale**: probing frontier models (GPT-4, Claude) requires API access and is expensive. Methods for efficient probing with limited data are active research.

**Unsupervised probing**: discover properties without predefined labels, similar to SAEs but using different techniques.

**Causal probing**: combine probing with intervention to establish both encoding and use. The "causal scrubbing" framework formalizes this.

**Probing for safety**: probe for properties like deception, sycophancy, or harmful intent, and use the probe to monitor or steer model behavior.

## Interview questions

**What is the probing-the-probe critique, and how do control tasks address it?** The critique: a powerful probe (5-layer MLP) might learn a property from the input (via the activation) even if the model didn't encode it. Control tasks address this by giving the probe a fake task with random labels — if the probe achieves high accuracy on the random labels, it's too powerful (memorizing inputs). Selectivity = real-task accuracy − control-task accuracy; high selectivity means the probe is genuinely extracting model-encoded information.

**Why are linear probes preferred over MLP probes in modern interpretability?** Three reasons. (1) Selectivity: linear probes have the highest selectivity, meaning high accuracy genuinely reflects linear encoding. (2) Interpretability: a linear direction in activation space is interpretable as a "feature direction"; MLP probes are opaque. (3) Convention: if a property isn't linearly decodable, that's itself a finding (the property is either not encoded or encoded nonlinearly). Linear probes are the right default; nonlinear probes should be used only with explicit justification.

**Probing finds that POS is encoded with 95% accuracy at layer 12. Does this mean the model uses POS for its predictions?** No. Probing is correlational — it shows the information is *available* in the activations, not that the model *uses* it. To establish use, you need activation patching: ablate the POS direction and see if the model's predictions change. If they do, the model uses POS; if not, the POS information is "epiphenomenal" (encoded but unused).

**How would you probe an API-only model like GPT-4?** Two approaches: (1) logit-level probing — request the top-k logits for each input and train a probe on the logit vector (limited to final layer, requires logprob access in the API). (2) Embedding-level probing — use the embedding API to get a pooled representation, train a probe on that (limited to high-level properties, no layer-wise analysis). For full probing (all layers), you must use open-weights models.

**What is a steering vector, and how does it relate to probing?** A steering vector is a direction in activation space corresponding to a property (sentiment, honesty, toxicity), typically found by training a linear probe and extracting the weight direction. You can steer the model by adding or subtracting this direction from the residual stream during inference — adding amplifies the property, subtracting suppresses it. This is "representation engineering" — using probes not just to read but to *write* model behavior.

**What does probing reveal about how Transformers process language?** The "BERTology" findings generalize to most Transformers: (1) syntax is encoded early (layers 1-4), (2) semantics in middle layers (5-10), (3) entity and coreference information in late layers (8-12), (4) the model's final-layer representation is optimized for the training task (next-token prediction for decoder-only, MLM for BERT). The "peak then decline" pattern reflects that the model repurposes its capacity as it approaches the output.

## See also

- [[Interpretability and Research MOC]] — the area orientation for interpretability and research.
- [[Mechanistic Interpretability]] — the broader research program; probing is one tool in the toolkit.
- [[Logit Lens and Tuned Lens]] — a special case of probing where the "property" is the model's prediction.
- [[Sparse Autoencoders]] — the unsupervised alternative to probing.
- [[Activation Patching and Causal Tracing]] — the causal version of probing.
- [[In-Context Learning]] — probing reveals what the model encodes during ICL.
- [[Guardrails]] — probes can be used as guardrail classifiers.
- [[PII and Data Leakage]] — probing for training data extraction.
- [[GPT-4 Technical Report]] — the frontier model probed via logit- and embedding-level workarounds.
- [[Llama Family Architecture]] — the open-weights family used in the layer-wise POS example.
