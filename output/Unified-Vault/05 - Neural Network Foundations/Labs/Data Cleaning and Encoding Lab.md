---
title: Data Cleaning and Encoding Lab
type: tutorial
aliases:
  - Lab 3 Data Cleaning
  - "Lab 3: Data Cleaning, Normalization, and Encoding"
  - TP3
  - "Data Cleaning, Normalization, and Encoding Lab"
tags:
  - data-preparation
  - data-cleaning
  - normalization
  - feature-encoding
  - one-hot-encoding
  - pandas
  - scikit-learn
  - tutorial
sources:
  - "02. TP3 - Data Cleaning, Normalization, and Encoding - Solution Guide"
created_index: 7
---

This lab takes a raw, messy dataset — `students.csv`, a small table of student records — and prepares it for a machine learning model by performing the essential preprocessing steps: data cleaning, normalization, and encoding. It walks through the "Apprentissage Automatique" Lab 3 (French for machine learning) as a step-by-step guide of what to do and what not to do, fixing each classic data quality problem in a logical order. The payoff is a dataset that is clean, fully numeric, and appropriately scaled — exactly the shape a learning algorithm expects — and it is the hands-on counterpart of [[Data Preparation for Neural Networks]] within the [[Neural Network Foundations MOC]], next to the sibling [[Formal Neuron Lab]].

## Project structure

The lab lives in a single project folder, and it is worth laying that folder out before touching any data:

```text
/your-project-folder
|-- venv/                  # Your Python virtual environment
|-- students.csv           # The dataset file
|-- lab3_solution.ipynb    # The Jupyter Notebook with the solution
|-- README.md              # This guide
```

The `venv/` directory holds your Python virtual environment, `students.csv` is the dataset file, `lab3_solution.ipynb` is the Jupyter Notebook with the solution, and `README.md` is the guide itself. With the structure in place, the lab requires us to address several common data quality issues, and we will tackle them in a logical order: loading and inspection first, then cleaning, then normalization, and finally encoding.

## Load and inspect the dataset

Start by importing the necessary libraries, `pandas` and `numpy`, and loading the `students.csv` dataset into a pandas DataFrame. Do not clean anything yet — first use `df.head()` to inspect the first few rows, and `df.info()` to get a summary of the data types and non-null values. This initial inspection is crucial for understanding what problems exist; on the sample dataset below, it is how you notice the empty cells, the negative age, and the repeated rows.

## Clean the data

Cleaning is the most critical part of the lab, where we fix the "dirty" data. Three distinct defects call for three distinct treatments: completely identical rows, impossible values (the negative ages), and missing values (NaN). Each has a recommended fix and a tempting shortcut to avoid.

### Handling duplicates

The dataset contains completely identical rows, and these can bias a machine learning model by giving more weight to the duplicated samples — in the sample data, Alice's and Frank's rows each appear twice. The fix is two commands. First, `df.duplicated().sum()` counts how many duplicate rows exist; second, `df.drop_duplicates(inplace=True)` removes them permanently from our DataFrame. The `inplace=True` argument modifies the DataFrame directly, saving us from having to reassign it (e.g., `df = df.drop_duplicates()`).

> [!warning] What not to do
> Don't ignore duplicates. They are a common and easy-to-fix issue that can improve model performance.

### Handling irrelevant or invalid data (the negative ages problem)

The lab description mentions "irrelevant data (like negative ages)", and an age cannot be negative: such a row is a data entry error and represents impossible, invalid data — David is recorded with age -22 in the sample dataset. First identify these rows; a simple filter like `df[df['Age'] < 0]` will show them. Then decide on a strategy: removing the rows is the safest option if there are only a few, while replacing the value with the mean or median age assumes the rest of the data in that row is valuable and the error was isolated to the age — for this lab, removal is cleaner. We filter the DataFrame to keep only rows where Age is positive: `df = df[df['Age'] >= 0]`.

> [!warning] What not to do
> Don't just take the absolute value (e.g., `-22` becomes `22`). We don't know if `22` is the correct age, so it's safer to discard the invalid entry.

### Handling missing values (NaN)

Some cells in the dataset are empty (represented as `NaN`), and machine learning algorithms cannot process `NaN` values, so we must handle them — in the sample data, Eve and Oscar are missing a Score and Heidi is missing an Age. Use `df.isnull().sum()` to see which columns have missing values and how many, then choose a strategy based on the column. For the 'Score' column, a numerical value, a good strategy is imputation: fill the missing values with the mean or median score of the column — using the mean is simple and often effective, `df['Score'].fillna(df['Score'].mean(), inplace=True)`. For other columns, if a row has many missing values, or if a crucial piece of information (like `Name` or `Gender`) is missing, it might be better to drop the entire row using `df.dropna(inplace=True)`.

> [!warning] What not to do
> Don't drop every row that has a single missing value without thinking. You might lose a significant portion of your dataset. Always analyze the impact before dropping data.

