---
title: Installation and Distributions
type: concept
aliases:
  - "2. Installation and Distributions"
  - "02. Installation and Distributions"
  - "Installing Python"
  - "Python installation"
  - "Python distributions"
tags:
  - python
  - installation
  - distributions
  - anaconda
  - miniconda
  - conda
  - environment-setup
sources:
  - "02. Installation and Distributions"
created_index: 9
---

To use Python, you must install an interpreter on your machine, and in the context of data science there are two primary ways to do this. The first is the official, "vanilla" installation: the raw interpreter from the Python Software Foundation, lightweight but with every data science library left for you to install afterwards. The second is the Anaconda distribution, a Python build designed specifically for scientific computing that arrives with over 1,500 common data science packages pre-installed. Whichever route you choose, a quick verification confirms the install, and the surrounding tooling — environments, packages, editors — is covered by this note's siblings in the [[Python Language Overview]] area.

## Option 1: the official Python installation (the "vanilla" way)

This route installs the raw Python interpreter from the Python Software Foundation and nothing else around it.

### Installation steps

1. Visit [python.org/downloads](https://www.python.org/downloads).
2. Download the latest version (e.g., 3.11.x).
3. **Crucial step:** during installation, check the box **"Add Python to PATH"**.

> [!warning] Why "Add Python to PATH" matters
> The PATH is a system variable that allows your operating system to find the `python` executable from any command prompt window. Without this, typing `python` in the terminal will result in an error.

### Pros and cons

The trade-off is straightforward. On the plus side, the installation is lightweight — you only get what you need. On the minus side, you must manually install every single data science library (Pandas, NumPy, etc.) afterwards, which is the workflow [[Virtual Environments and Package Management]] develops.

## Option 2: the Anaconda distribution (the "data science" way)

Anaconda is a distribution of Python specifically designed for scientific computing. It includes Python *plus* over 1,500 common data science packages pre-installed, so a fresh installation is already a working data science environment rather than a starting point for one.

### Components of Anaconda

Four pieces ship together in the distribution:

| Component | What it is |
|---|---|
| Python interpreter | The core language |
| Conda | A robust package and environment manager (an alternative to `pip` and `venv`) |
| Standard libraries | NumPy, Pandas, Matplotlib, Scikit-Learn, Jupyter, etc., come pre-installed |
| Anaconda Navigator | A graphical user interface (GUI) for launching apps |

Conda is the piece that sets Anaconda apart beyond sheer package count: it is a single manager for both packages and environments, positioned as an alternative to `pip` and `venv` — a comparison developed in [[Virtual Environments and Package Management]].

### Installation steps

1. Visit [anaconda.com/download](https://www.anaconda.com/download).
2. Download the Graphical Installer.
3. Follow the instructions (default settings are usually fine).

### Miniconda

> [!tip] Miniconda
> If you find the full Anaconda installer too large (3GB+), you can install **Miniconda**. It includes *only* Python and the Conda manager, allowing you to install specific libraries later. This is preferred by experienced developers.

Miniconda splits the difference between the two options: it keeps the interpreter and the Conda manager but drops the pre-installed library collection, so you add the specific libraries you want later — the minimalist spirit of the vanilla route, with Conda instead of `pip`.

## Comparing the two routes

| | Official Python ("vanilla") | Anaconda |
|---|---|---|
| What you get | The raw interpreter from the Python Software Foundation | Python plus over 1,500 data science packages pre-installed |
| Package and environment tooling | `pip` and `venv` | Conda, an alternative to both, plus the Navigator GUI |
| Footprint | Lightweight | Large installer (3GB+), with Miniconda as the minimal alternative |
| Appeal | You only get what you need | A scientific-computing stack that works out of the box |

## Verifying the installation

To verify your installation, open your terminal (Command Prompt on Windows, Terminal on Mac/Linux) and type:

```bash
python --version
```

*Output:* `Python 3.11.5` (or similar).

If you are using Anaconda, you can also verify Conda:

```bash
conda --version
```

*Output:* `conda 23.7.4`.

A version string in reply means the interpreter — and, for Anaconda, the Conda manager — is installed and findable from the terminal; the "Add Python to PATH" checkbox on the vanilla route exists to make exactly this command work. From here the natural next steps are isolating your projects into environments and choosing where to write code, covered in [[Virtual Environments and Package Management]] and [[IDEs and Development Environments]].

## See also

- [[Python Language Overview]] — the area hub
- [[Virtual Environments and Package Management]] — `pip`, `venv` and Conda in depth
- [[IDEs and Development Environments]] — editors and notebooks for the installed interpreter
- [[Project Structure and Best Practices]] — organizing a project on top of a working installation
- [[Exercise - Hospital Data Project Setup]] — a hands-on walkthrough that builds a full project environment
