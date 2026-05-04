"""
Complexity Estimator
Fits timing data against known complexity classes using least-squares curve fitting.
"""

import math
import numpy as np
from scipy.optimize import curve_fit


class ComplexityEstimator:
    """
    Given a list of input sizes and measured runtimes, fits several
    theoretical complexity models and returns the best match.
    """

    MODELS = {
        "O(1)":        lambda n, a: a * np.ones_like(n, dtype=float),
        "O(log n)":    lambda n, a, b: a * np.log2(np.maximum(n, 1)) + b,
        "O(n)":        lambda n, a, b: a * n + b,
        "O(n log n)":  lambda n, a, b: a * n * np.log2(np.maximum(n, 1)) + b,
        "O(n²)":       lambda n, a, b: a * n**2 + b,
        "O(n² log n)": lambda n, a, b: a * n**2 * np.log2(np.maximum(n, 1)) + b,
        "O(n³)":       lambda n, a, b: a * n**3 + b,
        "O(2^n)":      lambda n, a, b: a * np.exp(np.minimum(n * 0.693, 700)) + b,
    }

    def estimate(self, sizes, times):
        """
        Returns (best_class: str, scores: dict[str, float])
        where scores map complexity class → goodness-of-fit (higher = better).
        """
        if len(sizes) < 2:
            return "Unknown", {}

        n = np.array(sizes, dtype=float)
        t = np.array(times, dtype=float)

        # Avoid division by zero / log of 0
        t = np.maximum(t, 1e-12)

        scores = {}
        for label, model in self.MODELS.items():
            try:
                params, _ = curve_fit(model, n, t, maxfev=5000,
                                      p0=self._initial_guess(label, n, t))
                fitted = model(n, *params)
                ss_res = np.sum((t - fitted) ** 2)
                ss_tot = np.sum((t - np.mean(t)) ** 2)
                r2 = 1 - ss_res / (ss_tot + 1e-20)
                scores[label] = max(r2, 0.0)
            except Exception:
                scores[label] = 0.0

        if not scores or all(v == 0 for v in scores.values()):
            return "Unknown", scores

        best = max(scores, key=scores.get)
        # Normalise to 0-100
        max_score = max(scores.values())
        norm = {k: round(v / max_score * 100, 1) for k, v in scores.items()}
        return best, norm

    @staticmethod
    def _initial_guess(label, n, t):
        """Reasonable initial parameters for each model."""
        mean_t = float(np.mean(t))
        mean_n = float(np.mean(n))
        a = mean_t / max(mean_n, 1)
        guesses = {
            "O(1)":        [mean_t],
            "O(log n)":    [a, 0.0],
            "O(n)":        [a, 0.0],
            "O(n log n)":  [a / 10, 0.0],
            "O(n²)":       [a / max(mean_n, 1), 0.0],
            "O(n² log n)": [a / max(mean_n, 1), 0.0],
            "O(n³)":       [a / max(mean_n**2, 1), 0.0],
            "O(2^n)":      [1e-6, 0.0],
        }
        return guesses.get(label, [a, 0.0])
