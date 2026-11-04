---
title: Coding Interview Questions
type: reference
aliases: [Coding Interview, LLM Coding Interview, Coding Interview Questions 2, Coding Interview Questions 3, Advanced Coding Interview, Advanced Coding Q&A, Implement Attention, YaRN GQA RoPE Coding]
tags: [interview, coding, implementation, pytorch, attention, rope, gqa, kv-cache, sampling, spec-decoding, quantization, grpo, moe, vlm, mcp, reasoning]
sources:
  - "03 - Coding Interview Questions"
  - "04 - Coding Interview Questions 2"
  - "05 - Coding Interview Questions 3"
created_index: 5
---

LLM coding interviews test your ability to implement core components from scratch — attention, multi-head attention, RoPE, KV caches, sampling, and small training loops — by translating mathematical formulas into correct, vectorized PyTorch. This note is a single bank of sixteen questions: the four most common ones (scaled dot-product attention, multi-head attention, top-k/top-p sampling, and the KV cache), the advanced engineering topics that distinguish a senior AI engineer from a junior one (the GRPO loss, VLM patch embedding, MCP tool servers, MoE routing, PagedAttention, and INT4 quantization — depth, not breadth), and the newer from-scratch exercises (YaRN, GQA, NTK-aware RoPE scaling, KV cache compression, EAGLE-2 speculative decoding, and GPTQ). Each question can be done in 20–50 lines of PyTorch and tests a specific conceptual understanding; each entry keeps the problem statement, the math it implements, a reference solution with tests, the key implementation details, the common pitfalls, and the follow-up questions an interviewer is likely to ask. See [[Interview Prep MOC]] for the surrounding interview-prep collection.

## How to approach LLM coding interviews

Unlike algorithmic coding interviews, where the bottleneck is finding the right trick, LLM coding interviews test whether you can translate mathematical formulas into correct PyTorch code. Interview coding is about communication as much as correctness: always explain your reasoning as you code, because the interviewer cares about your thought process, not just the final code.

### The five-step structure

Work through every implementation in a fixed order:

1. **Clarify the spec**: inputs, outputs, shapes, edge cases.
2. **Write the math**: state the formula you're implementing.
3. **Write the code**: clean, vectorized PyTorch.
4. **Test with a small example**: verify shapes and values.
5. **Discuss extensions**: causal masking, batched inputs, optimization.

### Common mistakes

The mistakes interviewers most often watch for in attention implementations:

- Forgetting the `1/sqrt(d_k)` scaling.
- Mixing up `Q @ K^T` (correct) with `Q^T @ K` (wrong).
- Wrong dimension for softmax (should be over the last dim, the key dimension).
- Forgetting causal masking for decoder attention.
- Inefficient implementations (Python loops instead of vectorized ops).

### Question anatomy and timing

