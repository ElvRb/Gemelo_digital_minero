"""
Scientific Hypothesis Evaluation Engine (H0 vs H1).
Formal verification of the 30% downtime reduction threshold with p < 0.05.
"""
from typing import Dict, Any, List
from statistics.mann_whitney import MannWhitneyTest
from statistics.bootstrap import BootstrapEstimator

class HypothesisEvaluator:
    @staticmethod
    def test_hypothesis(
        baseline_downtimes: List[float],
        strategy_downtimes: List[float],
        strategy_name: str = "Estrategia Resiliente Recomendada",
        alpha: float = 0.05,
        threshold_reduction_pct: float = 30.0
    ) -> Dict[str, Any]:
        """
        Formally tests H0 vs H1 based on empirical simulation results.
        H0: Reduction < 30% or p >= 0.05
        H1: Reduction >= 30% and p < 0.05
        """
        # 1. Mann-Whitney U test
        mw_res = MannWhitneyTest.evaluate(
            baseline_downtimes=baseline_downtimes,
            strategy_downtimes=strategy_downtimes,
            strategy_name=strategy_name,
            alpha=alpha
        )

        # 2. Bootstrap 10,000 resamples for 95% CI of reduction
        boot_res = BootstrapEstimator.estimate_downtime_reduction(
            baseline_downtimes=baseline_downtimes,
            strategy_downtimes=strategy_downtimes,
            n_bootstraps=10000,
            random_state=42
        )

        red_pct = boot_res["mean_reduction_pct"]
        ci_inf = boot_res["ci95_inf"]
        ci_sup = boot_res["ci95_sup"]
        p_val = mw_res["p_value"]

        # Evaluation criteria
        is_stat_sig = bool(p_val < alpha)
        meets_threshold = bool(red_pct >= threshold_reduction_pct)
        reject_h0 = bool(is_stat_sig and meets_threshold)

        verdict_title = "RECHAZAR H0 (Apoyo formal a H1)" if reject_h0 else "NO SE RECHAZA H0"
        
        if reject_h0:
            conclusion = (
                f"RECHAZAR H0: Existe evidencia estadística rigurosa de que la estrategia '{strategy_name}' "
                f"identificada por el Digital Twin reduce significativamente el downtime minero "
                f"en al menos un {threshold_reduction_pct}% respecto a la situación actual.\n"
                f"• Reducción media estimada: {red_pct:.1f}%\n"
                f"• Intervalo de Confianza Bootstrap al 95%: [{ci_inf:.1f}%, {ci_sup:.1f}%]\n"
                f"• p-valor (Mann-Whitney U): {p_val:.5e} (< {alpha})"
            )
        else:
            conclusion = (
                f"NO SE RECHAZA H0: La reducción estimada ({red_pct:.1f}%) o la significancia estadística "
                f"(p = {p_val:.4f}) no satisfacen simultáneamente el criterio del {threshold_reduction_pct}% "
                f"con α={alpha}."
            )

        return {
            "verdict": verdict_title,
            "reject_h0": reject_h0,
            "downtime_actual_horas": mw_res["downtime_actual_horas"],
            "downtime_optimo_horas": mw_res["downtime_estrategia_horas"],
            "reduccion_estimada_pct": red_pct,
            "ci95_inferior": ci_inf,
            "ci95_superior": ci_sup,
            "ci95_str": boot_res["ci95_str"],
            "p_value": p_val,
            "u_statistic": mw_res["u_statistic"],
            "alpha": alpha,
            "conclusion_completa": conclusion
        }
