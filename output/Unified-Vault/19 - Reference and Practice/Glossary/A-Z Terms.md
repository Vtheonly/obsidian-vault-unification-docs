---
title: A-Z Terms
type: reference
aliases: ["A-Z Terms", "Glossary Terms", "A-Z Glossary Terms"]
tags: [glossary, terms, reference]
sources: ["A-Z Terms"]
created_index: 1
---

This note is the alphabetical glossary of AI engineering terms used throughout the vault: each entry pairs a concise definition with a link to the dedicated concept note where one exists. Coverage runs from activation functions and attention mechanisms through training, retrieval, serving, and interpretability vocabulary. Entries are grouped by initial letter, with sparse letters sharing a band. For acronym expansions see [[Acronyms Index]]; for mathematical symbol conventions see [[Notation Conventions]].

## A

The A entries cover activation and attention machinery, agent and retrieval patterns, and general modeling vocabulary.

- **Activation function** — a nonlinear function applied to a neuron's output. Common: ReLU, GELU, SwiGLU. See [[Activation Functions]]
- **Activation patching** — intervention technique for establishing causality in interpretability. See [[Activation Patching and Causal Tracing]]
- **Adapter** — a small trainable module inserted into a frozen pretrained model for efficient fine-tuning. See [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]]
- **Additive attention** — Bahdanau's scoring function using a feed-forward network. See [[08 - Attention and Transformers/Attention Mechanism/Bahdanau Attention|Bahdanau Attention]]
- **Agent** — an LLM that reasons and takes actions via tools. See [[Agent vs Workflow vs LLM Application]]
- **Agentic RAG** — RAG where the LLM decides when to retrieve and what to query. See [[Advanced RAG Patterns]]
- **Alignment** — adjusting model behavior to be helpful, harmless, and honest. See [[InstructGPT]]
- **ALiBi** — positional encoding using attention biases. See [[ALiBi]]
- **Anchor box** — predefined bounding box in object detection.
- **Approximate Nearest Neighbor (ANN)** — algorithms for fast vector similarity search. See [[Vector Memory Backends]]
- **Attention** — mechanism for weighting different parts of the input. See [[Self-Attention]]
- **Attention head** — a single attention sublayer in multi-head attention. See [[Multi-Head Attention]]
- **Attention weight** — the softmax-normalized similarity between a query and a key.
- **Autonomous agent** — an agent that operates without human intervention for extended periods.
- **Autoregressive** — generating one token at a time, conditioning on previous outputs. See [[Decoder-Only Architecture]]

## B

The B entries cover the core gradient-computation algorithm, tokenization and decoding vocabulary, and two distinct senses of bias.

- **Backpropagation** — algorithm for computing gradients in neural networks. See [[Backpropagation]]
- **Bahdanau attention** — additive attention; the original attention mechanism. See [[08 - Attention and Transformers/Attention Mechanism/Bahdanau Attention|Bahdanau Attention]]
- **Batch size** — number of examples processed in one forward/backward pass.
- **Beam search** — decoding that maintains top-K candidate sequences. See [[Beam Search and Decoding Strategies]]
- **BERT** — bidirectional encoder Transformer. See [[08 - Attention and Transformers/Transformer Architecture/BERT|BERT]]
- **Bias** — systematic deviation from the true value; can refer to model bias (demographic) or statistical bias (estimator).
- **Block table** — PagedAttention's mapping from logical to physical KV cache blocks. See [[PagedAttention]]
- **BPE** — Byte-Pair Encoding; tokenization by merging frequent character pairs. See [[BPE]]
- **Broadcasting** — NumPy/tensor operation for combining arrays of different shapes. See [[Tensors and Broadcasting]]
- **Byte-level BPE** — BPE operating on bytes, avoiding out-of-vocabulary tokens. Used in GPT-2.

## C

The C entries span causal-intervention techniques, prompting and chat formats, RAG components, and convolutional and attention variants.

