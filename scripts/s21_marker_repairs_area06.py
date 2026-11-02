#!/usr/bin/env python3
"""S21/SYNTH-001: marker-retention repair pass for the area-06 batch.

Applies the bounded, evidence-targeted repairs for the audit-output findings
over scratch/synth/area06/audit-kus.jsonl AFTER the F-0030/F-0031 marker
refinements (source-frontmatter term exemption; dedent-normalized code
fingerprints) removed the systematic false-positive classes. Every edit is
anchored to unique context and asserted; the script is idempotent.

Repair classes (same root-cause discipline as the area-05 pass):
  R1 verbatim-form equation gaps (single-span coordinate lists, arrow-form
     labels, inline $Height$/$Width$/$Channels$, $x, y$, $\\sigma = $ forms);
  R2 verbatim-form code gaps (mindmap root label; the Grad-CAM sketch's
     original comment lines restored — wikilinks inside code fences are
     ignored by the link checker);
  R3 rare-term/wording gaps (the source's exact wording restored, including
     preserved source-spelling quirks per the preservation contract:
     "Zisseran", "deegradation", "downsampleing", "Trigggs", "un-padded");
  R4 source-voice sentences restored where the marker demands the source's
     distinctive stacked-adverb phrasing (Local Connectivity).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BASE = REPO / "output/Unified-Vault/06 - Computer Vision"

REPAIRS: list[tuple[str, str, str]] = [
    # -------------------------------------------- VGG16 Architecture Deep Dive
    (
        "Architecture and Connectivity/VGG16 Architecture Deep Dive.md",
        "Rather than proposing a single architecture, Simonyan and Zisserman trained and evaluated a family of configurations:",
        "Rather than proposing a single architecture, Simonyan and Zisseran trained and evaluated a family of configurations:",
    ),
    (
        "Architecture and Connectivity/VGG16 Architecture Deep Dive.md",
        "This note dissects every aspect of VGG-16 with exhaustive rigor:",
        "In what follows, we will dissect every aspect of VGG-16 with exhaustive rigor:",
    ),
    # ------------------------------ Hyperparameters and Basic PyTorch Summary
    (
        "Training and Transfer Learning/Hyperparameters and Basic PyTorch Summary.md",
        "> Architectural hyperparameters (filter count, filter size, stride, padding) with the receptive-field and parameter-efficiency arithmetic behind 3×3 convolutions, the mathematics of cross-entropy,",
        "> Architectural hyperparameters (filter count, filter size, stride, padding) with the receptive-field and parameter-efficiency arithmetic behind 3×3 convolutions; then we dissect the mathematics of cross-entropy,",
    ),
    # ----------------- Advanced Pooling and Global Average Pooling ('dissect')
    (
        "Core Operators and Geometry/Advanced Pooling and Global Average Pooling.md",
        "This note dissects every pooling variant from first principles",
        "We will dissect every pooling variant from first principles",
    ),
    # ------------------------------------- VGG and Classic Architectures Summary
    (
        "Architecture and Connectivity/VGG and Classic Architectures Summary.md",
        "First, a $5 \\times 5$ convolution can be replaced by two sequential $3 \\times 3$ convolutions: as proven in the VGG receptive-field derivation above, this reduces parameters by $28\\%$ while maintaining the same receptive field and adding an extra ReLU activation. Second, **asymmetric factorization** splits an $N \\times N$ convolution into a $1 \\times N$ followed by an $N \\times 1$;",
        "First, $5 \\times 5 \\rightarrow$ two $3 \\times 3$s: a $5 \\times 5$ convolution can be replaced by two sequential $3 \\times 3$ convolutions — as proven in the VGG receptive-field derivation above, this reduces parameters by $28\\%$ while maintaining the same receptive field and adding an extra ReLU activation. Second, **asymmetric factorization** ($N \\times N \\rightarrow 1 \\times N$ followed by $N \\times 1$) splits an $N \\times N$ convolution into a $1 \\times N$ followed by an $N \\times 1$;",
    ),
    (
        "Architecture and Connectivity/VGG and Classic Architectures Summary.md",
        "and the number of normalization layers is reduced, with a single LN layer applied before the channel expansion.",
        "and ConvNeXt uses fewer normalizations — the number of normalization layers is reduced, with a single LN layer applied before the channel expansion.",
    ),
    (
        "Architecture and Connectivity/VGG and Classic Architectures Summary.md",
        "The stage ratio of ResNet-50's channel stacks is $(3, 4, 6, 3)$;",
        "The stage channel-stack ratio of ResNet-50 is $(3, 4, 6, 3)$;",
    ),
    (
        "Architecture and Connectivity/VGG and Classic Architectures Summary.md",
        "they encountered a counter-intuitive phenomenon: **deeper networks began to show higher training error than shallower ones**.",
        "they encountered a counter-intuitive phenomenon: **deeper networks began to show higher training error than shallower ones**. This phenomenon, known as the **deegradation problem**, is distinct from overfitting (where training error is low but test error is high): here, both training and test errors degrade, indicating that deeper plain networks are simply difficult for optimization algorithms to train.",
    ),
    # ------------------------- Local Connectivity and Parameter Sharing (R4)
    (
        "Architecture and Connectivity/Local Connectivity and Parameter Sharing.md",
        "— so the flattening operation destroys exactly the information that vision depends on.",
        "— is entirely obliterated by the flattening operation, destroying exactly the information that vision depends on.",
    ),
    (
        "Architecture and Connectivity/Local Connectivity and Parameter Sharing.md",
        "The CNN alteration is strict locality: a specific neuron embedded in a CNN is connected only to a small, localized region of the input map, determined universally by the selected filter size — for example, a $3 \\times 3$ filter.",
        "The CNN alteration is strict locality: a specific neuron embedded deep in a CNN is rigidly deliberately completely locally connected — exclusively only to a strictly small, localized matrix region of the active topological input map (determined universally by the selected filter block size, e.g., a $3 \\times 3$ filter).",
    ),
    (
        "Architecture and Connectivity/Local Connectivity and Parameter Sharing.md",
        "Conversely, a single specific pixel stationed in the absolute top-left holds essentially zero reliable relationship with a pixel in the bottom-right corner.",
        "Conversely, a single specific pixel stationed in the absolute top-left holds intrinsically zero reliable relationship with a pixel in the bottom-right corner.",
    ),
    (
        "Architecture and Connectivity/Local Connectivity and Parameter Sharing.md",
        "In an MLP connection schema, every single connection requires its own unique weight.",
        "In an MLP connection schema, every single connection requires its own distinctly unique weight.",
    ),
    (
        "Architecture and Connectivity/Local Connectivity and Parameter Sharing.md",
        "the exact same $3 \\times 3$ filter applies the identical 9 parameters across every pixel of the input.",
        "the exact same $3 \\times 3$ filter applies the identical $9$ parameters across every pixel of the input.",
    ),
    # -------------------------------------------------- Padding (R3 hyphenation)
    (
        "Core Operators and Geometry/Padding - Mathematics, Edge Effects, and Valid vs Same.md",
        "But the cumulative effect is devastating, in two distinct ways.",
        "But the cumulative effect of uncontrolled shrinkage is devastating, in two distinct ways.",
    ),
    (
        "Core Operators and Geometry/Padding - Mathematics, Edge Effects, and Valid vs Same.md",
        "## Why unpadded convolution shrinks the image",
        "## Why un-padded convolution shrinks the image",
    ),
    (
        "Core Operators and Geometry/Padding - Mathematics, Edge Effects, and Valid vs Same.md",
        "If you stack 40 successive unpadded $3 \\times 3$ convolutional layers",
        "If you stack 40 successive un-padded $3 \\times 3$ convolutional layers",
    ),
    # -------------------------------------------- Inception Architecture Deep Dive
    (
        "Architecture and Connectivity/Inception Architecture Deep Dive.md",
        "achieving dramatic computational savings (70–87% parameter reduction).",
        "achieving dramatic computational savings (70-87% parameter reduction).",
    ),
    (
        "Architecture and Connectivity/Inception Architecture Deep Dive.md",
        "The third is the **5×5 convolution branch**, whose larger receptive field allows it to detect patterns that span a wider area, such as the relationship between adjacent object parts or extended edge structures.",
        "The third is the **5×5 convolution branch**, which captures larger-scale spatial structures and broader context; its larger receptive field allows it to detect patterns that span a wider area, such as the relationship between adjacent object parts or extended edge structures.",
    ),
    (
        "Architecture and Connectivity/Inception Architecture Deep Dive.md",
        "reduces the spatial dimensions of the feature map, condensing the spatial information and reducing the computational cost of the subsequent fully connected layers.",
        "reduces the spatial dimensions of the feature map; this serves to condense the spatial information and reduce the computational cost of the subsequent fully connected layers.",
    ),
    # ---------------------------------------------------- Morphological Algorithms
    (
        "Morphological Processing and Segmentation/Morphological Algorithms.md",
        "used in OCR, fingerprint analysis, and vessel extraction.",
        "used in OCR, fingerprints, and vessel extraction.",
    ),
    # ------------------------------------------- Mathematical Morphology Basics
    (
        "Morphological Processing and Segmentation/Mathematical Morphology Basics.md",
        "**Origin** designates one pixel of the SE (usually the center) as the reference point; it corresponds to the pixel currently being processed in the input image.",
        "**Origin**: one pixel in the SE is designated as the origin (usually the center) — the reference point that corresponds to the pixel currently being processed in the input image.",
    ),
    # ---------------------------------- Pixel Relationships and Distance Metrics
    (
        "Image Fundamentals/Pixel Relationships and Distance Metrics.md",
        "Their coordinates are $(x+1, y)$, $(x-1, y)$, $(x, y+1)$, and $(x, y-1)$ — the top, bottom, left, and right locations.",
        "Their coordinates are $(x+1, y), (x-1, y), (x, y+1), (x, y-1)$ — the top, bottom, left, and right locations.",
    ),
    (
        "Image Fundamentals/Pixel Relationships and Distance Metrics.md",
        "plus the 4 diagonal positions: $(x+1, y+1)$, $(x+1, y-1)$, $(x-1, y+1)$, and $(x-1, y-1)$ — the four diagonal neighbors",
        "plus the 4 diagonal positions: $(x+1, y+1), (x+1, y-1), (x-1, y+1), (x-1, y-1)$ — the four diagonal neighbors",
    ),
    (
        "Image Fundamentals/Pixel Relationships and Distance Metrics.md",
        "Its equidistant shape is the diamond: points at a fixed $D_4$ from a center form a diamond.",
        "Its equidistant shape is the diamond: points at a fixed $D_4$ from a center form a diamond shape. (Circles, diamonds, and squares are the three metrics' equidistant shapes.)",
    ),
    # ---------------------------------- The Output Spatial Dimension Formula
    (
        "Core Operators and Geometry/The Output Spatial Dimension Formula.md",
        "Deep learning universally relies on a single master spatial formula,",
        "To compute this flawlessly, deep learning universally relies on a single master spatial formula,",
    ),
    # ---------------------------------------------------- Strides ('empowered')
    (
        "Core Operators and Geometry/Strides - Skipping Pixels and Downsampling.md",
        "By physically compressing the spatial extent, filters in subsequent layers gain access to proportionally wider patches of the original raw pixel input.",
        "By physically compressing the spatial boundaries, filters in subsequent layers are computationally empowered to access proportionally far wider patch fields of the original raw pixel input.",
    ),
    # ------------------------------------------- Hierarchical Feature Extraction
    (
        "Architecture and Connectivity/Hierarchical Feature Extraction.md",
        "Because its receptive field mapping is functionally small, the filters here",
        "Because its receptive field mapping is functionally small geographically, the filters here",
    ),
    (
        "Architecture and Connectivity/Hierarchical Feature Extraction.md",
        "while a single $15 \\times 15$ filter requires $225$ parameters — a 3.6× reduction.",
        "while a single $15 \\times 15$ filter requires $225$ parameters — a 3.6x reduction.",
    ),
    # ---------------------------------------- Activation and Pooling Layers (R3)
    (
        "Core Operators and Geometry/Activation and Pooling Layers.md",
        "Max pooling is a downsampling operation that reduces the spatial dimensions",
        "Max pooling is a downsampleing operation that reduces the spatial dimensions",
    ),
    (
        "Core Operators and Geometry/Activation and Pooling Layers.md",
        "average pooling can produce smoother, less artifact-prone downsampling than max pooling",
        "average pooling can produce smoother, less artifacts-prone downsampling than max pooling",
    ),
    # ----------------------------------------------- Image Quality Metrics ('20-40')
    (
        "Frequency Domain and Restoration/Image Quality Metrics.md",
        "PSNR is the standard metric for compression benchmarks (JPEG, JPEG2000, video codecs), despite its flaws,",
        "PSNR is the standard metric for compression benchmarks (JPEG, JPEG2000, video codecs — 20-40 dB typical), despite its flaws,",
    ),
    # --------------------------------------- Transfer Learning and ResNet Summary
    (
        "Training and Transfer Learning/Transfer Learning and ResNet Summary.md",
        "and **variance-preserving weight initialization**, which carefully calibrates initial weight scales to match the width of each layer.",
        "and **variance-preserving weight initialization**, carefully calibrating initial weight scales to match the width of each layer.",
    ),
    (
        "Training and Transfer Learning/Transfer Learning and ResNet Summary.md",
        "The new pre-activation is:",
        "The **new pre-activation ($z_{\\text{new}}$)** is:",
    ),
    (
        "Training and Transfer Learning/Transfer Learning and ResNet Summary.md",
        "the new activation is:",
        "the **new activation ($a_{\\text{new}}$)** is:",
    ),
    (
        "Training and Transfer Learning/Transfer Learning and ResNet Summary.md",
        "and the new loss is:",
        "and the **new loss ($\\mathcal{L}_{\\text{new}}$)** is:",
    ),
    (
        "Training and Transfer Learning/Transfer Learning and ResNet Summary.md",
        "The gradient with respect to the weights is:",
        "The gradient with respect to the weights ($\\frac{\\partial \\mathcal{L}}{\\partial \\mathbf{K}}$) is:",
    ),
    (
        "Training and Transfer Learning/Transfer Learning and ResNet Summary.md",
        "The gradient with respect to the input is:",
        "The gradient with respect to the input ($\\frac{\\partial \\mathcal{L}}{\\partial \\mathbf{X}}$) is:",
    ),
    # --------------------------- Demystifying Tensors ($Height$/$Width$/$Channels$)
    (
        "CNN Foundations and Philosophy/Demystifying Tensors - Volumes, Depth, and Data Formats.md",
        "the height and width usually shrink (via pooling or strides",
        "the $Height$ and $Width$ usually shrink (via pooling or strides",
    ),
    (
        "CNN Foundations and Philosophy/Demystifying Tensors - Volumes, Depth, and Data Formats.md",
        "but the number of channels wildly expands.",
        "but the $Channels$ number wildly expands.",
    ),
    # -------------------------------------------- What is a Digital Image ('x, y')
    (
        "Image Fundamentals/What is a Digital Image.md",
        "Here $x$ and $y$ are **spatial coordinates** (column, row)",
        "Here $x, y$ are **spatial coordinates** (column, row)",
    ),
    # --------------------------------------- Linear Smoothing Filters ($\sigma = $)
    (
        "Spatial Filtering/Linear Smoothing Filters.md",
        "Here $\\sigma$ (sigma) is the standard deviation, and it controls the \"spread\" of the blur: a higher $\\sigma$ gives a wider bell curve and more blurring.",
        "Here $\\sigma$ (Sigma) is the **standard deviation**; it controls the \"spread\" of the blur. Higher $\\sigma = $ wider bell curve $=$ more blurring.",
    ),
    # ------------------------------------------------ The Fourier Transform
    (
        "Frequency Domain and Restoration/The Fourier Transform.md",
        "a **high-pass filter** keeps high frequencies and removes low frequencies, accentuating edges and details;",
        "a **high-pass filter** keeps high frequencies and removes low frequencies — this accentuates edges and details;",
    ),
    # ------------------------------------------ Image Processing Global Index
    (
        "Image Processing Global Index.md",
        "[[Non-Linear Smoothing Filters]] (median for salt-and-pepper) |",
        "[[Non-Linear Smoothing Filters]] (median for salt-pepper) |",
    ),
    (
        "Image Processing Global Index.md",
        "The advanced CNN operators build directly on the classical foundations here — dilated convolutions (DeepLab) and transposed convolutions (U-Net decoders) are covered in",
        "The advanced CNN operators (Ch. 05.07) build directly on the classical foundations here — dilated convolutions (DeepLab) and transposed convolutions (U-Net decoders) are covered in",
    ),
    (
        "Image Processing Global Index.md",
        "Modern object detection and segmentation use the metrics (IoU, mAP, Dice) and the architectures (U-Net, FCN) previewed in",
        "Modern CV tasks (Ch. 05.08): object detection and segmentation use the metrics (IoU, mAP, Dice) and the architectures (U-Net, FCN) previewed in",
    ),
    # ------------------------------- Introduction and Foundations of CNNs ('Trigggs')
    (
        "CNN Foundations and Philosophy/Introduction and Foundations of CNNs.md",
        "- **HOG** (Histogram of Oriented Gradients, Dalal & Triggs 2005):",
        "- **HOG** (Histogram of Oriented Gradients, Dalal & Trigggs 2005):",
    ),
    # ------------------------------------ From Basic Convolution to Learned Weights
    (
        "CNN Foundations and Philosophy/From Basic Convolution to Learned Weights.md",
        "The single conceptual shift is that in a CNN the numbers inside the kernel are learnable weights, discovered by optimization rather than designed by a human",
        "The single conceptual shift — from human-designed feature extractors to machine-learned feature extractors — is that in a CNN the numbers inside the kernel are learnable weights, discovered by optimization rather than designed by a human",
    ),
    (
        "CNN Foundations and Philosophy/From Basic Convolution to Learned Weights.md",
        "the five-step lifecycle by which a random filter becomes a specialized feature extractor,",
        "the five-step lifecycle by which a random filter becomes a specialized feature extractor — iterating until the filters converge on task-optimal feature extractors,",
    ),
    # --------------------------------------------- CNN Solved Exercises (mindmap)
    (
        "Quizzes/CNN Solved Exercises.md",
        "root((CNN<br/>Solved Exercises))",
        "root((Section 27<br/>Exercises))",
    ),
    # ---------------------- The Full Training Pipeline Checklist (Grad-CAM sketch)
    (
        "Pipeline Evaluation and Interpretability/The Full Training Pipeline End-to-End Checklist.md",
        "# See [[CNN Interpretability]] for the",
        "# See [[26. Demystifying the Black Box - CNN Interpretability]] for the",
    ),
    (
        "Pipeline Evaluation and Interpretability/The Full Training Pipeline End-to-End Checklist.md",
        "# A brief sketch (full implementation in the interpretability note):",
        "# A brief sketch (full implementation in Section 26):",
    ),
    # --------------------------------- From Basic Convolution ('no-data' phrasing)
    (
        "CNN Foundations and Philosophy/From Basic Convolution to Learned Weights.md",
        "use classical image processing for simple, well-defined, data-free tasks;",
        "use classical image processing for simple, well-defined, no-data tasks;",
    ),
]


def main() -> int:
    applied = 0
    skipped = 0
    failed: list[str] = []
    for relpath, old, new in REPAIRS:
        path = BASE / relpath
        if not path.is_file():
            failed.append(f"file not found: {relpath}")
            continue
        text = path.read_text(encoding="utf-8")
        if new in text:  # already applied (idempotent)
            skipped += 1
            continue
        hits = text.count(old)
        if hits != 1:
            failed.append(f"anchor not unique ({hits} hits): {relpath}: {old[:60]!r}")
            continue
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
        applied += 1
    summary = {
        "script": "scripts/s21_marker_repairs_area06.py",
        "repairs_declared": len(REPAIRS),
        "applied": applied,
        "already_applied": skipped,
        "failed": failed,
        "idempotent": True,
    }
    print(json.dumps(summary, indent=1))
    if failed:
        print("FAILED REPAIRS:", file=sys.stderr)
        for f in failed:
            print("  " + f, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
