---
title: Variables Operators and Type Casting
type: concept
aliases:
  - Variables, Operators, and Type Casting
  - "01. Variables, Operators, and Type Casting"
  - Python variables and operators
  - Type casting
  - Type conversion
tags:
  - python
  - variables
  - operators
  - type-casting
  - data-types
  - dynamic-typing
  - pep8
sources:
  - "01. Variables, Operators, and Type Casting"
created_index: 29
---

Every Python program binds objects to names, combines them with operators, and occasionally needs to move a value from one type to another. This note covers the three foundations of that mechanics: variables under Python's dynamic typing, the arithmetic, comparison, logical and membership operators, and type casting in both its implicit and explicit forms. It is the entry point of the Python Programming subfamily — [[Python Language Overview]] maps the whole area — and everything built on these basics, from [[Control Flow and Loops]] to [[Functions and Lambda Expressions]], assumes them.

## Variables and dynamic typing

In Python, a variable is a symbolic name that is a reference or pointer to an object. Once an object is assigned to a variable, you can refer to the object by that name. Unlike statically typed languages (like C++ or Java), Python is **dynamically typed**: you do not declare the type of the variable; the interpreter infers it at runtime based on the value assigned. Reassignment is allowed, so the same name can later point to an object of a completely different type:

```python
x = 5           # x is an integer
x = "Hello"     # x is now a string (Reassignment is allowed)
```

### Naming conventions (PEP 8)

Python's style guide fixes three naming conventions. Variables and functions use `snake_case`, as in `student_age` or `calculate_mean`. Constants use `UPPER_CASE`, as in `MAX_ITERATIONS` or `PI`. Classes use `PascalCase`, as in `LinearRegression` or `DataFrame`.

## Standard data types

The core built-in types cover whole numbers, decimals, text, truth values and "no value at all":

| Type | Name | Example | Description |
| :--- | :--- | :--- | :--- |
| **int** | Integer | `42`, `-5` | Whole numbers without decimals. |
| **float** | Floating Point | `3.14`, `1.0` | Numbers with decimals. Note: `1` is an int, `1.0` is a float. |
| **str** | String | `"Python"`, `'Data'` | Sequence of characters. Immutable. |
| **bool** | Boolean | `True`, `False` | Logical truth values. Capitalization matters. |
| **NoneType** | None | `None` | Represents the absence of a value (null). |

Two details in this table deserve emphasis: `1` and `1.0` are different types (int versus float), and boolean literals must be capitalized — `True` and `False`. Strings are immutable, and `None` is Python's null, representing the absence of a value.

## Operators

Operators combine values into expressions. Python organizes them into four families relevant here: arithmetic, comparison, logical and membership.

### Arithmetic operators

`+`, `-` and `*` are the standard addition, subtraction and multiplication. Division comes in two flavors: `/` is **true division** and always returns a float, so `10 / 2` gives `5.0`, while `//` is **floor division** and truncates the decimal part, so `10 // 3` gives `3`. The **modulus** operator `%` returns the remainder, so `10 % 3` gives `1`; it is useful for checking even/odd numbers. Finally, `**` is **exponentiation** — power — so `2 ** 3` gives `8`.

### Comparison operators

Comparison operators return a `bool` (`True` or `False`). `==` tests equal to, `!=` tests not equal to, and `>`, `<`, `>=`, `<=` provide the greater/less than logic. These comparisons are the raw material of the conditional statements covered in [[Control Flow and Loops]].

### Logical operators

Logical operators are used to combine conditional statements. `and` returns `True` if both statements are true, `or` returns `True` if at least one statement is true, and `not` reverses the result.

### Membership operators

The `in` operator returns `True` if a sequence with the specified value is present in the object:

```python
x = ["apple", "banana"]
print("banana" in x) # True
```

How expensive this test is depends on the container: it is instant on sets and slows down as a list grows, a distinction developed in [[Lists Tuples and Sets]].

## Type casting (conversion)

Type casting converts a variable from one data type to another. It happens in two ways in Python: implicitly, when the interpreter widens a type automatically, and explicitly, when you force the conversion yourself.

### Implicit conversion

Python automatically converts types when it makes sense without losing data. Mixing an int and a float in an arithmetic expression promotes the result to a float with no programmer intervention:

```python
x = 10      # int
y = 2.5     # float
z = x + y   # z becomes 12.5 (float) automatically
```

### Explicit conversion

Explicit conversion manually forces a type change using the built-in constructor functions:

- **int()** truncates floats: `int(3.9)` -> `3`.
- **float()** adds the decimal: `float(3)` -> `3.0`.
- **str()** converts any object to its string representation: `str(100)` -> `"100"`.
- **bool()** returns `False` for `0`, empty containers, or `None`; it returns `True` for everything else.

> [!warning] Data loss
> Converting a string to an int (`int("hello")`) will raise a `ValueError`.

Because a failed cast raises an exception, robust code wraps explicit conversions in `try`/`except` — the techniques covered in [[Error Handling and Exceptions]] and exercised end-to-end in [[Exercise - Sales Project Logic and OOP]].

## See also

- [[Python Language Overview]]
- [[Control Flow and Loops]]
- [[Lists Tuples and Sets]]
- [[Dictionaries]]
- [[Functions and Lambda Expressions]]
- [[Error Handling and Exceptions]]
- [[Exercise - Sales Project Logic and OOP]]
