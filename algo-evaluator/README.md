# Algorithm Performance Evaluator

> **Course:** Algorithms (CSE 2nd Year) — Computer and Systems Engineering  
> **Academic Year:** 2025/2026  
> **Subject Teacher:** Dr. Hend Gaballah  
> **Teaching Assistant:** Eng. Mahmoud Ibrahim  
> **Total Grade:** 15 Marks (10 Implementation + 5 Documentation)  
> **Deadline:** 3 May 2026

---

## Live Demo

Open `index.html` in any modern browser — no server required, no installation needed.

```
algo-evaluator/
├── index.html          ← Open this file
├── css/style.css
├── js/
│   ├── engine.js       ← Execution & timing engine
│   ├── classifier.js   ← Big O complexity classifier
│   ├── chart-manager.js← Chart.js integration
│   └── app.js          ← UI controller
└── README.md
```

---

## Features

### Two Operational Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **Mode 1: Manual** | User enters a custom array manually | Debug specific test cases |
| **Mode 2: Auto** | Generates random, sorted, reversed arrays at multiple sizes | Full Big O analysis |

### Complexity Classes Detected

| Symbol | Class | Example Algorithm |
|--------|-------|-------------------|
| O(1) | Constant | Array element access |
| O(log n) | Logarithmic | Binary search |
| O(n) | Linear | Linear search, single loop |
| O(n log n) | Linearithmic | Merge sort, heap sort |
| O(n²) | Quadratic | Bubble sort, selection sort |
| O(n² log n) | Quasilinear quadratic | Advanced nested sorts |
| O(n³) | Cubic | Triple-nested loops |
| O(2^n) | Exponential | Recursive Fibonacci |

### How It Works

1. User writes algorithm code inside the function body
2. Engine wraps code safely using `Function` constructor
3. For each input size, the engine runs multiple trials and takes the **median** (eliminates outliers)
4. Classifier fits each complexity curve using **least-squares regression**
5. **R² (coefficient of determination)** determines the best fit
6. Results are plotted with Chart.js alongside the fitted theoretical curve

---

## Usage

### Manual Mode

1. Select **Mode 1: Manual**
2. Write your algorithm in the code editor
3. Enter an array (e.g. `5, 3, 8, 1, 9`) or click a quick-generate button
4. Click **Run Analysis**

### Auto Mode

1. Select **Mode 2: Auto**
2. Write your algorithm in the code editor
3. Choose input size preset (Small / Medium / Large / Custom)
4. Choose number of runs per size (for statistical stability)
5. Check which cases to test: Random, Sorted, Reversed
6. Click **Run Analysis**

---

## Code Editor — Function Template

Your code runs inside this template:

```javascript
function algorithm(arr) {
  // ← Your code goes here
  // arr is a copy of the input array
  // return value is optional
}
```

### Example Algorithms

**O(1) — Constant:**
```javascript
return arr[0];
```

**O(n) — Linear:**
```javascript
let sum = 0;
for (let i = 0; i < arr.length; i++) sum += arr[i];
return sum;
```

**O(n log n) — Merge Sort:**
```javascript
function merge(l, r) {
  let res = [], i = 0, j = 0;
  while (i < l.length && j < r.length)
    res.push(l[i] <= r[j] ? l[i++] : r[j++]);
  return res.concat(l.slice(i), r.slice(j));
}
function ms(a) {
  if (a.length <= 1) return a;
  const m = a.length >> 1;
  return merge(ms(a.slice(0, m)), ms(a.slice(m)));
}
return ms(arr);
```

**O(n²) — Bubble Sort:**
```javascript
for (let i = 0; i < arr.length; i++)
  for (let j = 0; j < arr.length - i - 1; j++)
    if (arr[j] > arr[j+1]) [arr[j], arr[j+1]] = [arr[j+1], arr[j]];
return arr;
```

**O(n³) — Triple Nested Loop:**
```javascript
let count = 0;
for (let i = 0; i < arr.length; i++)
  for (let j = 0; j < arr.length; j++)
    for (let k = 0; k < arr.length; k++)
      count++;
return count;
```

