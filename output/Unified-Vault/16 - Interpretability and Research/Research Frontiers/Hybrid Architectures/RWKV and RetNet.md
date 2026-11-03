---
title: RWKV and RetNet
type: concept
aliases: ["RWKV and RetNet", "RWKV", "RetNet", "Retentive Network"]
tags: [research, rwkv, retnet, linear-attention, efficient-llm, hybrid-architectures]
sources: ["03 - RWKV and RetNet"]
created_index: 25
---

RWKV and RetNet are the alternative linear-time sequence models that preceded Mamba. RWKV combines an RNN-like recurrence — inference is $O(1)$ per token — with Transformer-like parallelism, so training is $O(N)$ and parallel across positions, while RetNet (Microsoft, 2023) uses a similar recurrence with a different formulation that its authors billed as achieving "the best of Transformer and RNN". Both demonstrated that linear-time models could match Transformer quality, paving the way for Mamba and the 2024–2025 hybrid architecture trend. This note covers how each architecture works, how they compare with Mamba, and why they matter historically; see [[Interpretability and Research MOC]] for the surrounding research area.

## RWKV

RWKV was introduced in *RWKV: Reinventing RNNs for the Transformer Era* (Peng, B., Alcaide, E., Anthony, Q., Albalak, A., Arcadinho, S., Cao, H., et al., 2023; arXiv:2305.13048). The name comes from the model's four components: R, W, K, and V. RWKV is a linear RNN that can be trained in parallel like a Transformer and inferred in $O(1)$ memory per token like an RNN. It was developed by Bo Peng and an open-source community, predating Mamba by several months.

### Linear attention as an RNN

The key idea is to recast attention as a recurrence. Standard attention is:

$$y_t = \sum_j \text{softmax}(q_t \cdot k_j) \cdot v_j$$

RWKV replaces the softmax with a linear (exponential) weighting:

$$y_t = \sum_j w_{t,j} \cdot k_j \cdot v_j$$

where $w_{t,j}$ is a decay factor that depends on the relative position $(t - j)$. This linearization allows the sum to be computed recurrently:

$$h_t = a_t \cdot h_{t-1} + k_t \cdot v_t^T$$

$$y_t = R_t \cdot h_t$$

The first equation is the state update (like an RNN) and the second is the output. The state $h$ accumulates past K·V products, weighted by position-dependent decay. This is $O(1)$ per token at inference (just update the state and read the output), but it can be parallelized during training, with all positions computed simultaneously using the attention-like formulation. This "linear attention as RNN" framing places RWKV in the same family as [[Linear Attention]], with the recurrence made explicit.

### The four components

The four namesake components divide the labor of the recurrence:

- **R (Receptance)**: controls how much of the state to use (like a gate).
- **W (Weight)**: the position-dependent decay factor.
- **K (Key)**: like attention keys.
- **V (Value)**: like attention values.

The interaction is compact: R gates the output, W decays the state, and K and V update the state.

### Why RWKV worked

Four properties made RWKV competitive. It runs in linear time: $O(N)$ training and $O(1)$ inference per token. It is parallelizable, because training uses the attention-like formulation with all positions computed at once. It avoids the quadratic attention matrix — the recurrence never materializes N×N matrices. And it is Transformer-compatible: RWKV layers can be swapped into Transformer architectures.

### Results

RWKV-4 (2023) matched comparable-size GPT-2 and small Transformers on language modeling while being faster at inference. RWKV-5 and RWKV-6 (2024) improved quality further and scaled to 14B+ parameters.

### Limitations

The W factor is a fixed function of relative position, which is less flexible than attention's content-based weighting. Like all linear-time models, RWKV underperforms attention on precise retrieval. And RWKV has a dedicated but smaller community compared to Transformer-based models.

## RetNet

RetNet was introduced in *Retentive Network: A Successor to Transformer for Large Language Models* (Sun, Y., Dong, L., Huang, B., Ma, S., Xia, X., Xue, J., et al., 2023; arXiv:2307.08621). Proposed by Microsoft in 2023 as a "successor to Transformer", it combines Transformer-quality training with RNN-quality inference efficiency. Like RWKV, it is a linear recurrence that can be parallelized for training.

### Retention

RetNet introduces "retention" — a mechanism that retains information across positions with a decay factor:

$$\text{Retention}(Q, K, V) = (Q \cdot D \cdot K^T) \cdot V$$

where $D$ is a decay matrix: $D_{i,j} = \gamma^{i-j}$ for $i \geq j$ (lower triangular), 0 otherwise. This is similar to RWKV's decay but formulated as a matrix operation.

The retention computation can be carried out in three ways:

1. **Parallel (training)**: like attention, compute the full matrix at once. $O(N^2)$ but parallelizable.
2. **Recurrent (inference)**: maintain a state $S_t = \gamma \cdot S_{t-1} + K_t^T \cdot V_t$, output $O_t = Q_t \cdot S_t$. $O(1)$ per token.
3. **Chunkwise (long sequences)**: split into chunks, use parallel within chunks and recurrent across chunks. Balances parallelism and memory.

### The three forms

