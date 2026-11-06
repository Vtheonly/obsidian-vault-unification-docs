---
title: Matrix Multiplication
type: concept
aliases:
  - Matrix Multiplication
  - Matrix Product
  - Matmul
  - Matrix Multiply
tags:
  - mathematics
  - linear-algebra
  - matrix-multiplication
  - deep-learning
  - flops
sources:
  - "04 - Matrix Multiplication"
created_index: 7
---

Matrix multiplication is the workhorse of deep learning: every linear layer, every attention computation, and every convolution can be expressed as a sequence of matrix multiplications. This note develops the mechanics of the product — the defining sum, the shape rules, the algebraic properties — and then the four complementary views that make it intelligible, the FLOP accounting that makes it expensive, and the hardware facts that make it fast. It sits in the Linear Algebra thread of [[Mathematics MOC]], alongside [[Vectors]] and [[Dot Product]].

> [!info] TL;DR
> Matrix multiplication is the workhorse of deep learning — every linear layer, every attention computation, every convolution can be expressed as a sequence of matrix multiplications. Understanding it deeply is non-negotiable.

## Definition

Given $\mathbf{A} \in \mathbb{R}^{m \times k}$ and $\mathbf{B} \in \mathbb{R}^{k \times n}$, the product $\mathbf{C} = \mathbf{A}\mathbf{B} \in \mathbb{R}^{m \times n}$ is defined by:

$$
C_{ij} = \sum_{l=1}^{k} A_{il} B_{lj}
$$

In words: each element $C_{ij}$ is the **dot product** of the $i$-th row of $\mathbf{A}$ with the $j$-th column of $\mathbf{B}$.

The **inner dimensions** ($k$) must match. The result has shape $(m, n)$ — the **outer dimensions**.

In PyTorch:

```python
A = torch.randn(m, k)
B = torch.randn(k, n)
C = A @ B            # shape (m, n)
C = torch.matmul(A, B)  # equivalent
```

## Intuition

There are several complementary ways to think about matrix multiplication, and each one is developed in detail below.

### As a batch of dot products

Each entry of $\mathbf{C}$ is a dot product. The whole operation is just $m \times n$ dot products, each of length $k$.

### As a linear transformation

Multiplying a matrix $\mathbf{A} \in \mathbb{R}^{m \times k}$ by a vector $\mathbf{x} \in \mathbb{R}^k$ produces a vector $\mathbf{y} = \mathbf{A}\mathbf{x} \in \mathbb{R}^m$. This is a **linear map** from $\mathbb{R}^k$ to $\mathbb{R}^m$.

The columns of $\mathbf{A}$ tell you where the standard basis vectors of $\mathbb{R}^k$ land in $\mathbb{R}^m$. So a matrix multiplication is just "apply this linear transformation to the input".

### As a composition of linear maps

If $\mathbf{A}$ represents a linear map $f$ and $\mathbf{B}$ represents $g$, then $\mathbf{A}\mathbf{B}$ represents the composition $f \circ g$ — apply $g$ first, then $f$.

This is why deep networks stack matrix multiplications: each layer is a linear map followed by a nonlinearity, and the whole network is a composition of such maps.

### As a sum of outer products (rare but useful)

$$
\mathbf{A}\mathbf{B} = \sum_{l=1}^{k} \mathbf{a}_l \mathbf{b}_l^T
$$

where $\mathbf{a}_l$ is the $l$-th column of $\mathbf{A}$ and $\mathbf{b}_l^T$ is the $l$-th row of $\mathbf{B}$. This view is useful for understanding low-rank approximations (e.g., [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]]).

## Properties

Matrix multiplication obeys most of the familiar algebraic laws, with one critical exception:

