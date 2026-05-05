"""
Complexity Estimator  –  v5  (Final)
======================================
Five-stage detection pipeline:

  Stage 1 – O(1)
    max/min ratio < 4.0  →  times are flat regardless of n

  Stage 2 – O(log n)
    ratio < 20 AND log-log slope < 0.5  →  very slow sub-linear growth

  Stage 3 – O(2^n)
    Pearson(n, log t) > 0.99  →  log(t) grows linearly with n

  Stage 4 – O(n) vs O(n log n) fine-grained test
    When slope is in 0.9-1.3, compare R² of both models directly.
    If R²(n log n) > R²(n) → O(n log n), else → O(n).

  Stage 5 – log-log slope classifier (all remaining classes)
    slope → O(n²), O(n² log n), O(n³)
"""

import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import pearsonr


class ComplexityEstimator:

    MODELS = {
        "O(1)":        lambda n, a:    a * np.ones_like(n, dtype=float),
        "O(log n)":    lambda n, a, b: a * np.log2(np.maximum(n, 2)) + b,
        "O(n)":        lambda n, a, b: a * n + b,
        "O(n log n)":  lambda n, a, b: a * n * np.log2(np.maximum(n, 2)) + b,
        "O(n²)":       lambda n, a, b: a * n ** 2 + b,
        "O(n² log n)": lambda n, a, b: a * n ** 2 * np.log2(np.maximum(n, 2)) + b,
        "O(n³)":       lambda n, a, b: a * n ** 3 + b,
        "O(2^n)":      lambda n, a, b: a * np.exp(np.minimum(n * 0.693, 700)) + b,
    }

    # ── Public API ─────────────────────────────────────────────────────────────
    def estimate(self, sizes: list, times: list):
        if len(sizes) < 2:
            return "Unknown", {}

        n = np.array(sizes, dtype=float)
        t = np.maximum(np.array(times, dtype=float), 1e-12)

        scores = self._all_r2_scores(n, t)

        # Stage 1: O(1)
        if self._is_o1(t):
            scores["O(1)"] = 100.0
            return "O(1)", self._normalise(scores)

        # Stage 2: O(log n)
        if self._is_logn(n, t):
            scores["O(log n)"] = 100.0
            return "O(log n)", self._normalise(scores)

        # Stage 3: O(2^n)
        if self._is_exponential(n, t):
            scores["O(2^n)"] = 100.0
            return "O(2^n)", self._normalise(scores)

        # Stage 4: O(n) vs O(n log n)
        slope = self._loglog_slope(n, t)
        if 0.9 <= slope <= 1.3:
            best = self._n_vs_nlogn(n, t)
            scores[best] = 100.0
            return best, self._normalise(scores)

        # Stage 5: slope classifier for the rest
        best = self._slope_to_class(slope)
        scores[best] = 100.0
        return best, self._normalise(scores)

    # ── Stage 1: O(1) ──────────────────────────────────────────────────────────
    @staticmethod
    def _is_o1(t) -> bool:
        """
        When n grows 500×, O(1) times stay flat.
        A ratio < 4 means times never grew more than 4×, consistent with noise.
        """
        return float(np.max(t)) / float(np.min(t)) < 4.0

    # ── Stage 2: O(log n) ──────────────────────────────────────────────────────
    @staticmethod
    def _is_logn(n, t) -> bool:
        """
        O(log n) over a 500× range of n grows only ~3–5×.
        Ratio check (< 20) + flat log-log slope (< 0.5) together.
        """
        ratio = float(np.max(t)) / float(np.min(t))
        if ratio >= 20:
            return False
        slope = ComplexityEstimator._loglog_slope(n, t)
        return slope < 0.5

    # ── Stage 3: O(2^n) ────────────────────────────────────────────────────────
    @staticmethod
    def _is_exponential(n, t) -> bool:
        """
        For O(2^n): log(t) grows linearly with n.
        Guard: linear fit must beat the log-log (power-law) fit.
        """
        log_t = np.log(t)
        r_lin, _ = pearsonr(n, log_t)
        r_log, _ = pearsonr(np.log(np.maximum(n, 2)), log_t)
        return r_lin > 0.99 and r_lin > r_log + 0.02

    # ── Stage 4: O(n) vs O(n log n) ────────────────────────────────────────────
    @staticmethod
    def _n_vs_nlogn(n, t) -> str:
        """
        When slope is ambiguous (0.9–1.3), compare R² of both models directly.
        The log factor adds only ~10-20% to slope values, so R² is more reliable.
        """
        def r2_of(model, p0):
            try:
                params, _ = curve_fit(model, n, t, p0=p0, maxfev=8000)
                fitted = model(n, *params)
                ss_res = np.sum((t - fitted) ** 2)
                ss_tot = np.sum((t - np.mean(t)) ** 2)
                return 1.0 - ss_res / (ss_tot + 1e-30)
            except Exception:
                return 0.0

        a_guess = float(np.mean(t) / np.mean(n))
        r2_n     = r2_of(lambda n, a, b: a * n + b,
                         [a_guess, 0.0])
        r2_nlogn = r2_of(lambda n, a, b: a * n * np.log2(np.maximum(n, 2)) + b,
                         [a_guess / 10, 0.0])

        return "O(n log n)" if r2_nlogn > r2_n else "O(n)"

    # ── Stage 5: slope → class ─────────────────────────────────────────────────
    @staticmethod
    def _slope_to_class(slope: float) -> str:
        if   slope < 1.70:  return "O(n log n)"
        elif slope < 2.30:  return "O(n²)"
        elif slope < 2.55:  return "O(n² log n)"
        else:               return "O(n³)"

    # ── Shared: log-log slope ──────────────────────────────────────────────────
    @staticmethod
    def _loglog_slope(n, t) -> float:
        """Weighted polyfit of log(t) vs log(n); more weight on large n."""
        log_n = np.log2(np.maximum(n, 2))
        log_t = np.log2(t)
        w     = np.sqrt(n / np.max(n))
        return float(np.polyfit(log_n, log_t, 1, w=w)[0])

    # ── R² scores for candidate bars ──────────────────────────────────────────
    def _all_r2_scores(self, n, t) -> dict:
        scores = {}
        for label, model in self.MODELS.items():
            try:
                p0 = self._p0(label, n, t)
                params, _ = curve_fit(model, n, t, p0=p0, maxfev=8000)
                fitted  = model(n, *params)
                ss_res  = float(np.sum((t - fitted) ** 2))
                ss_tot  = float(np.sum((t - np.mean(t)) ** 2))
                r2      = 1.0 - ss_res / (ss_tot + 1e-30)
                scores[label] = max(r2, 0.0)
            except Exception:
                scores[label] = 0.0
        return scores

    @staticmethod
    def _normalise(scores: dict) -> dict:
        max_s = max(scores.values()) if scores else 1.0
        return {k: round(v / max(max_s, 1e-9) * 100, 1) for k, v in scores.items()}

    @staticmethod
    def _p0(label, n, t):
        mean_t = float(np.mean(t))
        mean_n = float(np.mean(n))
        a = mean_t / max(mean_n, 1)
        return {
            "O(1)":        [mean_t],
            "O(log n)":    [a * 10,  0.0],
            "O(n)":        [a,       0.0],
            "O(n log n)":  [a / 10,  0.0],
            "O(n²)":       [a / max(mean_n,    1), 0.0],
            "O(n² log n)": [a / max(mean_n,    1), 0.0],
            "O(n³)":       [a / max(mean_n**2, 1), 0.0],
            "O(2^n)":      [1e-9,   0.0],
        }.get(label, [a, 0.0])