---
title: Computer Vision Evaluation Metrics
type: reference
aliases:
  - CV Metrics
  - Computer Vision Metrics
  - Intersection over Union
  - IoU
  - mean Average Precision
  - mAP
  - Dice Coefficient
  - mIoU
tags:
  - machine-learning
  - model-evaluation
  - computer-vision
  - object-detection
  - semantic-segmentation
  - evaluation-metrics
  - iou
  - map
  - dice-coefficient
  - miou
sources:
  - "Computer Vision Metrics - IoU, mAP, Dice"
created_index: 8
---

Classification metrics measure whether the model predicted the right **label**, but vision tasks usually ask for more: **where** objects are (bounding boxes) or **which pixels** belong to which class (segmentation masks). Judging those outputs requires metrics that measure **spatial agreement**, not just label agreement, and that requirement produced a metric family of its own — IoU and mAP for object detection, pixel accuracy, mIoU, and Dice for segmentation. This note covers the family, the evaluation pipelines built on top of it, and the failure modes of using the wrong member for the task. The classification metrics that serve as its foundation are consolidated in [[Model Evaluation Metrics]]; the surrounding map is [[Machine Learning MOC]].

## Why classification metrics are not enough

Classification metrics (precision, recall, F1) measure whether the model predicted the right label. But CV tasks often require predicting where objects are (bounding boxes) or which pixels belong to which class (segmentation masks). For these, you need metrics that measure spatial agreement, not just label agreement — a prediction can have the right class and still be a bad detection because the box is in the wrong place, or the right mask shape and still miss the object boundary.

## Object detection metrics

### Intersection over union (IoU)

IoU measures the overlap between a predicted bounding box and a ground-truth bounding box:

$$\text{IoU} = \frac{\text{Area of Overlap}}{\text{Area of Union}} = \frac{|B_{pred} \cap B_{true}|}{|B_{pred} \cup B_{true}|}$$

- IoU = 1: perfect overlap.
- IoU = 0: no overlap at all.
- IoU = 0.5: the standard "detection threshold" — a prediction is counted as a true positive if IoU ≥ 0.5 with a ground-truth box.

Why IoU instead of just "did the boxes match"? Because boxes rarely match exactly. A predicted box that is slightly shifted or slightly too large is still a good detection — IoU captures this graduated agreement. A binary "exact match" metric would be too harsh.

The visual intuition is worth holding onto: IoU is the area of overlap divided by the area of union. Two perfectly overlapping boxes have IoU = 1. Two boxes that share half their area have IoU = 0.33 (overlap = 0.5, union = 1.5). Two touching boxes (no overlap) have IoU = 0.

### Average precision and mean average precision (mAP)

Object detection produces many predicted boxes per image, each with a confidence score. To evaluate:

1. **Match predictions to ground truth** using an IoU threshold (typically 0.5). A prediction with IoU ≥ threshold against an unmatched ground-truth box is a True Positive; otherwise it is a False Positive. Unmatched ground-truth boxes are False Negatives.
2. **Rank predictions by confidence** and compute precision-recall at every rank.
3. **Average Precision (AP)** = area under the precision-recall curve (for one class).
4. **mAP** = mean of AP across all classes.

Common variants:

- **mAP@0.5**: IoU threshold = 0.5 (the COCO/PASCAL VOC standard for years).
- **mAP@0.5:0.95**: average mAP over IoU thresholds from 0.5 to 0.95 in steps of 0.05 (the modern COCO standard — much stricter, rewards precise localization).
- **mAP@0.75**: IoU threshold = 0.75 (a single strict threshold).

Why mAP instead of just precision/recall? Because detection models output many predictions at many confidence levels, and you need a single number that summarizes quality across the entire precision-recall tradeoff. mAP is that number.

One terminology warning: detection mAP shares its name ("mean average precision") with the ranking metric MAP used in search and recommendation, which averages precision across the relevant items of a ranked list. The two are different constructions that happen to share a name — detection mAP averages per-class areas under precision-recall curves after IoU-based spatial matching, while ranking MAP has no spatial matching at all. Whenever "mAP" appears, check which family is meant; the ranking side is covered in [[Model Evaluation Metrics]].

### The detection evaluation pipeline, step by step

The full procedure that turns a trained detector into a mAP number:

1. Run the detector on all test images, producing predicted boxes + classes + confidences.
2. For each class, for each image:
   a. Match predictions to ground-truth boxes (greedy by IoU, highest confidence first).
   b. Mark matches as TP (IoU ≥ threshold) or FP (IoU < threshold or duplicate match).
3. Pool all predictions across images, sort by confidence.
4. Compute precision and recall at each confidence threshold.
5. Integrate the precision-recall curve to get AP for this class.
6. Average AP across classes to get mAP.

This is more complex than classification evaluation because of the spatial matching step — but it is the standard, and understanding it is essential for reading detection papers.

## Segmentation metrics

### Pixel accuracy