- **Associative**: $(\mathbf{A}\mathbf{B})\mathbf{C} = \mathbf{A}(\mathbf{B}\mathbf{C})$
- **Distributive over addition**: $\mathbf{A}(\mathbf{B} + \mathbf{C}) = \mathbf{A}\mathbf{B} + \mathbf{A}\mathbf{C}$
- **NOT commutative** in general: $\mathbf{A}\mathbf{B} \neq \mathbf{B}\mathbf{A}$. Order matters.
- **Transpose**: $(\mathbf{A}\mathbf{B})^T = \mathbf{B}^T \mathbf{A}^T$
- **Inverse** (when defined): $(\mathbf{A}\mathbf{B})^{-1} = \mathbf{B}^{-1} \mathbf{A}^{-1}$

The non-commutativity is the property most worth internalizing, because it is the everyday source of shape bugs and silent logic errors: transposing an operand or swapping two matrices changes the result, not just its shape.

## Computational complexity

For $\mathbf{A} \in \mathbb{R}^{m \times k}$, $\mathbf{B} \in \mathbb{R}^{k \times n}$:

- **FLOPs**: $2mkn$ (multiply-adds count as 2 ops; or $mkn$ if you count MACs as 1)
- **Memory**: $mk + kn + mn$ to store inputs and output

The asymptotic complexity for square $n \times n$ matrices is $O(n^3)$ with the naive algorithm. The best known theoretical bound is around $O(n^{2.37})$ (Coppersmith-Winograd and successors), but these algorithms have huge constant factors and are not used in practice. For deep learning, the practical algorithm is **always** the naive one, but accelerated by **Tensor Cores** that perform many MACs in parallel.

## Worked example

$$
\mathbf{A} = \begin{pmatrix} 1 & 2 \\ 3 & 4 \end{pmatrix}, \quad \mathbf{B} = \begin{pmatrix} 5 & 6 \\ 7 & 8 \end{pmatrix}
$$

$$
\mathbf{A}\mathbf{B} = \begin{pmatrix} 1\cdot 5 + 2\cdot 7 & 1\cdot 6 + 2\cdot 8 \\ 3\cdot 5 + 4\cdot 7 & 3\cdot 6 + 4\cdot 8 \end{pmatrix} = \begin{pmatrix} 19 & 22 \\ 43 & 50 \end{pmatrix}
$$

Note: $\mathbf{B}\mathbf{A} = \begin{pmatrix} 23 & 34 \\ 31 & 46 \end{pmatrix} \neq \mathbf{A}\mathbf{B}$. Multiplication is **not** commutative.

## The four views in detail

Understanding all four views unlocks intuition for ML:

### View 1: dot products (element-level)

$C_{ij} = \mathbf{a}_{i,:} \cdot \mathbf{b}_{:,j}$. Each entry is a dot product. Useful for understanding what each entry "means" — it's the similarity between row $i$ of A and column $j$ of B.

### View 2: linear transformation (column-level)

$\mathbf{A}\mathbf{x}$ transforms vector $\mathbf{x}$. The columns of $\mathbf{A}$ are the images of the standard basis vectors. $\mathbf{A}\mathbf{B}$ is the composition: apply $\mathbf{B}$ first, then $\mathbf{A}$. This is why stacked linear layers are compositions of linear maps.

### View 3: sum of outer products (rank-1 decomposition)

$\mathbf{A}\mathbf{B} = \sum_{l=1}^{k} \mathbf{a}_{:,l} \mathbf{b}_{l,:}$. Each term is a rank-1 matrix (outer product of column $l$ of A with row $l$ of B). This view is the foundation of:
- **Low-rank approximation** (SVD, LoRA): truncate the sum to the top-$r$ terms.
- **Streaming computation**: compute one term at a time, accumulate.
- **Distributed matmul**: different GPUs compute different terms, sum the results.

### View 4: block multiplication (cache-level)

Partition A and B into blocks; multiply block-by-block. This is how GPUs actually compute matmuls — blocks are sized to fit in SRAM cache. FlashAttention is a sophisticated block-level algorithm that avoids materializing the full attention matrix.

