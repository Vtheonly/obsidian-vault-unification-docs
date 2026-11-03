---
title: Seaborn
type: concept
aliases:
  - "Seaborn - Statistical Data Visualization"
  - Statistical Data Visualization
  - seaborn
tags:
  - python
  - seaborn
  - data-visualization
  - statistical-visualization
  - matplotlib
  - pandas
  - heatmap
  - pairplot
  - feature-selection
sources:
  - "05. Seaborn - Statistical Data Visualization"
created_index: 20
---

**Seaborn** is a high-level library built on top of Matplotlib for statistical data visualization: it integrates closely with Pandas DataFrames and provides beautiful default styles, so polished statistical charts come out of very few lines of code. This note covers the philosophy that separates it from Matplotlib, the three modules it organizes its plots into, the two standout tools — the correlation heatmap and the pairplot — and its interoperability with the Matplotlib layer underneath. It is part of the Python data tooling surveyed in [[Python Language Overview]].

## Design philosophy: high level versus low level

The difference between the two libraries is the level of the request you make of them:

| Library | The request | Level |
|---|---|---|
| Matplotlib | "Draw a blue line from (0,0) to (1,1)." | Low level |
| Seaborn | "Draw a scatterplot of Price vs. Size, colored by Neighborhood." | High level |

With Matplotlib you spell out the geometry: which color of line, between which coordinates. With Seaborn you name the statistical view — relate Price to Size, color the points by Neighborhood — and the library works out the drawing. This is also why it pairs so naturally with DataFrames: its vocabulary is the columns of a table.

## Plot categories

Seaborn organizes its plots into modules, one per kind of statistical question — relationships, distributions, and categories.

### Relational plots

`sns.scatterplot()` and `sns.lineplot()` are the two relational functions, and `sns.relplot()` is the wrapper that gives access to this family.

### Distribution plots

The distribution family has four functions: `sns.histplot()` draws a histogram, `sns.kdeplot()` draws a kernel density estimate (a smooth curve), `sns.boxplot()` shows summary statistics, and `sns.violinplot()` combines a boxplot with a KDE. The wrapper for this family is `sns.displot()`.

### Categorical plots

For categorical data, `sns.barplot()` shows an estimate of central tendency (the mean), `sns.countplot()` shows the count of observations, and `sns.stripplot()` is a scatterplot for categorical data.

## The correlation heatmap

The correlation heatmap is one of the most useful tools in Data Science for Feature Selection. The workflow is two steps: compute the correlation matrix from the DataFrame, then hand it to `sns.heatmap()`:

```python
import seaborn as sns

# Calculate correlation matrix
corr = df.corr()

# Plot heatmap
sns.heatmap(corr, annot=True, cmap='coolwarm')
```

With `annot=True` the correlation values are written into the cells of the grid, and `cmap='coolwarm'` selects the colormap.

## Pairplot

Where the heatmap summarizes a single matrix, the pairplot visualizes the pairwise relationships in an entire dataset with one call:

```python
sns.pairplot(df, hue='Species')
```

The `hue` argument colors the points by the `Species` column, so the structure of each pairwise relationship is visible separately for every group.

## Interoperability with Matplotlib

Seaborn is a layer on top of Matplotlib, not a separate universe, so when a Seaborn default is not quite right the layer below is always within reach:

> [!tip] Integration
> Since Seaborn is built on Matplotlib, you can use Matplotlib commands to tweak Seaborn plots (e.g., `plt.title()`, `plt.figure()`).

## See also

- [[Python Language Overview]]
- [[Matplotlib]]
- [[Pandas]]
- [[DataFrames]]
- [[NumPy]]
- [[Plotly]]
- [[The Data Science Workflow]]
