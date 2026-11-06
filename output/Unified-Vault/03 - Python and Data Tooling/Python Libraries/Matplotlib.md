---
title: Matplotlib
type: concept
aliases:
  - "Matplotlib - Static Data Visualization"
  - Static Data Visualization
  - Pyplot
  - matplotlib.pyplot
tags:
  - python
  - matplotlib
  - data-visualization
  - plotting
  - pyplot
  - subplots
sources:
  - "04. Matplotlib - Static Data Visualization"
created_index: 16
---

**Matplotlib** is the foundational plotting library for Python, built for static data visualization with complete control over every pixel of a figure. Everything you do with it reduces to a small set of concepts: two alternative interfaces, a three-level figure anatomy, a handful of core plot types, and a styling-and-saving step. This note walks through each of those in turn, as part of the Python data tooling surveyed in [[Python Language Overview]].

## Two interfaces: pyplot and object-oriented

There are two ways to use Matplotlib — the pyplot interface and the object-oriented (OO) interface — and mixing them causes confusion, so it pays to understand both and to choose one deliberately for the figure you are building.

### The pyplot interface (state-based)

The pyplot interface is state-based: you issue plotting commands to the `matplotlib.pyplot` module itself, and the module keeps track of the current figure for you. It is good for quick, simple interactive plots.

```python
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [1, 4, 9])
plt.title("Simple Plot")
plt.show()
```

### The object-oriented interface (recommended)

The object-oriented interface is the recommended style, good for complex scripts, dashboards, and complete control. You create the objects explicitly — `plt.subplots()` returns a `Figure` and an `Axes` — and then call methods on the `Axes`:

```python
fig, ax = plt.subplots()  # Create Figure and Axes objects
ax.plot([1, 2, 3], [1, 4, 9])
ax.set_title("OO Plot")
ax.set_xlabel("X Axis")
plt.show()
```

The same data is drawn either way, but in the OO style the title and the x-axis label are set with `ax.set_title()` and `ax.set_xlabel()` — methods on an object you hold — which makes this the style to reach for in complex scripts and dashboards.

## Anatomy of a figure

Every figure is built from three nested levels, and the object-oriented interface exposes each of them by name:

| Object | Role |
|---|---|
| `Figure` (`fig`) | The top-level container — the canvas. It holds everything. |
| `Axes` (`ax`) | The region where data is plotted — a graph. A figure can contain multiple Axes (subplots). |
| `Axis` | The x-axis and y-axis lines (spines), ticks, and labels. |

The `fig, ax = plt.subplots()` line above creates the first two of these in a single call. Watch the near-identical names: the plural **Axes** is the whole plotting region, while the singular **Axis** is one of its number lines, together with its spines, ticks, and labels.

## Common plot types

The everyday chart types are all methods on the `Axes` object:

| Call | Plot type |
|---|---|
| `ax.plot(x, y)` | Line plot |
| `ax.scatter(x, y)` | Scatter plot |
| `ax.bar(x, height)` | Bar chart |
| `ax.hist(data, bins)` | Histogram (distribution) |
| `ax.boxplot(data)` | Box and whisker plot |

The calls differ in the shape of the data they take: paired `x`/`y` series for `plot` and `scatter`, positions plus heights for `bar`, a batch of raw data plus a bin count for `hist`, and raw data alone for `boxplot`.

## Customization and saving

Styling happens inside the plotting call through keyword arguments, and legend, grid, and file export are each a single additional line:

```python
ax.plot(x, y, color='red', linestyle='--', marker='o', label='Trend')
ax.legend()       # Show legend
ax.grid(True)     # Show grid
plt.savefig('my_plot.png') # Save to disk
```

Here the series is drawn as a red dashed line with circle markers and carries the label `'Trend'`; `ax.legend()` shows the legend, `ax.grid(True)` turns on the grid, and `plt.savefig('my_plot.png')` writes the finished figure to disk as a PNG image.

## See also

- [[Python Language Overview]]
- [[NumPy]]
- [[Pandas]]
- [[DataFrames]]
- [[Seaborn]]
- [[Plotly]]
- [[The Data Science Workflow]]