**O(2^n) — Recursive Fibonacci (test with small n ≤ 25):**
```javascript
function fib(n) {
  if (n <= 1) return n;
  return fib(n-1) + fib(n-2);
}
return fib(arr[0]);
```

---

## Technical Architecture

```
┌─────────────────────────────────────────┐
│              User Interface              │
│  Code Editor │ Mode Toggle │ Config UI  │
└──────────────┬───────────────────────────┘
               │ userCode + config
               ▼
┌─────────────────────────────────────────┐
│           Engine (engine.js)             │
│  buildFunction() → safe eval via new    │
│  Function()                              │
│  timedRuns() → performance.now()        │
│  generateArray() → random/sorted/rev    │
└──────────────┬───────────────────────────┘
               │ measurements[]
               ▼
┌─────────────────────────────────────────┐
│        Classifier (classifier.js)        │
│  classify() → least-squares for each   │
│               O() class                 │
│  computeR²()  → coefficient of deter.  │
│  classifyByType() → per case analysis  │
└──────────────┬───────────────────────────┘
               │ classified data
               ▼
┌─────────────────────────────────────────┐
│       ChartManager (chart-manager.js)   │
│  render() → measured + fitted curves   │
│  setScale() → linear / log             │
│  exportPng() → download chart           │
└─────────────────────────────────────────┘
```

---

## Mathematical Basis

For each complexity class `f(n)`, we find coefficient `a` via least-squares:

```
minimize Σ(yᵢ - a·f(nᵢ))²

solution: a = Σ(f(nᵢ)·yᵢ) / Σ(f(nᵢ)²)
```

Then compute R² (coefficient of determination):

```
R² = 1 - SS_res / SS_tot

where:
  SS_res = Σ(yᵢ - ŷᵢ)²     (residual sum of squares)
  SS_tot = Σ(yᵢ - ȳ)²      (total sum of squares)
```

R² = 1.0 → perfect fit. R² ≥ 0.95 → strong match. R² < 0.80 → poor fit.

---

## Grading Criteria Addressed

### Implementation (10 marks)

**GUI & User Experience (3 marks)**
- Professional dark theme with grid background
- Two clear operational modes (Manual + Auto)
- Input validation and error messages
- Progress bar during analysis
- Responsive layout

**Execution Engine (7 marks)**
- Timeout-safe function execution using `Function` constructor
- `performance.now()` for high-resolution timing
- Multiple runs per size with median (removes outliers)
- Warm-up run before measurement (avoids JIT bias)
- Separate analysis for random, sorted, and reversed inputs

### Documentation (5 marks)
See `docs/Report.pdf` (generated separately for submission).

---

## Test Cases

| Complexity | Test Code | Expected R² |
|-----------|-----------|-------------|
| O(1) | `return arr[0];` | ≥ 0.95 |
| O(n) | Single for loop | ≥ 0.99 |
| O(n log n) | Merge sort | ≥ 0.98 |
| O(n²) | Bubble sort | ≥ 0.99 |
| O(n³) | Triple nested loop | ≥ 0.99 |
| O(2^n) | `fib(arr[0])` (n≤25) | ≥ 0.97 |

---

## Team Contributions

| Name | Role | Responsibilities |
|------|------|-----------------|
| Member 1 | Team Lead + UI | HTML/CSS design, layout |
| Member 2 | Engine | Execution, timing, array generation |
| Member 3 | Classifier | Curve fitting, R² analysis |
| Member 4 | Charts | Chart.js integration, export |
| Member 5 | QA + Docs | Testing, documentation, report |

---

## Submission

**Form:** https://forms.gle/KofyTYydrss5gnbm9  
**Deadline:** 3 May 2026

---

## Browser Compatibility

Works in any modern browser. No dependencies to install.

| Browser | Supported |
|---------|-----------|
| Chrome 90+ | ✅ |
| Firefox 88+ | ✅ |
| Edge 90+ | ✅ |
| Safari 14+ | ✅ |
