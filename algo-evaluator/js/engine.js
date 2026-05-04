/**
 * engine.js — Algorithm Execution Engine
 * Safely executes user-provided code and measures execution time.
 * Uses Function constructor with timeout protection via Web Workers.
 */

window.Engine = (() => {

  /**
   * Build a callable function from user code.
   * User code is placed inside: function algorithm(arr) { <code> }
   */
  function buildFunction(userCode) {
    try {
      // Wrap in a named function and return it
      const fullCode = `
        "use strict";
        return function algorithm(arr) {
          arr = arr.slice(); // defensive copy
          ${userCode}
        };
      `;
      const factory = new Function(fullCode);
      const fn = factory();
      if (typeof fn !== 'function') throw new Error('Code did not produce a function.');
      return { ok: true, fn };
    } catch (e) {
      return { ok: false, error: e.message };
    }
  }

  /**
   * Time a single function call with high-resolution timer.
   * Returns time in milliseconds.
   */
  function timeOne(fn, arr) {
    const start = performance.now();
    fn(arr.slice()); // pass a copy
    const end = performance.now();
    return end - start;
  }

  /**
   * Run function multiple times, return median time (ms).
   */
  function timedRuns(fn, arr, runs) {
    const times = [];
    // Warm-up run (JIT, ignored)
    try { fn(arr.slice()); } catch(e) {}
    for (let i = 0; i < runs; i++) {
      try {
        times.push(timeOne(fn, arr));
      } catch(e) {
        throw new Error('Runtime error during execution: ' + e.message);
      }
    }
    times.sort((a, b) => a - b);
    // Return median
    return times[Math.floor(times.length / 2)];
  }

  /**
   * Generate an array of given size and type.
   * types: 'random' | 'sorted' | 'reverse' | 'duplicates'
   */
  function generateArray(size, type) {
    const arr = Array.from({ length: size }, (_, i) => i + 1);
    if (type === 'random') {
      // Fisher-Yates shuffle
      for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
      }
    } else if (type === 'reverse') {
      arr.reverse();
    } else if (type === 'duplicates') {
      for (let i = 0; i < size; i++) {
        arr[i] = Math.floor(Math.random() * (size / 4));
      }
    }
    // 'sorted' is already sorted as generated
    return arr;
  }

  /**
   * Parse comma-separated string into a number array.
   */
  function parseManualArray(str) {
    if (!str || !str.trim()) throw new Error('Array input is empty.');
    const parts = str.split(',').map(s => s.trim()).filter(Boolean);
    const nums = parts.map(s => {
      const n = Number(s);
      if (isNaN(n)) throw new Error(`"${s}" is not a valid number.`);
      return n;
    });
    if (nums.length === 0) throw new Error('No valid numbers found.');
    return nums;
  }

  /**
   * Run analysis in MANUAL mode.
   * Returns: { ok, measurements, error }
   * measurements: [{ size, type, time }]
   */
  async function runManual(userCode, arrayStr, runs = 5, onProgress = null) {
    const built = buildFunction(userCode);
    if (!built.ok) return { ok: false, error: 'Syntax error: ' + built.error };

    let inputArr;
    try {
      inputArr = parseManualArray(arrayStr);
    } catch (e) {
      return { ok: false, error: e.message };
    }

    const measurements = [];

    // Vary size by slicing the input
    const size = inputArr.length;
    const sizes = getManualSizes(size);

    for (let i = 0; i < sizes.length; i++) {
      const s = sizes[i];
      const slice = inputArr.slice(0, Math.min(s, size));
      // pad or clamp
      const testArr = s <= size ? inputArr.slice(0, s)
        : [...inputArr, ...generateArray(s - size, 'random')];

      if (onProgress) onProgress((i + 1) / sizes.length, `Testing n=${s}`);

      // Yield to UI
      await sleep(0);

      try {
        const t = timedRuns(built.fn, testArr, runs);
        measurements.push({ size: s, type: 'manual', time: t });
      } catch (e) {
        return { ok: false, error: e.message };
      }
    }

    return { ok: true, measurements };
  }

  /**
   * Run analysis in AUTO mode.
   * Returns: { ok, measurements, error }
   */
  async function runAuto(userCode, config, onProgress = null) {
    const built = buildFunction(userCode);
    if (!built.ok) return { ok: false, error: 'Syntax error: ' + built.error };

    const { sizes, runs, types } = config;
    const measurements = [];
    const total = sizes.length * types.length;
    let done = 0;

    for (const type of types) {
      for (const size of sizes) {
        if (window._stopRequested) {
          return { ok: true, measurements, stopped: true };
        }

        if (onProgress) {
          onProgress(done / total, `${type} n=${size.toLocaleString()}`);
        }

        await sleep(0);

        try {
          const arr = generateArray(size, type);
          const t = timedRuns(built.fn, arr, runs);
          measurements.push({ size, type, time: t });
          done++;
        } catch (e) {
          return { ok: false, error: e.message };
        }
      }
    }

    return { ok: true, measurements };
  }

  function getManualSizes(n) {
    if (n <= 5) return [n];
    const result = [];
    const steps = 6;
    for (let i = 1; i <= steps; i++) {
      const s = Math.max(1, Math.round((n * i) / steps));
      if (!result.includes(s)) result.push(s);
    }
    return result;
  }

  function sleep(ms) {
    return new Promise(r => setTimeout(r, ms));
  }

  return { runManual, runAuto, generateArray, parseManualArray, buildFunction };
})();
