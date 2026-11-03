---
title: Exercise - Medical Dataset Pipeline
type: tutorial
aliases:
  - Exercise 5 - Medical Dataset Pipeline
  - Medical Dataset Pipeline
tags:
  - python
  - data-cleaning
  - preprocessing
  - exercise
  - pandas
  - scikit-learn
sources:
  - "06. Exercise 5 - Medical Dataset Pipeline"
created_index: 3
---

This exercise is the capstone of the data-cleaning workflow: starting from a raw "Medical" dataset full of messy values, you build one complete preprocessing pipeline — loading, text cleaning, imputation, outlier removal, encoding and scaling — that ends in a numeric matrix a model can actually train on. Each stage applies one of the techniques from the concept notes in this subfamily, so the exercise doubles as an end-to-end review of the preprocessing toolkit.

## The problem

You have a raw "Medical" dataset with messy values — the `Gender` column, for example, mixes 'Female', 'male', 'Male', 'female' and 'MALE'. The task is to build a full preprocessing pipeline:

1. **Load data:** read `medical_raw.csv`.
2. **Clean text:** standardize "Gender" and "Diagnosis".
3. **Missing values:** categorical -> mode; numeric -> median.
4. **Outliers:** remove using IQR on "Cholesterol".
5. **Encode:** one-hot encode "Gender".
6. **Scale:** MinMax scale "Age" and "BloodPressure".

## The solution

```python
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# 1. Load (Simulated)
data = {
    'PatientID': ['P1', 'P2', 'P3', 'P4', 'P5'],
    'Age': [25, np.nan, 65, 50, 120], # 120 is outlier?
    'BloodPressure': [120, 130, np.nan, 110, 200],
    'Cholesterol': [200, 180, 250, 190, 900], # 900 is outlier
    'Gender': ['Female', 'male', 'Male', 'female', 'MALE'], # Messy
    'Diagnosis': ['Diabetes', 'Healthy', 'Diabetes', 'Healthy', 'None']
}
df = pd.DataFrame(data)

# 2. Text Cleaning
df['Gender'] = df['Gender'].str.lower().str.strip()
df['Diagnosis'] = df['Diagnosis'].str.lower().str.strip()
# Replace string 'none' with NaN
df.replace('none', np.nan, inplace=True)

# 3. Missing Values
# Categorical -> Mode
for col in ['Gender', 'Diagnosis']:
    mode_val = df[col].mode()[0]
    df[col].fillna(mode_val, inplace=True)

# Numeric -> Median
for col in ['Age', 'BloodPressure', 'Cholesterol']:
    median_val = df[col].median()
    df[col].fillna(median_val, inplace=True)

# 4. Outliers (IQR Method) on Cholesterol
Q1 = df['Cholesterol'].quantile(0.25)
Q3 = df['Cholesterol'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

# Filter
df_clean = df[(df['Cholesterol'] >= lower_bound) & (df['Cholesterol'] <= upper_bound)]

# 5. Encoding
df_encoded = pd.get_dummies(df_clean, columns=['Gender'], drop_first=True)

# 6. Scaling
scaler = MinMaxScaler()
cols_to_scale = ['Age', 'BloodPressure', 'Cholesterol']
df_encoded[cols_to_scale] = scaler.fit_transform(df_encoded[cols_to_scale])

print("Final Processed Data:")
print(df_encoded.head())
```

## How the pipeline works

### Loading the raw data

The script simulates `medical_raw.csv` with five patients, and the inline comments flag everything that is wrong with it: `Age` contains an `np.nan` plus a suspicious 120, `BloodPressure` contains an `np.nan`, `Cholesterol` contains a 900 ("# 900 is outlier"), `Gender` arrives in five different spellings (`'Female'`, `'male'`, `'Male'`, `'female'`, `'MALE'`), and `Diagnosis` uses the string `'None'` where a real missing value should be.

### Cleaning the text

`.str.lower().str.strip()` collapses all the gender spellings onto a single lowercase category — the text-normalization steps from [[Categorical Encoding and Text Normalization]] — and the same treatment is applied to `Diagnosis`. The subtle move is `df.replace('none', np.nan, inplace=True)`: the placeholder string `'none'` is converted into a genuine `NaN` so the imputation stage can see it. Missing data has to be identifiable before it can be filled.

### Imputing missing values

Categorical columns (`Gender`, `Diagnosis`) are filled with their mode and numeric columns (`Age`, `BloodPressure`, `Cholesterol`) with their median — the robust default choice from [[Missing Data and Imputation]].

### Removing outliers with the IQR rule

The pipeline computes `Q1`, `Q3` and `IQR = Q3 - Q1` for `Cholesterol` and keeps only the rows within `lower_bound = Q1 - 1.5 * IQR` and `upper_bound = Q3 + 1.5 * IQR` — the same IQR fence used in [[Outlier Detection and Treatment]]. The row flagged in the data comment (`Cholesterol = 900`) falls outside those bounds and is filtered out; since that same row also carries the questionable `Age = 120`, the Cholesterol filter removes it incidentally.

### Encoding the categorical column

`pd.get_dummies(df_clean, columns=['Gender'], drop_first=True)` one-hot encodes the cleaned gender column and drops the first level, which avoids the multicollinearity of the dummy variable trap.

### Scaling the numeric features

Finally a `MinMaxScaler` squeezes the numeric columns into [0, 1], per [[Feature Scaling and Normalization]]. Note that although the task highlights "Age" and "BloodPressure", the solution scales all three numeric columns — `Age`, `BloodPressure` and `Cholesterol` — so the final matrix is uniformly scaled, and `df_encoded.head()` previews the processed frame.

## Key insight

This script transforms raw, unusable data into a clean numeric matrix ready for machine learning, handling errors, missingness and scale differences automatically. Every stage is a small, reusable transformation — exactly the composition that scikit-learn's `Pipeline` and `ColumnTransformer` formalize when the same preprocessing has to be applied consistently to train and test splits.

## See also

- [[Python Language Overview]]
- [[Missing Data and Imputation]]
- [[Categorical Encoding and Text Normalization]]
- [[Outlier Detection and Treatment]]
- [[Feature Scaling and Normalization]]
- [[Duplicate Detection and Record Linkage]]
- [[Exercise - Hospital Data Project Setup]]
- [[Pandas]]
- [[NumPy]]