- **Causal masking** — preventing attention to future tokens; used in decoders. See [[Decoder-Only Architecture]]
- **Causal tracing** — a specific activation patching technique for localizing information. See [[Activation Patching and Causal Tracing]]
- **Chain-of-Thought (CoT)** — prompting the model to reason step by step. See [[Chain of Thought]]
- **Chat template** — format for wrapping user/assistant messages. See [[Instruction Tuning and Chat Templates]]
- **Checkpoint** — saved model state during training, used for resumption or evaluation.
- **Chunking** — splitting documents into passages for RAG. See [[Chunking, Hybrid Search, and Reranking]]
- **Circuit** — a subnetwork of attention heads/MLPs performing a specific function. See [[Mechanistic Interpretability]]
- **Classifier** — a model that predicts discrete labels.
- **CLIP** — contrastive vision-language model. See [[CLIP]]
- **Compute-optimal** — training at the optimal ratio of parameters to data. See [[Pretraining Objectives and Scaling Laws]]
- **Concat attention** — Bahdanau-style additive attention.
- **Conditioning** — providing context to a generative model to guide output.
- **Constitutional AI** — alignment via AI feedback on the model's own outputs.
- **Context window** — the maximum sequence length an LLM can process.
- **Continuous batching** — iteration-level batching for LLM serving. See [[Continuous Batching]]
- **Contrastive learning** — training to pull similar examples together, push dissimilar apart. See [[CLIP]]
- **Control task** — a baseline for probing experiments. See [[Probing]]
- **Convolution** — sliding-window operation over an input. See [[The Convolution Operation]]
- **Cross-attention** — attention between two sequences (e.g., encoder-decoder). See [[Cross-Modal Attention]]
- **Cross-encoder** — a model that takes (query, document) pairs and outputs a relevance score. Used for reranking.
- **Cross-entropy** — loss function for classification. See [[Entropy Cross-Entropy and KL Divergence]]
- **Curriculum learning** — training on increasingly difficult examples.

## D

The D entries collect decoding and architecture terms, data hygiene, and the adaptation and regularization basics.

- **Decoder** — the generation part of a Transformer. See [[Decoder-Only Architecture]]
- **Deduplication** — removing duplicate data in pretraining. See [[Pretraining Objectives and Scaling Laws]]
- **Deep learning** — neural networks with many layers.
- **Dense model** — non-MoE model; all parameters active per token.
- **Diffusion** — generative process that iteratively denoises. See [[DiT and FLUX]]
- **Distillation** — training a smaller model to mimic a larger one.
- **Distributed training** — training across multiple GPUs/nodes. See [[Distributed Training]]
- **Dot product** — sum of element-wise products; a similarity measure. See [[Dot Product]]
- **DPO** — Direct Preference Optimization. See [[DPO]]
- **Dropout** — regularization that randomly zeros activations during training.

## E

The E entries cover evaluation splits, agent memory, the encoder side of the Transformer, and information-theoretic vocabulary.

- **Early stopping** — stopping training when validation performance stops improving.
- **Edge device** — resource-constrained device (phone, IoT). See [[Ollama and llama.cpp]]
- **Embedding** — vector representation of a token or document.
- **Encoder** — the understanding part of a Transformer. See [[08 - Attention and Transformers/Transformer Architecture/BERT|BERT]]
- **Entropy** — measure of uncertainty or information content. See [[Entropy Cross-Entropy and KL Divergence]]
- **Episodic memory** — memory of specific past events. See [[Memory Types]]
- **Eval set** — held-out data for evaluating model performance.
- **Expert** — a subnetwork in a Mixture-of-Experts model. See [[Mixture of Experts]]

## F

The F entries deal with representations and adaptation: features, in-context examples, the feed-forward sublayer, fine-tuning, and efficient attention.

- **Feature** — an individual measurable property or learned representation.
- **Few-shot** — providing a few examples in the prompt. See [[In-Context Learning]]
- **FFN** — Feed-Forward Network; the MLP sublayer in a Transformer. See [[Feed-Forward Network]]
- **Fine-tuning** — adapting a pretrained model to a specific task. See [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]]
- **FlashAttention** — IO-aware exact attention. See [[08 - Attention and Transformers/Efficient Attention/FlashAttention|FlashAttention]]
- **Float16 (FP16)** — 16-bit floating point; standard for LLM training.
- **Format validation** — checking that model output matches expected schema.
- **Foundation model** — a large pretrained model adapted to many tasks. See [[Foundation Models and Multimodal MOC]]

