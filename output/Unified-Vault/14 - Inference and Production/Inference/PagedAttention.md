---
title: PagedAttention
type: concept
aliases: [PagedAttention, Paged Attention, Paged KV Cache, Block-Based KV Cache]
tags: [inference, paged-attention, kv-cache, vllm, serving]
sources: ["PagedAttention"]
created_index: 9
---

PagedAttention manages the KV cache as fixed-size pages (blocks) rather than one contiguous allocation per request, borrowing the idea directly from operating-system virtual memory. Introduced with vLLM (Kwon et al. 2023), it eliminates the internal and external fragmentation that wastes 60–80% of GPU memory under naive management, and in doing so enables variable-length batching and prefix caching. This note covers the fragmentation problem, the block-table mechanics and shared blocks, an implementation sketch, quantified memory savings with a worked throughput example, and the related techniques — continuous batching, RadixAttention, chunked prefill, and preemption — that build on the paged design.

> [!info] TL;DR
> PagedAttention (vLLM, Kwon et al. 2023) manages the KV cache as **pages** (fixed-size blocks) rather than contiguous memory. Inspired by OS virtual memory paging. Eliminates fragmentation, enables variable-length batching, and gives 2–4x throughput improvement over HuggingFace's `generate`. The foundation of modern LLM serving.

## The problem: KV cache fragmentation

Naive KV cache management pre-allocates a contiguous block per request, sized for the maximum possible sequence length. This causes severe memory fragmentation in two forms:

- **Internal fragmentation**: a request that ends up using 500 tokens but was allocated 2048 tokens wastes 1548 tokens of memory.
- **External fragmentation**: freed blocks of varying sizes can't be reused for new requests of different sizes.

Empirically, naive KV cache management wastes 60–80% of GPU memory to fragmentation. This limits batch size and throughput.

## The inspiration: OS virtual memory

Operating systems solved this problem decades ago with **virtual memory paging**. Physical memory is divided into fixed-size **pages** (e.g., 4 KB). Each process has a virtual address space, mapped to physical pages via a **page table**. Pages can be allocated and freed independently; the virtual address space appears contiguous to the process.

PagedAttention applies the same idea to the KV cache.

## How PagedAttention works

### Block-based KV cache

The KV cache is divided into fixed-size **blocks** (e.g., 16 tokens per block). Each request has a **block table** mapping its logical token positions to physical blocks:

```text
Logical:  [t0 t1 t2 t3 | t4 t5 t6 t7 | t8 t9 ...]
            Block 0       Block 1       Block 2
              ↓             ↓             ↓
Physical:  [Block 0]    [Block 5]    [Block 2]
           (slot 12)    (slot 47)    (slot 8)
```

Blocks are allocated on demand as the sequence grows. When a sequence ends, its blocks are returned to a free pool and reused by other sequences.

### Attention with block indexing

The attention kernel is modified to:

1. Look up the block table for each sequence.
2. Gather K, V from the physical blocks.
3. Compute attention normally.

Conceptually the lookup is just tensor indexing — logical positions are mapped through the block table before K and V are gathered. This adds a small indirection but eliminates all fragmentation. The kernel is implemented in CUDA with custom kernel fusion.

### Sharing blocks across sequences

A key benefit: blocks can be **shared** across sequences that share a prefix. For example, two chat completions with the same system prompt share the system prompt's blocks — the KV cache is computed once and reused. This is **prefix caching** for free.

Block-level reference counting handles sharing: a block is freed only when its refcount drops to 0.

## Implementation sketch (conceptual)

The mechanics collapse into a small class — a pool of physical blocks, a free list, and a per-request block table:

```python
class PagedKVCache:
    def __init__(self, num_blocks, block_size, num_layers, num_heads, head_dim):
        # Pool of physical blocks
        self.kv_pool = torch.zeros(num_blocks, num_layers, 2, block_size, num_heads, head_dim)
        self.free_blocks = list(range(num_blocks))
        self.block_tables = {}  # request_id -> list of block indices

    def allocate(self, request_id, num_tokens):
        """Allocate enough blocks for num_tokens."""
        blocks_needed = (num_tokens + self.block_size - 1) // self.block_size
        blocks = [self.free_blocks.pop() for _ in range(blocks_needed)]
        self.block_tables[request_id] = blocks
        return blocks

    def append_token(self, request_id, token_pos, k, v):
        """Append a token's K, V to the cache."""
        block_idx = token_pos // self.block_size
        within_block = token_pos % self.block_size
        physical_block = self.block_tables[request_id][block_idx]
        self.kv_pool[physical_block, :, 0, within_block] = k
        self.kv_pool[physical_block, :, 1, within_block] = v

    def free(self, request_id):
        """Release all blocks for a request."""
        for block in self.block_tables[request_id]:
            self.free_blocks.append(block)
        del self.block_tables[request_id]
```

The real implementation is in CUDA for performance; see vLLM source.

## Memory savings

For a workload with variable-length sequences (typical chatbot traffic):