## Normalize the age column with min-max scaling

Features can have vastly different scales: 'Age' might range from 18-40, while 'Score' ranges from 0-100. Algorithms that rely on distance calculations (like K-NN or SVM) can be biased by the feature with the larger range. Normalization addresses this by rescaling numerical features onto a common footing, and the conceptual background is developed in [[Data Preparation for Neural Networks]].

We will use Min-Max Scaling on the 'Age' column as instructed. This technique rescales the data to a fixed range, usually [0, 1]. The steps are: import `MinMaxScaler` from `sklearn.preprocessing`; create an instance of the scaler, `scaler = MinMaxScaler()`; and apply it to the 'Age' column:

```python
df['Age'] = scaler.fit_transform(df[['Age']])
```

Note the double square brackets around 'Age' in that call, which are required because the scaler expects a 2D array-like input rather than a 1D Series.

> [!warning] What not to do
> Don't normalize categorical data that has been encoded (like 'Gender' or 'City'). Normalization is intended for numerical features.

## Encode the categorical variables

Most machine learning models only understand numbers, not text categories like "Male", "Female", or "New York", so we need to convert these text labels into numbers. The right conversion depends on the column: a binary category can be label-encoded, while a multi-category column needs one-hot encoding. Using the wrong technique quietly injects a fake ordering into the data.

### Label encoding for gender

'Gender' has two categories ("Male", "Female"), and Label Encoding will convert them to `0` and `1`, which is acceptable for binary categories. Import `LabelEncoder`, then apply it: `df['Gender'] = encoder.fit_transform(df['Gender'])`. In the solution script the encoder is named `le`, and a commented-out line shows how to recover the mapping: `le.classes_` will show `['Female', 'Male']`, so 0 is Female and 1 is Male.

### One-hot encoding for city

'City' has multiple categories (e.g., "New York", "London", "Tokyo"). If we used Label Encoding here (0, 1, 2), the model might incorrectly assume an ordered relationship — i.e., Tokyo > London > New York. One-Hot Encoding is the correct technique here: it creates a new binary column for each city, and the simple pandas function `pd.get_dummies()` does the job: `df = pd.get_dummies(df, columns=['City'], drop_first=True)`. The `drop_first=True` is important to avoid multicollinearity, a situation where features are highly correlated, which can be an issue for some models.

## The final result

After all these steps, our dataset will be clean, fully numeric, and scaled appropriately, making it ready to be fed into a machine learning algorithm. Concretely: the duplicate rows and the negative age are gone, the missing scores have been imputed and the row with a missing age has been dropped, 'Age' has been rescaled into [0, 1], 'Gender' is a 0/1 column, and each city contributes its own binary column. That is the input format the models described in [[Artificial Neural Networks]] expect.

## The sample dataset

First, you need the `students.csv` file; when it isn't provided, a sample one that includes all the problems mentioned in the lab can be used instead. It plants exactly one of each defect: two duplicate rows (Alice's and Frank's), one negative age (David, -22), two missing Scores (Eve and Oscar), and one missing Age (Heidi). Save this text into a file named `students.csv` in your project folder.

```csv
Name,Age,Gender,Score,Grade,City
Alice,22,Female,85,A,New York
Bob,23,Male,90,A,London
Charlie,21,Male,78,B,Tokyo
David,-22,Male,92,A,New York
Eve,24,Female,,B,Paris
Frank,23,Male,88,A,London
Alice,22,Female,85,A,New York
Grace,25,Female,95,A,Tokyo
Heidi,,Female,82,B,Paris
Ivan,22,Male,79,B,New York
Judy,24,Female,91,A,London
Frank,23,Male,88,A,London
Mallory,21,Male,65,C,Tokyo
Nancy,23,Female,89,A,Paris
Oscar,22,Male,,B,New York
```

## The complete solution script

The solution can be saved as `lab3_solution.py` or run as a Jupyter Notebook (`lab3_solution.ipynb`). It is the complete, commented Python code to execute the lab steps.

