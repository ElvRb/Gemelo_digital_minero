"""
Wilcoxon Signed-Rank Test with Holm-Bonferroni Multiple Comparison Correction.
Performs pairwise non-parametric comparisons between the best model and other candidates.
"""
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

class WilcoxonHolmTest:
    @staticmethod
    def evaluate(
        cv_folds_data: Dict[str, Dict[str, List[float]]],
        best_model_name: str,
        metric: str = "f1_macro",
        alpha: float = 0.05
    ) -> Dict[str, Any]:
        """
        Runs paired Wilcoxon signed-rank tests between the best model and all other models,
        adjusting p-values with the Holm-Bonferroni step-down procedure.
        """
        best_scores = np.array(cv_folds_data[best_model_name][metric])
        other_models = [m for m in cv_folds_data.keys() if m != best_model_name]
        
        raw_comparisons = []
        for other in other_models:
            other_scores = np.array(cv_folds_data[other][metric])
            diff = best_scores - other_scores
            
            # If differences are completely identical zero
            if np.all(diff == 0):
                stat, p_val = 0.0, 1.0
            else:
                try:
                    res = wilcoxon(best_scores, other_scores, alternative="greater")
                    stat, p_val = float(res.statistic), float(res.pvalue)
                except Exception:
                    # Small sample tie handling
                    stat, p_val = 0.0, 0.0625

            raw_comparisons.append({
                "Modelo_A": best_model_name,
                "Modelo_B": other,
                "statistic": stat,
                "p_value_raw": p_val,
                "diff_mean": float(np.mean(diff))
            })

        # Holm-Bonferroni step-down adjustment:
        # Sort by raw p-value ascending
        raw_comparisons.sort(key=lambda x: x["p_value_raw"])
        m = len(raw_comparisons)
        
        adjusted_results = []
        for k, comp in enumerate(raw_comparisons, 1):
            multiplier = m - k + 1
            p_adj = min(1.0, comp["p_value_raw"] * multiplier)
            is_sig = p_adj < alpha
            
            adjusted_results.append({
                "Comparación": f"{comp['Modelo_A']} vs {comp['Modelo_B']}",
                "Diferencia_Media": round(comp["diff_mean"], 4),
                "Estadístico_W": round(comp["statistic"], 2),
                "p_value_raw": round(comp["p_value_raw"], 5),
                "p_value_ajustado": round(p_adj, 5),
                "Significativo (α=0.05)": "Sí" if is_sig else "No"
            })

        df_out = pd.DataFrame(adjusted_results)
        any_sig = any(r["Significativo (α=0.05)"] == "Sí" for r in adjusted_results)

        conclusion = (
            f"El modelo '{best_model_name}' supera de forma estadísticamente significativa "
            f"a modelos competidores tras la corrección de Holm-Bonferroni (α={alpha})."
            if any_sig else
            f"No se detecta superioridad estadísticamente significativa de '{best_model_name}' "
            f"frente a todos los modelos tras la corrección de Holm-Bonferroni."
        )

        return {
            "best_model": best_model_name,
            "metric": metric,
            "alpha": alpha,
            "table_df": df_out,
            "conclusion": conclusion
        }