$$\text{Pixel Accuracy} = \frac{\text{Number of correctly classified pixels}}{\text{Total number of pixels}}$$

Pixel accuracy measures the fraction of pixels classified correctly. Its pitfall is the majority-class trap in pixel form: it is misleading for imbalanced classes. If 90% of the image is background, a model that always predicts "background" gets 90% pixel accuracy but is useless for the actual segmentation task — the same degenerate majority-prediction pattern that makes classification accuracy meaningless on imbalanced data, instantiated one pixel at a time.

### Mean IoU (mIoU)

For each class, compute IoU between the predicted mask and the ground-truth mask, treating the masks as sets of pixels:

$$\text{IoU}_c = \frac{|M_{pred}^c \cap M_{true}^c|}{|M_{pred}^c \cup M_{true}^c|}$$

**mIoU** is the mean of IoU across all classes.

mIoU is the standard metric for semantic segmentation, and its virtue is that it handles class imbalance: each class contributes equally to the mean, regardless of frequency. The pitfalls come from small and boundary structure:

- Small objects can have very low IoU even with good predictions — a single misclassified pixel on a 10-pixel object drops IoU from 1.0 to 0.8.
- Boundary pixels are often ambiguous — should they count? Some variants exclude a boundary region.

### Dice coefficient (F1 for pixels)

$$\text{Dice} = \frac{2 |M_{pred} \cap M_{true}|}{|M_{pred}| + |M_{true}|} = \frac{2 \cdot \text{TP}}{2 \cdot \text{TP} + \text{FP} + \text{FN}}$$

Dice is the F1 score computed at the pixel level — equivalent to the harmonic mean of precision and recall on the pixel-level classification, which is why it is often introduced as "F1 for pixels."

Its relationship to IoU is fixed and monotone: $\text{Dice} = \frac{2 \cdot \text{IoU}}{1 + \text{IoU}}$. The two are monotonically related — optimizing one optimizes the other — but Dice is sometimes preferred because it is also a loss function (Dice loss) that handles class imbalance well.

Use Dice for medical image segmentation, where it is the standard metric, and whenever you want a loss function and a metric that are the same (Dice loss + Dice metric) — a convenience IoU does not offer.

## Choosing a metric for the task

| Task | Primary metric | Also report |
| :--- | :--- | :--- |
| Object detection | mAP@0.5:0.95 (COCO) | mAP@0.5, mAP@0.75, per-class AP |
| Semantic segmentation | mIoU | Pixel accuracy, per-class IoU, Dice |
| Instance segmentation | Mask AP (AP computed on masks instead of boxes) | mIoU, per-class mask AP |
| Medical segmentation | Dice coefficient | IoU, Hausdorff distance (for boundary quality) |

Detection, semantic segmentation, and instance segmentation are different tasks with different metrics. Do not use mAP for semantic segmentation or mIoU for detection. Match the metric to the task's output structure: boxes want box-overlap matching, masks want pixel-set overlap, and instance-level tasks want detection machinery applied to masks.

## Common pitfalls

### Reporting only mAP@0.5

mAP@0.5 is lenient — a box with 50% overlap counts as correct. Modern papers report mAP@0.5:0.95, which rewards precise localization. If you only report mAP@0.5, your model may look good but actually have poor localization.

### Ignoring small objects

mAP averaged across all object sizes can hide poor performance on small objects. COCO reports mAP separately for small, medium, and large objects — do the same.

### Using pixel accuracy for imbalanced segmentation

If 95% of pixels are background, pixel accuracy is dominated by background performance. Use mIoU (which weights all classes equally) or report per-class IoU.

### Not matching the metric to the task

Detection, semantic segmentation, and instance segmentation are different tasks with different output structures, and each has its own primary metric — mixing them up produces numbers that measure the wrong thing. The table above is the reference; the rule is to match the metric to the task's output structure.

## Key takeaways

The family in compressed form: **IoU** measures overlap between predicted and true boxes or masks, and the standard detection threshold is IoU ≥ 0.5. **mAP** is the mean across classes of the area under the precision-recall curve, computed after IoU-based matching, with mAP@0.5:0.95 as the modern COCO standard. **Pixel accuracy** is misleading for imbalanced segmentation — use mIoU instead. **mIoU** is the standard semantic segmentation metric, averaging IoU across classes so that rare classes count. **Dice** is the F1 score at the pixel level, the standard for medical segmentation, and also usable as a loss function.

Two habits complete the picture: match the metric to the task (mAP for detection, mIoU for semantic segmentation, Mask AP for instance segmentation, Dice for medical), and report metrics at multiple thresholds and object sizes to avoid hiding poor performance on hard cases. Together with the classification, regression, and clustering families, these complete the model-evaluation toolkit — and the common thread through all of them is that the right metric is the one that mirrors what the task actually needs to get right.

## See also

The classification foundations (precision, recall, F1, and the precision-recall curve that AP integrates) and the other metric families are collected in:

- [[Machine Learning MOC]]
- [[Model Evaluation Metrics]]