Each view is "correct" — they're algebraically identical. But different views make different properties obvious:
- View 1 makes element computation obvious.
- View 2 makes composition/linearity obvious.
- View 3 makes low-rank structure obvious.
- View 4 makes hardware implementation obvious.

## Block matrix multiplication

Large matrix multiplications are often computed in **blocks** to fit in cache. This is the foundation of tiling — see [[08 - Attention and Transformers/Efficient Attention/FlashAttention|FlashAttention]] for the canonical example. The block form:

$$
\mathbf{A}\mathbf{B} = \begin{pmatrix} \mathbf{A}_{11} & \mathbf{A}_{12} \\ \mathbf{A}_{21} & \mathbf{A}_{22} \end{pmatrix} \begin{pmatrix} \mathbf{B}_{11} & \mathbf{B}_{12} \\ \mathbf{B}_{21} & \mathbf{B}_{22} \end{pmatrix}
$$

multiplies out block-by-block just like scalar multiplication.

## Batched matrix multiplication (bmm)

In ML we usually process batches. PyTorch's `torch.bmm` (or `@` with 3D tensors) computes independent matrix multiplications per batch element:

```python
# A: (batch, m, k), B: (batch, k, n) → C: (batch, m, n)
A = torch.randn(batch, m, k)
B = torch.randn(batch, k, n)
C = A @ B  # broadcasted bmm
```

For attention, we have 4D tensors: `(batch, num_heads, seq_len, head_dim)`. The `@` operator handles this naturally.

## Why it matters for AI

### Every linear layer is a matrix multiplication

A dense layer: $\mathbf{y} = \mathbf{W}\mathbf{x} + \mathbf{b}$. The weight matrix $\mathbf{W} \in \mathbb{R}^{m \times n}$ is the learnable parameters. See [[Perceptrons and Multi-Layer Perceptrons]].

### Attention is built on matrix multiplications

[[Scaled Dot-Product Attention|Scaled dot-product attention]] — the core of [[Self-Attention]] — is essentially:

$$
\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{Q K^T}{\sqrt{d_k}}\right) V
$$

— four matrix multiplications and a softmax. The vast majority of compute in an LLM forward pass is in these (and the FFN's) matrix multiplications.

### Backpropagation is also matrix multiplication

The backward pass of a linear layer is also a matrix multiplication:

$$
\frac{\partial L}{\partial \mathbf{x}} = \mathbf{W}^T \frac{\partial L}{\partial \mathbf{y}}
$$

$$
\frac{\partial L}{\partial \mathbf{W}} = \frac{\partial L}{\partial \mathbf{y}} \mathbf{x}^T
$$

So a forward + backward pass is roughly 3x the FLOPs of a forward pass alone. This is the origin of the common rule of thumb that training takes ~3x the compute of inference per token (ignoring optimizer state). See [[Backpropagation]] and [[Matrix Implementation of Backpropagation]].

### Quantization and sparsity are about matrix multiplication

Almost all "make the model faster" techniques (quantization, pruning, sparsity, low-rank decomposition) work by reducing the cost of matrix multiplications. See [[Quantization]] and [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]].

## FLOP counting for LLMs

Concrete FLOP counts for common LLM operations:

### Linear layer: $\mathbf{Y} = \mathbf{X}\mathbf{W}^T$

- $\mathbf{X} \in \mathbb{R}^{B \times d_{\text{in}}}$, $\mathbf{W} \in \mathbb{R}^{d_{\text{out}} \times d_{\text{in}}}$, $\mathbf{Y} \in \mathbb{R}^{B \times d_{\text{out}}}$.
- FLOPs = $2 \cdot B \cdot d_{\text{in}} \cdot d_{\text{out}}$.

### Attention: $\text{softmax}(QK^T / \sqrt{d_k}) V$

- $Q, K, V \in \mathbb{R}^{B \times n \times d_k}$.
- $QK^T$: $2 \cdot B \cdot n^2 \cdot d_k$ FLOPs.
- $\text{attn} \cdot V$: $2 \cdot B \cdot n^2 \cdot d_k$ FLOPs.
- Total attention: $4 \cdot B \cdot n^2 \cdot d_k$.