The key insight is that the same computation has parallel, recurrent, and chunkwise forms, and you choose the form based on the use case. Training uses the parallel form (fast, uses GPU parallelism). Inference over short spans uses the recurrent form ($O(1)$ per token, minimal memory). Inference over long sequences uses the chunkwise form (balances parallelism and memory).

### Results

RetNet matched or exceeded same-size Transformers on language modeling while being 2–4× faster at inference. The theoretical analysis showed that RetNet's recurrence is equivalent to attention with an exponential decay — a structured attention matrix, an early anticipation of the attention/SSM unification later formalized as SSD (see [[Mamba-2 and Structured Attention]]).

### Limitations

Like RWKV, the decay is position-based, not content-based, which is less flexible than attention. Retrieval is weaker, the same limitation as all linear-time models. And adoption was limited: RetNet didn't gain the traction that Mamba did, partly because Microsoft didn't open-source large RetNet models.

## Comparing RWKV, RetNet, and Mamba

| Aspect              | RWKV              | RetNet             | Mamba                  |
|---------------------|-------------------|--------------------|------------------------|
| Released            | 2023 (community)  | 2023 (Microsoft)   | 2023 (Stanford/Princeton) |
| Selection mechanism | Fixed decay       | Fixed decay        | Input-dependent (selective) |
| Theoretical basis   | Linear attention  | Retention (structured attention) | Selective SSM |
| Inference           | $O(1)$ per token  | $O(1)$ per token   | $O(N)$ per token (parallel scan) |
| Training            | Parallel          | Parallel           | Parallel scan          |
| Open-source scale   | 14B+              | Limited            | 3B+                    |

The key difference is selectivity: Mamba's input-dependent parameters give it more flexibility than RWKV/RetNet's fixed decay. This is why [[Mamba]] outperformed RWKV/RetNet on most benchmarks and became the dominant linear-time architecture.

## Why RWKV and RetNet matter

### They pioneered linear-time LLMs

RWKV and RetNet demonstrated that linear-time models could match Transformer quality before Mamba did, establishing the conceptual foundation that Mamba built upon.

### They showed the RNN/attention connection

Both showed that RNNs and attention are related — attention is a parallel form of an RNN with specific decay. This insight, later formalized by Mamba-2's SSD, originated with RWKV and RetNet.

### They have active communities

RWKV has a dedicated open-source community that continues to develop the architecture (RWKV-6, RWKV-7). While smaller than the Transformer ecosystem, it produces competitive models for specific use cases.

### They influenced hybrid architectures

The demonstration that linear-time models work motivated the hybrid architecture trend. The reasoning: if pure linear models are 90% as good as attention, then hybrids (linear + a little attention) can be 99% as good at half the cost — the bet behind hybrid models like [[Jamba]].

## Limitations of the linear-time approach

### Fixed decay is less expressive

RWKV and RetNet use position-based decay — the same decay applies to all tokens at a given relative position. This can't represent content-dependent relationships ("attend more to the noun, less to the verb"). Mamba's selectivity addressed this weakness; RWKV-6 added some selectivity later.

### Retrieval weakness

Like all linear-time models, RWKV and RetNet underperform attention on precise retrieval tasks. The state accumulates information but can't selectively retrieve specific facts as precisely as attention does.

### Memory decay

The exponential decay means old information is gradually forgotten. For tasks requiring exact recall of distant information, this is a limitation: attention retains all information equally, while linear models decay it.

## Impact and legacy

RWKV and RetNet's influence runs through four channels. They pioneered linear-time LLMs, proving the concept before Mamba and establishing that linear-time models could be competitive. They influenced Mamba's design: Mamba's selective mechanism was a direct response to RWKV/RetNet's fixed-decay limitation, and the progression RWKV → RetNet → Mamba → Mamba-2 is a clear lineage.

They also sustain an active open-source ecosystem: RWKV continues to be developed by its community, with models competitive in specific niches (especially efficient inference). And they informed the hybrid architecture trend — the demonstration that linear-time models work, with known limitations, motivated hybrids that combine linear efficiency with attention retrieval, the trajectory traced in [[SSMs Mamba and Frontiers]].

For AI engineers, RWKV and RetNet are mostly of historical interest — Mamba-2 and hybrid architectures have largely superseded them. But understanding the RWKV/RetNet/Mamba progression clarifies how the field arrived at current linear-time architectures and what trade-offs they make.

## Further reading

The primary sources for this line of work:

- RWKV paper: arXiv:2305.13048
- RWKV project: github.com/BlinkDL/RWKV-LM
- RetNet paper: arXiv:2307.08621

## See also

- [[Interpretability and Research MOC]] — the area orientation for interpretability and research.
- [[SSMs Mamba and Frontiers]] — the broader state-space lineage.
- [[Mamba-2 and Structured Attention]] — the SSD unification of attention and recurrence.
- [[Hyena and Long Convolutions]] — the convolutional branch of sub-quadratic sequence mixing.
- [[Long-Context Architectures]] — where linear-time cost pays off.
- [[DeltaNet and Titans]] — later linear-time successors.
- [[Mamba]] — the successor that dominated.
- [[Linear Attention]] — the attention-family relative of RWKV's formulation.
- [[Jamba]] — the hybrid trend these models motivated.