| Method                | KV cache memory efficiency |
|-----------------------|---------------------------|
| Naive (max-size alloc)| 20–40%                    |
| PagedAttention        | 95%+                       |

The 2–4x effective memory increase translates directly to 2–4x larger batches and 2–4x higher throughput. Overall, PagedAttention gives 2-4x throughput vs naive serving (which pre-allocates max-size per request), and the improvement comes from three sources: (1) 95%+ memory efficiency (vs 20-40% with naive); (2) larger batch sizes (more concurrent requests); (3) prefix caching (shared system prompts). Fragmentation itself is nearly gone: internal fragmentation is limited to the last partial block (<16 tokens), and external fragmentation is eliminated entirely.

## Worked throughput example

For a Llama 2 7B server on A100 80GB:

- KV cache available: ~50 GB (after model weights and activations)
- Per-token KV: 1 MB
- Naive (2048 max per request): 50 GB / 2 MB = 25000 max concurrent tokens, but with fragmentation effective ~10000
- PagedAttention: 50000 effective concurrent tokens — **5x improvement**

This means 5x more concurrent users, or 5x more requests per second. In summary form, the same comparison for a 7B model on A100 reads ~250 concurrent tokens (naive) → ~50000 (PagedAttention) — 5x improvement.

## Related techniques

### Continuous batching (iteration-level batching)

Instead of batching all requests together for their entire generation, continuous batching joins/leaves requests at every token (iteration). Combined with PagedAttention, this maximizes GPU utilization. The dependency runs one way: without paging, you can't add new requests to a batch mid-generation because the contiguous KV caches don't have room; with paging, you just allocate new blocks for the new sequence. This lets vLLM process sequences of different lengths and arrival times in the same batch — continuous batching (iteration-level batching).

### RadixAttention (SGLang)

An alternative prefix-cache structure using a radix tree. Provides more flexible prefix sharing (any shared prefix, not just exact-match). Used by SGLang.

### Chunked prefill

For very long prompts, split the prefill into chunks and interleave with decode steps. Reduces prefill latency for long prompts.

### Preemption: recompute or swap

When the KV cache is full, the scheduler must evict a request. Two strategies: (1) recompute — evict the request, recompute its KV when memory frees; (2) swap — evict the KV to CPU memory, swap back when memory frees. PagedAttention supports both. Swap is the production default (faster resume, costs CPU memory).

## Why this matters

PagedAttention made **high-throughput LLM serving** practical. Without it, LLM APIs would be 2–4x more expensive. vLLM popularized PagedAttention and is the dominant open-source LLM serving engine. The block-based design also enables **prefix caching** (system prompts shared across requests) and **speculative decoding** (draft and target sequences share a prefix). The OS-paging analogy is a beautiful example of cross-disciplinary inspiration in systems design.

## Production implications

Use vLLM (or TGI, which has similar techniques) for production LLM serving — don't use HuggingFace `generate` directly, as it lacks these optimizations. Block size matters: too small → high block-table overhead; too large → internal fragmentation. vLLM defaults to 16, which works well — smaller blocks (e.g., 4) mean less internal fragmentation but more block-table overhead (more pointers per sequence), while larger blocks (e.g., 64) mean less overhead but more internal fragmentation (more wasted tokens in the last partial block); 16 is the empirical sweet spot, and the optimal size depends on the workload's sequence length distribution. Prefix caching is critical for chatbot workloads — ensure your serving engine supports it (vLLM does). Continuous batching (also from vLLM) complements PagedAttention — it lets new requests join a batch as soon as space frees up, rather than waiting for the whole batch to finish.

## Common pitfalls

The recurring failure modes:

- **Forgetting to enable prefix caching** — many vLLM deployments ship with it off by default. Enable explicitly.
- **Block size mismatch** — if you change block size, you must restart vLLM. Don't change at runtime.
- **Running out of blocks** — if you see " KV cache is full" errors, reduce max batch size or upgrade GPU memory.
- **Confusing PagedAttention with model quantization** — they're orthogonal. You can use PagedAttention with INT8 KV cache quantization for even more memory savings.

## Further reading

For primary sources, see Kwon et al. (2023), *Efficient Memory Management for Large Language Model Serving with PagedAttention* (vLLM); the vLLM documentation at https://docs.vllm.ai; and SGLang's RadixAttention at https://github.com/sgl-project/sglang.

## See also

- [[Inference and Production MOC]] — orientation for the inference and production area.
- [[KV Cache Mechanics]] — what PagedAttention manages.
- [[14 - Inference and Production/Inference/vLLM|vLLM]] — the engine that implements PagedAttention.
- [[Continuous Batching]] — enabled by PagedAttention.
- [[Speculative Decoding]] — draft and target share prefix blocks.
- [[Quantization]] — orthogonal to paging; combine with INT8 KV cache for further savings.
- [[08 - Attention and Transformers/Efficient Attention/FlashAttention|FlashAttention]] — the complementary kernel-level attention optimization.
