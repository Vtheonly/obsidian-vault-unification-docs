---
title: Dictionaries
type: concept
aliases:
  - Dictionaries and Key Value Management
  - "04. Dictionaries and Key Value Management"
  - Python Dictionaries
  - dict
  - Key-Value Management
tags:
  - python
  - data-structures
  - dictionaries
  - key-value-pairs
  - dictionary-comprehension
sources:
  - "04. Dictionaries and Key Value Management"
created_index: 22
---

A dictionary is an unordered, mutable collection of key-value pairs: Python's built-in way of mapping keys to values. Because data is retrieved by key rather than by position, dictionaries are the natural container for labelled records — a student's name and grades, for instance. This note covers the rules that govern keys and values, the two access patterns (bracket indexing and the safe `.get()` method), in-place modification, the three iteration styles, and dictionary comprehensions. [[Python Language Overview]] maps the wider area; the other core collections are treated in [[Lists Tuples and Sets]].

## What a dictionary is

A **dictionary** is an unordered, mutable collection of key-value pairs. The constraints sit on the keys: each key must be unique and immutable, which is why strings, numbers, and tuples are the admissible key types, while values can be any object. The literal syntax assigns values to keys inside curly braces: `my_dict = {"name": "Alice", "age": 25}`.

| Aspect | Rule |
| --- | --- |
| Ordering | Unordered |
| Mutability | Mutable |
| Keys | Must be unique and immutable (strings, numbers, tuples) |
| Values | Can be any object |

## Accessing data

The standard access pattern indexes the dictionary by key with square brackets. It works only when the key exists — reading a missing key raises a `KeyError` rather than returning a fallback (see [[Error Handling and Exceptions]] for the exception machinery):

```python
student = {
    "name": "John",
    "grades": [85, 90, 88]
}

# Standard Access
print(student["name"])  # "John"

# Error Handling
# print(student["gender"]) -> Raises KeyError because key doesn't exist
```

### The `.get()` method

The `.get()` method safely accesses a key: if the key is missing, it returns `None` (or a default value) instead of crashing. Passing the default as the second argument makes the fallback explicit:

```python
print(student.get("gender", "Unknown"))  # Returns "Unknown"
```

## Modifying dictionaries

Dictionaries are mutable, so their contents change in place. Assignment to a key adds a new pair when the key is absent and updates the value when it is present, while `del` removes a pair entirely:

- **Add/Update:** `student["age"] = 22`
- **Delete:** `del student["grades"]`

## Iteration

When looping through a dictionary, you have three options: the keys alone, the values alone, or both together. Iterating over the dictionary directly yields the keys.

### Keys (the default)

Looping over the dictionary object itself produces its keys:

```python
for k in student:
    print(k)
```

### Values

Calling `.values()` in the loop produces the values:

```python
for v in student.values():
    print(v)
```

### Items (both)

Calling `.items()` produces key-value pairs that unpack into two loop variables, one of the loop patterns covered in [[Control Flow and Loops]]:

```python
for k, v in student.items():
    print(f"{k}: {v}")
```

## Dictionary comprehensions

Dictionary comprehensions are similar to list comprehensions, but for creating dictionaries: a `{key: value}` expression is built for each iteration step. The classic pattern zips two parallel lists into a single mapping from keys to values:

```python
keys = ['a', 'b', 'c']
values = [1, 2, 3]

# Create dict mapping key to value
my_dict = {k: v for k, v in zip(keys, values)}
# Result: {'a': 1, 'b': 2, 'c': 3}
```

## See also

- [[Python Language Overview]]
- [[Lists Tuples and Sets]]
- [[Control Flow and Loops]]
- [[Iterators and Generators]]
- [[Functions and Lambda Expressions]]
- [[Error Handling and Exceptions]]
