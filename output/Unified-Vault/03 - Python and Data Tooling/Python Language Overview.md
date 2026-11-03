---
title: Python Language Overview
type: overview
aliases: [Python Overview, What is Python, Introduction to Python]
tags: [python, programming, data-science, overview]
sources:
  - "Python Language Overview"
created_index: 13
---

Python is the working language of data science and machine learning, and this note is the entry point to the whole Python and Data Tooling area. It covers what Python is, the language characteristics that shape how you will use it, why it came to dominate data work, and the Python 2 versus Python 3 split that still occasionally bites. The rest of the area builds on it: the language itself, the core libraries, the environment setup, and the data-cleaning practice.

## What is Python?

Python is a high-level, interpreted, general-purpose programming language. Created by **Guido van Rossum** and released in **1991**, it emphasizes code readability with its use of significant indentation.

> [!info] Design philosophy
> "There should be one-- and preferably only one --obvious way to do it."
> — *The Zen of Python (Tim Peters)*

That philosophy — one obvious way, enforced in practice by the language's syntax and its community conventions — is a large part of why Python code written by different people tends to look alike, which matters when notebooks and pipelines are shared across a team.

## Key characteristics

### Interpreted language

Unlike C++ or Java, which must be *compiled* into machine code before execution, Python code is processed at runtime by an **interpreter**.

- **Pros:** Rapid development (write → run → fix). No compilation step.
- **Cons:** Generally slower execution speed than compiled languages — though optimized libraries like [[NumPy]] mitigate this by doing the heavy lifting in compiled code.

### Dynamically typed

You do not need to declare the data type of a variable; the interpreter infers the type at runtime.

- *Static (Java):* `int x = 5;`
- *Dynamic (Python):* `x = 5`

Dynamic typing trades a class of compile-time safety for flexibility and speed of iteration — the trade-off data exploration usually wants.

### Multi-paradigm

Python supports multiple styles of programming:

- **Procedural:** organizing code into functions and tasks.
- **Object-oriented:** organizing code into classes and objects.
- **Functional:** treating computation as the evaluation of mathematical functions.

The notes on [[Functions and Lambda Expressions]] and [[Object Oriented Programming]] develop the paradigms you will use daily.

## Why Python for data science?

Python has overtaken R as the dominant language in data science. The reasons are structural rather than accidental:

1. **The ecosystem:** a massive collection of open-source libraries — [[NumPy]], [[Pandas]], Scikit-Learn — that solve almost every data problem imaginable.
2. **Glue language:** Python integrates easily with other languages (C/C++) and systems. High-performance libraries like TensorFlow are written in C++ but expose Python "wrappers," offering the speed of C++ with the ease of Python.
3. **Community:** a vast community means that for any error you encounter, a solution likely already exists on StackOverflow.
4. **Readability:** Python syntax resembles English, which lowers the barrier to entry for analysts and scientists who are not computer scientists by training.

## Python 2 versus Python 3

- **Python 2:** the legacy version. It reached end of life on January 1, 2020. **Do not use it.**
- **Python 3:** the current standard (specifically 3.10+). All modern data science libraries require Python 3.

The practical consequence is that any tutorial, code snippet or legacy pipeline you inherit that prints with the `print "..."` syntax or uses `xrange` is Python 2 and needs porting before it will run.

## Where this area goes

The Python and Data Tooling area is organized into four subfamilies, each building toward data work:

- **The language itself** — [[Variables Operators and Type Casting]], [[Control Flow and Loops]], [[Lists Tuples and Sets]], [[Dictionaries]], [[Functions and Lambda Expressions]], [[Object Oriented Programming]], [[Iterators and Generators]], [[Error Handling and Exceptions]], with exercises in [[Exercise - Sales Project Logic and OOP]].
- **The core libraries** — [[NumPy]], [[DataFrames]], [[Pandas]], [[Matplotlib]], [[Seaborn]], [[Plotly]], with exercises in [[Exercise - Temperature and Grade Analysis]].
- **Environment setup** — [[Installation and Distributions]], [[IDEs and Development Environments]], [[Virtual Environments and Package Management]], [[Project Structure and Best Practices]], [[Version Control with Git and GitHub]], with exercises in [[Exercise - Hospital Data Project Setup]].
- **Data cleaning and preprocessing** — [[Missing Data and Imputation]], [[Feature Scaling and Normalization]], [[Categorical Encoding and Text Normalization]], [[Outlier Detection and Treatment]], [[Duplicate Detection and Record Linkage]], with the capstone exercise [[Exercise - Medical Dataset Pipeline]].

Read the language notes first, then the libraries, then environment setup as your projects start needing it; the data-cleaning subfamily is the bridge into real datasets.

## See also

- [[Foundations MOC]] — the orientation map for the whole foundations layer.
- [[Mathematics MOC]] — the mathematical foundations that pair with these tooling skills.
- [[Pandas]] and [[NumPy]] — the two libraries you will reach for first.
