---
title: Project Structure and Best Practices
type: concept
aliases:
  - Project Structure
  - Data Science Project Structure
  - Cookiecutter Data Science
  - Reproducible Project Structure
tags:
  - python
  - project-structure
  - best-practices
  - reproducibility
  - cookiecutter
  - naming-conventions
sources:
  - "06. Project Structure and Best Practices"
created_index: 10
---

Organizing a data science project correctly is crucial for reproducibility and collaboration. If you dump all your files into one folder, you will eventually lose track of which dataset is "clean" and which notebook is the "final" version. This note presents a standard directory layout (adapted from "Cookiecutter Data Science") together with the rules that keep it working: immutable raw data, exploration in notebooks but production in scripts, full documentation, and consistent naming. It anchors [[Python Language Overview]] alongside [[Virtual Environments and Package Management]] and [[Version Control with Git and GitHub]].

## Standard directory structure

A widely accepted standard (adapted from "Cookiecutter Data Science") looks like this:

```text
MyProject/
│
├── data/
│   ├── raw/            # Original, immutable data dump. NEVER edit this.
│   ├── processed/      # Cleaned data ready for modeling.
│   └── external/       # Data from third-party sources.
│
├── notebooks/          # Jupyter notebooks for exploration.
│   ├── 01_cleaning.ipynb
│   └── 02_analysis.ipynb
│
├── src/                # Source code (Python scripts).
│   ├── __init__.py     # Makes src a Python module.
│   ├── data_prep.py    # Functions to clean data.
│   └── visualization.py # Functions to plot graphs.
│
├── models/             # Trained models (pickles, h5 files).
│
├── env/                # Virtual Environment (Ignored by Git).
├── .gitignore          # Files to ignore.
├── README.md           # Documentation for the project.
└── requirements.txt    # List of dependencies.
```

The layout separates concerns so that nothing ambiguous ever ships. Raw, processed, and external data live in distinct subfolders of `data/`, so the provenance of every dataset is unambiguous. Exploration happens in numbered notebooks under `notebooks/`, while the code that survives exploration graduates to `src/` — the `__init__.py` file makes `src` a Python module, and scripts like `data_prep.py` and `visualization.py` hold the cleaning and plotting functions. Trained artifacts (pickles, h5 files) go to `models/`. The remaining files are infrastructure: `env/` is the virtual environment (ignored by Git), `.gitignore` lists what Git should skip, `README.md` documents the project, and `requirements.txt` records its dependencies — the pieces covered in [[Virtual Environments and Package Management]] and [[Version Control with Git and GitHub]].

## Key rules

### Data is immutable

Never manually edit a raw CSV file in Excel. Always write a script to clean it and save the result as a *new* file in `data/processed/`. This ensures you can always trace back to the source.

### Notebooks are for exploration, scripts are for production

Notebooks are great for visualizing data. However, if you copy-paste the same function into 5 different notebooks, you are creating technical debt. The sustainable workflow is:

1. Write code in a notebook.
2. Once it works, move the function to `src/my_script.py`.
3. Import the function back into the notebook (`from src.my_script import my_func`).

This is the same exploratory-versus-production split described in [[IDEs and Development Environments]], applied at the level of files rather than tools.

### Document everything

Your `README.md` should explain three things: what the project does, how to install dependencies, and how to run the code.

## Naming conventions

Consistent naming keeps a project navigable. Python files use `snake_case.py` and data files use `lower_case_with_underscores.csv`. Notebooks are numbered to show order — `01_load_data.ipynb`, `02_clean_data.ipynb` — so the exploration sequence is visible at a glance. Variables get descriptive names: `patient_age` is better than `x`.

## See also

- [[Python Language Overview]]
- [[Virtual Environments and Package Management]]
- [[Version Control with Git and GitHub]]
- [[IDEs and Development Environments]]
- [[The Data Science Workflow]]
