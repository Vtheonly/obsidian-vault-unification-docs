---
title: Exercise - Sales Project Logic and OOP
type: tutorial
aliases:
  - Exercise 3 - Sales Project Logic and OOP
  - "09. Exercise 3 - Sales Project Logic and OOP"
  - Sales project exercise
  - Sales data exercise
tags:
  - python
  - exercise
  - project
  - oop
  - parsing
  - error-handling
  - sales-data
sources:
  - "09. Exercise 3 - Sales Project Logic and OOP"
created_index: 24
---

This exercise tests your ability to clean string data, use helper functions, and implement Object Oriented Programming to manage sales data. The solution is built in three steps — helper functions, a `Product` class, and the main execution script — with every task, code block and the expected output preserved below. It draws on [[Functions and Lambda Expressions]], [[Object Oriented Programming]] and [[Error Handling and Exceptions]]; [[Python Language Overview]] maps the wider area.

## Scenario

You have a raw text file (`data.txt`) containing messy sales records in the format `Product, Price, Quantity`. The task:

1. Read the file.
2. Clean the lines.
3. Parse them into objects.
4. Calculate total revenue.

## Step 1: helper functions (`utils/helpers.py`)

We need robust functions to handle string manipulation. `clean_lines` removes empty lines and strips whitespace; `parse_line` converts a string like `'Laptop, 1000, 3'` into the tuple `('Laptop', 1000.0, 3)` and handles errors gracefully:

```python
def clean_lines(lines):
    """
    Removes empty lines and strips whitespace.
    """
    cleaned = []
    for line in lines:
        if line.strip():  # If line is not empty
            cleaned.append(line.strip())
    return cleaned

def parse_line(line):
    """
    Converts string 'Laptop, 1000, 3' into tuple ('Laptop', 1000.0, 3)
    Handles errors gracefully.
    """
    try:
        parts = line.split(',')
        if len(parts) != 3:
            raise ValueError("Malformed line")
        
        name = parts[0].strip()
        price = float(parts[1].strip())
        qty = int(parts[2].strip())
        
        return name, price, qty
    except Exception as e:
        print(f"Skipping line '{line}': {e}")
        return None
```

The parsing logic splits each line on commas and rejects any line that does not have exactly three parts by raising `ValueError("Malformed line")`. Each field is stripped of surrounding whitespace, the price is cast to `float` and the quantity to `int`, and the three values come back as a tuple. Any exception is caught, a message naming the skipped line is printed, and `None` is returned so the caller can drop the record instead of crashing.

## Step 2: the product class (`utils/product.py`)

The `Product` class is a model of a single sales record. `__init__` stores the name, price and quantity, `get_total` computes the line's revenue as price times quantity, and `__str__` renders the product as a printable string:

```python
class Product:
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity
    
    def get_total(self):
        return self.price * self.quantity
    
    def __str__(self):
        return f"{self.name}: ${self.get_total()}"
```

## Step 3: main execution (`scripts/main.py`)

The main script simulates the raw data as a Python list, with the helper and product classes assumed imported. The simulated input deliberately includes an empty line and a corrupt line — `'Corrupt Data Line'`, for example, fails the three-part check — so that the cleaning and error-handling paths are exercised. The script then runs the three pipeline stages — clean, parse and create objects, calculate revenue — and prints each product followed by the total:

```python
# Assume helper and product classes are imported
# RAW DATA SIMULATION
raw_data = [
    "Laptop, 1000, 3",
    "Mouse, 20, 50",
    "",  # Empty line
    "Monitor, 200, 5",
    "Corrupt Data Line"  # Error line
]

# 1. Clean
clean_data = clean_lines(raw_data)

# 2. Parse and Create Objects
products = []
for line in clean_data:
    parsed = parse_line(line)
    if parsed:
        name, price, qty = parsed
        products.append(Product(name, price, qty))

# 3. Calculate Revenue
total_revenue = sum([p.get_total() for p in products])

# Output
for p in products:
    print(p)
    
print(f"Total Revenue: ${total_revenue}")
```

## Expected output

Running the program produces the following output. The empty line never survives cleaning, and the corrupt line is skipped with a diagnostic message rather than crashing the run:

```text
Skipping line 'Corrupt Data Line': Malformed line
Laptop: $3000.0
Mouse: $1000.0
Monitor: $1000.0
Total Revenue: $5000.0
```

## Key takeaways

Three lessons generalize beyond this exercise. **Modularity:** logic is separated into parsing versus object modeling, so string handling and the data model evolve independently. **Error handling:** the program did not crash on the "Corrupt Data Line" — the exception was caught, the line was reported, and execution continued. **OOP:** the `Product` object handles its own logic (`get_total`), so revenue computation lives next to the data it belongs to.

## See also

- [[Python Language Overview]]
- [[Object Oriented Programming]]
- [[Functions and Lambda Expressions]]
- [[Error Handling and Exceptions]]
- [[Control Flow and Loops]]
- [[Lists Tuples and Sets]]
- [[Exercise - Temperature and Grade Analysis]]
- [[Exercise - Medical Dataset Pipeline]]
