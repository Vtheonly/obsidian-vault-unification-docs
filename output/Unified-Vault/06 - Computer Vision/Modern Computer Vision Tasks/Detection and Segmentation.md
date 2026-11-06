---
title: Detection and Segmentation
type: concept
aliases:
  - Modern Computer Vision Tasks - Detection and Segmentation
  - Modern Computer Vision Tasks — Detection and Segmentation
  - Object Detection and Segmentation
  - Object Detection
  - Semantic Segmentation
  - Instance Segmentation
  - Panoptic Segmentation
tags:
  - cnn
  - computer-vision
  - deep-learning
  - object-detection
  - semantic-segmentation
  - instance-segmentation
  - panoptic-segmentation
  - anchor-boxes
  - non-maximum-suppression
  - faster-r-cnn
  - yolo
  - ssd
  - detr
  - fcn
  - u-net
  - deeplab
  - mask-r-cnn
sources:
  - "01. Modern Computer Vision Tasks - Detection and Segmentation"
created_index: 46
---

Classification — the task the standard CNN toolkit solves — assigns one label per image, but most real vision questions ask *where* the objects are or *which pixels* they occupy. Object detection (bounding box prediction) and semantic segmentation (pixel-level classification) are the tasks that drove CNN research from 2014 to 2020 and that underpin self-driving cars, medical imaging, and surveillance. This note walks the full ladder of visual understanding — classification, detection, semantic segmentation, instance segmentation, panoptic segmentation — and the architectures built for each rung: anchors and non-maximum suppression, Faster R-CNN, YOLO and SSD, DETR, FCN, U-Net, DeepLab, and Mask R-CNN. It builds on [[06 - Computer Vision/CNN Foundations and Philosophy/Introduction and Foundations of CNNs|Introduction and Foundations of CNNs]] and [[Advanced Convolutional Operators - Depthwise, Dilated, Transposed, Grouped]], and it uses the classification backbones traced in [[06 - Computer Vision/Architecture and Connectivity/Evolution of CNN Architectures|Evolution of CNN Architectures]].

## The three levels of visual understanding

Every vision task sits somewhere on a ladder of increasing output granularity, and the table below fixes the vocabulary for the rest of this note.

| Task | Output | Example question |
| :--- | :--- | :--- |
| **Classification** | One label per image | "Is there a cat in this image?" |
| **Object detection** | Bounding boxes + labels | "Where are the cats, and how many?" |
| **Semantic segmentation** | Pixel-level labels | "Which pixels belong to cats?" |
| **Instance segmentation** | Pixel-level labels, separate instances | "Which pixels belong to *this* cat vs *that* cat?" |

Classification tells you *what* is in the image. Detection tells you *where*. Segmentation tells you *exactly which pixels*. Each level requires a different architecture and a different loss function, because the output structure itself changes — from a fixed-size score vector, to a variable-length list of boxes, to a full-resolution label map.

## Object detection

### The detection problem

Given an image, predict a set of bounding boxes, each with three components: a **location** $(x, y, w, h)$ — center, width, and height; a **class** — what object is in the box; and a **confidence** — how sure the model is. The number of objects varies per image (0 to many), so the output is a variable-length list, not a fixed-size vector. This variable-length output is the structural challenge that separates detection from classification, and it shapes every architecture in this section.

### Anchor boxes

How does a neural network output a variable number of boxes? The standard answer is **anchor boxes** (also called priors). Predefine a set of $K$ anchor boxes at each spatial position of the feature map, with different scales and aspect ratios (e.g., 3 scales × 3 ratios = 9 anchors per position). For a $7 \times 7$ feature map with 9 anchors each, the model predicts $7 \times 7 \times 9 = 441$ boxes. Each prediction is:

- **Objectness score:** is there an object in this anchor? (binary classification)
- **Box regression:** offsets to adjust the anchor to fit the actual object ($\Delta x, \Delta y, \Delta w, \Delta h$)
- **Class probabilities:** what class is the object? (multi-class classification, only if objectness is high)

At inference, the model outputs hundreds or thousands of boxes (one per anchor). Most have low objectness and are discarded; the rest are filtered by **Non-Maximum Suppression**, described next.

### Non-maximum suppression

Multiple anchors may detect the same object, so a single object typically produces several overlapping boxes. **Non-Maximum Suppression (NMS)** removes these duplicates:

1. Sort all boxes by confidence (descending).
2. Take the highest-confidence box, add it to the output.
3. Remove all boxes with IoU > threshold (e.g., 0.5) with the selected box — they are detecting the same object.
4. Repeat with the next-highest-confidence box.
5. Stop when all boxes are processed or a max count is reached.

