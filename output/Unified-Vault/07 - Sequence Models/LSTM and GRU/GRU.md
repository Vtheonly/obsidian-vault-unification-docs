---
title: GRU
type: concept
aliases:
  - Gated Recurrent Unit
  - Gated Recurrent Units
  - GRU cell
  - Simplifying the LSTM
tags:
  - gru
  - gated-recurrent-unit
  - recurrent-neural-networks
  - sequence-models
  - update-gate
  - reset-gate
sources:
  - "02. GRU — Simplifying the LSTM"
created_index: "02"
---

The Gated Recurrent Unit (GRU) is a gated recurrent cell that strips the [[LSTM]] down to its essential machinery: two gates instead of three, and a single state that serves as both memory and output. Introduced by Cho et al. in 2014, it costs roughly 3× the parameters of a vanilla RNN (versus the LSTM's 4×), and empirically it matches or slightly beats LSTMs on many tasks at a lower computational cost. Its update rule still provides a gradient highway, so it solves [[07 - Sequence Models/Motivation and Recurrence/Vanishing and Exploding Gradients|vanishing gradients]] just as the LSTM does.

## The motivation

The LSTM works, but it has three gates, a separate cell state, and ~4× the parameters of a vanilla RNN. In 2014, Cho et al. asked: **how much of this machinery is actually necessary?** Their answer was the **Gated Recurrent Unit (GRU)**, which makes three structural moves. It merges the forget and input gates into a single **update gate**. It drops the separate cell state — there is only one state, $h_t$, which serves as both memory and output. And it merges the output gate's role into a **reset gate** that controls how much of the previous state to use when computing the candidate.

The result is a cell with **two gates instead of three** and **one state instead of two**, at ~3× the parameter cost of a vanilla RNN (vs the LSTM's 4×). Empirically, GRUs match or slightly beat LSTMs on many tasks at a lower computational cost.

## The GRU equations

$$z_t = \sigma(W_z \cdot [h_{t-1}, x_t] + b_z) \quad \text{(update gate)}$$
$$r_t = \sigma(W_r \cdot [h_{t-1}, x_t] + b_r) \quad \text{(reset gate)}$$
$$\tilde{h}_t = \tanh(W \cdot [r_t \odot h_{t-1}, x_t] + b) \quad \text{(candidate state)}$$
$$h_t = (1 - z_t) \odot h_{t-1} + z_t \odot \tilde{h}_t \quad \text{(new state)}$$

### What each piece does

The **update gate $z_t$** is the merged forget+input gate. In the LSTM, $f_t$ decided how much to keep and $i_t$ decided how much to write, and they were independent. In the GRU, $z_t$ plays both roles at once via the $(1-z_t) \odot h_{t-1} + z_t \odot \tilde{h}_t$ form: keeping the old and writing the new are forced to sum to 1, so "keep more" automatically means "write less." This is a constraint the LSTM does not impose, and it is the main structural simplification.

The **reset gate $r_t$** controls how much of the previous state to use when computing the candidate $\tilde{h}_t$. When $r_t \to 0$, the candidate is computed from the current input alone, effectively "forgetting" the past for this step's candidate. When $r_t \to 1$, the candidate is computed from the full previous state plus input.

The **candidate $\tilde{h}_t$** is what the network would *like* the new state to be, computed from a reset-gate-filtered view of the past plus the current input. The **new state $h_t$** is the convex combination of old state and candidate, weighted by the update gate.

## The key structural difference from LSTM

Look at the final update:

$$h_t = (1 - z_t) \odot h_{t-1} + z_t \odot \tilde{h}_t$$

The gradient $\partial h_t / \partial h_{t-1}$ has a term $(1 - z_t)$ from the additive path — exactly analogous to the LSTM's $f_t$ on the cell state. So the GRU *also* has a gradient highway, just routed through $h_t$ directly rather than through a separate $C_t$.

The difference is that in the LSTM, the highway ($C_t$) and the output ($h_t$) are decoupled — the output gate can hide the cell state's contents from the rest of the network while still letting the cell state accumulate. In the GRU, the highway *is* the output: whatever the GRU stores in $h_t$ is also what it exposes. This is slightly less flexible but removes a gate's worth of parameters.

## When the simplification helps and when it hurts

The GRU's simplification is preferable in three situations. On **smaller datasets**, fewer parameters means less overfitting — on text-classification tasks with <100k samples, GRUs often outperform LSTMs. On **shorter sequences**, when the relevant dependencies are within ~50 steps, the GRU's highway is sufficient and the LSTM's extra flexibility is wasted overhead. And in **latency-sensitive deployment**, the 25% parameter reduction translates directly to faster inference, which matters for real-time translation and speech recognition.

The LSTM keeps the edge in two situations. On **very long sequences**, the decoupled cell state lets the LSTM maintain information that is not currently relevant but will be needed later — on music generation, long-document summarization, and character-level language modeling with sequences of 1000+ steps, LSTMs tend to edge out GRUs. And on **tasks requiring "silent memory"**, if the network needs to remember something for a long time without that memory affecting intermediate outputs, the LSTM's output gate can suppress the cell state's contribution to $h_t$ while $C_t$ keeps accumulating. The GRU cannot do this — anything in $h_t$ is also in the output.

## The empirical reality

A much-cited 2017 study (Jozefowicz et al., "An Empirical Exploration of Recurrent Network Architectures") ran a large-scale comparison of RNN variants across many tasks. The headline finding: **on most tasks, the difference between LSTM and GRU is within noise.** The right choice is usually task-dependent and best determined by validation, not by theory. The theoretical differences above are real but small in practice.

The practical advice: **start with GRU** (cheaper, faster to train, easier to tune) and **switch to LSTM** only if the GRU plateaus on a task that you suspect requires longer-range memory than the GRU can provide.

## Key takeaways

Five points summarize the design. The GRU merges the LSTM's forget+input gates into a single update gate $z_t$, and drops the separate cell state. The update $h_t = (1-z_t) \odot h_{t-1} + z_t \odot \tilde{h}_t$ still provides a gradient highway (the $(1-z_t)$ term), so the GRU also solves vanishing gradients. The cost is ~3× a vanilla RNN (vs 4× for LSTM) — a useful saving. The main structural loss vs LSTM is that the highway *is* the output, so the GRU cannot silently accumulate memory the way an LSTM can. And in practice, LSTM and GRU perform similarly on most tasks — start with the GRU, and switch to the LSTM only if you need very long-range or silent memory. The [[LSTM vs GRU]] note works through the selection decision in detail.

## See also

- [[07 - Sequence Models/Chapter Overview|Chapter Overview]]
- [[LSTM]] — the architecture being simplified
- [[LSTM vs GRU]] — when to use which
- [[07 - Sequence Models/Motivation and Recurrence/Vanishing and Exploding Gradients|Vanishing and Exploding Gradients]] — the problem both gated cells solve
- [[The Recurrent Neuron]] — the unguarded baseline both designs improve on
- [[The Encoder-Decoder Pattern]] — where these gated cells are used in practice
