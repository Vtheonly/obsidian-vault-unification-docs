#!/usr/bin/env python3
"""DISC-002: emit the semantic-review decisions for the 114-candidate
prioritized review set (fragmented_derivation score>=0.85, cross-vault
unexplained_prerequisite score>=0.90, rare_essential score>=0.90).

Every rationale is grounded in corpus evidence gathered by
scripts/disc002_coverage_probe.py (definitional treatments located via
word-boundary search over both source vaults) or by noise classification.
Writes state/concept-candidates/002-disc002-decisions-batch1.jsonl.
"""
from __future__ import annotations

import json
from pathlib import Path

WORKING = Path("state/concept-candidates/.disc002-review-workingset.jsonl")
OUT = Path("state/concept-candidates/002-disc002-decisions-batch1.jsonl")
REVIEWER = "GLM-5.3 orchestrator, DISC-002 session 2026-10-28"

# term -> (action, rationale)
# Evidence citations come from scripts/disc002_coverage_probe.py output.
T: dict[str, tuple[str, str]] = {
    # ---- covered concepts (definitional treatments exist in the corpus) ----
    "bradley-terry": ("cover", "Bradley-Terry preference model is explicitly defined with the sigma(r_w)-r_l) formula in master-ai '12 - Fine-Tuning/DPO/04 - DPO Derivation.md:58' and applied in '26 - Papers/Alignment/07 - InstructGPT 2022.md:52' and the RLHF capstone; the discovery definition patterns missed it only because those notes phrase it as 'using the Bradley-Terry model'."),
    "curvature": ("cover", "loss-surface curvature is treated definitionally in master-ai '02 - Mathematics/Calculus/11 - Jacobians and Hessians.md:76' ('the curvature of f') and in optimization conditioning discussions ('02 - Mathematics/Optimization/12 - Optimization Essentials.md:437')."),
    "decoupled weight": ("cover", "fragment of 'decoupled weight decay' (AdamW); dedicated section '## AdamW: Decoupled Weight Decay' in master-ai '02 - Mathematics/Optimization/13 - Adam Derivation.md' plus Q&A at '12 - Optimization Essentials.md:445'."),
    "decoupled weight decay": ("cover", "dedicated section '## AdamW: Decoupled Weight Decay' in master-ai '02 - Mathematics/Optimization/13 - Adam Derivation.md'; contrast with L2-regularized Adam explained at '12 - Optimization Essentials.md:445'."),
    "detach": ("cover", "tensor.detach() semantics explained at ai-course '05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/03. Demystifying the Black Box - CNN Interpretability.md' ('.detach() disconnects the tensor from the graph') and in RNN pitfalls (master-ai '04 - Neural Networks/Architectures/04 - RNN LSTM GRU.md:547')."),
    "element-wise multiplication": ("cover", "the Hadamard product has dedicated headings in ai-course '01 - Foundations and Overview/01.2 - Mathematical Foundations/00. Linear Algebra Fundamentals.md' ('## The Hadamard product') and master-ai '02 - Mathematics/Linear Algebra/01 - Vectors.md' ('### Element-wise (Hadamard) Product')."),
    "encoder hidden": ("cover", "shorthand for encoder hidden states; defined and used throughout the seq2seq/attention material, e.g. master-ai '06 - Attention Mechanisms/Origins/02 - Bahdanau Attention.md:275' and ai-course '07 - Sequence Models and RNNs/07.4 - Sequence Modeling Pitfalls and Limits/01. The Bottleneck Problem - Why One Vector Is Not Enough.md:48'."),
    "encoder states": ("cover", "shorthand for encoder hidden states; treated definitionally in the encoder-decoder pattern notes (ai-course '07 - Sequence Models and RNNs/07.3 - Sequence to Sequence and Encoder-Decoder/01. The Encoder-Decoder Pattern - Conditional Generation.md:40') and Bahdanau notes."),
    "eval mode": ("cover", "model.eval()/train() mode semantics are part of the dropout and batch-norm treatments, e.g. ai-course '04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/06. Dropout and Regularization.md:140' (model.eval definitional hit)."),
    "false negatives": ("cover", "type II error / false negative is defined in master-ai '02 - Mathematics/Statistics/17 - Hypothesis Testing.md:47' and in the confusion-matrix treatments ('03 - Machine Learning/Evaluation/05 - ML Evaluation Metrics.md:28')."),
    "final linear": ("cover", "fragment of 'final linear layer' (transfer-learning classification head); head-replacement is treated in ai-course '05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/01. Transfer Learning and Fine-Tuning.md'."),
    "final linear layer": ("cover", "the replacement classification head in transfer learning is treated in the dedicated transfer-learning note (ai-course '04. Training, Transfer Learning, and PyTorch/01. Transfer Learning and Fine-Tuning.md')."),
    "high precision": ("cover", "as the metric, precision/recall are covered by the evaluation-metrics notes; as numerical precision, covered by mixed-precision training notes (master-ai '11 - Training/Optimization/04 - Mixed Precision Training.md'); both senses have corpus treatments."),
    "human preferences": ("cover", "preference-based alignment is the subject of the RLHF/DPO material; e.g. master-ai '08 - LLMs/Evaluation/06 - LLM Benchmarks.md:201' (Chatbot Arena 'measures real human preferences') and the alignment papers."),
    "imagenet pre-trained": ("cover", "pre-trained ImageNet backbones and their use in transfer learning are treated in ai-course '05 - Convolutional Neural Networks (CNN)/04. Training, Transfer Learning, and PyTorch/01. Transfer Learning and Fine-Tuning.md' and the weight-initialization note ('04.3 - Training Dynamics and Stability/01. Weight Initialization.md:724')."),
    "importance weights": ("cover", "importance weights w=p/q are part of the importance-sampling treatment with a dedicated heading in master-ai '02 - Mathematics/Probability/07 - Probability Essentials.md' ('### 1. Importance sampling') and the PPO ratio discussions."),
    "information theory": ("cover", "dedicated corpus material: master-ai '02 - Mathematics/Information Theory/15 - Entropy Cross-Entropy KL' note, the '### Information Theory' glossary section ('28 - Glossary/03 - Notation Conventions.md') and the Mathematics MOC."),
    "input activations": ("cover", "activations as a concept are treated in the activation-function and interpretability notes (e.g. master-ai '14 - Interpretability/Probing/05 - Probing.md'); the phrase is standard vocabulary, not a missing concept."),
    "intermediate activations": ("cover", "intermediate/hidden activations are the working material of the probing and mechanistic-interpretability notes (master-ai '14 - Interpretability/'); no dedicated treatment is missing."),
    "irreducible": ("cover", "fragment of 'irreducible error' inside the bias-variance decomposition, defined at master-ai '03 - Machine Learning/Generalization/01 - Bias Variance Tradeoff.md:12' (bias + variance + irreducible error) and the scaling-law irreducible loss ('11 - Training/Pretraining/01 - Pretraining Objectives and Scaling Laws.md:126')."),
    "jacobian product": ("cover", "Jacobian-vector products in backprop are treated in master-ai '02 - Mathematics/Calculus/11 - Jacobians and Hessians.md' and the vanishing/exploding-gradient analyses ('04 - Neural Networks/Training/08 - Vanishing and Exploding Gradients.md:22')."),
    "l2 norm": ("cover", "dedicated heading '## 5.4 The L2 Norm Squared' in ai-course '03 - Machine Learning/03.2 - Optimization Algorithms/06. Loss Functions and Error Calculation.md' and the vector-norm treatment in master-ai '02 - Mathematics/Linear Algebra/01 - Vectors.md:165'."),
    "last conv": ("cover", "fragment of 'last convolutional layer' in transfer learning; head replacement is treated in the transfer-learning notes (ai-course '04. Training, Transfer Learning, and PyTorch/01. Transfer Learning and Fine-Tuning.md')."),
    "last convolutional layer": ("cover", "the final conv layer as the feature-extractor boundary in transfer learning is treated in the transfer-learning material (ai-course '04. Training, Transfer Learning, and PyTorch/01. Transfer Learning and Fine-Tuning.md')."),
    "log-softmax": ("cover", "log-softmax inside CrossEntropyLoss is explained at ai-course '05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/04. Exercises Solved and Explained.md' ('CrossEntropyLoss internally applies log-softmax') and the reasoning-model capstone (master-ai '27 - Projects/Capstones/07 - Build a Reasoning Model Fine-Tune.md:247')."),
    "low-dimensional latent": ("cover", "fragment of 'low-dimensional latent space'; the latent-space concept has definitional treatments in the autoencoder and VAE notes (ai-course '10 - Generative Models/10.1 - Autoencoders/01. The Autoencoder - Compression as Learning.md:3') and master-ai '02 - Mathematics/Probability/09 - Gaussian Distribution.md:127'."),
    "majority class": ("cover", "majority-class prediction under imbalance is treated in ai-course '03 - Machine Learning/03.6 - Model Evaluation/02. Model Evaluation Metrics Beyond Accuracy.md:13' and '05 - Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and Interpretability/01. The Full Training Pipeline End-to-End Checklist.md'."),
    "proper initialization": ("cover", "dedicated note master-ai '04 - Neural Networks/Training/07 - Initialization Schemes.md' plus ai-course '04.3 - Training Dynamics and Stability/01. Weight Initialization.md'."),
    "pytorch's autograd": ("cover", "autograd mechanics have definitional treatments in master-ai '02 - Mathematics/Calculus/10 - Gradient and Chain Rule.md:22', '11 - Jacobians and Hessians.md:258', and the PyTorch training material."),
    "reference policy": ("cover", "the RLHF/DPO reference policy pi_ref is defined in master-ai '26 - Papers/Alignment/09 - DPO 2023.md:53' and used in the RLHF capstone KL-penalty discussion."),
    "relu activation": ("cover", "ReLU family has a dedicated heading in master-ai '04 - Neural Networks/Foundations/02 - Activation Functions.md' ('## The ReLU Family') and appears across 105 files; the derivation-position usages the tool found are downstream uses of a covered concept."),
    "residual connection": ("cover", "dedicated notes: ai-course '05 - Convolutional Neural Networks (CNN)/03. Architecture and Connectivity/08. The Degradation Problem and Residual Connections.md' and '09. ResNet Bottleneck Blocks and Architectural Variants.md'; transformer sublayer wrapping also defined (master-ai '26 - Papers/Transformers/02 - Vaswani Attention Is All You Need 2017.md:32')."),
    "save checkpoint": ("cover", "checkpointing is treated in master-ai '02 - Mathematics/Optimization/12 - Optimization Essentials.md:206' and '11 - Training/Optimization/05 - Loss Spikes and Stability.md:12'; routine operation vocabulary, not a missing concept."),
    "second moment": ("cover", "Adam's first/second moments and their bias corrections are defined in ai-course '03 - Machine Learning/03.2 - Optimization Algorithms/08. Loss Functions and Optimizers Deep Dive.md:315' and '04.3 - Training Dynamics and Stability/04. Hyperparameters and Network Configuration.md:290'."),
    "spatial position": ("cover", "spatial positions as the sites where shared kernels are applied are part of the weight-sharing treatments (ai-course '05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/01. The Convolution Operation Deep Dive.md:139'; master-ai '04 - Neural Networks/Architectures/03 - CNNs.md:284')."),
    "squeeze": ("cover", "tensor reshaping operations (squeeze/unsqueeze) are tensor-manipulation vocabulary treated in master-ai '02 - Mathematics/Linear Algebra/06 - Tensors and Broadcasting.md' (shape-manipulation guidance); not a standalone missing concept."),
    "true class": ("cover", "ground-truth class in loss/metric definitions is standard vocabulary defined alongside the confusion matrix and cross-entropy treatments (master-ai '03 - Machine Learning/Evaluation/05 - ML Evaluation Metrics.md')."),
    "true convolution": ("cover", "the true-convolution vs cross-correlation distinction is explicitly treated at ai-course '05 - Convolutional Neural Networks (CNN)/02. Core Operators and Geometry/01. The Convolution Operation Deep Dive.md:383'."),
    "3d tensor": ("cover", "3D volume/tensor treatment is foundational CNN material (ai-course '05 - Convolutional Neural Networks (CNN)/01. Foundations and Philosophy/01. Introduction and Foundations of CNNs.md:80', '05. Processing 3D Volumes, Depth Summation, and Biases.md'); master-ai '02 - Mathematics/Linear Algebra/06 - Tensors and Broadcasting.md' covers tensor shapes generally."),
    "upstream gradient": ("cover", "defined as 'the key quantity at each node' in master-ai '04 - Neural Networks/Training/06 - Backpropagation.md:48' and used in the gradient-and-chain-rule note ('02 - Mathematics/Calculus/10 - Gradient and Chain Rule.md:242')."),
    "update parameters": ("cover", "the optimizer-step operation is part of the training-loop treatments (definitional hits in 10 files incl. master-ai '27 - Projects/Implementations/05 - Build a Tiny LLM Trainer.md:12'); routine vocabulary."),
    "validation data": ("cover", "validation-set methodology is treated across the evaluation material (definitional hits in master-ai '03 - Machine Learning/Generalization/01 - Bias Variance Tradeoff.md:114', '05 - NLP Fundamentals/Language Modeling/08 - Perplexity.md:88')."),
    "val loss": ("cover", "validation-loss monitoring is standard vocabulary of the evaluation and overfitting treatments (same evidence class as 'validation data')."),
    "zero gradients": ("cover", "zero_grad() is part of the training-loop idiom treated across the corpus (definitional 'training loop' hits in 10 files); the underlying gradient-accumulation semantics are covered at master-ai '02 - Mathematics/Calculus/10 - Gradient and Chain Rule.md:155'."),
    "optimizer step": ("cover", "optimizer.step() is training-loop vocabulary; training loops have definitional treatments in 10 files (e.g. master-ai '27 - Projects/Implementations/05 - Build a Tiny LLM Trainer.md:12')."),
    "class logits": ("cover", "logits have definitional treatments in 10 files (e.g. master-ai '07 - Transformers/Architecture/01 - Transformer Block.md:150'); 'class logits' is vocabulary within those treatments."),
    "evaluation metric": ("cover", "evaluation metrics are the subject of dedicated notes (master-ai '03 - Machine Learning/Evaluation/05 - ML Evaluation Metrics.md'; ai-course '03 - Machine Learning/03.6 - Model Evaluation/')."),
    "pytorch accumulates": ("cover", "fragment of 'PyTorch accumulates gradients'; gradient-accumulation semantics are covered at master-ai '02 - Mathematics/Calculus/10 - Gradient and Chain Rule.md:155' and '02 - Mathematics/Optimization/12 - Optimization Essentials.md:46'."),
    "pytorch accumulates gradients": ("cover", "gradient-accumulation semantics (why zero_grad is needed, simulating large batches) are covered at master-ai '02 - Mathematics/Calculus/10 - Gradient and Chain Rule.md:155' and '02 - Mathematics/Optimization/12 - Optimization Essentials.md:46'."),
    "accumulates gradients": ("cover", "fragment of the gradient-accumulation concept; covered at master-ai '02 - Mathematics/Calculus/10 - Gradient and Chain Rule.md:155' ('Gradient accumulation lets you simulate large batch sizes...')."),
    "hessian eigenvalues": ("cover", "eigenvalues of the Hessian have a dedicated section in master-ai '02 - Mathematics/Calculus/11 - Jacobians and Hessians.md' ('### Eigenvalues of the Hessian') and the strong-convexity treatment at '02 - Mathematics/Optimization/12 - Optimization Essentials.md:227'."),
    "reject-placeholder": ("none", ""),
}