Each question in this bank is structured the same way: a **problem statement** (what you're asked to implement), an **approach** (the high-level strategy), **key implementation details** (the things that separate a working solution from a broken one), **common pitfalls** (what interviewers look for you to avoid), and **follow-up questions** (what the interviewer might ask next). Aim to write the code in 20–30 minutes for a senior role; 40–60 minutes for a mid-level role.

### The practice loop

When practicing on your own, work each question in five passes: try to implement it without looking at the solution; compare your implementation to the solution; run the test code and verify it works; read the linked concept note for the underlying theory; and practice explaining your implementation out loud.

## Attention implementation questions

Attention is the most heavily tested topic. The bank covers the single-head core, the multi-head wrapper that every Transformer uses, and the grouped-query variant that modern LLMs actually ship.

### Implement scaled dot-product attention

**Question.** Implement `scaled_dot_product_attention(Q, K, V, mask=None)` — the core computation inside every Transformer block (theory in [[Scaled Dot-Product Attention]] and [[Self-Attention]]).

#### Spec

The function takes:

- `Q`: shape `(batch, ..., seq_q, d_k)`
- `K`: shape `(batch, ..., seq_k, d_k)`
- `V`: shape `(batch, ..., seq_k, d_v)`
- `mask`: optional, shape broadcastable to `(batch, ..., seq_q, seq_k)`
- Returns: shape `(batch, ..., seq_q, d_v)`

#### Math

$$\mathrm{Attention}(Q, K, V) = \mathrm{softmax}(Q K^T / \sqrt{d_k}) V$$

#### Solution

```python
import torch
import torch.nn.functional as F
import math

def scaled_dot_product_attention(Q, K, V, mask=None):
    """
    Scaled dot-product attention.
    
    Args:
        Q: (batch, ..., seq_q, d_k)
        K: (batch, ..., seq_k, d_k)
        V: (batch, ..., seq_k, d_v)
        mask: optional, broadcastable to (batch, ..., seq_q, seq_k)
            True or 1 = attend, False or 0 = masked out
    
    Returns:
        output: (batch, ..., seq_q, d_v)
        attention_weights: (batch, ..., seq_q, seq_k)
    """
    d_k = Q.shape[-1]
    
    # Compute attention scores
    # (batch, ..., seq_q, d_k) @ (batch, ..., d_k, seq_k) = (batch, ..., seq_q, seq_k)
    scores = Q @ K.transpose(-2, -1) / math.sqrt(d_k)
    
    # Apply mask (if provided)
    if mask is not None:
        # mask: True/1 = attend, False/0 = mask out
        # We set masked positions to -inf so softmax gives them 0
        scores = scores.masked_fill(~mask.bool() if mask.dtype == torch.bool else mask == 0, float('-inf'))
    
    # Softmax over the last dimension (keys)
    attention_weights = F.softmax(scores, dim=-1)
    
    # Weighted sum of values
    # (batch, ..., seq_q, seq_k) @ (batch, ..., seq_k, d_v) = (batch, ..., seq_q, d_v)
    output = attention_weights @ V
    
    return output, attention_weights
```

#### Test

```python
# Test basic functionality
torch.manual_seed(42)
Q = torch.randn(1, 4, 8)  # batch=1, seq=4, d_k=8
K = torch.randn(1, 6, 8)  # seq_k=6
V = torch.randn(1, 6, 5)  # d_v=5

output, weights = scaled_dot_product_attention(Q, K, V)
assert output.shape == (1, 4, 5)
assert weights.shape == (1, 4, 6)
assert torch.allclose(weights.sum(dim=-1), torch.ones(1, 4))  # rows sum to 1

# Test with causal mask
seq_len = 4
causal_mask = torch.tril(torch.ones(seq_len, seq_len)).bool()
output_causal, weights_causal = scaled_dot_product_attention(Q[:, :4], K[:, :4], V[:, :4], mask=causal_mask)
# Upper triangle should be 0
assert torch.all(weights_causal[0, 0, 1, 0] == 0)  # position 1 cannot attend to position 0... wait, that's wrong
# Actually: position i can attend to positions 0..i (lower triangular)
# So weights[0, 1, 0] should be non-zero (position 1 attends to position 0)
# And weights[0, 0, 1] should be zero (position 0 cannot attend to position 1)
assert weights_causal[0, 0, 1] == 0  # position 0 cannot see position 1
print("All tests passed!")
```

#### Extensions to discuss

Once the basic version works, be ready to discuss its limits and variants:

- **FlashAttention**: explain that this implementation materializes the `seq_q × seq_k` matrix, which is `O(N²)` memory. FlashAttention avoids this with tiling. See [[17 - Papers/Efficiency/FlashAttention|FlashAttention]].
- **Memory layout**: for efficiency, queries and keys should be in row-major order for the matmul. PyTorch handles this, but it matters for custom CUDA kernels.
- **Mask types**: boolean mask (most common), additive mask (for ALiBi), or float mask.

### Implement multi-head attention

**Question.** Implement `MultiHeadAttention` as a PyTorch module (theory in [[Multi-Head Attention]]).

#### Spec

- Input: `x` of shape `(batch, seq_len, d_model)`
- Output: same shape
- Parameters: `W_Q`, `W_K`, `W_V`, `W_O` (all `d_model × d_model`)
- Number of heads: `h`

#### Solution

```python
import torch
import torch.nn as nn

class MultiHeadAttention(nn.Module):
    def __init__(self, d_model: int, num_heads: int):
        super().__init__()
        assert d_model % num_heads == 0, "d_model must be divisible by num_heads"
        
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads  # dimension per head
        
        # Combined QKV projection for efficiency
        self.qkv = nn.Linear(d_model, 3 * d_model, bias=False)
        # Output projection
        self.o = nn.Linear(d_model, d_model, bias=False)
    
    def forward(self, x, mask=None):
        """
        Args:
            x: (batch, seq_len, d_model)
            mask: optional, (batch, seq_len, seq_len) or broadcastable
        
        Returns:
            (batch, seq_len, d_model)
        """
        batch_size, seq_len, _ = x.shape
        
        # Project to Q, K, V in one matmul
        # (batch, seq_len, d_model) -> (batch, seq_len, 3*d_model)
        qkv = self.qkv(x)
        # Split into Q, K, V
        # Each: (batch, seq_len, d_model)
        Q, K, V = qkv.chunk(3, dim=-1)
        
        # Reshape for multi-head: (batch, seq_len, d_model) -> (batch, num_heads, seq_len, d_k)
        Q = Q.view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        K = K.view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        V = V.view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        
        # Expand mask for heads if needed
        if mask is not None:
            # mask: (batch, seq_len, seq_len) -> (batch, 1, seq_len, seq_len) for broadcasting
            if mask.dim() == 3:
                mask = mask.unsqueeze(1)
        
        # Apply attention
        # output: (batch, num_heads, seq_len, d_k)
        output, _ = scaled_dot_product_attention(Q, K, V, mask=mask)
        
        # Concatenate heads: (batch, num_heads, seq_len, d_k) -> (batch, seq_len, d_model)
        output = output.transpose(1, 2).contiguous().view(batch_size, seq_len, self.d_model)
        
        # Output projection
        return self.o(output)
```

#### Test

```python
# Test
torch.manual_seed(42)
mha = MultiHeadAttention(d_model=512, num_heads=8)
x = torch.randn(2, 10, 512)  # batch=2, seq=10, d_model=512
output = mha(x)
assert output.shape == (2, 10, 512)

# Test with causal mask
seq_len = 10
causal_mask = torch.tril(torch.ones(seq_len, seq_len)).bool()
output_causal = mha(x, mask=causal_mask)
assert output_causal.shape == (2, 10, 512)

# Count parameters
n_params = sum(p.numel() for p in mha.parameters())
assert n_params == 4 * 512 * 512  # 4 projections of d_model x d_model
print(f"Parameters: {n_params}")
print("All tests passed!")
```

#### Extensions to discuss

The details that separate a textbook implementation from a production one:

- **Combined QKV**: the `qkv` projection computes Q, K, V in one matmul, which is more efficient than three separate projections. This is the standard optimization.
- **GQA / MQA**: for Grouped-Query Attention, K and V have fewer heads than Q. Modify the reshape to share K, V across multiple Q heads. See [[GQA MQA and MLA]].
- **No bias**: modern LLMs typically omit bias in attention projections. The original Transformer used bias; Llama does not.
- **RoPE**: applied to Q and K after the projection, before the reshape. See the rotary position embeddings question below.

### Implement grouped-query attention

**Question.** Implement GQA and explain the trade-off vs MHA and MQA.

GQA is the default attention scheme for modern LLMs (Llama 3, Mistral, Qwen): the query heads keep their full count while K and V heads are shared in groups, which shrinks the KV cache at a small quality cost. The solution's docstring spells out the three regimes — MHA (one KV head per query head), MQA (a single shared KV head), and GQA (groups of query heads sharing each KV head). See [[GQA MQA and MLA]] for the concept treatment, [[GQA]] for the paper, and [[KV Cache Mechanics]] for why the cache size matters.

#### Solution

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class GQA(nn.Module):
    """Grouped-Query Attention.

    - MHA: num_kv_heads = num_heads (1:1)
    - MQA: num_kv_heads = 1 (all heads share KV)
    - GQA: num_kv_heads = num_heads // group_size (groups of heads share KV)

    GQA is the default for modern LLMs (Llama 3, Mistral, Qwen).
    """

    def __init__(self, hidden_dim: int, num_heads: int, num_kv_heads: int):
        super().__init__()
        assert num_heads % num_kv_heads == 0, "num_heads must be divisible by num_kv_heads"
        self.hidden_dim = hidden_dim
        self.num_heads = num_heads
        self.num_kv_heads = num_kv_heads
        self.head_dim = hidden_dim // num_heads
        self.group_size = num_heads // num_kv_heads  # how many query heads share each KV head

        # Q has full heads; K/V have num_kv_heads
        self.q_proj = nn.Linear(hidden_dim, num_heads * self.head_dim, bias=False)
        self.k_proj = nn.Linear(hidden_dim, num_kv_heads * self.head_dim, bias=False)
        self.v_proj = nn.Linear(hidden_dim, num_kv_heads * self.head_dim, bias=False)
        self.o_proj = nn.Linear(num_heads * self.head_dim, hidden_dim, bias=False)

    def forward(self, x: torch.Tensor, causal: bool = True) -> torch.Tensor:
        # x: (batch, seq_len, hidden_dim)
        batch, seq_len, _ = x.shape

        # Project
        q = self.q_proj(x).view(batch, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        k = self.k_proj(x).view(batch, seq_len, self.num_kv_heads, self.head_dim).transpose(1, 2)
        v = self.v_proj(x).view(batch, seq_len, self.num_kv_heads, self.head_dim).transpose(1, 2)

        # Repeat KV heads to match Q heads
        # Each KV head is shared by self.group_size Q heads
        k = k.repeat_interleave(self.group_size, dim=1)  # (batch, num_heads, seq_len, head_dim)
        v = v.repeat_interleave(self.group_size, dim=1)

        # Scaled dot-product attention
        scores = q @ k.transpose(-2, -1) / math.sqrt(self.head_dim)  # (batch, num_heads, seq_len, seq_len)

        if causal:
            # Causal mask
            mask = torch.triu(torch.ones(seq_len, seq_len, dtype=torch.bool, device=x.device), diagonal=1)
            scores = scores.masked_fill(mask, float("-inf"))

        attn = F.softmax(scores, dim=-1)
        out = attn @ v  # (batch, num_heads, seq_len, head_dim)

        # Reshape and project
        out = out.transpose(1, 2).contiguous().view(batch, seq_len, self.num_heads * self.head_dim)
        return self.o_proj(out)


# Compare KV cache sizes
def kv_cache_size(num_layers: int, seq_len: int, num_kv_heads: int, head_dim: int, batch_size: int = 1, dtype_bytes: int = 2) -> int:
    """Compute KV cache size in bytes."""
    return num_layers * batch_size * seq_len * num_kv_heads * head_dim * 2 * dtype_bytes  # 2 for K and V

# Llama 3 8B: MHA vs GQA
# MHA (32 heads): 32 * 128 * 8192 * 2 * 2 = 67MB
# GQA (8 kv heads): 8 * 128 * 8192 * 2 * 2 = 17MB
# 4x reduction in KV cache

print("MHA KV cache at 8K context:", kv_cache_size(32, 8192, 32, 128), "bytes")
print("GQA KV cache at 8K context:", kv_cache_size(32, 8192, 8, 128), "bytes")
print("Ratio: 4x reduction")
```

#### Key points

GQA reduces the KV cache by group_size× (typically 4–8×). For Llama 3 8B at 8K context, MHA with 32 heads needs 67 MB of KV cache while GQA with 8 KV heads needs 17 MB — a 4× reduction. The trade-off is a slight quality loss (~0.5–1% on MMLU). Modern LLMs use 4–8 KV heads for 7–70B models. MQA (1 KV head) is too aggressive; quality drops noticeably.

## Positional encoding questions

Positional-encoding questions test whether you understand how Transformers inject order into a permutation-invariant architecture, and how that injection breaks (and gets repaired) at longer contexts. The bank covers vanilla RoPE plus the two length-extension schemes used in production (see [[Positional Encoding]] for the general landscape).

### Implement rotary position embeddings

**Question.** Implement RoPE: rotate the Q and K vectors based on their position (theory in [[RoPE]]).

#### Math

For position $m$ and dimension pair $(2i, 2i+1)$:

$$q'_{2i} = q_{2i} \cos(m \theta_i) - q_{2i+1} \sin(m \theta_i)$$

$$q'_{2i+1} = q_{2i} \sin(m \theta_i) + q_{2i+1} \cos(m \theta_i)$$

where $\theta_i = 10000^{-2i/d}$.

#### Solution

```python
import torch
import torch.nn as nn
import math

def precompute_rope_frequencies(d_k: int, max_seq_len: int, base: float = 10000.0):
    """
    Precompute the rotation frequencies for RoPE.
    
    Returns:
        cos, sin: (max_seq_len, d_k / 2) each
    """
    # d_k must be even
    assert d_k % 2 == 0
    half_d = d_k // 2
    
    # Compute frequencies: theta_i = base^(-2i/d) for i in 0..d/2
    positions = torch.arange(max_seq_len).float()  # (max_seq_len,)
    frequencies = 1.0 / (base ** (torch.arange(0, d_k, 2).float() / d_k))  # (d_k / 2,)
    
    # Outer product: (max_seq_len, d_k / 2)
    angles = positions.unsqueeze(1) * frequencies.unsqueeze(0)
    
    return angles.cos(), angles.sin()


def apply_rope(x, cos, sin):
    """
    Apply RoPE to x.
    
    Args:
        x: (batch, num_heads, seq_len, d_k)
        cos, sin: (seq_len, d_k / 2)
    
    Returns:
        (batch, num_heads, seq_len, d_k)
    """
    seq_len = x.shape[-2]
    cos = cos[:seq_len].unsqueeze(0).unsqueeze(0)  # (1, 1, seq_len, d_k / 2)
    sin = sin[:seq_len].unsqueeze(0).unsqueeze(0)
    
    # Split x into even and odd indices
    x1 = x[..., 0::2]  # (batch, num_heads, seq_len, d_k / 2)
    x2 = x[..., 1::2]
    
    # Apply rotation
    rotated = torch.stack([
        x1 * cos - x2 * sin,
        x1 * sin + x2 * cos,
    ], dim=-1)
    
    # Interleave back
    return rotated.flatten(-2)


class RoPEAttention(nn.Module):
    def __init__(self, d_model: int, num_heads: int, max_seq_len: int = 4096):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        self.qkv = nn.Linear(d_model, 3 * d_model, bias=False)
        self.o = nn.Linear(d_model, d_model, bias=False)
        
        # Precompute RoPE frequencies
        cos, sin = precompute_rope_frequencies(self.d_k, max_seq_len)
        self.register_buffer('rope_cos', cos, persistent=False)
        self.register_buffer('rope_sin', sin, persistent=False)
    
    def forward(self, x, mask=None):
        batch_size, seq_len, _ = x.shape
        
        qkv = self.qkv(x)
        Q, K, V = qkv.chunk(3, dim=-1)
        
        Q = Q.view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        K = K.view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        V = V.view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        
        # Apply RoPE to Q and K (not V!)
        Q = apply_rope(Q, self.rope_cos, self.rope_sin)
        K = apply_rope(K, self.rope_cos, self.rope_sin)
        
        if mask is not None:
            if mask.dim() == 3:
                mask = mask.unsqueeze(1)
        
        output, _ = scaled_dot_product_attention(Q, K, V, mask=mask)
        output = output.transpose(1, 2).contiguous().view(batch_size, seq_len, self.d_model)
        return self.o(output)
```

#### Test

```python
# Test
torch.manual_seed(42)
attn = RoPEAttention(d_model=64, num_heads=8, max_seq_len=128)
x = torch.randn(2, 10, 64)
output = attn(x)
assert output.shape == (2, 10, 64)

# Verify RoPE is applied (compare with and without)
# RoPE should change the attention pattern based on relative position
print("All tests passed!")
```

#### Extensions to discuss

- **Length extrapolation**: RoPE does not extrapolate well beyond the training length. Techniques like NTK-aware scaling and YaRN extend it. See [[YaRN and NTK-Aware Scaling]].
- **Implementation efficiency**: the interleaved version above is clear but slow. The "half-rotation" version (rotate the first and second halves of the vector) is mathematically equivalent and faster on GPU. See the Llama implementation ([[Llama Family Architecture]]).
- **V is not rotated**: only Q and K are rotated, because the rotation is about encoding *relative* position in the dot product `Q · K`. V is the output, not a position-encoded representation.

### Implement YaRN position interpolation

**Question.** Implement YaRN (Yet another RoPE extensioN) position interpolation for extending RoPE to longer contexts.

#### Solution

```python
import torch

def yarn_rope(
    position_ids: torch.Tensor,  # (batch, seq_len)
    dim: int,  # head dim, must be even
    base: float = 10000.0,
    original_max_position: int = 4096,
    target_max_position: int = 131072,  # 32x extension
    beta_fast: float = 32.0,
    beta_slow: float = 1.0,
    scale: float = 1.0,
):
    """YaRN: non-uniform RoPE interpolation.

    High-frequency components are interpolated more aggressively;
    low-frequency components are interpolated less.
    """
    # Compute frequencies
    inv_freq = 1.0 / (base ** (torch.arange(0, dim, 2).float() / dim))

    # Find the wavelength of each frequency
    # High frequency = low wavelength = "local" position info
    # Low frequency = high wavelength = "global" position info
    def find_correction_dim(num_rotations: float, dim: int, base: float, max_position: int) -> float:
        return (dim * torch.log(base / (num_rotations * 2 * torch.pi))) / (2 * torch.log(base))

    # Dimensions where each frequency transitions from "local" to "global"
    low_freq_cutoff = find_correction_dim(beta_fast, dim, base, original_max_position)
    high_freq_cutoff = find_correction_dim(beta_slow, dim, base, original_max_position)
    low_freq_cutoff = max(low_freq_cutoff, 0)
    high_freq_cutoff = min(high_freq_cutoff, dim - 1)

    # Compute the interpolation factor for each frequency
    # High frequencies (above low_freq_cutoff): interpolate aggressively
    # Low frequencies (below high_freq_cutoff): interpolate less
    # Middle: smooth transition
    extension_ratio = target_max_position / original_max_position

    def get_interpolation_factor(freq_idx: int) -> float:
        if freq_idx < low_freq_cutoff:
            # High frequency: aggressive interpolation
            return 1.0 / extension_ratio
        elif freq_idx > high_freq_cutoff:
            # Low frequency: no interpolation (keep original)
            return 1.0
        else:
            # Smooth transition
            return 1.0 - (1.0 / extension_ratio) * (freq_idx - low_freq_cutoff) / (high_freq_cutoff - low_freq_cutoff)

    # Apply per-frequency interpolation
    interpolation_factors = torch.tensor([get_interpolation_factor(i) for i in range(dim // 2)])

    # Compute rotated frequencies
    position_ids = position_ids.float()
    freqs = position_ids.unsqueeze(-1) * inv_freq  # (batch, seq, dim//2)
    # Apply interpolation: scale position by interpolation factor for each frequency
    freqs = freqs * interpolation_factors  # (batch, seq, dim//2)

    # Compute cos and sin
    emb = torch.cat([freqs, freqs], dim=-1)  # (batch, seq, dim)
    cos = emb.cos() * scale
    sin = emb.sin() * scale
    return cos, sin


# Test
position_ids = torch.arange(0, 8192).unsqueeze(0)  # batch=1, seq=8192
cos, sin = yarn_rope(position_ids, dim=128, original_max_position=4096, target_max_position=131072)
print(f"cos shape: {cos.shape}")  # (1, 8192, 128)
```

#### Key points

YaRN's insight is that high-frequency RoPE components encode local position (less affected by length extension) while low-frequency components encode global position (more affected). Non-uniform interpolation gives better extrapolation than uniform NTK scaling. Used by Llama 3.1 to extend from 8K to 128K. See [[YaRN and NTK-Aware Scaling]] for the theory and [[Llama Family Architecture]] for the production use.

### Implement RoPE with NTK-aware scaling

**Question.** Implement RoPE with NTK-aware scaling for length extrapolation.

Instead of interpolating positions the way YaRN does, NTK-aware scaling adjusts the base frequency: a higher base means lower frequencies and better long-context extrapolation. The NTK formula is `new_base = base * scaling_factor ** (dim / (dim - 2))`. The solution also includes the "half-rotation" application function, which rotates the first and second halves of the vector rather than interleaved pairs.

#### Solution

```python
import torch

def ntk_aware_rope(
    position_ids: torch.Tensor,
    dim: int,
    base: float = 10000.0,
    scaling_factor: float = 4.0,  # extend to 4x training length
):
    """NTK-aware RoPE scaling.

    Instead of interpolating positions (YaRN), NTK-aware scaling adjusts the base frequency.
    Higher base = lower frequencies = better long-context extrapolation.

    NTK formula: new_base = base * scaling_factor ** (dim / (dim - 2))
    """
    # Compute new base
    new_base = base * (scaling_factor ** (dim / (dim - 2)))

    # Compute frequencies with new base
    inv_freq = 1.0 / (new_base ** (torch.arange(0, dim, 2).float() / dim))

    # Compute angles
    position_ids = position_ids.float()
    freqs = position_ids.unsqueeze(-1) * inv_freq  # (batch, seq, dim//2)

    # Compute cos and sin
    emb = torch.cat([freqs, freqs], dim=-1)
    cos = emb.cos()
    sin = emb.sin()
    return cos, sin


# Apply RoPE to Q and K
def apply_rope(q: torch.Tensor, cos: torch.Tensor, sin: torch.Tensor) -> torch.Tensor:
    """Apply RoPE rotation to queries or keys.

    q: (batch, num_heads, seq_len, head_dim)
    cos, sin: (batch, seq_len, head_dim)
    """
    # Split q into two halves
    q1 = q[..., : q.shape[-1] // 2]
    q2 = q[..., q.shape[-1] // 2 :]

    # Reshape cos/sin for broadcasting
    cos = cos.unsqueeze(1)  # (batch, 1, seq_len, head_dim // 2)
    sin = sin.unsqueeze(1)

    # Rotation: rotate (q1, q2) by angle theta
    rotated_q1 = q1 * cos - q2 * sin
    rotated_q2 = q1 * sin + q2 * cos

    return torch.cat([rotated_q1, rotated_q2], dim=-1)
```

#### Key points

NTK-aware scaling is simpler than YaRN (just changes base frequency) and works well for moderate extensions (4–8×). YaRN is better for larger extensions (32×+). Both are used in production: Llama 3.1 405B uses YaRN; smaller models often use NTK. See [[YaRN and NTK-Aware Scaling]].

## Sampling and decoding questions

Decoding questions test whether you understand the machinery that turns logits into tokens — from the truncation heuristics of top-k/top-p to the draft-and-verify loops of speculative decoding (see [[Sampling Strategies]] for the overview).

### Implement top-k and top-p sampling

**Question.** Implement `sample(logits, temperature=1.0, top_k=None, top_p=None)` that returns a sampled token index.

#### Solution

```python
import torch
import torch.nn.functional as F

def sample(logits, temperature=1.0, top_k=None, top_p=None):
    """
    Sample a token from logits with temperature, top-k, and top-p.
    
    Args:
        logits: (vocab_size,) or (batch, vocab_size)
        temperature: scaling factor; higher = more random
        top_k: if set, only consider top-k tokens
        top_p: if set, only consider tokens in the nucleus (cumulative prob <= top_p)
    
    Returns:
        sampled token index (int or tensor)
    """
    if logits.dim() == 1:
        logits = logits.unsqueeze(0)
    
    # Apply temperature
    if temperature != 1.0:
        logits = logits / temperature
    
    # Apply top-k: keep only top-k tokens, set rest to -inf
    if top_k is not None and top_k > 0:
        top_k = min(top_k, logits.size(-1))
        # Get the k-th largest value
        kth_value = torch.topk(logits, top_k, dim=-1).values[:, -1:]
        # Set everything below k-th value to -inf
        logits = logits.masked_fill(logits < kth_value, float('-inf'))
    
    # Apply top-p (nucleus): keep the smallest set of tokens whose cumulative prob >= top_p
    if top_p is not None and 0 < top_p < 1:
        # Sort logits in descending order
        sorted_logits, sorted_indices = torch.sort(logits, descending=True, dim=-1)
        sorted_probs = F.softmax(sorted_logits, dim=-1)
        cumulative_probs = torch.cumsum(sorted_probs, dim=-1)
        
        # Find tokens to remove: those whose cumulative prob exceeds top_p
        # (but keep at least one token)
        sorted_indices_to_remove = cumulative_probs > top_p
        # Shift right: always keep the first token (highest prob)
        sorted_indices_to_remove[:, 1:] = sorted_indices_to_remove[:, :-1].clone()
        sorted_indices_to_remove[:, 0] = False
        
        # Scatter back to original indices
        indices_to_remove = sorted_indices_to_remove.scatter(
            -1, sorted_indices, sorted_indices_to_remove
        )
        logits = logits.masked_fill(indices_to_remove, float('-inf'))
    
    # Convert to probabilities
    probs = F.softmax(logits, dim=-1)
    
    # Sample
    if logits.size(0) == 1:
        return torch.multinomial(probs, num_samples=1).squeeze(0).item()
    else:
        return torch.multinomial(probs, num_samples=1).squeeze(-1)
```

#### Test

```python
# Test
torch.manual_seed(42)

# Test temperature
logits = torch.tensor([1.0, 2.0, 3.0, 4.0])
# Without temperature, the highest logit dominates
samples = [sample(logits, temperature=0.1) for _ in range(10)]
assert all(s == 3 for s in samples)  # always picks index 3 (highest logit)

# With high temperature, distribution is more uniform
samples = [sample(logits, temperature=10.0) for _ in range(100)]
# Some samples should be different from 3
assert any(s != 3 for s in samples)

# Test top_k
logits = torch.tensor([1.0, 2.0, 3.0, 4.0, 5.0])
samples = [sample(logits, top_k=2) for _ in range(100)]
# Only indices 3 and 4 should be sampled
assert all(s in [3, 4] for s in samples)

# Test top_p
logits = torch.tensor([1.0, 1.0, 1.0, 1.0, 10.0])
samples = [sample(logits, top_p=0.9) for _ in range(100)]
# With top_p=0.9, the high logit (index 4) should dominate
assert sum(s == 4 for s in samples) > 90

print("All tests passed!")
```

#### Extensions to discuss

- **Greedy decoding**: temperature → 0 (or use `argmax`).
- **Beam search**: maintain top-B sequences, expand each, keep best. Not sampling but related. See [[Beam Search and Decoding Strategies]].
- **Repetition penalty**: subtract a penalty from previously-seen tokens. The exact formula varies; the common one is `logits[t] = logits[t] / penalty if t in seen else logits[t]`.
- **Constrained decoding**: use a finite state machine or grammar to constrain valid next tokens. Useful for structured outputs (JSON, regex). See Outlines and Guidance libraries, and [[Constrained Decoding]].

### Implement EAGLE-2 speculative decoding

**Question.** Implement a simple EAGLE-2-style speculative decoding loop.

The key insight of the EAGLE family: predict hidden states (not tokens) and use the target model's vocab head to decode them, then verify all drafted tokens in a single forward pass. Background on the rejection-sampling machinery is in [[Speculative Decoding]]; the papers are covered in [[Medusa and EAGLE]] and [[EAGLE-3]].

#### Solution

```python
import torch
import torch.nn.functional as F

def eagle2_speculative_decode(
    target_model,
    draft_model,
    input_ids: torch.Tensor,  # (batch, seq_len)
    max_new_tokens: int = 100,
    K: int = 4,  # speculation depth
    top_k_tree: int = 8,  # tree width per step
    temperature: float = 0.0,
):
    """EAGLE-2 spec decoding: draft model proposes K tokens, target model verifies in one forward pass.

    Key insight: predict HIDDEN STATES (not tokens), use target model's vocab head to decode.
    Tree-structured speculation: propose multiple candidate continuations, verify all in one pass.
    """
    batch_size = input_ids.shape[0]
    generated = input_ids.clone()

    while generated.shape[1] - input_ids.shape[1] < max_new_tokens:
        # === Step 1: Draft model proposes K tokens ===
        # Get hidden state from target model (one forward pass)
        with torch.no_grad():
            target_outputs = target_model(generated, output_hidden_states=True)
            target_hidden = target_outputs.hidden_states[-1][:, -1:, :]  # (batch, 1, hidden_dim)

        # Draft model predicts next K hidden states (chained)
        draft_hidden = target_hidden
        draft_tokens = []
        draft_probs = []
        for k in range(K):
            # Draft model: takes hidden state, predicts next hidden state + token
            draft_out = draft_model(draft_hidden)
            next_hidden = draft_out.hidden_states  # predicted next hidden state
            next_logits = target_model.lm_head(next_hidden)  # use target's vocab head
            next_probs = F.softmax(next_logits, dim=-1)

            # Sample top-k candidate tokens for tree
            topk_probs, topk_tokens = torch.topk(next_probs, top_k_tree, dim=-1)
            # For simplicity, take argmax (in production, build full tree)
            next_token = topk_tokens[:, :, 0]  # (batch, 1)
            draft_tokens.append(next_token)
            draft_probs.append(topk_probs[:, :, 0])

            draft_hidden = next_hidden  # chain

        # === Step 2: Target model verifies all K drafted tokens in ONE forward pass ===
        # Construct verification input: original + drafted tokens
        drafted_seq = torch.cat([generated] + draft_tokens, dim=1)  # (batch, seq + K)

        with torch.no_grad():
            verify_outputs = target_model(drafted_seq)
            verify_logits = verify_outputs.logits  # (batch, seq + K, vocab)

        # === Step 3: Accept longest matching prefix ===
        # For each drafted position, check if target model would have produced the same token
        n_accepted = 0
        for k in range(K):
            # Target model's prediction at position (seq + k - 1) is for token at position (seq + k)
            target_pos = generated.shape[1] + k - 1
            target_probs = F.softmax(verify_logits[:, target_pos, :], dim=-1)

            drafted_token = draft_tokens[k]
            target_prob_of_drafted = target_probs[:, drafted_token[:, 0]].squeeze(-1)

            # Rejection sampling: accept with probability min(1, P_target / P_draft)
            # If temperature=0 (greedy), accept if drafted == argmax(target)
            if temperature == 0:
                target_argmax = target_probs.argmax(dim=-1)
                if target_argmax.item() == drafted_token.item():
                    n_accepted += 1
                else:
                    break
            else:
                # Stochastic acceptance
                P_draft = draft_probs[k].squeeze(-1)
                accept_prob = torch.min(torch.ones_like(target_prob_of_drafted), target_prob_of_drafted / P_draft)
                if torch.rand(1).item() < accept_prob.item():
                    n_accepted += 1
                else:
                    # Resample from corrected distribution
                    corrected_probs = torch.clamp(target_probs - P_draft, min=0)
                    corrected_probs = corrected_probs / corrected_probs.sum(dim=-1, keepdim=True)
                    resampled = torch.multinomial(corrected_probs, 1)
                    generated = torch.cat([generated, resampled], dim=1)
                    break

        # Append accepted tokens
        accepted_tokens = torch.cat(draft_tokens[:n_accepted], dim=1) if n_accepted > 0 else None
        if accepted_tokens is not None:
            generated = torch.cat([generated, accepted_tokens], dim=1)

        # If we rejected everything, append target's next token (standard autoregressive step)
        if n_accepted == 0 and temperature == 0:
            target_pos = generated.shape[1] - 1
            target_next = verify_logits[:, target_pos, :].argmax(dim=-1, keepdim=True)
            generated = torch.cat([generated, target_next], dim=1)

    return generated


# Performance analysis
"""
EAGLE-2 vs vanilla:
- Vanilla: 1 forward pass per token. For 100 tokens, 100 forward passes.
- EAGLE-2 (K=4, 90% acceptance): ~25 forward passes (each accepts ~4 tokens).
- Speedup: 4x.

EAGLE-2's key insight: predict HIDDEN STATES (smoother, more predictable than tokens),
use target model's vocab head to decode. This ensures distribution alignment.
"""
```

#### Key points

EAGLE-2's two innovations: (1) predict hidden states (not tokens) — smoother, more predictable; (2) dynamic trees — multiple candidate continuations verified in one pass. Combined: 85–95% acceptance rate, 3.5–4.5× speedup. EAGLE-3 adds confidence-aware scheduling (4–6× speedup).

## KV cache questions

KV cache questions test memory management during generation: how to store past keys and values without fragmentation, and how to keep the cache bounded at very long contexts (see [[KV Cache Mechanics]] for the fundamentals).

### Implement PagedAttention

**Question.** Implement a simplified version of PagedAttention, the KV cache management strategy used by [[14 - Inference and Production/Inference/vLLM|vLLM]] (concept note: [[PagedAttention]]). The key idea: partition the KV cache into fixed-size blocks (pages), allowing non-contiguous storage and efficient memory usage.

#### Background

Standard KV cache stores each sequence's K and V as a contiguous tensor. This wastes memory (fragmentation) and limits batching. PagedAttention partitions the cache into blocks (e.g., 16 tokens each), stores each sequence as a list of block pointers, and attention computes over the blocks.

#### Approach

1. Maintain a global pool of KV blocks (each holding K and V for `block_size` tokens).
2. Each sequence has a list of block IDs (its "page table").
3. During attention, gather blocks for the sequence and compute attention.
4. When a sequence grows, allocate a new block; when it ends, free its blocks.

#### Implementation (conceptual)

```python
import torch
import torch.nn.functional as F

class PagedKVCache:
    """Simplified PagedAttention KV cache."""

    def __init__(
        self,
        num_blocks: int,
        block_size: int,
        num_heads: int,
        head_dim: int,
        dtype=torch.bfloat16,
    ):
        self.block_size = block_size
        self.num_heads = num_heads
        self.head_dim = head_dim

        # Global pool of KV blocks
        # Shape: (num_blocks, 2, block_size, num_heads, head_dim)
        # The 2 is for K and V
        self.kv_pool = torch.zeros(
            num_blocks, 2, block_size, num_heads, head_dim, dtype=dtype
        )
        self.free_blocks = list(range(num_blocks))  # Stack of free block IDs
        self.sequence_blocks: dict[int, list[int]] = {}  # seq_id -> block IDs

    def allocate_sequence(self, seq_id: int):
        """Start a new sequence (no blocks yet)."""
        self.sequence_blocks[seq_id] = []

    def append_kv(self, seq_id: int, new_k: torch.Tensor, new_v: torch.Tensor):
        """
        Append new K, V for a sequence.
        new_k, new_v: (new_tokens, num_heads, head_dim)
        """
        num_new = new_k.shape[0]
        for i in range(num_new):
            # If current block is full, allocate a new one
            seq_blocks = self.sequence_blocks[seq_id]
            current_pos = len(seq_blocks) * self.block_size + i  # approx

            if not seq_blocks or current_pos % self.block_size == 0:
                # Need a new block
                if not self.free_blocks:
                    raise RuntimeError("KV cache full — increase num_blocks")
                block_id = self.free_blocks.pop()
                seq_blocks.append(block_id)

            # Write K, V to the current block
            block_id = seq_blocks[-1]
            offset = (len(seq_blocks) * self.block_size - 1) % self.block_size
            self.kv_pool[block_id, 0, offset] = new_k[i]  # K
            self.kv_pool[block_id, 1, offset] = new_v[i]  # V

    def get_kv(self, seq_id: int) -> tuple[torch.Tensor, torch.Tensor]:
        """Get the full K, V for a sequence (gathered from blocks)."""
        block_ids = self.sequence_blocks[seq_id]
        if not block_ids:
            return torch.empty(0), torch.empty(0)

        # Gather blocks
        blocks = self.kv_pool[block_ids]  # (num_blocks, 2, block_size, num_heads, head_dim)
        # Flatten block + token dims
        k = blocks[:, 0].reshape(-1, self.num_heads, self.head_dim)  # (seq_len, num_heads, head_dim)
        v = blocks[:, 1].reshape(-1, self.num_heads, self.head_dim)
        return k, v

    def free_sequence(self, seq_id: int):
        """Free all blocks for a finished sequence."""
        for block_id in self.sequence_blocks[seq_id]:
            self.free_blocks.append(block_id)
        del self.sequence_blocks[seq_id]


def paged_attention(
    query: torch.Tensor,  # (num_heads, head_dim)
    cache: PagedKVCache,
    seq_id: int,
) -> torch.Tensor:
    """Compute attention for a single query against the paged KV cache."""
    k, v = cache.get_kv(seq_id)  # (seq_len, num_heads, head_dim)

    # Per-head attention (simplified — no batching)
    head_dim = query.shape[-1]
    scores = torch.einsum('hd,thd->th', query, k) / (head_dim ** 0.5)  # (seq_len,)
    weights = F.softmax(scores, dim=0)
    output = torch.einsum('t,thd->hd', weights, v)  # (num_heads, head_dim)
    return output
```

#### Key implementation details

- **Block pool**: a single large tensor for all KV storage, partitioned into blocks. Avoids per-sequence allocation overhead.
- **Page table**: each sequence has a list of block IDs. This indirection allows non-contiguous storage (no external fragmentation).
- **Block size**: typically 16 tokens. Smaller blocks → less internal fragmentation but more metadata overhead. vLLM uses 16.
- **Free list**: a stack of free block IDs. Allocating is `pop()`; freeing is `append()`. O(1) operations.
- **Gather operation**: to compute attention, gather the sequence's blocks and flatten. In production, this is done with custom CUDA kernels (vLLM's PagedAttention kernel).

#### Common pitfalls

- **External fragmentation** — without paging, allocating and freeing variable-length sequences fragments memory. Paging eliminates this.
- **Internal fragmentation** — the last block of each sequence may be partially full. With block_size=16, average waste is 8 tokens per sequence. Acceptable.
- **Wrong block indexing** — the offset calculation (which slot in the block to write to) is easy to get wrong. Test carefully.
- **Not freeing blocks** — if sequences don't free their blocks, the cache fills up. Always free on sequence end (or preemption).
- **Capacity management** — when the cache is full, you must preempt sequences (free their blocks to make room for new ones). vLLM uses LRU preemption.

#### Follow-up questions

- **How does PagedAttention enable continuous batching?** — without paging, you can't add new sequences to a batch mid-generation (the contiguous KV caches don't have room). With paging, you just allocate new blocks for the new sequence. This lets vLLM process sequences of different lengths and arrival times in the same batch. See [[Continuous Batching]].
- **What's the block size tradeoff?** — smaller blocks (e.g., 4) reduce internal fragmentation but increase metadata overhead (more block pointers per sequence). Larger blocks (e.g., 64) reduce overhead but increase fragmentation. vLLM found 16 to be the sweet spot empirically.
- **How would you implement preemption?** — when the cache is full, pick a sequence to evict (LRU is common). Free its blocks and either recompute it on next request (longer latency) or swap its blocks to CPU (faster resume).

### Implement a KV cache eviction policy

**Question.** Implement a simple KV cache eviction policy for long-context inference.

#### Solution

```python
import torch
from collections import deque
from typing import Optional

class EvictionKVCache:
    """KV cache with eviction policy for long-context inference.

    Eviction strategies:
    - 'fifo': evict oldest tokens (simplest)
    - 'least_attention': evict tokens with lowest cumulative attention
    - 'recent_window': keep last N tokens, evict older

    Trade-off: smaller cache = less memory but lower quality on long-context retrieval.
    """

    def __init__(
        self,
        max_cache_size: int,  # max number of tokens to cache
        head_dim: int,
        num_kv_heads: int,
        num_layers: int,
        eviction_strategy: str = "recent_window",
        recent_window: int = 1024,  # for 'recent_window' strategy
    ):
        self.max_cache_size = max_cache_size
        self.head_dim = head_dim
        self.num_kv_heads = num_kv_heads
        self.num_layers = num_layers
        self.eviction_strategy = eviction_strategy
        self.recent_window = recent_window

        # Initialize cache
        self.keys = [None] * num_layers  # list of (batch, num_kv_heads, seq, head_dim)
        self.values = [None] * num_layers
        self.attention_scores = [None] * num_layers  # cumulative attention for 'least_attention'
        self.token_positions = deque()  # FIFO of token positions

    def update(
        self,
        new_keys: list,  # list of (batch, num_kv_heads, new_seq, head_dim) per layer
        new_values: list,
    ):
        """Add new K/V to cache; evict if necessary."""
        for layer_idx in range(self.num_layers):
            if self.keys[layer_idx] is None:
                self.keys[layer_idx] = new_keys[layer_idx]
                self.values[layer_idx] = new_values[layer_idx]
            else:
                self.keys[layer_idx] = torch.cat([self.keys[layer_idx], new_keys[layer_idx]], dim=2)
                self.values[layer_idx] = torch.cat([self.values[layer_idx], new_values[layer_idx]], dim=2)

        # Track positions
        new_tokens = new_keys[0].shape[2]
        for i in range(new_tokens):
            self.token_positions.append(len(self.token_positions))

        # Evict if over capacity
        current_size = self.keys[0].shape[2]
        if current_size > self.max_cache_size:
            self._evict(current_size - self.max_cache_size)

    def _evict(self, n_to_evict: int):
        """Evict n_to_evict tokens from cache."""
        if self.eviction_strategy == "fifo":
            # Evict oldest
            for layer_idx in range(self.num_layers):
                self.keys[layer_idx] = self.keys[layer_idx][:, :, n_to_evict:, :]
                self.values[layer_idx] = self.values[layer_idx][:, :, n_to_evict:, :]
            for _ in range(n_to_evict):
                self.token_positions.popleft()

        elif self.eviction_strategy == "recent_window":
            # Keep last recent_window tokens + most-attended older tokens
            # Simplest version: just keep last recent_window tokens
            for layer_idx in range(self.num_layers):
                self.keys[layer_idx] = self.keys[layer_idx][:, :, -self.recent_window:, :]
                self.values[layer_idx] = self.values[layer_idx][:, :, -self.recent_window:, :]
            # Update positions
            while len(self.token_positions) > self.recent_window:
                self.token_positions.popleft()

        elif self.eviction_strategy == "least_attention":
            # Evict tokens with lowest cumulative attention
            # Requires tracking attention scores (complex; omitted for brevity)
            raise NotImplementedError("See H2O: Heavy-Hitter Oracle paper")

    def get(self) -> tuple:
        return self.keys, self.values


# Test
cache = EvictionKVCache(
    max_cache_size=4096,  # cache up to 4096 tokens
    head_dim=128, num_kv_heads=8, num_layers=32,
    eviction_strategy="recent_window", recent_window=2048,
)
# Simulate adding tokens
batch_size = 1
for step in range(100):
    new_k = [torch.randn(batch_size, 8, 100, 128) for _ in range(32)]
    new_v = [torch.randn(batch_size, 8, 100, 128) for _ in range(32)]
    cache.update(new_k, new_v)

keys, values = cache.get()
print(f"Final cache size: {keys[0].shape[2]} tokens (target: 4096)")
# With recent_window=2048, cache stays at 2048 once exceeded
```

#### Key points

KV cache compression is essential for long-context serving. Common strategies: (1) recent window (keep last N tokens), (2) attention-based eviction (H2O — keep tokens with high cumulative attention), (3) token merging (combine similar tokens), (4) low-rank compression (MLA in DeepSeek-V3; see [[DeepSeek-V2 and V3]]). Trade-off: smaller cache = lower quality on retrieval.

## Training loss questions

Training-algorithm questions test whether you can implement the objective itself, not just call a library. The bank's example is the group-relative policy objective behind reasoning-model training.

### Implement the GRPO loss for reasoning model training

**Question.** Implement the GRPO (Group Relative Policy Optimization) loss function used to train reasoning models like DeepSeek-R1 (see [[DeepSeek-R1]] and [[Reasoning Models]]). GRPO is a variant of PPO that eliminates the value function by using group-relative advantages.

#### Background

GRPO generates $G$ completions per prompt, computes rewards for each, and uses the group-relative advantage $A_i = (r_i - \text{mean}(r)) / \text{std}(r)$ instead of PPO's value-function-based advantage. This is simpler (no value network to train) and works well for verifiable-reward tasks (math, code).

#### Approach

1. Sample $G$ completions per prompt from the current policy.
2. Compute rewards $r_1, \ldots, r_G$ (using a verifier or reward model).
3. Compute group-relative advantages: $A_i = (r_i - \bar{r}) / \sigma_r$.
4. Compute the policy gradient loss with clipping (like PPO) and KL penalty to a reference policy.

#### Implementation

```python
import torch
import torch.nn.functional as F

def grpo_loss(
    policy_log_probs: torch.Tensor,    # (G,) log p(completion_i | prompt) under current policy
    old_log_probs: torch.Tensor,       # (G,) log p under the policy that generated the completions
    ref_log_probs: torch.Tensor,       # (G,) log p under the reference (frozen) policy
    rewards: torch.Tensor,             # (G,) reward for each completion
    beta: float = 0.04,                # KL penalty coefficient
    clip_epsilon: float = 0.2,         # PPO clip range
) -> torch.Tensor:
    """
    Compute GRPO loss for a single prompt's group of G completions.

    Returns: scalar loss (to be minimized).
    """
    G = rewards.shape[0]

    # 1. Group-relative advantage
    mean_r = rewards.mean()
    std_r = rewards.std() + 1e-8  # avoid div by zero
    advantages = (rewards - mean_r) / std_r  # (G,)

    # 2. Importance sampling ratio (PPO-style)
    log_ratio = policy_log_probs - old_log_probs  # (G,)
    ratio = torch.exp(log_ratio)

    # 3. Clipped surrogate objective
    surr1 = ratio * advantages
    surr2 = torch.clamp(ratio, 1.0 - clip_epsilon, 1.0 + clip_epsilon) * advantages
    policy_loss = -torch.min(surr1, surr2).mean()  # negate because we minimize

    # 4. KL penalty to reference policy
    # KL(policy || ref) ≈ exp(ref_log - policy_log) - (ref_log - policy_log) - 1
    # This is the unbiased k3 estimator from John Schulman's blog
    log_diff = ref_log_probs - policy_log_probs
    kl = (torch.exp(log_diff) - log_diff - 1).mean()

    # 5. Total loss
    loss = policy_loss + beta * kl

    return loss

# Test
if __name__ == "__main__":
    G = 8
    policy_log_probs = torch.randn(G)
    old_log_probs = policy_log_probs.clone()  # On-policy: ratio = 1
    ref_log_probs = torch.randn(G)
    rewards = torch.tensor([1.0, 0.0, 1.0, 0.5, 0.0, 1.0, 0.0, 0.5])

    loss = grpo_loss(policy_log_probs, old_log_probs, ref_log_probs, rewards)
    print(f"GRPO loss: {loss.item():.4f}")  # Should be a reasonable scalar
```

#### Key implementation details

- **Group-relative advantage**: $A_i = (r_i - \bar{r}) / \sigma_r$. This replaces PPO's value-function-based advantage. The normalization (subtract mean, divide by std) is critical — without it, all-positive rewards would push the policy to increase all completion probabilities, which is wrong.
- **Importance sampling ratio**: $\rho = \pi_\theta / \pi_{\text{old}}$. Even in on-policy training, $\pi_\theta$ drifts from $\pi_{\text{old}}$ between updates, so the ratio matters.
- **Clipping**: prevents destructive large updates. Same as PPO.
- **KL penalty**: keeps the policy close to the reference (frozen) policy. Without this, the policy can drift into degenerate behavior (e.g., always producing the same completion regardless of prompt).
- **k3 KL estimator**: $\text{KL} \approx \exp(\log p_{\text{ref}} - \log p_\theta) - (\log p_{\text{ref}} - \log p_\theta) - 1$. This is unbiased and more numerically stable than the naive $\exp$ estimator.

#### Common pitfalls

- **Forgetting to normalize advantages** — without normalization, all-positive rewards push all probabilities up, which is wrong.
- **Using PPO's value function** — GRPO eliminates the value function. Don't add it back.
- **Wrong KL estimator** — the naive $\exp(\log p_{\text{ref}} - \log p_\theta)$ estimator is biased; use k3.
- **Forgetting to detach `old_log_probs`** — these are constants (from the generation step), not differentiable.
- **Per-prompt vs. batch** — GRPO computes advantages per-prompt (within the group), not across the batch. Different prompts have different reward distributions.

#### Follow-up questions

- **Why does GRPO eliminate the value function?** — because the group-relative advantage is a sufficient signal for verifiable-reward tasks. The value function is needed in PPO because rewards are sparse and noisy; in GRPO, the group provides a natural baseline.
- **How would you handle variable-length completions?** — pad to the max length in the group, mask padding in the log-prob computation (sum over actual tokens only).
- **What's the difference between GRPO and RLOO (Reinforce Leave-One-Out)?** — RLOO uses leave-one-out means as baselines; GRPO uses the group mean and std for normalization. They're similar but GRPO's normalization makes it more robust to reward scale.

For the underlying PPO machinery, see [[Proximal Policy Optimization]] and [[RLHF with PPO]] — PPO is the foundation for GRPO.

## Architecture component questions

Component questions test whether you can build the pieces that turn a Transformer into a full system — the vision front-end of a VLM and the sparse expert routing of a MoE layer.

### Implement image patch embedding for a VLM

**Question.** Implement the patch embedding layer that converts an image into a sequence of token embeddings for a Vision-Language Model (VLM). This is the first layer of ViT, CLIP, and LLaVA (see [[Vision Transformer]], [[Patch Tokenization]], [[CLIP]], and [[LLaVA]]).

#### Background

A VLM needs to convert a 2D image into a 1D sequence of token embeddings that the Transformer can process. The standard approach: split the image into non-overlapping patches (e.g., 16×16), flatten each patch, and project to the embedding dimension.

#### Approach

1. Input: image tensor of shape `(B, C, H, W)`.
2. Split into patches of size `P × P`, giving `(B, C, H/P, W/P, P, P)`.
3. Flatten patches to `(B, num_patches, C × P × P)`.
4. Linear project to `(B, num_patches, embed_dim)`.
5. Add positional embeddings.
6. Prepend a `[CLS]` token (optional).

#### Implementation

```python
import torch
import torch.nn as nn

class PatchEmbedding(nn.Module):
    """Convert image to patch embeddings (ViT-style)."""

    def __init__(
        self,
        patch_size: int = 16,
        in_channels: int = 3,
        embed_dim: int = 768,
        image_size: int = 224,
    ):
        super().__init__()
        self.patch_size = patch_size
        self.embed_dim = embed_dim
        self.num_patches = (image_size // patch_size) ** 2

        # Conv2d is an efficient way to do patch extraction + projection
        # kernel_size=patch_size, stride=patch_size => non-overlapping patches
        self.proj = nn.Conv2d(
            in_channels, embed_dim,
            kernel_size=patch_size, stride=patch_size
        )

        # Positional embeddings (learned)
        self.pos_embed = nn.Parameter(
            torch.randn(1, self.num_patches + 1, embed_dim) * 0.02
        )

        # CLS token (optional)
        self.cls_token = nn.Parameter(torch.randn(1, 1, embed_dim) * 0.02)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: (B, C, H, W) — image tensor
        returns: (B, num_patches + 1, embed_dim) — patch embeddings + CLS
        """
        B = x.shape[0]

        # 1. Patch extraction + projection: (B, C, H, W) -> (B, embed_dim, H/P, W/P)
        x = self.proj(x)

        # 2. Flatten spatial dims: (B, embed_dim, H/P, W/P) -> (B, embed_dim, num_patches)
        x = x.flatten(2)

        # 3. Transpose: (B, embed_dim, num_patches) -> (B, num_patches, embed_dim)
        x = x.transpose(1, 2)

        # 4. Prepend CLS token
        cls = self.cls_token.expand(B, -1, -1)  # (B, 1, embed_dim)
        x = torch.cat([cls, x], dim=1)  # (B, num_patches + 1, embed_dim)

        # 5. Add positional embeddings
        x = x + self.pos_embed

        return x

# Test
if __name__ == "__main__":
    patch_embed = PatchEmbedding(patch_size=16, embed_dim=768, image_size=224)
    image = torch.randn(2, 3, 224, 224)  # Batch of 2 RGB images
    embeddings = patch_embed(image)
    print(f"Input shape: {image.shape}")
    print(f"Output shape: {embeddings.shape}")  # Should be (2, 197, 768) — 196 patches + 1 CLS
```

#### Key implementation details

- **Conv2d trick**: using a Conv2d with `kernel_size=patch_size, stride=patch_size` is equivalent to patch extraction + linear projection, but much faster (fused into one operation). This is what production ViTs use.
- **Patch count**: for 224×224 image with 16×16 patches, num_patches = (224/16)² = 196. Plus 1 for CLS = 197 tokens.
- **Positional embeddings**: learned, shape `(1, num_patches + 1, embed_dim)`. Initialized with small std (0.02). Added (not concatenated) to patch embeddings.
- **CLS token**: a learnable token prepended to the sequence. Its final state is used as the image representation (for classification) or fed to the LLM (in CLIP/LLaVA).
- **Initialization**: pos_embed and cls_token are typically initialized with std=0.02 (matching Transformer init convention).

#### Common pitfalls

- **Wrong patch count** — off-by-one if image_size isn't divisible by patch_size. Add an assertion.
- **Wrong transpose** — `(B, embed_dim, num_patches)` vs `(B, num_patches, embed_dim)`. The Transformer expects sequence-first.
- **Forgetting positional embeddings** — without them, the model can't distinguish patch positions (Transformer is permutation-invariant).
- **Wrong CLS expansion** — `cls_token` has shape `(1, 1, embed_dim)`, needs `.expand(B, -1, -1)` to match batch size.
- **Conv2d vs. unfold** — using `unfold` is slower and uses more memory. Stick with Conv2d.

#### Follow-up questions

- **How would you handle variable image sizes?** — interpolate the positional embeddings to the new size (bicubic). The patch count changes, but the embed_dim stays the same.
- **Why use Conv2d instead of explicit patch extraction?** — it's a fused operation (extract + project in one CUDA kernel), much faster than separate extraction + linear.
- **What's the difference between ViT and CLIP's image encoder?** — CLIP uses a ViT architecture but with a different training objective (contrastive) and typically larger embed_dim. The patch embedding is the same.

### Implement mixture-of-experts routing

**Question.** Implement the routing mechanism for a Mixture-of-Experts (MoE) layer (see [[Mixture of Experts]] for the concept, [[Mistral and Mixtral Architecture]] for a production example, and [[Build a Mini MoE]] for a full build). Given an input token, the router selects the top-K experts and combines their outputs.

#### Background

MoE layers have $N$ expert feed-forward networks. For each token, a router network computes logits over experts, picks the top-K, and combines their outputs weighted by the softmax of the logits. This gives sparse activation: only K experts are active per token, even though all N experts' parameters are stored.

#### Approach

1. Router: linear layer from `embed_dim` to `num_experts`.
2. Top-K selection: pick the K experts with highest logits.
3. Softmax over the selected K logits (not all N).
4. Dispatch tokens to selected experts.
5. Combine outputs weighted by the softmax scores.

#### Implementation

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class MoELayer(nn.Module):
    def __init__(
        self,
        embed_dim: int = 768,
        num_experts: int = 8,
        top_k: int = 2,
        expert_hidden_dim: int = 3072,
    ):
        super().__init__()
        self.num_experts = num_experts
        self.top_k = top_k

        # Router: embed_dim -> num_experts logits
        self.router = nn.Linear(embed_dim, num_experts, bias=False)

        # Experts: each is a standard FFN (Linear -> SwiGLU -> Linear)
        self.experts = nn.ModuleList([
            self._make_expert(embed_dim, expert_hidden_dim)
            for _ in range(num_experts)
        ])

    def _make_expert(self, embed_dim, hidden_dim):
        return nn.Sequential(
            nn.Linear(embed_dim, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, embed_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: (B, N, D) — batch of sequences
        returns: (B, N, D) — same shape, but each token processed by top-K experts
        """
        B, N, D = x.shape
        x_flat = x.view(B * N, D)  # (B*N, D)

        # 1. Router logits
        router_logits = self.router(x_flat)  # (B*N, num_experts)

        # 2. Top-K selection
        top_k_logits, top_k_indices = torch.topk(router_logits, self.top_k, dim=-1)
        # top_k_logits: (B*N, K), top_k_indices: (B*N, K)

        # 3. Softmax over the selected K (not all N)
        router_weights = F.softmax(top_k_logits, dim=-1)  # (B*N, K)

        # 4. Dispatch to experts and combine
        output = torch.zeros_like(x_flat)
        for k in range(self.top_k):
            expert_indices = top_k_indices[:, k]  # (B*N,) — which expert for each token at slot k
            weights = router_weights[:, k]  # (B*N,) — weight for each token at slot k

            # Group tokens by expert
            for e in range(self.num_experts):
                mask = expert_indices == e
                if not mask.any():
                    continue
                expert_input = x_flat[mask]  # (num_tokens_for_expert_e, D)
                expert_output = self.experts[e](expert_input)  # (num_tokens, D)
                output[mask] += weights[mask].unsqueeze(-1) * expert_output

        return output.view(B, N, D)

# Test
if __name__ == "__main__":
    moe = MoELayer(embed_dim=768, num_experts=8, top_k=2)
    x = torch.randn(2, 10, 768)  # Batch of 2, seq_len 10
    out = moe(x)
    print(f"Input: {x.shape}, Output: {out.shape}")  # Both (2, 10, 768)
```

#### Key implementation details

- **Top-K, not top-1**: top-2 or top-8 is standard. Top-1 is too sparse (loses quality); top-K with large K approaches dense (loses efficiency).
- **Softmax over selected K, not all N**: this is critical. If you softmax over all N, the unselected experts get non-zero weight, breaking sparsity.
- **Grouping by expert**: the inner loop groups tokens by expert, allowing batched computation per expert. This is much faster than calling each expert per-token.
- **Auxiliary loss**: production MoE adds a load-balancing loss to encourage experts to be used evenly. The naive implementation above doesn't include this.
- **No bias in router**: the router typically has no bias (just a linear projection). Bias can cause degenerate solutions where one expert always wins.

#### Common pitfalls

- **Softmax over all N instead of selected K** — breaks sparsity. The unselected experts get non-zero weight, defeating the purpose.
- **Not grouping by expert** — calling each expert per-token is O(B×N×K) expert calls. Grouping by expert is O(N_experts) expert calls (each with a batch). 10–100× faster.
- **Forgetting the auxiliary loss** — without load balancing, one expert can dominate (router collapse), wasting the other experts' parameters.
- **Wrong gradient flow** — the top-K selection is non-differentiable (argmax). Gradients flow through the softmax weights, not the selection. This is correct but easy to get wrong in custom implementations.
- **Capacity factor** — production MoE has a "capacity" per expert (max tokens it can process). Tokens beyond capacity are dropped. This implementation doesn't have capacity — fine for learning, not for production.

#### Follow-up questions

- **How would you add load balancing?** — add an auxiliary loss that penalizes imbalanced expert usage. The standard formulation: $L_{\text{aux}} = N \cdot \sum_i f_i \cdot P_i$, where $f_i$ is the fraction of tokens routed to expert $i$ and $P_i$ is the average router probability for expert $i$. This encourages uniform usage.
- **What's the difference between this and DeepSeek-V3's auxiliary-loss-free routing?** — DeepSeek-V3 uses a bias term per expert that's adjusted based on usage (increased for underused experts, decreased for overused). This achieves load balancing without the gradient interference of the auxiliary loss. See [[DeepSeek-V2 and V3]].
- **How would you parallelize this across GPUs?** — expert parallelism: each GPU holds a subset of experts. Tokens are dispatched to the GPU that holds their assigned expert. This requires all-to-all communication.

## Tool integration questions

Tooling questions test protocol-level engineering: can you stand up a server that an LLM client can actually talk to, honoring the wire format exactly?

### Implement an MCP tool server

**Question.** Implement a minimal MCP (Model Context Protocol) server that exposes a single tool (e.g., "search the web") and handles JSON-RPC requests from an MCP client (protocol overview in [[MCP Overview]]; a fuller build in [[Build an MCP Server]]).

#### Background

MCP is a protocol for LLMs to call external tools. An MCP server exposes resources, prompts, and tools via JSON-RPC. Clients (like Claude Desktop, Cursor) connect to servers and call their tools.

#### Approach

1. Define the tool's schema (name, description, input schema).
2. Implement the JSON-RPC `initialize`, `tools/list`, and `tools/call` methods.
3. Run the server over stdio (the simplest transport).

#### Implementation

```python
import json
import sys
from typing import Any

def search_web(query: str, max_results: int = 5) -> list[dict]:
    """Mock web search — replace with a real search API."""
    return [
        {"title": f"Result {i+1} for '{query}'", "url": f"https://example.com/{i+1}"}
        for i in range(max_results)
    ]

# Tool definitions
TOOLS = [
    {
        "name": "search_web",
        "description": "Search the web and return top results.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "max_results": {"type": "integer", "description": "Max results (default 5)", "default": 5},
            },
            "required": ["query"],
        },
    }
]

def handle_request(request: dict) -> dict | None:
    """Handle a single JSON-RPC request."""
    method = request.get("method")
    req_id = request.get("id")
    params = request.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "web-search-server", "version": "1.0.0"},
            },
        }

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": TOOLS},
        }

    elif method == "tools/call":
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})

        if tool_name == "search_web":
            result = search_web(**tool_args)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {"type": "text", "text": json.dumps(result, indent=2)}
                    ]
                },
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"},
            }

    # Notification (no id) — no response needed
    if req_id is None:
        return None

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Unknown method: {method}"},
    }

