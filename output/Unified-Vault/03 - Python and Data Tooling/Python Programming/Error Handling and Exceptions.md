---
title: Error Handling and Exceptions
type: concept
aliases:
  - Error Handling and Exception Management
  - Exception Handling
  - Python Exceptions
  - try...except
tags:
  - python
  - error-handling
  - exceptions
  - try-except
  - defensive-programming
sources:
  - "08. Error Handling and Exception Management"
created_index: 23
---

Robust code does not crash when it encounters unexpected input — it catches errors and handles them gracefully. Python's exception mechanism makes this possible: the `try...except` block intercepts failures at runtime, a small set of built-in exception types names the most common mistakes, and the `raise` statement lets your own code reject invalid input deliberately.

## The `try...except` block

The pattern wraps the code that might crash in a `try` block. If a specific error occurs while that block runs, control passes to the `except` clause naming that error, and its handler code runs instead of letting the program crash. Multiple `except` clauses can be stacked to respond to different failures differently. Two optional clauses complete the pattern: `else` runs only if no exception occurred, and `finally` runs always — regardless of success or failure — which makes it the natural place for cleanup work such as closing files.

```python
try:
    # Code that might crash
    numerator = 10
    denominator = 0
    result = numerator / denominator
except ZeroDivisionError:
    # Code that runs if the specific error occurs
    print("Error: You cannot divide by zero.")
except TypeError:
    print("Error: Inputs must be numbers.")
else:
    # Runs ONLY if no exception occurred
    print(f"Success! Result is {result}")
finally:
    # Runs ALWAYS (good for cleanup, closing files)
    print("Execution finished.")
```

In this example the division of `10` by `0` triggers the `ZeroDivisionError` handler, so its message prints and the `else` block is skipped; the `finally` block still prints its message. Had the inputs been of the wrong type instead, the `TypeError` handler would have caught that case with its own message. Alongside `if` statements and loops (see [[Control Flow and Loops]]), `try...except` is one of the constructs that determines which code runs next.

## Common Python exceptions

Python's built-in exceptions have descriptive names, and the same small set accounts for most of the errors a program produces. Knowing them by sight makes error messages immediately interpretable:

| Exception | What it means |
| --- | --- |
| `SyntaxError` | You wrote invalid Python code (e.g., missing `:`). |
| `NameError` | Variable not defined. |
| `TypeError` | Operation applied to object of inappropriate type (e.g., `"5" + 5`). |
| `ValueError` | Function receives argument of correct type but inappropriate value (e.g., `int("hello")`). |
| `KeyError` | Dictionary key not found. |
| `IndexError` | List index out of range. |

`TypeError` and `ValueError` are worth distinguishing carefully. A `TypeError` means the type itself is inappropriate for the operation — `"5" + 5` tries to combine a string with a number. A `ValueError` means the type is acceptable but the value is not: in `int("hello")` the argument is a string, the kind of input `int()` works with, but its particular content cannot be converted to a number. The last two entries are lookup failures from the core data structures: `KeyError` is raised when a dictionary key is missing (see [[Dictionaries]]), and `IndexError` when a list index falls outside the list's range (see [[Lists Tuples and Sets]]).

## Raising exceptions

Exceptions are not only something you catch — you can force an error to occur if specific conditions are met using `raise`. This is how a function defends itself against nonsensical input: rather than continuing with data that makes no sense, it stops and reports the problem with a clear message.

```python
def check_age(age):
    if age < 0:
        raise ValueError("Age cannot be negative.")
    return True
```

`check_age` validates its argument and raises a `ValueError` carrying a human-readable explanation whenever the age is negative. The choice of exception type is deliberate: a negative age is an integer — the correct type — but an inappropriate value, which is precisely the situation `ValueError` describes. A caller that wants to recover rather than crash can wrap the call in its own `try...except` block; see [[Functions and Lambda Expressions]] for the function definitions this pattern builds on.

## See also

- [[Python Language Overview]]
- [[Control Flow and Loops]]
- [[Functions and Lambda Expressions]]
- [[Dictionaries]]
- [[Lists Tuples and Sets]]
