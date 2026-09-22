"""
Bootstrap Resampling Engine (10,000 iterations, 95% CI).
Estimates non-parametric confidence intervals for:
1. Machine learning performance differences (F1-score, Recall).
2. Downtime reduction percentages between supply chain resilience strategies.
"""
from typing import Dict, Any, Tuple, List
import numpy as np
import pandas as pd

class BootstrapEstimator:
    @staticmethod
    def estimate_metric_difference(
        y_true: np.ndarray,
        preds_model_a: np.ndarray,
        preds_model_b: np.ndarray,
        n_bootstraps: int = 10000,
        random_state: int = 42
    ) -> Dict[str, Any]:
        """Estimates 95% CI for F1-score difference between Model A and Model B using 10k bootstrap replicates."""
        from sklearn.metrics import f1_score
        rng = np.random.RandomState(random_state)
        n = len(y_true)
        diffs = np.zeros(n_bootstraps)

        for b in range(n_bootstraps):
            idx = rng.randint(0, n, size=n)
            y_b = y_true[idx]
            p_a_b = preds_model_a[idx]
            p_b_b = preds_model_b[idx]
            
            f1_a = f1_score(y_b, p_a_b, average="macro", zero_division=0)
            f1_b = f1_score(y_b, p_b_b, average="macro", zero_division=0)
            diffs[b] = f1_a - f1_b

        mean_diff = float(np.mean(diffs))
        ci_inf = float(np.percentile(diffs, 2.5))
        ci_sup = float(np.percentile(diffs, 97.5))

        return {
            "n_bootstraps": n_bootstraps,
            "mean_difference": round(mean_diff, 4),
            "ci95_inf": round(ci_inf, 4),
            "ci95_sup": round(ci_sup, 4),
            "ci95_str": f"[{round(ci_inf, 4)}, {round(ci_sup, 4)}]",
            "is_significant": bool(ci_inf > 0.0 or ci_sup < 0.0),
            "distribution_sample": diffs[::50].tolist() # 200 points for UI histogram
        }

    @staticmethod
    def estimate_downtime_reduction(
        baseline_downtimes: List[float],
        strategy_downtimes: List[float],
        n_bootstraps: int = 10000,
        random_state: int = 42
    ) -> Dict[str, Any]:
        """
        Estimates 95% CI for percentage downtime reduction using 10k bootstrap resamples
        from Monte Carlo runs: Reduction = ((D_base - D_strat) / D_base) * 100%.
        """
        rng = np.random.RandomState(random_state)
        b_arr = np.array(baseline_downtimes)
        s_arr = np.array(strategy_downtimes)
        n = min(len(b_arr), len(s_arr))

        reduction_samples = np.zeros(n_bootstraps)
        for b in range(n_bootstraps):
            idx = rng.randint(0, n, size=n)
            b_sample = b_arr[idx]
            s_sample = s_arr[idx]
            
            mean_b = np.mean(b_sample)
            mean_s = np.mean(s_sample)
            red = ((mean_b - mean_s) / max(1.0, mean_b)) * 100.0
            reduction_samples[b] = red

        mean_red = float(np.mean(reduction_samples))
        ci_inf = float(np.percentile(reduction_samples, 2.5))
        ci_sup = float(np.percentile(reduction_samples, 97.5))

        return {
            "n_bootstraps": n_bootstraps,
            "mean_reduction_pct": round(mean_red, 2),
            "ci95_inf": round(ci_inf, 2),
            "ci95_sup": round(ci_sup, 2),
            "ci95_str": f"[{round(ci_inf, 2)}%, {round(ci_sup, 2)}%]",
            "meets_hypothesis_30_pct": bool(ci_inf >= 30.0),
            "distribution_sample": reduction_samples[::50].tolist()
        }
