"""
Machine Learning Training, Stratified 5-Fold Cross-Validation,
and Automated Best Model Selection Engine.
"""
import time
from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix
)
from ml.models.models_suite import get_model_instances
from ml.feature_engineering.pipeline import MiningFeaturePipeline

class ModelTrainer:
    @staticmethod
    def train_and_evaluate_all(
        df: pd.DataFrame,
        random_state: int = 42
    ) -> Dict[str, Any]:
        """
        Executes Stratified 5-Fold CV and held-out test evaluation on the 5 models.
        Returns complete real experimental metrics without fictitious data.
        """
        X_train, X_test, y_train, y_test, scaler, feature_names = MiningFeaturePipeline.prepare_train_test(
            df, target_col="riesgo_stockout", test_size=0.20, random_state=random_state
        )

        models = get_model_instances(random_state=random_state)
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=random_state)

        cv_results_by_model = {}
        test_results = []
        trained_models = {}
        confusion_matrices = {}

        for model_name, model in models.items():
            t0 = time.time()
            fold_metrics = {
                "accuracy": [], "precision": [], "recall_critico": [],
                "f1": [], "f1_macro": [], "roc_auc": []
            }

            # 1. Stratified 5-Fold Cross Validation
            for fold_idx, (train_idx, val_idx) in enumerate(skf.split(X_train, y_train), 1):
                X_tr, X_val = X_train[train_idx], X_train[val_idx]
                y_tr, y_val = y_train[train_idx], y_train[val_idx]

                # Train on fold
                model.fit(X_tr, y_tr)
                preds_val = model.predict(X_val)
                probs_val = model.predict_proba(X_val)[:, 1] if hasattr(model, "predict_proba") else preds_val

                acc = accuracy_score(y_val, preds_val)
                prec = precision_score(y_val, preds_val, zero_division=0)
                rec = recall_score(y_val, preds_val, pos_label=1, zero_division=0)
                f1 = f1_score(y_val, preds_val, zero_division=0)
                f1_m = f1_score(y_val, preds_val, average="macro", zero_division=0)
                roc = roc_auc_score(y_val, probs_val)

                fold_metrics["accuracy"].append(acc)
                fold_metrics["precision"].append(prec)
                fold_metrics["recall_critico"].append(rec)
                fold_metrics["f1"].append(f1)
                fold_metrics["f1_macro"].append(f1_m)
                fold_metrics["roc_auc"].append(roc)

            cv_results_by_model[model_name] = fold_metrics

            # 2. Train on full X_train and evaluate on held-out X_test
            model.fit(X_train, y_train)
            train_time = round(time.time() - t0, 2)
            trained_models[model_name] = model

            test_preds = model.predict(X_test)
            test_probs = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else test_preds

            cm = confusion_matrix(y_test, test_preds).tolist()
            confusion_matrices[model_name] = cm

            t_acc = accuracy_score(y_test, test_preds)
            t_prec = precision_score(y_test, test_preds, zero_division=0)
            t_rec = recall_score(y_test, test_preds, pos_label=1, zero_division=0)
            t_f1 = f1_score(y_test, test_preds, zero_division=0)
            t_f1_m = f1_score(y_test, test_preds, average="macro", zero_division=0)
            t_roc = roc_auc_score(y_test, test_probs)

            # Compute CV statistics for F1-Macro
            f1_m_arr = np.array(fold_metrics["f1_macro"])
            cv_mean = float(np.mean(f1_m_arr))
            cv_std = float(np.std(f1_m_arr))
            cv_ci_inf = cv_mean - 1.96 * (cv_std / np.sqrt(5))
            cv_ci_sup = cv_mean + 1.96 * (cv_std / np.sqrt(5))

            test_results.append({
                "Modelo": model_name,
                "Accuracy": round(t_acc, 4),
                "Precision": round(t_prec, 4),
                "Recall (Crítico)": round(t_rec, 4),
                "F1-Score": round(t_f1, 4),
                "F1-Macro": round(t_f1_m, 4),
                "ROC-AUC": round(t_roc, 4),
                "CV_F1_Macro_Mean": round(cv_mean, 4),
                "CV_F1_Macro_Std": round(cv_std, 4),
                "CV_95_CI": f"[{round(cv_ci_inf, 4)}, {round(cv_ci_sup, 4)}]",
                "Tiempo_Seg": train_time
            })

        df_comparison = pd.DataFrame(test_results)

        # 3. Best Model Selection (Ranked primarily by F1-Macro, then ROC-AUC & Recall)
        df_sorted = df_comparison.sort_values(
            by=["F1-Macro", "ROC-AUC", "Recall (Crítico)"], ascending=[False, False, False]
        )
        best_row = df_sorted.iloc[0]
        best_model_name = best_row["Modelo"]
        best_model_obj = trained_models[best_model_name]

        return {
            "comparison_df": df_comparison,
            "best_model_name": best_model_name,
            "best_model_metrics": best_row.to_dict(),
            "best_model_obj": best_model_obj,
            "trained_models": trained_models,
            "scaler": scaler,
            "feature_names": feature_names,
            "cv_folds_data": cv_results_by_model,
            "confusion_matrices": confusion_matrices,
            "test_data": {"X_test": X_test, "y_test": y_test}
        }
