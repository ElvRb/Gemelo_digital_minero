"""
Mann-Whitney U Test for Non-Parametric Resilience Strategy Downtime Comparison.
Tests if the downtime under a resilient strategy is significantly lower than baseline.
"""
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

class MannWhitneyTest:
    @staticmethod
    def evaluate(
        baseline_downtimes: List[float],
        strategy_downtimes: List[float],
        strategy_name: str = "Estrategia Resiliente",
        alpha: float = 0.05
    ) -> Dict[str, Any]:
        """
        Executes Mann-Whitney U test:
        H0: Downtime(Baseline) <= Downtime(Strategy)
        H1: Downtime(Baseline) > Downtime(Strategy) (alternative='greater')
        """
        b_arr = np.array(baseline_downtimes)
        s_arr = np.array(strategy_downtimes)

        stat, p_val = mannwhitneyu(b_arr, s_arr, alternative="greater")
        is_sig = bool(p_val < alpha)

        mean_base = float(np.mean(b_arr))
        mean_strat = float(np.mean(s_arr))
        reduction_pct = round(((mean_base - mean_strat) / max(1.0, mean_base)) * 100.0, 2)

        conclusion = (
            f"RECHAZAR H0: Existe evidencia estadística contundente de que '{strategy_name}' "
            f"reduce significativamente el downtime minero (U = {stat:.1f}, p-valor = {p_val:.5e} < {alpha})."
            if is_sig else
            f"NO SE RECHAZA H0: No se detecta una reducción estadísticamente significativa en el downtime (p = {p_val:.4f})."
        )

        return {
            "strategy_name": strategy_name,
            "downtime_actual_horas": round(mean_base, 1),
            "downtime_estrategia_horas": round(mean_strat, 1),
            "reduccion_pct": reduction_pct,
            "u_statistic": round(float(stat), 1),
            "p_value": float(p_val),
            "alpha": alpha,
            "is_significant": is_sig,
            "conclusion": conclusion
        }
