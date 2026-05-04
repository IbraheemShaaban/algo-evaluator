/**
 * classifier.js — Big O Complexity Classifier
 * Uses least-squares curve fitting and R² to detect algorithm complexity.
 */

window.Classifier = (() => {

  /**
   * All supported complexity classes with their fitting functions.
   * f(n) = theoretical time proportional to n
   */
  const CLASSES = [
    {
      key: 'O(1)',
      label: 'O(1)',
      name: 'Constant',
      color: '#22c55e',
      fn: (n) => 1,
      description: 'Constant time — independent of input size.'
    },
    {
      key: 'O(log n)',
      label: 'O(log n)',
      name: 'Logarithmic',
      color: '#86efac',
      fn: (n) => Math.log2(n),
      description: 'Logarithmic time — e.g. binary search.'
    },
    {
      key: 'O(n)',
      label: 'O(n)',
      name: 'Linear',
      color: '#3fefb4',
      fn: (n) => n,
      description: 'Linear time — e.g. linear search, single loop.'
    },
    {
      key: 'O(n log n)',
      label: 'O(n log n)',
      name: 'Linearithmic',
      color: '#00d4ff',
      fn: (n) => n * Math.log2(n),
      description: 'Linearithmic time — e.g. merge sort, heap sort.'
    },
    {
      key: 'O(n²)',
      label: 'O(n²)',
      name: 'Quadratic',
      color: '#fbbf24',
      fn: (n) => n * n,
      description: 'Quadratic time — e.g. bubble sort, selection sort.'
    },
    {
      key: 'O(n² log n)',
      label: 'O(n² log n)',
      name: 'Quasilinear quadratic',
      color: '#fb923c',
      fn: (n) => n * n * Math.log2(n),
      description: 'n² log n — e.g. some advanced sorting with extra log factor.'
    },
    {
      key: 'O(n³)',
      label: 'O(n³)',
      name: 'Cubic',
      color: '#f97316',
      fn: (n) => n * n * n,
      description: 'Cubic time — e.g. triple nested loops, naive matrix multiply.'
    },
    {
      key: 'O(2^n)',
      label: 'O(2^n)',
      name: 'Exponential',
      color: '#ef4444',
      fn: (n) => Math.pow(2, n),
      description: 'Exponential time — e.g. recursive Fibonacci, subset generation.'
    },
  ];

  /**
   * Compute coefficient of determination R² between observed and predicted values.
   * R² close to 1.0 = good fit.
   */
  function computeR2(observed, predicted) {
    const n = observed.length;
    if (n < 2) return 0;
    const meanObs = observed.reduce((a, b) => a + b, 0) / n;
    let ssTot = 0, ssRes = 0;
    for (let i = 0; i < n; i++) {
      ssTot += Math.pow(observed[i] - meanObs, 2);
      ssRes += Math.pow(observed[i] - predicted[i], 2);
    }
    if (ssTot === 0) return 1; // constant function
    return Math.max(0, 1 - ssRes / ssTot);
  }

  /**
   * Least-squares linear regression: fit y = a * f(x)
   * Returns slope 'a'.
   */
  function leastSquares(xs, ys, fFn) {
    const fxs = xs.map(fFn);
    let num = 0, den = 0;
    for (let i = 0; i < xs.length; i++) {
      num += fxs[i] * ys[i];
      den += fxs[i] * fxs[i];
    }
    return den === 0 ? 0 : num / den;
  }

  /**
   * Classify a set of (size, time) measurements.
   * Returns array of candidates sorted by R² descending.
   */
  function classify(measurements) {
    if (!measurements || measurements.length < 2) {
      return [];
    }

    const sizes = measurements.map(m => m.size);
    const times = measurements.map(m => m.time);

    // Normalize times to reduce numerical instability
    const maxTime = Math.max(...times);
    const normTimes = maxTime === 0 ? times : times.map(t => t / maxTime);

    const results = [];

    for (const cls of CLASSES) {
      // Skip exponential for large n (numerical overflow)
      const maxN = Math.max(...sizes);
      if (cls.key === 'O(2^n)' && maxN > 40) continue;

      const fxs = sizes.map(n => cls.fn(n));
      // Check for Infinity/NaN
      if (fxs.some(x => !isFinite(x) || isNaN(x))) continue;

      // Normalize f(n) values too
      const maxFx = Math.max(...fxs);
      const normFxs = maxFx === 0 ? fxs : fxs.map(x => x / maxFx);

      // Fit: predicted = a * normFx
      let num = 0, den = 0;
      for (let i = 0; i < sizes.length; i++) {
        num += normFxs[i] * normTimes[i];
        den += normFxs[i] * normFxs[i];
      }
      const a = den === 0 ? 0 : num / den;
      const predicted = normFxs.map(x => a * x);

      const r2 = computeR2(normTimes, predicted);

      results.push({
        ...cls,
        r2: Math.round(r2 * 10000) / 10000,
        coefficient: a * (maxTime / (maxFx || 1)),
      });
    }

    // Sort by R² descending
    results.sort((a, b) => b.r2 - a.r2);
    return results;
  }

  /**
   * Get best match (highest R²).
   */
  function bestMatch(measurements) {
    const candidates = classify(measurements);
    return candidates.length > 0 ? candidates[0] : null;
  }

  /**
   * Group measurements by type and classify each group.
   * Returns: { random: {...}, sorted: {...}, reverse: {...}, manual: {...} }
   */
  function classifyByType(allMeasurements) {
    const groups = {};
    for (const m of allMeasurements) {
      if (!groups[m.type]) groups[m.type] = [];
      groups[m.type].push(m);
    }

    const results = {};
    for (const [type, meas] of Object.entries(groups)) {
      const sorted = [...meas].sort((a, b) => a.size - b.size);
      const candidates = classify(sorted);
      results[type] = {
        measurements: sorted,
        candidates,
        best: candidates[0] || null,
      };
    }
    return results;
  }

  /**
   * Get the "overall" best complexity considering all types.
   * Uses the type with the highest R² confidence.
   */
  function overallBest(classifiedByType) {
    let best = null;
    let bestR2 = -1;
    for (const [type, data] of Object.entries(classifiedByType)) {
      if (data.best && data.best.r2 > bestR2) {
        bestR2 = data.best.r2;
        best = data.best;
      }
    }
    return best;
  }

  /**
   * Generate theoretical curve points for plotting.
   * Returns array of y-values normalized to match scale of measurements.
   */
  function theoreticalCurve(complexityKey, sizes, measurements) {
    const cls = CLASSES.find(c => c.key === complexityKey);
    if (!cls || sizes.length === 0 || measurements.length === 0) return [];

    const fxs = sizes.map(n => cls.fn(n));
    const times = measurements.map(m => m.time);

    if (fxs.every(x => x === 0) || times.every(t => t === 0)) return fxs;

    const maxFx = Math.max(...fxs) || 1;
    const normFxs = fxs.map(x => x / maxFx);
    const maxT = Math.max(...times) || 1;
    const normT = times.map(t => t / maxT);

    // Fit coefficient
    let num = 0, den = 0;
    const measSizes = measurements.map(m => m.size);
    for (let i = 0; i < measSizes.length; i++) {
      const fx = cls.fn(measSizes[i]) / maxFx;
      num += fx * normT[i];
      den += fx * fx;
    }
    const a = den === 0 ? 1 : num / den;

    return sizes.map(n => a * (cls.fn(n) / maxFx) * maxT);
  }

  return { classify, bestMatch, classifyByType, overallBest, theoreticalCurve, CLASSES };
})();
