---
title: Lists Tuples and Sets
type: concept
aliases:
  - Data Structures - Lists, Tuples, and Sets
  - "03. Data Structures - Lists, Tuples, and Sets"
  - Data Structures. Lists, Tuples, and Sets
  - Python data structures
tags:
  - python
  - data-structures
  - lists
  - tuples
  - sets
  - collections
  - indexing
  - slicing
sources:
  - "03. Data Structures - Lists, Tuples, and Sets"
created_index: 27
---

Data structures are containers that organize and store data, and choosing the right one is essential for memory efficiency and performance. This note covers the three core built-in collections: lists, the ordered and mutable workhorse; tuples, their immutable counterpart; and sets, the unordered container of unique elements with instant membership tests. The dictionary, the remaining core collection, is treated in [[Dictionaries]]; [[Python Language Overview]] maps the wider area.

## Lists

A list is an ordered, mutable (changeable) collection of items that allows duplicates. Its literal syntax is `my_list = [1, "two", 3.0]` — a single list can mix types, as the example shows.

### Indexing and slicing

Python uses 0-based indexing: `my_list[0]` is the first item, `my_list[-1]` the last, and `my_list[start:stop:step]` performs slicing.

```python
nums = [0, 1, 2, 3, 4, 5]
print(nums[1:4])    # [1, 2, 3] (Stop is exclusive)
print(nums[::2])    # [0, 2, 4] (Every second item)
print(nums[::-1])   # [5, 4, 3, 2, 1, 0] (Reverses list)
```

The three comments call out the behaviors that matter: the stop index is exclusive, a step of 2 takes every second item, and a negative step reverses the list.

### Key methods

The workhorse list methods are `.append(x)`, which adds x to the end; `.pop(i)`, which removes and returns the item at index i; and `.sort()`, which sorts the list in place.

## Tuples

A tuple is an ordered, **immutable** collection: once created, it cannot be changed. Its literal syntax is `my_tuple = (1, 2, 3)`. There are three reasons to reach for a tuple when the data does not need to change:

1. **Safety:** it ensures data isn't accidentally modified.
2. **Performance:** it is slightly faster than a list.
3. **Keys:** it can be used as a key in a dictionary — lists cannot.

### Unpacking

Tuples allow for variable assignment in a single line:

```python
coordinates = (4, 5)
x, y = coordinates  # x=4, y=5
```

## Sets

A set is an unordered, mutable collection of **unique** elements — no duplicates allowed. Its literal syntax is `my_set = {1, 2, 3}`.

### Use cases

The first classic use is **deduplication**: removing duplicates from a list. Converting the list to a set drops the duplicates, and converting back yields a clean list:

```python
raw_data = [1, 2, 2, 3, 3, 3]
unique_data = list(set(raw_data)) # [1, 2, 3]
```

The second is **membership testing**: checking `if x in my_set` is $O(1)$ (instant), whereas checking a list is $O(n)$ (slower as the list grows). This is the same distinction that makes the `in` operator of [[Variables Operators and Type Casting]] cheap on sets and expensive on lists.

### Set operations

Sets support the standard algebraic operations directly. **Union** (`|`) collects all elements from both sets, **intersection** (`&`) keeps only the elements present in both, and **difference** (`-`) keeps the elements in A but not in B.

## See also

- [[Python Language Overview]]
- [[Dictionaries]]
- [[Control Flow and Loops]]
- [[Variables Operators and Type Casting]]
- [[Iterators and Generators]]
- [[Functions and Lambda Expressions]]
- [[Duplicate Detection and Record Linkage]]