### Full Transformer layer

- Self-attention: $4 B n^2 d_k$ (the $n^2$ term).
- QKV projections: $3 \cdot 2 B n d \cdot d_k \cdot n_{\text{heads}} = 6 B n d^2$ (if $d = n_{\text{heads}} \cdot d_k$).
- Output projection: $2 B n d^2$.
- FFN (with expansion $4d$): $2 \cdot 2 B n \cdot d \cdot 4d = 16 B n d^2$.
- Total per layer: $\approx 24 B n d^2 + 4 B n^2 d$.

### Rule of thumb: 6N FLOPs per token

For a dense model with $N$ parameters, training (forward + backward) costs ~$6N$ FLOPs per token. This is the origin of the Chinchilla scaling law's compute estimates:
- Forward: $2N$ (matmuls in forward pass).
- Backward: $4N$ (gradients w.r.t. weights + inputs).
- Total: $6N$.

For Llama 3 8B training on 15T tokens: $6 \times 8 \times 10^9 \times 15 \times 10^{12} = 7.2 \times 10^{23}$ FLOPs. At 500 TFLOP/s on an H100, that's ~45,000 GPU-hours = ~1900 GPU-days = ~6 GPU-years. Reality (with MFU ~50%): ~12 GPU-years on H100s.

## Worked example: FLOP counting for a Transformer forward pass

```python
def count_transformer_flops(d_model, n_heads, d_ff, n_layers, seq_len, batch_size):
    """Count FLOPs for a Transformer decoder forward pass."""
    d_k = d_model // n_heads
    B, n, d = batch_size, seq_len, d_model

    # Per-layer FLOPs
    # QKV projections: 3 * (B*n*d) * d = 6 B n d^2
    qkv = 6 * B * n * d * d
    # QK^T: 2 * B * n_heads * n * n * d_k = 2 B n^2 d
    qk = 2 * B * n * n * d
    # attn @ V: 2 B n^2 d
    av = 2 * B * n * n * d
    # Output projection: 2 B n d^2
    o_proj = 2 * B * n * d * d
    # FFN: 2 * (2 * B * n * d * d_ff) = 4 B n d * d_ff
    ffn = 4 * B * n * d * d_ff

    per_layer = qkv + qk + av + o_proj + ffn
    total = per_layer * n_layers

    # Add embedding + output projection (small)
    total += 2 * B * n * d * 50257  # vocab=50257

    return total

# Llama 3 8B: d=4096, n_heads=32, d_ff=14336, n_layers=32
flops = count_transformer_flops(4096, 32, 14336, 32, seq_len=4096, batch_size=1)
print(f"Forward FLOPs: {flops:.2e}")
# Should be ~1.7e12 (1.7 TFLOP) per forward pass
# Training (6N rule): ~6 * 8e9 = 4.8e10 FLOPs per token
```

## Hardware-aware matmul

### Tensor Cores

NVIDIA Tensor Cores (V100+) perform matrix multiplication in blocks of $16 \times 16$ (FP16) or $8 \times 8$ (INT8). They compute $\mathbf{D} = \mathbf{A}\mathbf{B} + \mathbf{C}$ in a single cycle for these block sizes. This is why:
- Dimensions should be multiples of 16 (pad if not).
- FP16/BF16 is 2-8× faster than FP32.
- FP8 (H100+) is another 2× faster.
- INT8 is another 2-4× faster (with quantization).

### Memory hierarchy

