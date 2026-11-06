---
title: Whisper
type: concept
aliases: [Whisper, OpenAI Whisper, Speech Recognition, ASR Transformer]
tags: [multimodal, whisper, speech, asr, audio]
sources: ["04 — Whisper"]
created_index: 13
---

> [!info] TL;DR
> Whisper is OpenAI's speech-to-text model, trained on 680,000 hours of multilingual audio-transcript pairs scraped from the web. It uses a standard encoder-decoder Transformer, with the audio converted to a log-Mel spectrogram as input. Whisper achieves near-human accuracy on speech recognition across 99 languages, with strong robustness to accents, background noise, and technical jargon. It became the default open-source ASR model and is deployed in production by countless applications.

Whisper is OpenAI's open-source speech-to-text model and, since its release, the default choice for automatic speech recognition (ASR) across the ecosystem. Its contribution is not architectural novelty but a data strategy: a vanilla encoder-decoder Transformer trained on 680,000 hours of noisy, web-scraped audio-transcript pairs turned out to be enough for robust, multilingual transcription. This note covers the problem Whisper solved, its architecture and multitask token format, the training data, the benchmark results, why the approach worked, its limitations, and the variant ecosystem that grew around it.

## The problem being solved

Before Whisper, automatic speech recognition was dominated by specialized models trained on narrow datasets (LibriSpeech, Common Voice). These models worked well on clean, accented-less English, but they failed on accents, background noise, or non-standard speech; they required language-specific models for each language; and they needed fine-tuning for domain-specific vocabulary (medical, legal, technical).

The fundamental issue: supervised ASR data is expensive to collect (human transcribers), so datasets were small and narrow. This limited model capability and robustness.

Whisper's approach: use **weak supervision** from web data. Millions of hours of audio on YouTube, podcasts, and other platforms come with transcripts (subtitles, captions). These transcripts are noisy (auto-generated, incomplete, mistimed), but they're free and cover diverse languages, accents, and topics. By training on this large, diverse, noisy dataset, Whisper learned robust speech recognition without expensive human-labeled data.

## Architecture

Whisper uses a standard encoder-decoder Transformer — no novel architecture, just scale and data.

### Input processing

The audio front-end converts the raw waveform into a sequence the encoder can consume:

1. **Audio sampling**: 16 kHz mono audio.
2. **Spectrogram conversion**: compute an 80-channel log-Mel spectrogram with 10ms windows.
3. **Convolutional downsampling**: two conv layers reduce the spectrogram length by 2× (to 50ms per frame).
4. **Positional encoding**: sinusoidal, added to the spectrogram features.

After these steps the spectrogram is just another sequence of feature vectors, and everything downstream is a plain Transformer.

### Encoder

The encoder is a standard Transformer encoder with no vision- or audio-specific components. It takes the spectrogram sequence and produces hidden states. The same design ships at several sizes:

| Model    | Encoder layers | Decoder layers | Hidden | Heads | Params |
|----------|----------------|----------------|--------|-------|--------|
| Tiny     | 4              | 4              | 384    | 6     | 39M    |
| Base     | 6              | 6              | 512    | 8     | 74M    |
| Small    | 12             | 12             | 768    | 12    | 244M   |
| Medium   | 24             | 24             | 1024   | 16    | 769M   |
| Large    | 32             | 32             | 1280   | 20    | 1550M  |
| Large-v2 | 32             | 32             | 1280   | 20    | 1550M  |
| Large-v3 | 32             | 32             | 1280   | 20    | 1550M  |

### Decoder

The decoder is likewise a standard Transformer decoder. It takes the encoder's hidden states (via cross-attention, the audio-to-text bridge — see [[Cross-Modal Attention]]) and the previously-generated tokens (via self-attention), and generates the transcript autoregressively. Whisper's task flexibility lives entirely in the token stream, where special tokens control behavior:

- `<|startoftranscript|>` — begins generation.
- `<|en|>` (or other language codes) — sets the output language.
- `<|translate|>` — translates non-English audio to English text.
- `<|transcribe|>` — transcribes in the original language.
- `<|notimestamps|>` or timestamp tokens — controls timestamp generation.

The full pipeline from waveform to generated token:

```mermaid
graph LR
  Audio[Audio: 16kHz mono] --> Mel[Log-Mel spectrogram: 80 channels]
  Mel --> Conv[Conv downsampling]
  Conv --> Enc[Transformer Encoder]
  Enc --> Cross[Cross-attention]
  Tokens[Generated tokens so far] --> Dec[Transformer Decoder]
  Cross --> Dec
  Dec --> Next[Next token]
```

## The multitask format

Whisper frames ASR as a multitask problem: the decoder's first tokens determine the task.

- **Transcription**: `<|en|> <|transcribe|> <|notimestamps|> [transcript]`
- **Translation**: `<|en|> <|translate|> <|notimestamps|> [English translation]`
- **Language ID**: `<|startoftranscript|> [detected language code] ...`
- **Timestamps**: include timestamp tokens to align transcript with audio.

This unified format means a single model handles transcription, translation, language identification, and timestamping — all through the decoder's token sequence.

## Training data

Whisper was trained on 680,000 hours of audio-transcript pairs: 438,000 hours of English audio (YouTube, podcasts) and 242,000 hours of audio in 98 other languages.

The data is "weakly supervised" — transcripts are auto-generated or crowd-sourced, not professionally transcribed. In practice this means some transcripts are inaccurate or incomplete, some audio-transcript pairs are misaligned, and quality varies wildly across the dataset.