R_NOISE = {
    "numeric-literal": "numeric literal from code/config, not a concept",
    "code-identifier": "code identifier / API name, not a concept",
    "import-fragment": "import-statement fragment, not a concept",
    "citation-fragment": "author-citation fragment, not a concept",
    "prose-fragment": "verb/prose fragment without conceptual denotation",
    "generic-vocabulary": "generic vocabulary, not a distinct concept",
}

REJECTS: dict[str, tuple[str, str]] = {
    "10 classes": ("numeric-literal", ""),
    "2048": ("numeric-literal", "embedding dimension literal"),
    "64 channels": ("numeric-literal", "channel-count literal"),
    "230": ("numeric-literal", ""),
    "always call": ("prose-fragment", ""),
    "apply softmax": ("prose-fragment", "softmax itself is covered in the attention/classification notes"),
    "args": ("code-identifier", ""),
    "average loss": ("generic-vocabulary", "loss averaging is part of the loss-function treatments"),
    "bahdanau et": ("citation-fragment", "Bahdanau attention itself has dedicated corpus notes"),
    "bahdanau et al": ("citation-fragment", "Bahdanau attention itself has dedicated corpus notes"),
    "cho": ("citation-fragment", "Cho et al. seq2seq; the seq2seq material is covered"),
    "class names": ("generic-vocabulary", ""),
    "classes equally": ("prose-fragment", "class-imbalance handling is covered by the evaluation notes"),
    "cmap": ("code-identifier", "matplotlib parameter"),
    "cuda'": ("code-identifier", "device string literal"),
    "data flow": ("generic-vocabulary", ""),
    "data import": ("import-fragment", ""),
    "data import dataloader": ("import-fragment", ""),
    "datasets import": ("import-fragment", ""),
    "decoder computes": ("prose-fragment", ""),
    "def forward": ("code-identifier", "PyTorch method definition"),
    "device configuration": ("generic-vocabulary", "routine setup"),
    "different models": ("generic-vocabulary", ""),
    "different normalization": ("generic-vocabulary", "normalization methods have dedicated notes"),
    "eagle-2's": ("code-identifier", "model-name fragment"),
    "entire dataset": ("generic-vocabulary", ""),
    "every parameter": ("prose-fragment", ""),
    "execute": ("prose-fragment", ""),
    "figsize": ("code-identifier", "matplotlib parameter"),
    "generate token": ("prose-fragment", "decoding/token generation is covered by the inference notes"),
    "generalize better": ("prose-fragment", ""),
    "imagefolder": ("code-identifier", "torchvision dataset class"),
    "import dataloader": ("import-fragment", ""),
    "import image": ("import-fragment", ""),
    "import math": ("import-fragment", ""),
    "import matplotlib": ("import-fragment", ""),
    "information across": ("prose-fragment", ""),
    "lambdalr": ("code-identifier", "scheduler class name"),
    "large batches": ("prose-fragment", "batch-size effects are covered in the hyperparameter notes"),
    "large learning": ("prose-fragment", "fragment of 'large learning rate'; LR effects are covered"),
    "line count": ("generic-vocabulary", ""),
    "lr'": ("code-identifier", "variable name with quote artifact"),
    "metrics import": ("import-fragment", ""),
    "model entirely": ("prose-fragment", ""),
    "network learns": ("prose-fragment", ""),
    "only add": ("prose-fragment", ""),
    "output step": ("prose-fragment", "decoder-step concept is covered by the encoder-decoder notes"),
    "params'": ("code-identifier", "variable name with quote artifact"),
    "per-parameter": ("prose-fragment", "Adam's per-parameter adaptivity is covered by the Adam notes"),
    "pil image": ("code-identifier", "PIL API"),
    "plt": ("code-identifier", "matplotlib alias"),
    "prerequisites": ("generic-vocabulary", "generic word in course-frontmatter context"),
    "previous step": ("prose-fragment", "recurrence over previous steps is covered by the RNN notes"),
    "probs": ("code-identifier", "variable name"),
    "propagate backward": ("prose-fragment", "backpropagation is covered by dedicated notes"),
    "randint": ("code-identifier", "API name"),
    "randomly zeros": ("prose-fragment", "dropout's zeroing is covered by the dedicated dropout notes"),
    "rejected": ("generic-vocabulary", "adjective; rejected samples in RLHF are covered by the alignment notes"),
    "saves memory": ("prose-fragment", ""),
    "uint8": ("code-identifier", "dtype name"),
    "use batch": ("prose-fragment", ""),
    "xlabel": ("code-identifier", "matplotlib parameter"),
    "ylabel": ("code-identifier", "matplotlib parameter"),
}


def main() -> int:
    records = [
        json.loads(line)
        for line in WORKING.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    decisions = []
    n = 0
    missing = []
    for rec in sorted(records, key=lambda r: r["candidate_id"]):
        term = rec["term"]
        if term in T and T[term][0] != "none":
            action, rationale = T[term]
        elif term in REJECTS:
            noise, note = REJECTS[term]
            action = "reject"
            rationale = (
                f"Non-concept noise ({noise}): {R_NOISE[noise]}."
                + (f" Note: {note}." if note else "")
            )
        else:
            missing.append(term)
            continue
        n += 1
        decisions.append(
            {
                "candidate_id": rec["candidate_id"],
                "decision_id": f"D-DISC002-{n:04d}",
                "action": action,
                "rationale": rationale,
                "reviewer": REVIEWER,
            }
        )
    if missing:
        print("MISSING TERMS (no decision):", missing)
        return 1
    OUT.write_text(
        "".join(json.dumps(d, sort_keys=True) + "\n" for d in decisions),
        encoding="utf-8",
    )
    from collections import Counter

    print(f"wrote {len(decisions)} decisions -> {OUT}")
    print("by action:", dict(Counter(d["action"] for d in decisions)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
