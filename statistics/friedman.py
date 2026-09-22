"""
Friedman Test: Non-parametric statistical comparison across 5 ML models
evaluated over the 5 cross-validation folds.
"""
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from scipy.stats import friedmanchisquare

class FriedmanTest:
    @staticmethod
    def evaluate(cv_folds_data: Dict[str, Dict[str, List[float]]], metric: str = "f1_macro", alpha: float = 0.05) -> Dict[str, Any]:
        """
        Executes the Friedman test across models.
        cv_folds_data schema: {model_name: {metric: [fold1, fold2, fold3, fold4, fold5]}}
        """
        model_names = list(cv_folds_data.keys())
        matrix = []
        for name in model_names:
            scores = cv_folds_data[name][metric]
            matrix.append(scores)
        
        # scipy friedmanchisquare expects args: (group1, group2, ...)
        stat, p_val = friedmanchisquare(*matrix)
        is_sig = bool(p_val < alpha)

        # Compute mean ranks
        arr = np.array(matrix) # shape: (n_models, n_folds)
        # Rank across models for each fold (higher is better rank 1..5)
        ranks = np.zeros_like(arr)
        for fold in range(arr.shape[1]):
            col = arr[:, fold]
            # argsort twice gives ranks
            ranks[:, fold] = len(model_names) - np.argsort(np.argsort(col))

        mean_ranks = np.mean(ranks, axis=1)
        df_ranks = pd.DataFrame({
            "Modelo": model_names,
            "Rango_Promedio": np.round(mean_ranks, 2)
        }).sort_values(by="Rango_Promedio")

        conclusion = (
            f"RECHAZAR H0: Existen diferencias estadísticamente significativas en {metric} "
            f"entre los modelos (Chi2 = {stat:.3f}, p-valor = {p_val:.5f} < {alpha})."
            if is_sig else
            f"NO SE RECHAZA H0: No se observan diferencias significativas entre los modelos "
            f"(Chi2 = {stat:.3f}, p-valor = {p_val:.5f} >= {alpha})."
        )

        return {
            "statistic": round(float(stat), 4),
            "p_value": float(p_val),
            "alpha": alpha,
            "is_significant": is_sig,
            "conclusion": conclusion,
            "mean_ranks_df": df_ranks,
            "models": model_names
        }
