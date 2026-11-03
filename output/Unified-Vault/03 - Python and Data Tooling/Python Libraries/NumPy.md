---
title: NumPy
type: concept
aliases:
  - Numerical Python
  - NumPy - Numerical Computation and Arrays
  - ndarray
  - NumPy arrays
tags:
  - python
  - numpy
  - arrays
  - vectorization
  - broadcasting
  - scientific-computing
sources:
  - "01. NumPy - Numerical Computation and Arrays"
created_index: 17
---

**NumPy** (Numerical Python) is the foundational library for scientific computing in Python. It provides the high-performance multidimensional array object — the `ndarray` — together with the tools for working with these arrays, and it is the numerical substrate that the rest of the Python data stack, including [[Pandas]], builds on. This note covers the array object itself, how arrays are created and inspected, and the ideas that make NumPy fast and expressive: vectorization, broadcasting, and axis-aware aggregation.

## The NumPy array (`ndarray`)

Unlike Python lists, which can hold mixed data types and are scattered in memory, NumPy arrays are:

1. **Homogeneous:** all elements must be of the same type (e.g., all `int64` or all `float32`).
2. **Contiguous:** stored in a continuous block of memory.
3. **Vectorized:** operations are applied to whole arrays at once, avoiding slow Python loops.

These properties work together: because every element has the same type and sits in one continuous block of memory, compiled code can process whole arrays in tight loops instead of walking scattered Python objects. This is the decisive difference from the plain containers of [[Lists Tuples and Sets]].

> [!INFO] **Performance**
> NumPy operations are implemented in C. They can be 10x to 100x faster than standard Python lists for large datasets.

## Creating arrays

Arrays come from existing data, from fixed-value constructors, from ranges, or from random number generators:

```python
import numpy as np

# From a list
arr = np.array([1, 2, 3])

# Fixed Types
zeros = np.zeros((3, 3))        # 3x3 matrix of 0s
ones = np.ones((2, 4))          # 2x4 matrix of 1s
identity = np.eye(3)            # 3x3 Identity matrix

# Ranges
range_arr = np.arange(0, 10, 2) # [0, 2, 4, 6, 8] (Start, Stop, Step)
lin_space = np.linspace(0, 1, 5)# [0.0, 0.25, 0.5, 0.75, 1.0] (5 equal steps)

# Random
rand = np.random.rand(3, 2)     # Uniform distribution [0, 1)
randn = np.random.randn(3, 2)   # Standard Normal distribution (Mean=0, Std=1)
randint = np.random.randint(0, 10, (2,2)) # Random integers
```

`np.array` converts an existing list; `np.zeros`, `np.ones` and `np.eye` build fixed-pattern matrices of a given shape. For ranges, `np.arange` takes start, stop and step (stop excluded), while `np.linspace` takes start, stop and a count, returning exactly that many evenly spaced points including both endpoints. The random constructors cover the three everyday cases: uniform floats in $[0, 1)$, standard normal samples (mean 0, standard deviation 1), and random integers.

## Inspecting arrays

Understanding the structure of your data is crucial before processing it. Every array exposes four attributes that describe its layout:

| Attribute | Description | Example |
| :--- | :--- | :--- |
| `.ndim` | Number of dimensions (axes). | `2` |
| `.shape` | Tuple of dimensions. | `(3, 4)` (3 rows, 4 cols) |
| `.size` | Total number of elements. | `12` |
| `.dtype` | Data type of elements. | `float64`, `int32` |

For a `(3, 4)` array, `.ndim` is `2`, `.shape` is the tuple `(3, 4)` — 3 rows and 4 columns — and `.size` is `12`; `.dtype` reports the concrete element type, such as `float64` or `int32`.

## Vectorization

**Vectorization** is the ability to perform mathematical operations on arrays without writing loops. The operation is written once and applied to the whole array at once:

```python
arr = np.array([1, 2, 3])
print(arr + 10)  # [11, 12, 13]
print(arr * 2)   # [2, 4, 6]
```

Instead of iterating element by element in Python, `arr + 10` dispatches a single operation that produces a new array of the same shape with the arithmetic applied throughout.

## Broadcasting

**Broadcasting** is the set of rules that allows NumPy to perform arithmetic on arrays of different shapes.

- **Rule:** dimensions are compatible when they are equal, or one of them is 1.

```python
matrix = np.ones((3, 3)) # 3x3
row = np.array([1, 2, 3]) # 1x3

# The row is "stretched" (broadcasted) down to match the matrix
result = matrix + row 
# Result:
# [[2, 3, 4],
#  [2, 3, 4],
#  [2, 3, 4]]
```

The row is "stretched" (broadcast) down to match the matrix, so its three values are added to every row of the matrix. Broadcasting is the same mechanism used across the tensor frameworks of deep learning, and its formal rules — right-alignment of shapes and stretching of size-1 dimensions — are developed in [[Tensors and Broadcasting]].

## Indexing and slicing

**Standard slicing** follows the pattern `arr[row_start:row_end, col_start:col_end]`, one slice per dimension, separated by commas.

**Boolean masking (filtering)** selects elements through a boolean array produced by a condition:

```python
arr = np.array([1, 10, 3, 25])
mask = arr > 5            # [False, True, False, True]
filtered = arr[mask]      # [10, 25]
```

The comparison `arr > 5` produces a mask of the same length as the array, and indexing with that mask keeps only the elements where it is `True` — here `[10, 25]`.

## Aggregation

Reduction functions collapse an array into a single value (or smaller array):

- `np.sum(arr)`: sum of all elements.
- `np.mean(arr)`: average.
- `np.std(arr)`: standard deviation.
- `np.max(arr)` / `np.argmax(arr)`: maximum value / index of max value.

**The `axis` parameter** controls the direction of a reduction:

- `axis=0`: operate down the columns (vertical).
- `axis=1`: operate across the rows (horizontal).

A reduction along `axis=0` collapses the rows and leaves one value per column, while `axis=1` collapses the columns and leaves one value per row. The same distinction drives the per-city versus per-day maxima and the per-student averages in [[Exercise - Temperature and Grade Analysis]].

## See also

- [[Python Language Overview]]
- [[Pandas]]
- [[DataFrames]]
- [[Lists Tuples and Sets]]
- [[Tensors and Broadcasting]]
- [[Matplotlib]]
- [[Exercise - Temperature and Grade Analysis]]