## G

The G entries span gating mechanisms, gradients and training diagnostics, decoding strategies, and the attention variants that cut inference cost.

- **Gate** — a multiplicative scaling factor (e.g., in LSTM, SwiGLU).
- **Gated attention** — attention combined with a gating mechanism.
- **GELU** — Gaussian Error Linear Unit; common activation function. See [[Activation Functions]]
- **Generalization** — performing well on unseen data.
- **Generative model** — a model that produces new data (text, images).
- **Global attention** — tokens that attend to everything (Longformer). See [[Longformer]]
- **GPU** — Graphics Processing Unit; the workhorse of deep learning.
- **Gradient** — vector of partial derivatives; direction of steepest increase. See [[Gradient and Chain Rule]]
- **Gradient checkpointing** — trading compute for memory by recomputing activations during backprop.
- **Gradient clipping** — limiting gradient magnitude to prevent instability. See [[Learning Rate Schedules]]
- **GraphRAG** — RAG over a knowledge graph. See [[Advanced RAG Patterns]]
- **Greedy decoding** — always picking the highest-probability token. See [[Sampling Strategies]]
- **GRPO** — Group Relative Policy Optimization (DeepSeek). See [[DeepSeek-R1]]
- **GQA** — Grouped-Query Attention. See [[GQA MQA and MLA]]
- **Guardrail** — input/output filter for safety and policy. See [[Guardrails]]

## H

The H entries hold failure modes and retrieval infrastructure: hallucination, vector indexes, human oversight, and hybrid search.

- **Hallucination** — model produces fabricated information. See [[Hallucination]]
- **HNSW** — Hierarchical Navigable Small World; popular vector index. See [[Vector Memory Backends]]
- **Human-in-the-loop (HiTL)** — requiring human approval at certain agent steps. See [[LangGraph]]
- **Hybrid search** — combining vector and keyword search. See [[Chunking, Hybrid Search, and Reranking]]
- **HyDE** — Hypothetical Document Embeddings; RAG query rewriting technique.

## I

The I entries cover in-context learning, interpretability vocabulary, and efficiency terminology.

- **In-context learning (ICL)** — learning from examples in the prompt. See [[In-Context Learning]]
- **Induction head** — attention head that performs pattern completion. See [[Mechanistic Interpretability]]
- **Inference** — running a trained model on inputs.
- **Instruction tuning** — fine-tuning on instruction-response pairs. See [[Instruction Tuning and Chat Templates]]
- **IO-aware** — algorithm optimized for memory access patterns. See [[08 - Attention and Transformers/Efficient Attention/FlashAttention|FlashAttention]]

## J-K

This band bridges calculus (the Jacobian), information theory (KL divergence), knowledge representation, and the KV cache.

- **Jacobian** — matrix of all first-order partial derivatives. See [[02 - Mathematics/Calculus/Jacobians and Hessians|Jacobians and Hessians]]
- **KL divergence** — Kullback-Leibler divergence; measure of distribution difference. See [[Entropy Cross-Entropy and KL Divergence]]
- **Knowledge distillation** — training a smaller model to mimic a larger one.
- **Knowledge graph** — structured representation of entities and relationships.
- **KV cache** — cached keys/values for efficient autoregressive generation. See [[KV Cache Mechanics]]

## L

The L entries cover normalization, the learning rate, attention approximations, and interpretability tooling.

