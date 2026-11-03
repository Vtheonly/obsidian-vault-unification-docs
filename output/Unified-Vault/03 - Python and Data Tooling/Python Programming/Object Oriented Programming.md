---
title: Object Oriented Programming
type: concept
aliases:
  - Object Oriented Programming (OOP) in Data Science
  - "06. Object Oriented Programming (OOP) in Data Science"
  - OOP in Data Science
  - OOP
  - Classes and Objects
  - Python Classes
tags:
  - python
  - object-oriented-programming
  - classes
  - objects
  - inheritance
  - encapsulation
  - dunder-methods
sources:
  - "06. Object Oriented Programming (OOP) in Data Science"
created_index: 28
---

Object oriented programming (OOP) is a programming paradigm based on the concept of **objects**, which contain data (attributes) and code (methods). A class acts as the blueprint from which objects are instantiated, and each instance carries its own data. This note covers the core vocabulary, the basic class syntax built around the constructor and `self`, and the tools that make the paradigm productive in practice: inheritance, the encapsulation naming conventions, and magic (dunder) methods. [[Python Language Overview]] maps the wider area.

## Classes and objects

Two terms anchor the paradigm. A **class** is the blueprint or template — `CarBlueprint` in the classic framing — while an **object** is a specific instance of the class, such as `MyRedToyota`. One class can be instantiated many times, and every instance is an independent object with its own data.

| Term | Meaning | Example |
| --- | --- | --- |
| Class | The blueprint or template | `CarBlueprint` |
| Object | A specific instance of the class | `MyRedToyota` |

## Basic syntax

A class definition opens with the `class` keyword and a name. Inside it, the constructor `__init__` runs when an instance is created and assigns the incoming arguments to attributes; further methods define behavior. Calling the class like a function creates instances:

```python
class Student:
    # The Constructor
    def __init__(self, name, age):
        self.name = name  # Attribute
        self.age = age    # Attribute

    # Method
    def introduce(self):
        return f"Hi, I am {self.name} and I am {self.age} years old."

# Creating Instances
s1 = Student("Alice", 20)
s2 = Student("Bob", 22)

print(s1.introduce())
```

### The `self` parameter

`self` represents the specific instance of the class. It allows each object to maintain its own data: `s1` and `s2` are both `Student` instances, yet each keeps its own `name` and `age`.

## Inheritance

Inheritance allows a class (the child) to derive attributes and methods from another class (the parent). This promotes code reuse: the child keeps everything the parent provides and adds its own attributes and methods on top. The child lists its parent in parentheses, extends the constructor with its own parameter, and delegates the shared setup to the parent with `super().__init__()`:

```python
class DataScientist(Student): # Inherits from Student
    def __init__(self, name, age, tool):
        super().__init__(name, age) # Initialize parent
        self.tool = tool

    def code(self):
        return f"{self.name} is coding in {self.tool}."
```

## Encapsulation

Encapsulation marks data as internal to the object. In Python, we denote private variables (internal use only) with an underscore `_`, and the naming yields three visibility levels:

| Notation | Visibility |
| --- | --- |
| `self.name` | Public |
| `self._password` | Protected (convention) |
| `self.__secret` | Private (Python name mangling) |

A public attribute like `self.name` is open to any caller. A single leading underscore signals "protected" — internal use, marked by convention. A double leading underscore makes the attribute private through Python's name mangling.

## Magic methods (dunder methods)

Magic methods — also called dunder methods — are special methods surrounded by double underscores. They allow objects to behave like built-in types. Three common ones:

| Method | Role |
| --- | --- |
| `__init__` | Constructor |
| `__str__` | Defines the string representation (for `print()`) |
| `__len__` | Defines behavior for `len()` |

Adding a `__str__` method to the `Student` class defines what `print()` shows for an instance:

```python
def __str__(self):
    return f"Student({self.name})"
```

## See also

- [[Python Language Overview]]
- [[Functions and Lambda Expressions]]
- [[Iterators and Generators]]
- [[Exercise - Sales Project Logic and OOP]]
