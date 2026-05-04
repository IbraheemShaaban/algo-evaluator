# Algorithm Performance Evaluator 🚀

> **Course:** Algorithms (CSE 2nd Year) — Computer and Systems Engineering
> **Academic Year:** 2025/2026[cite: 3]
> **Subject:** Data Structures and Algorithms Analysis
> **Total Grade:** 15 Marks (10 Implementation + 5 Documentation)
> **Deadline:** 5 May 2026

---

## Overview

A professional desktop application built with **Python** to estimate the time complexity (**Big O Notation**) of algorithms through empirical measurement and mathematical regression.[cite: 1, 3]
---

## Features

### Two Operational Modes[cite: 3]

| Mode | Description | Use Case |
|------|-------------|----------|
| **Mode 1: Manual** | User enters a custom array manually[cite: 3] | Debug specific test cases |
| **Mode 2: Auto** | Generates best, average, and worst-case arrays automatically[cite: 3] | Full Big O analysis across sizes |

### Complexity Classes Detected

| Symbol | Class | Example Algorithm |
|--------|-------|-------------------|
| $O(1)$ | Constant | Array element access |
| $O(\log n)$ | Logarithmic | Binary search |
| $O(n)$ | Linear | Linear search, single loop |
| $O(n \log n)$ | Linearithmic | Merge sort, heap sort |
| $O(n^2)$ | Quadratic | Bubble sort, selection sort |
| $O(n^2 \log n)$ | Quasilinear quadratic | Advanced nested sorts |
| $O(n^3)$ | Cubic | Triple-nested loops |
| $O(2^n)$ | Exponential | Recursive Fibonacci |

### How It Works

1. **Sandboxed Execution:** The engine executes user code using Python's `exec()` within a restricted namespace for safety.[cite: 2]
2. **High-Res Timing:** Uses `time.perf_counter()` to measure execution time.[cite: 2]
3. **Statistical Cleaning:** Runs multiple trials per input size and calculates the **Median** to eliminate OS-level noise.[cite: 2]
4. **Mathematical Fitting:** Fits the data against theoretical models using **Non-linear Least Squares** via `scipy.optimize.curve_fit`.[cite: 1]
5. **R² Scoring:** Determines the "Goodness of Fit" (0-100%). A higher $R^2$ indicates a stronger match to that complexity class.[cite: 1]

---

## Installation & Usage

### 1. Requirements
Ensure you have Python 3.8+ installed. Install the mathematical stack:
```bash
pip install numpy scipy matplotlib

## Technical Architecture
┌─────────────────────────────────────────┐
│           User Interface (main.py)      │
│   Code Editor │ Mode Toggle │ Matplotlib │
└──────────────┬───────────────────────────┘
               │ userCode + InputData
               ▼
┌─────────────────────────────────────────┐
│         Engine (executor.py)            │
│  - Restricted execution via exec()      │
│  - Median timing logic (10 repeats)     │
│  - Memory isolation (copy.deepcopy)     │
└──────────────┬───────────────────────────┘
               │ measurements[]
               ▼
┌─────────────────────────────────────────┐
│     Estimator (complexity_estimator.py)  │
│  - Least-squares curve fitting (SciPy)  │
│  - R² (Coefficient of Determination)    │
│  - Model normalization (0-100 scale)    │
└─────────────────────────────────────────┘