```python
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, LabelEncoder

# --- 1. Import basic libraries and Load the dataset ---
print("--- Step 1 & 2: Loading dataset and initial inspection ---")
try:
    df = pd.read_csv('students.csv')
    print("Dataset loaded successfully.")
except FileNotFoundError:
    print("Error: students.csv not found. Make sure the file is in the same directory.")
    exit()

print("\nOriginal DataFrame head:")
print(df.head())

print("\nOriginal DataFrame info:")
df.info()

# --- 3. Check for duplicates and remove them ---
print("\n--- Step 3: Checking for and removing duplicates ---")
num_duplicates = df.duplicated().sum()
print(f"Number of duplicate rows found: {num_duplicates}")

# Displaying the duplicate rows before removing them
print("\nDuplicate rows:")
print(df[df.duplicated()])

# Removing duplicates
df.drop_duplicates(inplace=True)
print(f"\nNumber of rows after dropping duplicates: {len(df)}")


# --- Adding a step to handle irrelevant data (negative ages) ---
# This was mentioned in the lab description but not in the code examples.
print("\n--- Bonus Step: Handling Invalid Data (e.g., Negative Age) ---")
invalid_age_rows = df[df['Age'] < 0]
print(f"Number of rows with invalid (negative) age: {len(invalid_age_rows)}")
if not invalid_age_rows.empty:
    print("Rows with negative age:")
    print(invalid_age_rows)

    # Filter out rows with negative age
    df = df[df['Age'] >= 0]
    print(f"\nNumber of rows after removing invalid ages: {len(df)}")


# --- 4. Check for missing data and process them ---
print("\n--- Step 4: Checking for and handling missing data ---")
print("Missing values before handling:")
print(df.isnull().sum())

# Strategy 1: Imputation for 'Score' (numerical column)
# We fill missing scores with the mean of the existing scores.
score_mean = df['Score'].mean()
print(f"\n'Score' column mean is: {score_mean:.2f}. Using this for imputation.")
df['Score'].fillna(score_mean, inplace=True)

# Strategy 2: Drop rows where other crucial data might be missing (like 'Age')
# The dropna() function is a simple way to remove any remaining rows with NaN.
df.dropna(inplace=True)
# Note: In our case, after handling Score, dropna() will handle the missing 'Age'.

print("\nMissing values after handling:")
print(df.isnull().sum())
print(f"\nNumber of rows after handling all missing values: {len(df)}")


# --- Data Normalization ---
print("\n--- Step 5: Data Normalization (Min-Max Scaling on 'Age') ---")
print("'Age' column before normalization:")
print(df[['Name', 'Age']].head())

# Initialize the scaler
scaler = MinMaxScaler()

# Reshape the data and apply the scaler
# We use df[['Age']] to select the column as a DataFrame (2D), which the scaler expects
df['Age'] = scaler.fit_transform(df[['Age']])

print("\n'Age' column after Min-Max Scaling:")
print(df[['Name', 'Age']].head())


# --- Data Encoding ---
print("\n--- Step 6: Data Encoding (Categorical to Numerical) ---")

# --- Label Encoding for 'Gender' ---
print("\nEncoding 'Gender' column using Label Encoding...")
print("'Gender' column before encoding:")
print(df['Gender'].head())

le = LabelEncoder()
df['Gender'] = le.fit_transform(df['Gender'])
# To see which number corresponds to which label:
# print(le.classes_) # Will show ['Female', 'Male'] -> 0 is Female, 1 is Male

print("\n'Gender' column after Label Encoding:")
print(df['Gender'].head())


# --- One-Hot Encoding for 'City' ---
print("\nEncoding 'City' column using One-Hot Encoding...")
print("DataFrame shape before One-Hot Encoding:", df.shape)
print("Original columns:", df.columns.tolist())

# Use pandas get_dummies for one-hot encoding
# drop_first=True helps prevent multicollinearity in some models
df = pd.get_dummies(df, columns=['City'], drop_first=True)

print("\nDataFrame shape after One-Hot Encoding:", df.shape)
print("New columns:", df.columns.tolist())


# --- Final Cleaned DataFrame ---
print("\n--- Final, Cleaned, Normalized, and Encoded DataFrame ---")
print(df.head())

print("\nFinal DataFrame info:")
df.info()
print("\nLab successfully completed!")
```

### How the script runs the walkthrough

The script loads the dataset inside a `try/except FileNotFoundError` that prints "Error: students.csv not found. Make sure the file is in the same directory." and exits when the file is missing, then shows the original head and info before changing anything. It counts the duplicate rows, displays the duplicate rows before removing them, and prints the number of rows after each operation, so the dataset's shrinking is visible step by step. The negative-age handling appears as a bonus step — it was mentioned in the lab description but not in the code examples — and the filtering sits inside an `if not invalid_age_rows.empty:` guard, so it only fires when invalid rows actually exist.

For the missing values, the script first imputes 'Score' with the column mean (printing the mean it is using, to two decimals) and then calls `df.dropna()` to remove any remaining rows with NaN — with the note that, in our case, after handling Score, dropna() will handle the missing 'Age'. The normalization block prints the 'Age' column (alongside 'Name') before and after Min-Max Scaling so the rescaling is visible. The encoding block prints 'Gender' before and after Label Encoding, then the DataFrame's shape and column list before and after One-Hot Encoding, and the script closes by printing the head and info of the final, cleaned, normalized, and encoded DataFrame, followed by "Lab successfully completed!".

## See also

- [[Neural Network Foundations MOC]]
- [[Data Preparation for Neural Networks]] — the conceptual treatment of cleaning, scaling, and encoding
- [[Formal Neuron Lab]] — the sibling lab implementing the formal neuron and its activations
- [[Artificial Neural Networks]] — the models that consume the prepared data
- [[Perceptrons and Multi-Layer Perceptrons]] — the trainable units on the other side of preprocessing