> [!warning] NMS is essential
> Without it, each object is detected 5-10 times — once for every anchor that latched onto it. The confidence sort keeps the best box per object, and the IoU test deletes the redundant remainder.

### Two-stage detectors: Faster R-CNN

**Faster R-CNN** (Ren et al., 2015) is the canonical two-stage detector. **Stage 1 — Region Proposal Network (RPN):** a small CNN examines the feature map and proposes candidate object regions (anchors with high objectness). This stage does not classify — it just says "there is probably an object here." **Stage 2 — classification and refinement:** for each proposed region, the model crops the corresponding feature map region (via **RoI Pooling** or **RoI Align**), applies a classification head to predict the class, and refines the bounding box.

The division of labor is both the architecture's strength and its cost. The pros: high accuracy, because the two stages allow the model to focus on promising regions. The cons: slower (two forward passes) and more complex.

### One-stage detectors: YOLO and SSD

**YOLO (You Only Look Once)** (Redmon et al., 2016) and **SSD (Single Shot MultiBox Detector)** (Liu et al., 2016) skip the region proposal stage and predict boxes directly from the feature map in a single pass.

**YOLO** divides the image into an $S \times S$ grid. Each grid cell predicts $B$ bounding boxes (with objectness and class probabilities) directly, and a single forward pass produces all predictions. YOLO is extremely fast (real-time on a GPU) but historically less accurate than two-stage detectors.

**SSD** takes a similar approach but uses multiple feature maps at different scales (multi-scale detection). Lower-resolution maps detect large objects; higher-resolution maps detect small objects. This improves small-object detection over YOLO.

The YOLO family has been continuously improved — **YOLOv5, v8, v9, v10** — and is now both fast *and* accurate. YOLOv8 and later are competitive with two-stage detectors on accuracy while remaining real-time. They are the default choice for practical object detection.

### The accuracy-speed tradeoff

| Detector | Accuracy | Speed | Use case |
| :--- | :--- | :--- | :--- |
| Faster R-CNN | High | Slow | High-accuracy, offline |
| YOLO (modern) | High | Real-time | Production, video, edge |
| SSD | Medium | Fast | Good baseline |
| DETR (Transformer-based) | High | Medium | Modern, end-to-end |

The last row is the newest entry in the tradeoff. The **DETR** (Carion et al., 2020) is a Transformer-based detector that removes the need for anchors and NMS entirely — it directly outputs a fixed set of predictions using a Transformer decoder with learned object queries. It is elegant but currently slower than YOLO for practical use. Read the table as a design menu: accuracy-critical offline pipelines still reach for Faster R-CNN, production video and edge deployment reach for modern YOLO, and SSD remains a good baseline.

## Semantic segmentation

### The segmentation problem

Given an image, predict a **class label for every pixel**. The output is a $H \times W$ label map, the same size as the input. Where detection emits a sparse list of boxes, segmentation emits a dense prediction at full input resolution — and that density is what shapes the architectures below.

### Fully convolutional networks

**FCN** (Long, Shelhamer, and Darrell, 2015) is the foundational architecture: take a classification CNN (VGG, ResNet), replace the fully-connected layers with convolutional layers, and add a **transposed convolution** (or upsampling) to restore the spatial resolution. The output is a $H \times W \times C$ prediction (per-pixel class scores).

The key insight is that a CNN's convolutional layers already produce spatial feature maps; you just need to upsample them back to the input resolution and apply a per-pixel classifier. The fully-connected head is the part of a classifier that throws spatial structure away (see [[The Fully Connected Layer and Flattening]]), so removing it converts a classifier into a dense predictor. The transposed convolution that performs the upsampling is one of the advanced operators covered in [[Advanced Convolutional Operators - Depthwise, Dilated, Transposed, Grouped]].

### U-Net

**U-Net** (Ronneberger et al., 2015) — met from the restoration side in [[Deep Learning for Imaging]] — is the dominant architecture for medical segmentation. Its innovation is **skip connections** from encoder to decoder:

```text
Encoder                          Decoder
[Conv 64] ───────────skip──────── [Conv 64]
   ↓ (pool)                            ↑ (transpose conv)
[Conv 128] ──────────skip─────── [Conv 128]
   ↓ (pool)                            ↑
[Conv 256] ──────────skip─────── [Conv 256]
   ↓ (pool)                            ↑
[Conv 512] ──────────skip─────── [Conv 512]
   ↓ (pool)                            ↑
[Conv 1024] (bottleneck) ──────────────
```

The encoder downsamples (capturing context); the decoder upsamples (restoring resolution). The skip connections pass high-resolution detail from encoder to decoder, so the decoder has both the global context (from the bottleneck) and the local detail (from the skips). Without the skip connections, the decoder would have to reconstruct pixel-level detail from a heavily-compressed bottleneck, which is impossible. The skips are what make U-Net work.

