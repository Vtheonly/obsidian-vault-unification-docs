---
title: Exercise - Hospital Data Project Setup
type: tutorial
aliases:
  - "Exercise 2 - Hospital Data Project Setup"
  - "7. Exercise 2. Hospital Data Project Setup"
  - "07. Exercise 2 - Hospital Data Project Setup"
  - "Hospital Data Project Setup"
tags:
  - python
  - exercise
  - tutorial
  - environment-setup
  - command-line
  - virtual-environments
  - pip
  - git
  - project-structure
sources:
  - "07. Exercise 2 - Hospital Data Project Setup"
created_index: 7
---

This exercise tests your ability to set up a professional data science environment from scratch using the Command Line Interface (CLI). The brief is a new project called **"HospitalDataAnalysis"** that needs to analyze patient records, and by the end of the eight steps below that project has a virtual environment, its analysis libraries, a conventional folder layout, a Git repository with a `.gitignore`, and a `requirements.txt` file that lets anyone recreate the setup exactly. Every command is run in the terminal, and the concepts behind each step — virtual environments, project layout, version control — are developed in [[Virtual Environments and Package Management]], [[Project Structure and Best Practices]] and [[Version Control with Git and GitHub]] within the [[Python Language Overview]] area.

## Scenario

You are starting a new project called **"HospitalDataAnalysis"**. You need to analyze patient records. That is the whole brief — the exercise is about the professional scaffolding around the data rather than about the analysis itself, and each of the eight steps below contributes one piece of that scaffolding.

## Step-by-step instructions

Work through the eight steps in order; each assumes the previous one succeeded, and the solution checklist at the end shows what the finished project should look like.

### Step 1: create the project directory

Open your terminal and run:

```bash
mkdir HospitalDataAnalysis
cd HospitalDataAnalysis
```

For example, this first command creates the top-level folder and moves your terminal into it, so every command that follows operates inside the project.

### Step 2: create a virtual environment

Create an isolated environment named `env`:

- *Windows:* `python -m venv env`
- *Mac/Linux:* `python3 -m venv env`

The `env` folder holds this project's interpreter and packages, walled off from your system Python and from every other project on the machine — the isolation rationale is covered in [[Virtual Environments and Package Management]].

### Step 3: activate the environment

Activate the environment you just created:

- *Windows:* `.\env\Scripts\activate`
- *Mac/Linux:* `source env/bin/activate`

*Check:* your terminal prompt should now show `(env)`.

That `(env)` prefix is the visible confirmation that activation worked and that the environment is now the Python your terminal will use.

### Step 4: install libraries

Install the essentials for data analysis:

```bash
pip install pandas numpy matplotlib jupyterlab
```

With the environment active, `pip` places these four packages inside `env`, which is what makes the setup deletable and recreatable later on.

### Step 5: create the project structure

Create the necessary subfolders and empty files:

```bash
# Create folders
mkdir data notebooks scripts

# Create empty files (Mac/Linux syntax; on Windows use New-Item or GUI)
touch data/patients.csv notebooks/analysis.ipynb README.md .gitignore
```

Note the caveat in the comment: `touch` is Mac/Linux syntax, so on Windows create the same empty files with `New-Item` or the GUI. The result is the conventional layout — raw data under `data/`, analysis work under `notebooks/`, code under `scripts/` — whose rationale is the subject of [[Project Structure and Best Practices]].

### Step 6: initialize Git

```bash
git init
```

This turns the folder into a Git repository so the project's history can be tracked from the very start — the workflow is covered in [[Version Control with Git and GitHub]].

### Step 7: configure .gitignore

Open the `.gitignore` file in a text editor and add the following lines (to prevent committing the environment and cache):

```text
env/
__pycache__/
*.pyc
.ipynb_checkpoints/
```

The first line keeps the `env/` folder out of version control, and the remaining three keep Python bytecode caches and Jupyter's checkpoint folders out as well.

### Step 8: freeze requirements

Save your library list so others can reproduce your environment:

```bash
pip freeze > requirements.txt
```

`pip freeze` prints every installed package with its exact version — entries like `pandas==2.0.3` — and redirecting that output into `requirements.txt` captures the snapshot as a plain file you can commit.

## Solution checklist

At the end of this exercise, your folder should look like this:

```text
HospitalDataAnalysis/
├── env/                # [Contains Python files]
├── data/
│   └── patients.csv    # [Empty]
├── notebooks/
│   └── analysis.ipynb  # [Empty]
├── scripts/            # [Empty folder]
├── .gitignore          # [Contains "env/"]
├── README.md           # [Empty]
└── requirements.txt    # [Contains "pandas==2.0.3", etc.]
```

Every entry traces back to a step: `env/` is the virtual environment from steps 2 and 3; `data/patients.csv`, `notebooks/analysis.ipynb`, `scripts/` and `README.md` are the structure from step 5; `.gitignore` carries the rules from step 7; and `requirements.txt` is the frozen library list from step 8.

## Why this setup matters

You now have a portable, isolated, version-controlled project structure. Isolation comes from `env`, which holds the interpreter and packages and can be deleted without touching anything else on the machine. Portability comes from `requirements.txt`: you can delete the `env` folder, send the rest of the project to a colleague, and they can run `pip install -r requirements.txt` to recreate your exact setup. Version control comes from Git together with the `.gitignore`, which keeps the environment and cache files out of the repository.

## See also

- [[Python Language Overview]] — the area hub
- [[Virtual Environments and Package Management]] — why `env` exists and how `pip` fits in
- [[Project Structure and Best Practices]] — the reasoning behind `data/`, `notebooks/` and `scripts/`
- [[Version Control with Git and GitHub]] — `git init`, `.gitignore` and tracked history
- [[Installation and Distributions]] — getting the interpreter onto the machine in the first place
- [[Exercise - Medical Dataset Pipeline]] — a related hands-on exercise working with a medical dataset
