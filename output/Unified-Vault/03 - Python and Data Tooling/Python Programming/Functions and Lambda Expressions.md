---
title: Functions and Lambda Expressions
type: concept
aliases:
  - Functions and Lambdas
  - "05. Functions and Lambda Expressions"
  - Python Functions
  - Lambda Expressions
  - Anonymous Functions
tags:
  - python
  - functions
  - lambda
  - anonymous-functions
  - higher-order-functions
  - default-arguments
sources:
  - "05. Functions and Lambda Expressions"
created_index: 25
---

Functions are reusable blocks of code: they wrap a piece of logic under a name so it can be called wherever needed, which helps them adhere to the **DRY principle** (Don't Repeat Yourself). This note covers how functions are defined and documented, the distinction between parameters and arguments, returning multiple values via tuples, default arguments together with the mutable-default pitfall, and lambda expressions — the small, anonymous functions that are best used as arguments to higher-order functions such as `map` and `filter`. [[Python Language Overview]] maps the wider area.

## Defining functions

A function definition opens with the `def` keyword, the function's name, and a parameter list in parentheses, followed by an indented body. A string literal placed immediately under the signature serves as the docstring, recording what the function does, its arguments, and its return type. The example below calculates the average of a list of numbers, guarding the empty-list case by returning `0`:

```python
def calculate_mean(numbers):
    """
    Docstring: Calculates the average of a list of numbers.
    Args: numbers (list)
    Returns: float
    """
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)
```

### Parameters versus arguments

The two words describe the same slot at two different moments. A **parameter** is the variable listed inside the parentheses in the function definition (`numbers`); an **argument** is the value sent to the function when it is called (`[1, 2, 3]`).

| Term | Where it lives | Example |
| --- | --- | --- |
| Parameter | The function definition, inside the parentheses | `numbers` |
| Argument | The function call, as the value passed in | `[1, 2, 3]` |

### Return values

Python functions can return multiple values using tuples: listing several expressions after `return` packs them into a tuple, and the caller unpacks the result into separate variables:

```python
def get_stats(nums):
    return min(nums), max(nums)

low, high = get_stats([10, 20, 30]) # Unpacking result
```

## Default arguments and keywords

A parameter can be given a default value with `=` in the definition. The caller may omit the argument — the default is then used — or supply a value to override it:

```python
def greet(name, message="Hello"):
    print(f"{message}, {name}")

greet("Alice")           # Uses default: "Hello, Alice"
greet("Bob", "Goodbye")  # Overrides default: "Goodbye, Bob"
```

> [!warning] Mutable defaults
> Never use a mutable object (like a list) as a default argument. It retains values between calls. Use `None` instead.

## Lambda expressions

A **lambda** is a small, anonymous function defined with the `lambda` keyword. It can take any number of arguments, but can only have **one expression**, whose value becomes the function's result. The syntax is `lambda arguments : expression`.

### Lambdas versus standard functions

Every lambda has an equivalent standard function; the difference is form, not capability. A standard function carries a name, a docstring, and room for multiple statements, while a lambda collapses everything into a single expression. Squaring a number both ways:

```python
def square(x):
    return x ** 2
```

```python
square = lambda x: x ** 2
```

### Practical use with `map` and `filter`

Lambdas are best used as arguments to higher-order functions. `map` applies a function to all items, and `filter` keeps the items where the function returns `True`:

```python
nums = [1, 2, 3, 4]

# Map: Apply function to all items
squared = list(map(lambda x: x**2, nums))  # [1, 4, 9, 16]

# Filter: Keep items where function returns True
evens = list(filter(lambda x: x%2 == 0, nums)) # [2, 4]
```

## See also

- [[Python Language Overview]]
- [[Control Flow and Loops]]
- [[Iterators and Generators]]
- [[Lists Tuples and Sets]]
- [[Dictionaries]]
- [[Object Oriented Programming]]
- [[Error Handling and Exceptions]]