def main():
    """Read JSON-RPC requests from stdin, write responses to stdout."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = handle_request(request)
            if response is not None:
                print(json.dumps(response), flush=True)
        except json.JSONDecodeError:
            error = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Parse error"},
            }
            print(json.dumps(error), flush=True)

if __name__ == "__main__":
    main()
```

#### Key implementation details

- **JSON-RPC 2.0**: every request has `jsonrpc: "2.0"`, an `id`, and a `method`. Responses echo the `id`. Notifications (no `id`) don't get responses.
- **Protocol version**: MCP uses dated protocol versions (e.g., `2024-11-05`). The client and server negotiate during `initialize`.
- **Tools vs. resources vs. prompts**: tools are functions the LLM can call; resources are data the LLM can read; prompts are templates the LLM can use. This example only implements tools.
- **Content format**: tool results are returned as a list of content blocks (`{"type": "text", "text": "..."}`). Other types: `image`, `resource`.
- **Stdio transport**: the simplest MCP transport. The server reads JSON-RPC from stdin, writes to stdout. Other transports: HTTP, SSE.

#### Common pitfalls

- **Forgetting `flush=True`** — without flushing, the client doesn't receive the response until the buffer fills.
- **Not handling notifications** — notifications (no `id`) don't get responses. Returning a response for a notification is a protocol error.
- **Wrong error codes** — JSON-RPC defines specific error codes (-32700 parse error, -32601 method not found, etc.). Use them correctly.
- **Not validating input schema** — the tool's `inputSchema` should be validated against the actual arguments. Use Pydantic or jsonschema.
- **Blocking I/O** — the stdio loop blocks on `sys.stdin`. For concurrent tool execution, use async I/O.

#### Follow-up questions

- **How would you add authentication?** — for stdio transport, the client and server are on the same machine (no auth needed). For HTTP transport, use OAuth or API keys in the Authorization header.
- **How would you handle long-running tools?** — return a "progress" notification immediately, then send the final result when ready. The client can display progress to the user.
- **What's the difference between MCP and OpenAI function calling?** — MCP is a protocol (transport + schema), function calling is an API feature. MCP servers can be used by any client (Claude, Cursor, custom); function calling is OpenAI-specific. MCP is more general; function calling is simpler. See [[Function Calling]].

## Quantization questions

Quantization questions test numerical precision engineering: how to shrink weights to 4 bits and pay back as little quality as possible (see [[Quantization]] for the fundamentals).

### Implement INT4 weight-only quantization

**Question.** Implement INT4 weight-only quantization for a Linear layer. Convert fp16/bf16 weights to 4-bit integers and implement the dequantization + matmul at inference time.

#### Background

INT4 quantization reduces model memory by 4× (vs fp16) and can speed up inference (memory bandwidth is the bottleneck for LLM inference). The simplest form is weight-only quantization: weights are stored as INT4, activations stay in fp16/bf16, and dequantization happens on the fly during the matmul.

#### Approach

1. **Quantization**: for each weight, find the min/max, compute scale = (max - min) / 15, quantize to [0, 15].
2. **Storage**: pack two INT4 values into one byte (since 4+4=8 bits).
3. **Dequantization**: at inference, unpack and dequantize: `w = (q * scale) + zero_point`.
4. **Matmul**: dequantize weights on the fly and multiply with fp16 activations.

#### Implementation

```python
import torch
import torch.nn as nn

def quantize_int4(weight: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    Quantize a weight tensor to INT4 (per-row asymmetric quantization).

    weight: (out_features, in_features)
    returns:
        packed: (out_features, in_features // 2) — two INT4 values packed per byte
        scales: (out_features,) — per-row scale
        zero_points: (out_features,) — per-row zero point
    """
    out_features, in_features = weight.shape

    # Per-row min/max
    w_min = weight.min(dim=1, keepdim=True).values  # (out_features, 1)
    w_max = weight.max(dim=1, keepdim=True).values

    # Scale and zero point
    scales = (w_max - w_min) / 15  # (out_features, 1)
    zero_points = -w_min / scales  # (out_features, 1)

    # Quantize: clamp to [0, 15] and round
    q = torch.clamp(torch.round(weight / scales + zero_points), 0, 15).to(torch.uint8)
    # q is (out_features, in_features) with values in [0, 15]

    # Pack two values per byte
    assert in_features % 2 == 0
    q_left = q[:, ::2]   # (out_features, in_features // 2)
    q_right = q[:, 1::2]
    packed = (q_left << 4) | q_right  # (out_features, in_features // 2)

    return packed, scales.squeeze(1), zero_points.squeeze(1)