- **Latent space** — the learned representation space.
- **LayerNorm** — layer normalization. See [[Normalization Layers]]
- **Learning rate** — step size for gradient descent. See [[Learning Rate Schedules]]
- **Linear attention** — attention approximated to be O(N). See [[Linear Attention]]
- **Logit** — raw output of a model before softmax.
- **Logit lens** — applying the unembedding to intermediate activations. See [[Logit Lens and Tuned Lens]]
- **Long context** — sequence lengths >8K tokens. See [[Longformer]]
- **LoRA** — Low-Rank Adaptation. See [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]]
- **Loss function** — measure of prediction error. See [[Entropy Cross-Entropy and KL Divergence]]
- **Luong attention** — multiplicative (dot-product) attention. See [[08 - Attention and Transformers/Attention Mechanism/Luong Attention|Luong Attention]]

## M

The M entries are dense: sequence models, attention variants, agent memory, and model-lifecycle terminology.

- **Mamba** — selective state-space model. See [[Mamba]]
- **Masked Language Modeling (MLM)** — pretraining objective: predict masked tokens. See [[08 - Attention and Transformers/Transformer Architecture/BERT|BERT]]
- **Matrix multiplication** — fundamental linear algebra operation. See [[Matrix Multiplication]]
- **Maxout** — activation function taking the max over linear projections.
- **MCP** — Model Context Protocol. See [[MCP Overview]]
- **MemGPT** — OS-inspired memory hierarchy for agents. See [[MemGPT and Letta]]
- **Memory** — persistent state for agents. See [[Memory Types]]
- **Mixture of Experts (MoE)** — conditional computation with expert subnetworks. See [[Mixture of Experts]]
- **MLA** — Multi-head Latent Attention (DeepSeek). See [[GQA MQA and MLA]]
- **Model card** — documentation describing a model's capabilities, limitations, and intended use.
- **Model editing** — surgically modifying specific knowledge in a model. See [[Activation Patching and Causal Tracing]]
- **Model registry** — versioned store for model artifacts. See [[Model Registry and Versioning]]
- **Monosemantic** — a feature that represents a single concept. See [[Sparse Autoencoders]]
- **MQA** — Multi-Query Attention. See [[GQA MQA and MLA]]
- **Multi-agent system** — multiple agents coordinating. See [[Multi-Agent Architectures]]
- **Multi-head attention** — parallel attention heads. See [[Multi-Head Attention]]
- **Multi-hop retrieval** — iterative retrieval for complex queries. See [[Advanced RAG Patterns]]
- **Multimodal** — processing multiple modalities (text, image, audio). See [[Multimodal AI Overview]]

## N

The N entries cover language-modeling objectives and the basic vocabulary of neural networks.

- **N-gram** — sequence of N consecutive tokens. See [[N-Gram Language Models]]
- **Neural network** — a model composed of layers of neurons.
- **Neuron** — a single unit in a neural network.
- **Next-token prediction** — pretraining objective: predict the next token. See [[Decoder-Only Architecture]]
- **Normalization** — standardizing activations. See [[Normalization Layers]]
- **NSP** — Next Sentence Prediction; BERT's auxiliary objective. See [[08 - Attention and Transformers/Transformer Architecture/BERT|BERT]]

## O

The O entries collect production monitoring, prompting regimes, and optimization vocabulary.

- **Observability** — monitoring, logging, and tracing for production systems. See [[Observability Stack]]
- **One-shot** — providing a single example in the prompt. See [[In-Context Learning]]
- **Optimization** — finding model parameters that minimize loss. See [[Optimization Essentials]]
- **Overfitting** — model learns training data too well, generalizes poorly.

## P

The P entries span inference infrastructure, training objectives, and prompt-centric terminology.

- **PagedAttention** — block-level KV cache management. See [[PagedAttention]]
- **Parameter** — a learnable weight in a model.
- **Perceptron** — the simplest neural network unit. See [[Perceptrons and Multi-Layer Perceptrons]]
- **Perplexity** — exponentiated cross-entropy; a language modeling metric. See [[Perplexity]]
- **PGvector** — Postgres extension for vector storage. See [[Vector Storage with pgvector]]
- **Positional encoding** — encoding token positions. See [[Positional Encoding]]
- **PPO** — Proximal Policy Optimization. See [[Proximal Policy Optimization]]
- **Pre-norm** — normalization before the sublayer (more stable than post-norm). See [[Pre-Norm vs Post-Norm]]
- **Pretraining** — initial training on large unlabeled data. See [[Pretraining Objectives and Scaling Laws]]
- **Prompt** — input to an LLM.
- **Prompt engineering** — crafting prompts for desired outputs. See [[Prompt Management]]
- **Prompt injection** — adversarial input that overrides system instructions. See [[LLM Security and Prompt Injection]]
- **Probing** — training a classifier on activations to test what they encode. See [[Probing]]
- **PyTorch** — popular deep learning framework.