### DeepLab

**DeepLab** (Chen et al., 2017+) takes a different approach: instead of downsampling then upsampling (U-Net), it uses **dilated convolutions** (see [[Advanced Convolutional Operators - Depthwise, Dilated, Transposed, Grouped]]) to maintain resolution while expanding the receptive field. This avoids the information loss from downsampling. DeepLabv3+ adds an **ASPP (Atrous Spatial Pyramid Pooling)** module that applies dilated convolutions with different dilation rates (6, 12, 18) in parallel, capturing context at multiple scales. It also adds a decoder module that refines the boundaries.

### Instance segmentation: Mask R-CNN

**Instance segmentation** (separate pixel masks for each object instance) is harder than semantic segmentation (one label per pixel, regardless of instance) — the distinction is exactly the cat example in the opening table: *this* cat vs *that* cat. **Mask R-CNN** (He et al., 2017) extends Faster R-CNN by adding a third output: in addition to the class and bounding box, the model predicts a binary mask for each detected instance.

The architecture integrates detection and mask prediction in one pipeline:

1. **RPN** proposes regions (same as Faster R-CNN).
2. **RoI Align** crops the feature map for each proposed region (with bilinear interpolation to avoid quantization).
3. Three heads: classification (what class), box regression (where), and **mask prediction** (a small FCN that predicts a per-pixel binary mask within the box).

Mask R-CNN is the standard for instance segmentation and won the COCO 2017 challenge.

### Panoptic segmentation

**Panoptic segmentation** (Kirillov et al., 2019) unifies semantic and instance segmentation: every pixel is assigned a class label *and* an instance ID. Background classes (sky, road, grass) get one label for all pixels; "thing" classes (person, car, dog) get a separate label per instance. This is the current frontier of segmentation research.

## The architecture landscape

The whole field compresses into one lookup table.

| Task | Canonical architecture | Key innovation |
| :--- | :--- | :--- |
| Object detection (two-stage) | Faster R-CNN | Region Proposal Network |
| Object detection (one-stage) | YOLO, SSD | Single-pass, anchors |
| Object detection (Transformer) | DETR | Learned object queries, no NMS |
| Semantic segmentation | FCN, U-Net, DeepLab | Encoder-decoder / dilated convs |
| Instance segmentation | Mask R-CNN | Adds mask head to Faster R-CNN |
| Panoptic segmentation | Panoptic FPN, MaskFormer | Unifies semantic + instance |

The rows build on each other rather than replacing one another. Mask R-CNN literally adds a mask head to Faster R-CNN, reusing its proposal stage; the panoptic systems (Panoptic FPN, MaskFormer) unify the semantic and instance branches on top of both families. DETR stands apart by deleting the anchor and NMS machinery altogether.

## Key takeaways

Object detection predicts bounding boxes plus classes: anchors are the predefined boxes, the model predicts offsets and objectness, and NMS removes duplicate detections. Two-stage detectors (Faster R-CNN) propose regions then classify — accurate but slow. One-stage detectors (YOLO, SSD) predict directly in a single pass — fast, and modern YOLOs are also accurate. Semantic segmentation labels every pixel: FCN is the foundation, U-Net pairs an encoder-decoder with skip connections, and DeepLab uses dilated convolutions. Instance segmentation (Mask R-CNN) adds per-instance masks to detection, and panoptic segmentation unifies the semantic and instance views. All of these tasks are scored with the standard vision metrics — mAP for detection, mIoU/Dice for segmentation. Together with the advanced operators and vision transformers, they complete the spectrum from classical CNNs to modern detection and segmentation to Transformers.

## See also

- [[CNN Course Overview]]
- [[CNN Mastery Roadmap]]
- [[Deep Learning for Imaging]] — the restoration-side treatment of U-Net and learned denoising
- [[Advanced Convolutional Operators - Depthwise, Dilated, Transposed, Grouped]] — the dilated and transposed convolutions behind DeepLab and U-Net
- [[06 - Computer Vision/Architecture and Connectivity/Evolution of CNN Architectures|Evolution of CNN Architectures]] — the classification backbones these tasks build on
- [[06 - Computer Vision/CNN Foundations and Philosophy/Introduction and Foundations of CNNs|Introduction and Foundations of CNNs]]
- [[The Fully Connected Layer and Flattening]] — the layer FCN removes to stay fully convolutional
- [[Image Pyramids and Multi-Scale Representation]] — the classical multi-scale idea behind SSD's multi-scale detection
- [[Watershed Segmentation]] — the classical route to pixel-level region outputs
