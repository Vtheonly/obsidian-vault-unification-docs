---
title: Exercise - Temperature and Grade Analysis
type: tutorial
aliases:
  - Exercise 4 - Temperature and Grade Analysis
  - Exercise 4. Temperature and Grade Analysis
  - Temperature and Grade Analysis
tags:
  - python
  - numpy
  - pandas
  - matplotlib
  - seaborn
  - exercise
  - data-analysis
  - tutorial
sources:
  - "07. Exercise 4 - Temperature and Grade Analysis"
created_index: 15
---

This exercise combines NumPy, pandas, and Matplotlib/Seaborn to solve two distinct analytical problems. Part 1 analyzes a 2D array of city temperatures with NumPy, exercising axis-aware aggregation, index unraveling and boolean masking; part 2 moves student grades into a pandas DataFrame and finishes with a Seaborn visualization. It draws on the array fundamentals from [[NumPy]], the labeled data structures of [[Pandas]] and [[DataFrames]], and the plotting layers of [[Matplotlib]] and [[Seaborn]].

## Part 1: Temperature analysis with NumPy

**Problem:** you have a 2D array of temperatures for 3 cities over 7 days.

**Tasks:** find max temps, average temps, and filter specific conditions.

The data is stored with rows as days and columns as cities, and the solution works through the tasks in order: maxima per city, maxima per day, the overall maximum, the location of that maximum, and a boolean-mask filter comparing two cities.

```python
import numpy as np

# Data: Rows = Days (7), Cols = Cities (3: Alger, Annaba, Oran)
temps = np.array([
    [22, 25, 20],
    [24, 27, 21],
    [19, 20, 22],
    [25, 29, 28],
    [26, 30, 27],
    [21, 21, 23],
    [20, 26, 25]
])

# 1. Max Temp per City (Axis 0 = down columns)
max_per_city = np.max(temps, axis=0) 
# Output: [26, 30, 28]

# 2. Max Temp per Day (Axis 1 = across rows)
max_per_day = np.max(temps, axis=1)

# 3. Overall Max
global_max = np.max(temps)

# 4. Location of Max (Day, City)
# argmax gives flattened index, unravel_index converts to (row, col)
row, col = np.unravel_index(np.argmax(temps), temps.shape)
cities = ['Alger', 'Annaba', 'Oran']
print(f"Hottest: {global_max}°C in {cities[col]} on Day {row+1}")

# 5. Boolean Masking: Days where Annaba > Alger
annaba = temps[:, 1]
alger = temps[:, 0]
hottest_days = np.where(annaba > alger)[0] + 1
```

### How the solution works

Steps 1–3 are all `np.max` with different scopes, and the `axis` argument decides what collapses. With `axis=0`, for instance, the operation runs down the columns, so each city's seven daily readings collapse into a single maximum: the output `[26, 30, 28]` is one maximum per city, for Alger, Annaba and Oran respectively. With `axis=1` the operation runs across the rows, giving the hottest of the three cities for each day, and calling `np.max` with no axis at all collapses everything into the overall maximum.

Step 4 locates that overall maximum. `np.argmax` returns the flattened index of the largest element — a single position counted as if the array were unrolled into one long list — and `np.unravel_index` converts that flat index back into a `(row, col)` pair given the array's shape. The row is the day and the column is the city, so `cities[col]` names the hottest city and `row+1` turns the zero-based day index into a one-based day number for the printed message.

Step 5 is boolean masking. `temps[:, 1]` slices out Annaba's column and `temps[:, 0]` Alger's, the comparison produces a boolean array, and `np.where(annaba > alger)[0]` extracts the positions where it is `True`. Adding 1 converts those zero-based positions into one-based day numbers, giving the days on which Annaba was hotter than Alger.

## Part 2: Student grades with pandas

**Problem:** analyze student grades in a DataFrame.

The grades start as a dictionary of lists and become a DataFrame, then move through three steps: a per-student average, a filter for the passing students, and a Seaborn bar plot with the pass line drawn on it.

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

data = {
    'Student': ['Ali', 'Sara', 'Rami', 'Lina', 'Omar'],
    'Math': [12, 18, 9, 15, 8],
    'Physics': [10, 19, 11, 16, 7],
    'CS': [14, 20, 12, 18, 9]
}
df = pd.DataFrame(data)

# 1. Average Grade per Student
df['Average'] = df[['Math', 'Physics', 'CS']].mean(axis=1)

# 2. Filtering
# Find students passing (Average >= 10)
passing = df[df['Average'] >= 10]

# 3. Visualization
# Melt dataframe for Seaborn (Wide to Long format)
df_melt = df.melt(id_vars='Student', value_vars=['Math', 'Physics', 'CS'], 
                  var_name='Subject', value_name='Grade')

plt.figure(figsize=(10, 6))
sns.barplot(data=df_melt, x='Student', y='Grade', hue='Subject')
plt.axhline(10, color='red', linestyle='--', label='Pass Line')
plt.title("Student Grades by Subject")
plt.legend()
plt.show()
```

### How the solution works

The dictionary of lists becomes a five-row DataFrame with one column per subject. Step 1 selects the three subject columns and calls `.mean(axis=1)`, which operates across each row — averaging each student's three grades — and assigning the result to `df['Average']` attaches it as a new column. This is the same axis convention as in part 1: `axis=1` works across the rows.

Step 2 is conditional selection. The condition `df['Average'] >= 10` produces a boolean Series, and indexing the DataFrame with it keeps only the rows where the condition holds — the students at or above the pass line.

Step 3 reshapes and plots. Seaborn's `barplot` wants long-format data — one row per student-subject pair — so `df.melt` converts the wide, one-column-per-subject table: `id_vars='Student'` keeps the identifier column, `value_vars` lists the columns to stack, and `var_name='Subject'` and `value_name='Grade'` name the two resulting columns. The plot then draws a grouped bar chart with `hue='Subject'` splitting each student's bars by subject, while `plt.axhline(10, color='red', linestyle='--')` draws the dashed red pass line at grade 10, so at a glance you can see which bars clear it.

## See also

- [[Python Language Overview]]
- [[NumPy]]
- [[Pandas]]
- [[DataFrames]]
- [[Matplotlib]]
- [[Seaborn]]
