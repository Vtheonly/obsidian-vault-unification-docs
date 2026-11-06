---
title: Control Flow and Loops
type: concept
aliases:
  - Advanced Control Flow and Loops
  - "02. Advanced Control Flow and Loops"
  - Python conditionals and loops
tags:
  - python
  - control-flow
  - conditionals
  - loops
  - for-loop
  - while-loop
  - list-comprehensions
  - range
sources:
  - "02. Advanced Control Flow and Loops"
created_index: 21
---

Control flow is the order in which individual statements, instructions, or function calls are executed or evaluated. This note covers the tools Python gives you to direct that order: `if...elif...else` conditionals, the `for` and `while` loops together with `range()` and the `break`/`continue`/`pass` controls, and list comprehensions — a concise, faster way to build lists from iterables. It assumes the variable and operator basics of [[Variables Operators and Type Casting]]; [[Python Language Overview]] maps the wider area.

## Conditional logic

The `if...elif...else` structure allows the program to make decisions: conditions are tested in order, and the block belonging to the first true one runs.

```python
grade = 85

if grade >= 90:
    print("A")
elif grade >= 80:
    print("B")
else:
    print("Fail")
```

**Indentation is critical.** Python uses whitespace (4 spaces) to define the scope of the block.

## Loops

### The for loop

The `for` loop is used for iterating over a sequence — a list, tuple, dictionary, set, or string:

```python
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)
```

### The range() function

`range()` generates a sequence of numbers. Its syntax is `range(start, stop, step)`, and the stop value is exclusive: `range(5)` produces 0, 1, 2, 3, 4, while `range(1, 10, 2)` produces 1, 3, 5, 7, 9.

### The while loop

The `while` loop executes a set of statements as long as a condition is true:

```python
count = 0
while count < 5:
    print(count)
    count += 1  # Crucial: Increment to avoid infinite loops
```

The increment is crucial: without it, the condition would never become false and the loop would never end.

## Loop controls

Three statements fine-tune execution inside loops. **break** terminates the loop immediately. **continue** skips the rest of the current iteration and jumps to the next one. **pass** is a null operation — nothing happens — and is used as a placeholder for future code.

## List comprehensions

A list comprehension is a concise way to create lists. It is faster and more Pythonic than standard loops, and its syntax is:

`[expression for item in iterable if condition]`

As a worked example, create a list of squares for even numbers only. The old way builds the list with a loop, a condition and `append`:

```python
squares = []
for x in range(10):
    if x % 2 == 0:
        squares.append(x**2)
```

The Pythonic way collapses the same logic into a single expression:

```python
squares = [x**2 for x in range(10) if x % 2 == 0]
```

> [!tip] Performance
> List comprehensions are generally faster than `for` loops because the iteration is performed at C-language speed inside the interpreter.

## See also

- [[Python Language Overview]]
- [[Variables Operators and Type Casting]]
- [[Lists Tuples and Sets]]
- [[Dictionaries]]
- [[Functions and Lambda Expressions]]
- [[Iterators and Generators]]
- [[Exercise - Sales Project Logic and OOP]]