Whisper's robustness comes from this diversity: the model sees enough varied (if noisy) data to generalize across accents, noise conditions, and languages.

## Key results

Whisper achieved state-of-the-art zero-shot ASR performance:

| Benchmark               | Previous SOTA | Whisper Large |
|-------------------------|---------------|---------------|
| LibriSpeech (WER)       | 1.8%          | 1.9%          |
| Common Voice (WER, avg) | ~15%          | 9.1%          |
| Fleurs (WER, avg)       | ~20%          | 11.2%         |
| CallHome (WER)          | ~30%          | 19.4%         |

Three observations stand out. On clean English (LibriSpeech), Whisper matched specialized models. On noisy and multilingual data (Common Voice, Fleurs, CallHome), Whisper significantly outperformed specialized models — this is where the diverse training data paid off. And Whisper achieved usable accuracy on languages with very little training data (low-resource languages), demonstrating transfer from related languages.

## Why it worked

### Scale and diversity of data

680K hours of audio across 99 languages provided enough diversity for the model to learn robust speech recognition. The noise in the data was outweighed by the coverage.

### Sufficiency of weak supervision

The transcripts didn't need to be perfect — they needed to be "good enough" on average. The model learned to recognize speech patterns from the audio, with the transcripts providing the target signal. Noisy targets degraded quality somewhat, but the scale compensated.

### A standard architecture without specialized components

Whisper's architecture is a vanilla Transformer encoder-decoder. There is no specialized audio processing beyond the spectrogram, and no specialized attention mechanisms. The simplicity made the model easy to train, deploy, and fine-tune.

### The multitask format as a unifier

The token-based multitask format let one model handle transcription, translation, and language ID. This unified approach is more efficient than training separate models for each task.

## Limitations

### No real-time streaming (originally)

Whisper processes the entire audio at once. Real-time applications (live transcription, voice assistants) require streaming adaptations; Faster-Whisper and whisper.cpp added streaming support.

### Hallucination

On silent or noisy audio, Whisper can "hallucinate" transcripts — generating text that wasn't spoken. This is a known issue with the model, and it is the same failure mode discussed for text models in [[Hallucination]].

### Language-specific quality

While Whisper covers 99 languages, quality varies dramatically. English and other high-resource languages have low WER; low-resource languages (African, indigenous) have much higher WER.

### Domain shift

Whisper trained on web data may underperform on highly specialized domains (medical dictation, legal proceedings) with domain-specific vocabulary. Fine-tuning on domain data addresses this.

### Thirty-second segments

Whisper processes audio in 30-second chunks. Long files require chunking, which can cause boundary artifacts. Specialized chunking strategies (VAD-based, sliding window) mitigate this.

## Successors and variants

### Large-v2 and Large-v3

Improved training data and slight architectural tweaks, with better performance on more languages.

### Faster-Whisper

A CTranslate2-based implementation, 4× faster than the original with minimal quality loss. It is the standard for production deployment.

### whisper.cpp

A C++ implementation by Georgi Gerganov (creator of llama.cpp). It runs on CPU, including mobile devices, which enables on-device ASR.

### Distil-Whisper

Distilled versions that are 6× faster with ~1% WER increase, aimed at high-throughput applications.

### WhisperX

Adds word-level timestamps, speaker diarization, and improved accuracy via forced alignment with phoneme models.

## Impact and legacy

Whisper transformed speech recognition in five distinct ways:

1. **Default open-source ASR**. Whisper is the standard for open-source speech recognition; most applications that need ASR use Whisper or a derivative.
2. **Multilingual ASR accessible**. Before Whisper, multilingual ASR required language-specific models; Whisper made 99 languages accessible from a single model.
3. **Enabled voice applications**. Voice assistants, transcription services, podcast indexing, and video subtitle generation all became dramatically better and cheaper with Whisper.
4. **On-device ASR**. whisper.cpp and similar implementations run on phones and laptops, enabling privacy-preserving voice processing without cloud dependency.
5. **Weak supervision as a paradigm**. Whisper demonstrated that weakly supervised training on web data can match or exceed fully supervised training, given enough scale — and this influenced other domains (vision, text) to leverage web-scale noisy data.

For AI engineers, Whisper is the go-to ASR model. If you need speech-to-text in an application, Whisper (specifically Faster-Whisper or whisper.cpp) is almost certainly the right choice. Understanding Whisper clarifies how to deploy ASR, what performance to expect, and how to handle multilingual or domain-specific needs.

## Citation and further reading

The original paper is Radford, A., Kim, J. W., Xu, T., Brockman, G., McLeavey, C., & Sutskever, I. (2023). *Robust Speech Recognition via Large-Scale Weak Supervision*. ICML 2023. arXiv:2212.04356. For the variant ecosystem: Faster-Whisper lives at github.com/SYSTRAN/faster-whisper, whisper.cpp at github.com/ggerganov/whisper.cpp, and Distil-Whisper is described in arXiv:2310.16086.

## See also

- [[Foundation Models and Multimodal MOC]] — the orientation note for this area.
- [[Multimodal AI Overview]] — where Whisper sits in the multimodal landscape.
- [[Multimodal Foundation Models]] — the broader family of web-scale foundation models Whisper belongs to.
- [[CLIP]] — OpenAI's contrastive vision-language model, the other web-scale success from the same lab.
- [[Cross-Modal Attention]] — the encoder-decoder cross-attention pattern Whisper's decoder relies on.
- [[LLaVA]] — the analogous open-source template on the vision-language side.
- [[Hallucination]] — the failure mode behind Whisper's hallucinated transcripts on silent audio.
- [[Attention Is All You Need]]
