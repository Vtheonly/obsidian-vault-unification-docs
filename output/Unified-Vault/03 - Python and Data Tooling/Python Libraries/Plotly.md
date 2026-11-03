---
title: Plotly
type: concept
aliases:
  - Interactive Plotting with Plotly
  - Plotly Express
  - plotly.express
  - Plotly Graph Objects
  - plotly.graph_objects
tags:
  - python
  - plotly
  - data-visualization
  - interactive-plots
  - plotting
  - dashboards
sources:
  - "06. Interactive Plotting with Plotly"
created_index: 19
---

**Plotly** is a graphing library that makes interactive, publication-quality graphs. Unlike Matplotlib, which produces static images, Plotly renders figures as HTML/JavaScript — which is what makes zooming, panning, and hovering possible. This note covers the two APIs — Plotly Express for minimal-code everyday charts and Graph Objects for fine-grained control — together with the interactive features every figure carries. It is part of the Python data tooling surveyed in [[Python Language Overview]].

## Plotly Express

`plotly.express` — imported as `px` — is the high-level API, similar to Seaborn, and it covers 90% of use cases with minimal code. A complete interactive scatter plot with hover data is a single call:

```python
import plotly.express as px

# Scatter plot with hover data
fig = px.scatter(df, 
                 x='GDP', 
                 y='Life Expectancy', 
                 color='Continent',
                 hover_name='Country',
                 size='Population')
fig.show()
```

The arguments map DataFrame columns straight onto the visual encoding: `GDP` on the x-axis, `Life Expectancy` on the y-axis, one color per `Continent`, the `Country` name on hover, and the point size driven by `Population`. `fig.show()` then renders the figure.

## Key interactive features

Every Plotly figure comes with the same four behaviors:

| Feature | What the user can do |
|---|---|
| Interactivity | Hover over points to see exact values |
| Zooming | Selecting a region zooms into it |
| Toggles | Clicking legend items hides/shows groups |
| Export | Save plots as interactive HTML files (`fig.write_html("plot.html")`) |

Because the export path writes HTML rather than a static image, the saved file keeps the zoom, hover, and toggle behavior.

## Plotly Graph Objects

For fine-grained control, or for creating complex dashboards with multiple types of charts overlaid, the API to reach for is `plotly.graph_objects`, imported as `go`. Instead of one function per chart, you create an empty figure and add traces to it one at a time:

```python
import plotly.graph_objects as go

fig = go.Figure()
fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='Line'))
fig.add_trace(go.Bar(x=x, y=y2, name='Bar'))
fig.show()
```

Each `add_trace()` call attaches one chart — here a `go.Scatter` drawn in lines mode and a `go.Bar` — and because traces are added individually, different chart types can be overlaid in the same figure. The two APIs are complementary: Plotly Express covers the common case with minimal code, and Graph Objects handles the fine-grained and the complex.

## See also

- [[Python Language Overview]]
- [[Matplotlib]]
- [[Seaborn]]
- [[Pandas]]
- [[DataFrames]]
- [[NumPy]]