## Q

The Q entries cover the query-key-value trio and precision-reduction techniques.

- **Q-K-V** — Query, Key, Value in attention. See [[Queries Keys and Values]]
- **QLoRA** — Quantized LoRA. See [[QLoRA]]
- **Quantization** — reducing precision (e.g., FP16 → INT4) for efficiency. See [[Quantization]]
- **Query rewriting** — transforming a user query for better retrieval.

## R

The R entries are anchored by retrieval-augmented generation and reinforcement learning, with normalization and request routing alongside.

- **RAG** — Retrieval-Augmented Generation. See [[RAG Pipeline Overview]]
- **Reasoning model** — model trained for multi-step reasoning (o1, R1). See [[Reasoning Models]]
- **ReAct** — Reasoning + Acting pattern. See [[ReAct Pattern]]
- **Recall** — fraction of relevant items retrieved.
- **Recurrent** — processing sequences step by step. See [[Recurrent Neural Networks]]
- **Reflexion** — agent pattern with self-critique. See [[Reflection]]
- **Refusal** — model declines to answer.
- **Reinforcement Learning (RL)** — learning from reward signals. See [[Markov Decision Processes and Bellman Equations]]
- **Reranking** — re-scoring retrieved documents with a more expensive model. See [[Chunking, Hybrid Search, and Reranking]]
- **Residual connection** — skip connection that adds input to output. See [[Residual Connections]]
- **Retrieval** — finding relevant documents for a query. See [[RAG Pipeline Overview]]
- **Reward hacking** — model exploiting reward function flaws. See [[RLHF with PPO]]
- **Reward model (RM)** — model that scores response quality. See [[InstructGPT]]
- **RLHF** — Reinforcement Learning from Human Feedback. See [[InstructGPT]]
- **RMSNorm** — Root Mean Square Normalization. See [[Normalization Layers]]
- **RNN** — Recurrent Neural Network. See [[Recurrent Neural Networks]]
- **RoPE** — Rotary Position Embedding. See [[RoPE]]
- **Router** — component that routes requests to appropriate models. See [[Gateway and Router Patterns]]

## S

The S entries are the most numerous in the glossary, covering sampling, attention sparsity, interpretability, serving, and learning regimes.

- **SAE** — Sparse Autoencoder. See [[Sparse Autoencoders]]
- **Sampling** — selecting tokens from the probability distribution. See [[Sampling Strategies]]
- **ScaleNorm** — normalization variant.
- **Scheduler** — component that manages request queueing and batching. See [[PagedAttention]]
- **Self-attention** — attention within a single sequence. See [[Self-Attention]]
- **Semantic caching** — caching responses for semantically similar queries.
- **Semantic search** — search based on meaning, not keywords. See [[Vector Memory Backends]]
- **Sentiment analysis** — classifying text by emotional tone.
- **Seq2Seq** — sequence-to-sequence model. See [[Seq2Seq and the Information Bottleneck]]
- **Shadow deployment** — running new model in parallel without serving traffic. See [[A-B Testing and Shadow Deployment]]
- **SFT** — Supervised Fine-Tuning. See [[Instruction Tuning and Chat Templates]]
- **Sliding window attention** — local attention within a window. See [[Sliding Window Attention]]
- **Softmax** — converts logits to probabilities. See [[Self-Attention]]
- **Sparse attention** — attention restricted to a subset of tokens. See [[Sparse Attention]]
- **Speculative decoding** — using a draft model to accelerate generation. See [[Speculative Decoding]]
- **State Space Model (SSM)** — linear-time sequence model. See [[SSMs Mamba and Frontiers]]
- **Steering** — modifying activations to control model behavior. See [[Sparse Autoencoders]]
- **Stop sequence** — token that terminates generation.
- **Streaming** — returning output incrementally as it's generated.
- **Superposition** — model representing more features than dimensions. See [[Sparse Autoencoders]]
- **Supervised learning** — learning from labeled data.
- **SwiGLU** — Swish-Gated Linear Unit; common FFN activation. See [[Feed-Forward Network]]
- **System prompt** — initial instructions defining the model's role.

