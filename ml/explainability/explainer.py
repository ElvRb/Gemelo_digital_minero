"""
Model Explainability Module: Feature Importance, Permutation Importance,
and SHAP value attribution for mining logistics risk.
"""
from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
import shap

class ModelExplainer:
    @staticmethod
    def get_feature_importance(model: Any, feature_names: List[str]) -> pd.DataFrame:
        """Extracts native or permutation importance for the given model."""
        importances = None
        
        # Check native tree feature_importances_
        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
        elif hasattr(model, "coef_"):
            importances = np.abs(model.coef_[0])
        elif hasattr(model, "estimators_"):
            # Voting or Stacking: compute mean across sub-estimators if available
            sub_imps = []
            for name, est in getattr(model, "named_estimators_", {}).items():
                if hasattr(est, "feature_importances_"):
                    sub_imps.append(est.feature_importances_)
            if sub_imps:
                importances = np.mean(sub_imps, axis=0)

        if importances is None:
            # Fallback uniform
            importances = np.ones(len(feature_names)) / len(feature_names)

        df_imp = pd.DataFrame({
            "Variable": feature_names,
            "Importancia": importances
        }).sort_values(by="Importancia", ascending=False)
        
        # Normalize to 0-100%
        df_imp["Importancia_Pct"] = np.round((df_imp["Importancia"] / df_imp["Importancia"].sum()) * 100.0, 2)
        return df_imp

    @staticmethod
    def get_permutation_importance(model: Any, X_test: np.ndarray, y_test: np.ndarray, feature_names: List[str]) -> pd.DataFrame:
        """Computes Permutation Importance on held-out test data."""
        perm = permutation_importance(model, X_test, y_test, n_repeats=5, random_state=42, scoring="f1_macro")
        df_perm = pd.DataFrame({
            "Variable": feature_names,
            "Importancia_Media": np.round(perm.importances_mean, 4),
            "Importancia_Std": np.round(perm.importances_std, 4)
        }).sort_values(by="Importancia_Media", ascending=False)
        return df_perm

    @staticmethod
    def get_shap_summary(model: Any, X_sample: np.ndarray, feature_names: List[str]) -> Dict[str, Any]:
        """Calculates SHAP values for model interpretation."""
        try:
            # Subsample if large
            sample = X_sample[:250]
            if hasattr(model, "feature_importances_") or "XGB" in str(type(model)):
                explainer = shap.TreeExplainer(model)
                shap_vals = explainer.shap_values(sample)
                # For binary classification, pick class 1 if list
                if isinstance(shap_vals, list):
                    shap_vals = shap_vals[1]
            else:
                explainer = shap.Explainer(model.predict, sample)
                shap_vals = explainer(sample).values

            mean_abs_shap = np.mean(np.abs(shap_vals), axis=0)
            df_shap = pd.DataFrame({
                "Variable": feature_names,
                "Mean_SHAP": np.round(mean_abs_shap, 4)
            }).sort_values(by="Mean_SHAP", ascending=False)
            
            return {
                "shap_df": df_shap,
                "shap_values_sample": shap_vals[:20].tolist(),
                "feature_names": feature_names
            }
        except Exception as e:
            # Fallback to feature importance if shap compilation encounters issue
            df_fallback = ModelExplainer.get_feature_importance(model, feature_names)
            return {
                "shap_df": df_fallback.rename(columns={"Importancia": "Mean_SHAP"}),
                "shap_values_sample": [],
                "feature_names": feature_names,
                "fallback": True,
                "error": str(e)
            }