GPUs have: HBM (40-80GB, ~3TB/s) → L2 cache (~50MB, ~12TB/s) → SRAM (~256KB/SM, ~200TB/s). Matmul performance depends on keeping data in the fastest tier:
- **Weights**: streamed from HBM (large, can't fit in cache).
- **Activations**: can fit in SRAM for small batches.
- **Tiling**: load a block of A and B into SRAM, compute partial result, accumulate. This is the foundation of all high-performance matmul kernels (cuBLAS, FlashAttention).

### Arithmetic intensity

Arithmetic intensity = FLOPs / bytes moved. For matmul $\mathbf{A}\mathbf{B}$ with $\mathbf{A}, \mathbf{B} \in \mathbb{R}^{n \times n}$:
- FLOPs = $2n^3$.
- Bytes moved = $3n^2$ (read A, B; write C).
- Arithmetic intensity = $2n/3$.

For $n = 4096$: intensity ~2700 FLOPs/byte. H100's peak FP16 is ~1000 TFLOP/s with bandwidth ~3 TB/s, so the roofline cutoff is ~333 FLOPs/byte. At intensity 2700, matmul is **compute-bound** — good!

For batch-size-1 inference, $n$ is small (e.g., $n = d_{\text{model}} = 4096$ but only one token). The matmul becomes $\mathbf{W}\mathbf{x}$ where $\mathbf{x} \in \mathbb{R}^d$ — intensity drops to ~1 FLOP/byte. Now it's **memory-bound** — you spend all time streaming weights, not computing. This is why batching is critical for inference throughput.

## Numerical considerations

- **Mixed precision** (fp16, bf16): modern GPUs are 2–8x faster on fp16/bf16 matmul than fp32. Almost all LLM training and inference uses mixed precision. See [[Mixed Precision Training]].
- **fp8** (Hopper, Blackwell): another 2x speedup over fp16/bf16, with care for numerical stability.
- **Tensor Cores** require matrices to have dimensions that are multiples of 16 (or 8 for fp16). Padding to these multiples is standard practice.

## Common pitfalls

- **Dimension mismatch** — the most common bug. Always check shapes: `(m, k) @ (k, n) = (m, n)`.
- **Broadcasting surprises** — `@` broadcasts like other PyTorch ops. A `(4, 3, 2) @ (2, 5)` produces `(4, 3, 5)`, which is sometimes what you want and sometimes not (see [[Tensors and Broadcasting]]).
- **Confusing `*` (element-wise) with `@` (matmul)** — the most common typo. `A * B` is element-wise; `A @ B` is matrix product.

## Common failure modes

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| CUDA error: shape mismatch | Wrong dimension ordering | Check shapes: `(m,k) @ (k,n) = (m,n)` |
| Slow training, GPU util < 50% | Batch too small (memory-bound) | Increase batch size; use gradient accumulation |
| NaN after matmul | Overflow in FP16 | Use BF16; add gradient scaling |
| OOM on large batch | Activation memory too high | Gradient checkpointing; smaller micro-batch |
| Matmul 2× slower than expected | Dimensions not multiple of 16 | Pad to multiples of 16 |
| Different results across runs | Non-deterministic algorithms | Use `torch.use_deterministic_algorithms(True)` |

## Production implications

- **Matmul dominates compute.** In LLM inference, matmuls account for >95% of FLOPs. Optimizing them (FlashAttention, Tensor Cores, quantization) is the single highest-leverage optimization you can make.
- **Matmul is memory-bound for small batch sizes.** At batch size 1, you spend most of your time moving weights from HBM to SRAM, not computing. This is why batching is critical and why speculative decoding helps. See [[Continuous Batching]], [[Speculative Decoding]] and [[14 - Inference and Production/Inference/vLLM|vLLM]].
- **Kernel fusion** (combining matmul with adjacent operations like bias-add or activation into a single GPU kernel) avoids memory round-trips.

## Interview questions

1. **Q: What are the four views of matrix multiplication?**
   A: (1) Dot products: each entry $C_{ij}$ is a dot product of row $i$ of A and column $j$ of B. (2) Linear transformation: $\mathbf{A}\mathbf{B}$ is the composition of linear maps (apply B first, then A). (3) Sum of outer products: $\mathbf{A}\mathbf{B} = \sum_l \mathbf{a}_{:,l} \mathbf{b}_{l,:}$ — foundation of low-rank approximation. (4) Block multiplication: partition into blocks, multiply block-by-block — foundation of tiling and FlashAttention.

2. **Q: How many FLOPs in a Transformer forward pass?**
   A: Per layer: $\approx 24 B n d^2 + 4 B n^2 d$ where $B$ = batch, $n$ = seq_len, $d$ = d_model. The $d^2$ term (linear projections + FFN) dominates for short sequences; the $n^2 d$ term (attention) dominates for long sequences. Rule of thumb for training: $6N$ FLOPs per token where $N$ is parameter count (2N forward + 4N backward).

3. **Q: Why is batch-size-1 inference memory-bound?**
   A: At batch 1, matmul becomes $\mathbf{W}\mathbf{x}$ where $\mathbf{x} \in \mathbb{R}^d$. Arithmetic intensity = 1 FLOP/byte (compute 1 FLOP per weight byte read). GPUs need ~333 FLOP/byte (H100) to be compute-bound. At intensity 1, you spend all time streaming weights from HBM, not computing. Batching amortizes weight reads across multiple requests — intensity grows with batch size.

4. **Q: Why are dimensions padded to multiples of 16?**
   A: NVIDIA Tensor Cores compute matmul in 16×16 blocks (FP16) or 8×8 (INT8). If dimensions aren't multiples of 16, the kernel either pads (wasting compute) or falls back to a slower path. Padding to multiples of 16 (or 8 for FP8/INT8) ensures full Tensor Core utilization. Most frameworks (PyTorch, vLLM) handle this automatically, but custom kernels may not.

5. **Q: How does LoRA use the "sum of outer products" view of matmul?**
   A: LoRA approximates a weight update $\Delta \mathbf{W}$ as $\mathbf{B}\mathbf{A}$ where $\mathbf{A} \in \mathbb{R}^{r \times d}$, $\mathbf{B} \in \mathbb{R}^{d \times r}$, $r \ll d$. This is a rank-$r$ matrix = sum of $r$ outer products: $\Delta \mathbf{W} = \sum_{i=1}^r \mathbf{b}_{:,i} \mathbf{a}_{i,:}$. The "sum of outer products" view makes low-rank structure obvious — you're keeping only the top-$r$ terms in the decomposition.

6. **Q: How does FlashAttention exploit block multiplication?**
   A: FlashAttention tiles the attention computation: load blocks of Q, K, V into SRAM, compute partial attention scores, accumulate. This avoids materializing the full $n \times n$ attention matrix in HBM. The block view of matmul ($\mathbf{A}\mathbf{B}$ = block-by-block) is the mathematical foundation; FlashAttention adds softmax-aware tiling to keep the math exact. Result: 2-4× faster, 10× less memory, no quality loss.

## Further reading

- Strang, *Introduction to Linear Algebra* — Chapter 2.
- Goodfellow et al., *Deep Learning* — Chapter 2.
- For GPU matmul performance, see the FlashAttention paper (Dao et al., 2022).

## See also

- [[Mathematics MOC]]
- [[Vectors]] — the underlying objects.
- [[Dot Product]] — element-level view of matmul.
- [[Cosine Similarity]] — batched similarity via matmul.
- [[Matrix Decomposition]] — SVD, eigendecomposition.
- [[Tensors and Broadcasting]] — higher-rank generalization.
- [[Perceptrons and Multi-Layer Perceptrons]] — linear layers are matmuls.
- [[Backpropagation]] and [[Matrix Implementation of Backpropagation]] — the backward pass is matmuls too.
- [[Scaled Dot-Product Attention]] and [[Self-Attention]] — matmul-driven computation.
- [[08 - Attention and Transformers/Efficient Attention/FlashAttention|FlashAttention]] — hardware-aware matmul.
- [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]] — low-rank matmul approximation.
- [[Quantization]] — INT8/FP8 matmul.
- [[Mixed Precision Training]] — FP16/BF16 matmul.