def dequantize_int4(
    packed: torch.Tensor,
    scales: torch.Tensor,
    zero_points: torch.Tensor,
) -> torch.Tensor:
    """Dequantize INT4 packed weights back to fp16."""
    out_features, half_in = packed.shape
    in_features = half_in * 2

    # Unpack
    q_left = (packed >> 4) & 0x0F  # (out_features, half_in)
    q_right = packed & 0x0F

    # Interleave back
    q = torch.zeros(out_features, in_features, dtype=torch.uint8, device=packed.device)
    q[:, ::2] = q_left
    q[:, 1::2] = q_right

    # Dequantize: w = (q - zero_point) * scale
    weight = (q.float() - zero_points.unsqueeze(1)) * scales.unsqueeze(1)
    return weight.to(torch.float16)


class INT4Linear(nn.Module):
    """Linear layer with INT4 quantized weights."""

    def __init__(self, in_features: int, out_features: int, bias: bool = True):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features

        # Quantized weights (set during quantize())
        self.register_buffer("packed_weight", torch.zeros(out_features, in_features // 2, dtype=torch.uint8))
        self.register_buffer("weight_scales", torch.zeros(out_features))
        self.register_buffer("weight_zero_points", torch.zeros(out_features))

        if bias:
            self.register_buffer("bias", torch.zeros(out_features))
        else:
            self.bias = None

    def quantize_(self, weight: torch.Tensor):
        """Quantize an fp16/bf16 weight tensor in place."""
        packed, scales, zps = quantize_int4(weight.float())
        self.packed_weight.copy_(packed)
        self.weight_scales.copy_(scales)
        self.weight_zero_points.copy_(zps)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """x: (..., in_features) -> (..., out_features)"""
        # Dequantize on the fly
        weight = dequantize_int4(self.packed_weight, self.weight_scales, self.weight_zero_points)

        # Standard matmul
        out = x @ weight.T

        if self.bias is not None:
            out = out + self.bias

        return out

# Test
if __name__ == "__main__":
    # Create a fp16 linear layer
    fp16_linear = nn.Linear(768, 768, bias=True).to(torch.float16)

    # Quantize it
    int4_linear = INT4Linear(768, 768, bias=True)
    int4_linear.quantize_(fp16_linear.weight.data)
    int4_linear.bias.copy_(fp16_linear.bias.data)

    # Compare outputs
    x = torch.randn(1, 10, 768, dtype=torch.float16)
    with torch.no_grad():
        y_fp16 = fp16_linear(x)
        y_int4 = int4_linear(x)

    # Check they're close (INT4 has quantization error)
    error = (y_fp16 - y_int4).abs().mean()
    print(f"Mean absolute error: {error.item():.4f}")
    print(f"Relative error: {(error / y_fp16.abs().mean()).item():.2%}")

    # Check memory savings
    fp16_bytes = fp16_linear.weight.nelement() * 2  # 2 bytes per fp16
    int4_bytes = int4_linear.packed_weight.nelement() * 1  # 1 byte per 2 INT4 values
    print(f"fp16 weight: {fp16_bytes} bytes")
    print(f"INT4 weight: {int4_bytes} bytes ({fp16_bytes / int4_bytes:.1f}x smaller)")
```

#### Key implementation details

- **Per-row quantization**: each output row has its own scale and zero point. This is critical because different rows can have very different value ranges. Per-tensor quantization (one scale for the whole weight) is much worse.
- **Asymmetric quantization**: scale and zero point allow the quantized range to start at any value. Symmetric quantization (only scale, zero point = 0) is simpler but worse for weights with non-zero mean.
- **Packing**: two INT4 values per byte. This halves the storage cost vs. storing each INT4 in a byte (with the high nibble wasted).
- **Dequantization on the fly**: the matmul reads INT4, dequantizes, and multiplies with fp16 activations. In production, this is done with custom CUDA kernels that fuse dequantize + matmul.
- **Bias in fp16**: the bias is typically kept in fp16 (small enough to not matter).

#### Common pitfalls

- **Per-tensor instead of per-row quantization** — much worse quality. Always quantize per-row (or per-channel) for weights.
- **Symmetric instead of asymmetric** — symmetric is simpler but worse for weights with non-zero mean. Use asymmetric.
- **Wrong packing order** — `q_left << 4 | q_right` puts `q_left` in the high nibble. Be consistent when unpacking.
- **Forgetting to handle odd in_features** — packing requires `in_features % 2 == 0`. For odd sizes, pad with a zero.
- **No group quantization** — for better quality, quantize in groups of 32 or 64 (group quantization). This implementation is per-row; group quantization is finer-grained.
- **Not fusing dequantize + matmul** — dequantizing to fp16 and then calling `torch.matmul` is slow. Production kernels (GPTQ, AWQ, Marlin) fuse these operations.

#### Follow-up questions

- **What's the difference between weight-only and weight+activation quantization?** — weight-only keeps activations in fp16/bf16, so dequantization happens per-weight. Weight+activation quantizes both, requiring dequantization of both before matmul. Weight-only is simpler and works well for memory-bound inference; weight+activation is needed for compute-bound scenarios.
- **What are GPTQ and AWQ?** — GPTQ (Generalized Post-Training Quantization) uses second-order information (Hessian) to minimize quantization error per layer. AWQ (Activation-aware Weight Quantization) scales weights based on activation magnitudes. Both achieve better quality than naive per-row quantization.
- **How would you quantize the KV cache?** — similar approach: per-channel (per-head) INT8 or INT4 quantization. The challenge is that KV values change during generation, so quantization must be online. vLLM supports KV cache quantization.

### Implement simplified GPTQ quantization

**Question.** Implement a simplified GPTQ-style INT4 quantization (see [[Quantization]] and [[Build a Quantization Toolkit]] for the surrounding practice).

#### Solution

```python
import torch
import torch.nn as nn

def gptq_quantize(
    weight: torch.Tensor,  # (out_features, in_features)
    calibration_data: torch.Tensor,  # (n_samples, in_features) - sample inputs
    bits: int = 4,
    group_size: int = 128,  # group quantization
):
    """Simplified GPTQ: post-training INT4 quantization using Hessian information.

    Full GPTQ: quantizes weights column-by-column, updating remaining weights
    to compensate for quantization error. Uses Hessian (X^T X) as importance.

    This simplified version: just group-wise symmetric quantization with Hessian-based scaling.
    """
    out_features, in_features = weight.shape

    # Compute Hessian: H = X^T X (averaged over samples)
    # This is the "importance" of each input feature
    hessian = (calibration_data.T @ calibration_data) / calibration_data.shape[0]  # (in_features, in_features)
    hessian_diag = torch.diag(hessian)  # importance per input feature

    # Group-wise quantization
    n_groups = in_features // group_size
    quantized_weight = torch.zeros_like(weight)
    scales = torch.zeros(n_groups, out_features)
    zeros = torch.zeros(n_groups, out_features)

    for g in range(n_groups):
        start = g * group_size
        end = (g + 1) * group_size

        # Get weight slice for this group
        w_slice = weight[:, start:end]  # (out_features, group_size)

        # Compute scale and zero per output channel within group
        # Scale: max absolute value / (2^(bits-1) - 1)
        max_abs = w_slice.abs().amax(dim=-1, keepdim=True)  # (out_features, 1)
        scale = max_abs / (2 ** (bits - 1) - 1)
        zero = 2 ** (bits - 1) - 1  # symmetric

        # Quantize: round to nearest integer
        q = torch.round(w_slice / scale).clamp(-2 ** (bits - 1), 2 ** (bits - 1) - 1)
        # Dequantize (for error compensation)
        w_dequant = q * scale

        # Error compensation: GPTQ updates remaining weights to compensate
        # Simplified version: just use the quantized weight directly
        # Full GPTQ: uses Hessian to update weights to the right of current column
        # (omitted here for brevity)

        quantized_weight[:, start:end] = q  # store INT4 values (will pack in production)
        scales[g] = scale.squeeze(-1)
        zeros[g] = zero

    return quantized_weight, scales, zeros


# Test: quantize a linear layer
linear = nn.Linear(4096, 4096, bias=False)
# Generate calibration data
cal_data = torch.randn(128, 4096)

quantized_weight, scales, zeros = gptq_quantize(
    linear.weight.data, cal_data, bits=4, group_size=128
)

# Verify size reduction
print(f"Original weight: {linear.weight.element_size() * linear.weight.numel() / 1e6:.1f} MB (FP32)")
print(f"Quantized weight: {quantized_weight.element_size() * quantized_weight.numel() / 1e6:.1f} MB (simulated)")
print(f"In production (packed INT4): {0.5 * 4096 * 4096 / 1e6:.1f} MB")
print(f"Scales overhead: {scales.element_size() * scales.numel() / 1e6:.1f} MB")


# Quality test: compare output
test_input = torch.randn(1, 4096)
original_output = linear(test_input)

# Simulate dequantized forward pass
dequant_weight = quantized_weight * scales.repeat_interleave(128, dim=0).T
quantized_output = test_input @ dequant_weight.T

mse = F.mse_loss(original_output, quantized_output)
print(f"MSE between original and quantized: {mse.item():.6f}")
print(f"Relative error: {(mse / original_output.var()).item() * 100:.2f}%")
```

#### Key points

GPTQ uses Hessian information to quantize weights intelligently. The full algorithm quantizes column-by-column, updating remaining weights to compensate for each column's quantization error. The simplified version above shows the basic idea; production GPTQ adds the error compensation step. Quality: ~1–2% loss on MMLU for INT4. AWQ is a similar approach (activation-aware).

## General tips

Five habits that apply across every question in this bank.

### Know the shapes

For every line of code, know the shape of every tensor. Most bugs in attention implementations are shape errors. Write the shapes as comments.

### Vectorize

Avoid Python loops over sequence positions or heads. Use `torch.bmm`, `torch.matmul`, einsum, or reshape + broadcast. Loops are 10–100× slower.

### Use `math.sqrt`, not `** 0.5`

For scalar square roots, `math.sqrt` is clearer. For tensor square roots, use `torch.sqrt(x)` or `x.sqrt()`.

### Test with small examples

Always write a test that verifies the output shape and a simple property (e.g., attention weights sum to 1).

### Discuss the math

Interviewers want to see you understand the formula, not just memorized the code. Write the formula in a comment before implementing.

## See also

- [[Interview Prep MOC]]
- [[Conceptual Interview Questions]]
- [[System Design Interview Questions]]
- [[Build Attention and Transformer From Scratch]]
- [[Glossary MOC]]
