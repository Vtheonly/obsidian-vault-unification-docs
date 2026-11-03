---
title: Iterators and Generators
type: concept
aliases:
  - Iterators, Generators, and Memory Efficiency
  - "07. Iterators, Generators, and Memory Efficiency"
  - Generators and Yield
  - Python Iterators
  - Lazy Evaluation
tags:
  - python
  - iterators
  - generators
  - yield
  - lazy-evaluation
  - memory-efficiency
sources:
  - "07. Iterators, Generators, and Memory Efficiency"
created_index: 26
---

In data science we often handle datasets larger than our computer's RAM — loading a 100GB file into a standard list will crash the system. **Generators** solve this by producing values one at a time instead of materializing the whole collection in memory. This note distinguishes iterables from iterators, shows how generator functions use `yield` for lazy evaluation, and quantifies the memory advantage over eager lists; [[Python Language Overview]] maps the wider area.

## Iterables versus iterators

The two terms are related but distinct. An **iterable** is an object capable of returning its members one at a time — a list or a string, for example. An **iterator** is an object representing a stream of data: it returns data one element at a time using `__next__()`, one of the double-underscore methods that let objects behave like built-in types (see [[Object Oriented Programming]]).

| Concept | What it is |
| --- | --- |
| Iterable | An object capable of returning its members one at a time (e.g., list, string) |
| Iterator | An object representing a stream of data; it returns data one element at a time using `__next__()` |

## Generators and `yield`

A generator is a function that returns an iterator. Instead of returning a single value and exiting, it **yields** a series of values, pausing execution after each one until the next value is requested. The contrast is easiest to see when the same task is written both ways.

### Standard function (eager evaluation)

A standard function builds the entire list in memory and returns it — eager evaluation:

```python
def get_squares(n):
    result = []
    for i in range(n):
        result.append(i**2)
    return result
```

### Generator (lazy evaluation)

The generator version generates one item at a time, with zero memory overhead for storage — lazy evaluation:

```python
def get_squares_gen(n):
    for i in range(n):
        yield i**2
```

## Memory comparison

The difference matters at scale. If `n = 1,000,000`:

| Approach | What is stored | Footprint |
| --- | --- | --- |
| List | 1 million integers in RAM | ~40MB |
| Generator | Only the current integer and the formula | ~100 Bytes |

The list returned by the eager function holds every square in RAM at once, while the generator keeps only the current integer and the formula that produces the next value.

> [!tip] Use generators for large data
> Always use generators when processing large files (e.g., reading a CSV line-by-line) or streaming data.

## See also

- [[Python Language Overview]]
- [[Functions and Lambda Expressions]]
- [[Control Flow and Loops]]
- [[Lists Tuples and Sets]]
- [[Dictionaries]]
- [[Object Oriented Programming]]
- [[Pandas]]