## T

The T entries span tensors, tokenization, sampling controls, tool use, and the Transformer itself.

- **Temperature** — controls sampling randomness. See [[Sampling Strategies]]
- **Tensor** — multi-dimensional array. See [[Tensors and Broadcasting]]
- **Tensor parallelism** — splitting model layers across GPUs. See [[Distributed Training]]
- **Test set** — held-out data for final evaluation.
- **TF-IDF** — Term Frequency-Inverse Document Frequency. See [[TF-IDF]]
- **Token** — a unit of text (word, subword, or character).
- **Tokenization** — splitting text into tokens. See [[Tokenization Overview]]
- **Top-k** — sampling from the top K tokens. See [[Sampling Strategies]]
- **Top-p (nucleus)** — sampling from the smallest set of tokens with cumulative probability ≥ p. See [[Sampling Strategies]]
- **Tool calling** — LLM invoking external tools. See [[Function Calling]]
- **Trace** — distributed tracing for observability. See [[Observability Stack]]
- **Training** — optimizing model parameters on data.
- **Transfer learning** — applying knowledge from one task to another.
- **Transformer** — the dominant neural architecture. See [[Transformer Block]]
- **Trusted execution environment (TEE)** — secure area for running code.

## U

The U entries hold the fitting and learning regimes: underfitting, universal approximation, and unsupervised learning.

- **Underfitting** — model is too simple to capture the data.
- **Universal approximation** — neural networks can approximate any function. See [[Perceptrons and Multi-Layer Perceptrons]]
- **Unsupervised learning** — learning from unlabeled data.

## V

The V entries cover attention values, gradient pathologies, vector storage, and vision transformers.

- **Value** — the output vector in attention. See [[Queries Keys and Values]]
- **Vanishing gradient** — gradients become too small to learn. See [[05 - Neural Network Foundations/Training Dynamics and Stability/Vanishing and Exploding Gradients|Vanishing and Exploding Gradients]]
- **Vector** — a 1D tensor. See [[Vectors]]
- **Vector database** — database for storing and searching vectors. See [[Vector Memory Backends]]
- **Verifiable reward** — reward based on objective correctness (math, code). See [[DeepSeek-R1]]
- **ViT** — Vision Transformer. See [[ViT Architecture]]
- **vLLM** — popular LLM serving engine. See [[14 - Inference and Production/Inference/vLLM|vLLM]]

## W

The W entries collect training-schedule and parameter terminology plus two representation-learning methods.

- **Warmup** — gradually increasing learning rate at training start. See [[Learning Rate Schedules]]
- **Weight** — a learnable parameter in a model.
- **Weight decay** — L2 regularization on weights.
- **Word2Vec** — word embedding method. See [[Word2Vec GloVe and FastText]]
- **WordPiece** — tokenization method used by BERT. See [[WordPiece]]

## X-Y-Z

The final band covers a pretraining method, positional-encoding extensions, prompting regimes, and distributed-training optimizers.

- **XLNet** — generalized autoregressive pretraining.
- **YaRN** — Yet another RoPE extensioN. See [[YaRN and NTK-Aware Scaling]]
- **Zero-shot** — performing a task with no examples in the prompt. See [[In-Context Learning]]
- **ZeRO** — Zero Redundancy Optimizer for distributed training. See [[Distributed Training]]

## See also

The companion reference notes complete the glossary:

- [[Glossary MOC]] — the glossary hub
- [[Acronyms Index]] — expansions for every acronym used in the vault
- [[Notation Conventions]] — mathematical and symbolic conventions
