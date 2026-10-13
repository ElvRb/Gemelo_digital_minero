"""
Module: cv_evaluator.py
Phase 14 & 15: Rigorous 5-Fold Stratified Cross-Validation on TRAIN set.
Ensures identical fold splits across all 5 models for valid paired tests.
Outputs results/cross_validation/cv_results.csv
"""

import os
import time
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from src.evaluation.metrics import compute_classification_metrics, summarize_metric_distribution

def evaluate_models_cv(models_dict, X_train, y_train, output_csv_path, random_state=42):
    """
    Executes 5-fold CV across all models on identical fold splits.
    Returns:
    - cv_results_df (long format)
    - summary_df (aggregated metrics with IC95%)
    - fold_matrix (dict of model -> metric -> fold_values)
    """
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=random_state)
    splits = list(skf.split(X_train, y_train))
    
    cv_records = []
    # Matrix for statistical testing: fold_values[metric][model] = [v1, v2, v3, v4, v5]
    metrics_list = ['accuracy', 'precision', 'recall', 'f1', 'f1_macro', 'roc_auc', 'pr_auc']
    fold_matrix = {m: {model_name: [] for model_name in models_dict.keys()} for m in metrics_list}
    
    # Check if results already computed
    if os.path.exists(output_csv_path):
        try:
            df_cv_existing = pd.read_csv(output_csv_path)
            if len(df_cv_existing) >= 175:
                print(f"[CACHE] Cargando resultados existentes de validación cruzada desde {output_csv_path}")
                summary_records = []
                for (m_name, metric), grp in df_cv_existing.groupby(['model', 'metric']):
                    if metric in fold_matrix and m_name in fold_matrix[metric]:
                        vals = grp['value'].tolist()
                        fold_matrix[metric][m_name] = vals
                        stats_d = summarize_metric_distribution(vals)
                        summary_records.append({'model': m_name, 'metric': metric, **stats_d})
                df_summary = pd.DataFrame(summary_records)
                return df_cv_existing, df_summary, fold_matrix
        except Exception as e:
            print(f"[AVISO] No se pudo cargar caché de CV: {e}. Recomputando...")

    print("="*65)
    print("EJECUTANDO VALIDACIÓN CRUZADA 5-FOLD (FOLDS IDÉNTICOS)")
    print("="*65)
    
    for model_name, pipeline in models_dict.items():
        print(f"\nEntrenando y evaluando: {model_name}...")
        t0 = time.time()
        
        for fold_idx, (train_idx, val_idx) in enumerate(splits):
            X_tr, y_tr = X_train.iloc[train_idx], y_train.iloc[train_idx]
            X_val, y_val = X_train.iloc[val_idx], y_train.iloc[val_idx]
            
            # Fit strictly on train fold
            pipeline.fit(X_tr, y_tr)
            
            # Predict
            y_pred = pipeline.predict(X_val)
            if hasattr(pipeline, "predict_proba"):
                y_prob = pipeline.predict_proba(X_val)[:, 1]
            elif hasattr(pipeline, "decision_function"):
                df_scores = pipeline.decision_function(X_val)
                y_prob = 1.0 / (1.0 + np.exp(-df_scores))
            else:
                y_prob = None
                
            metrics = compute_classification_metrics(y_val, y_pred, y_prob)
            
            for m_name, m_val in metrics.items():
                cv_records.append({
                    'model': model_name,
                    'fold': fold_idx + 1,
                    'metric': m_name,
                    'value': m_val
                })
                fold_matrix[m_name][model_name].append(m_val)
                
        elapsed = time.time() - t0
        mean_f1 = np.mean(fold_matrix['f1'][model_name])
        mean_auc = np.mean(fold_matrix['roc_auc'][model_name])
        print(f"  {model_name} completado en {elapsed:.2f} s | F1 medio: {mean_f1:.4f} | ROC-AUC: {mean_auc:.4f}")
        
    df_cv = pd.DataFrame(cv_records)
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    df_cv.to_csv(output_csv_path, index=False)
    print(f"\n[OK] Resultados de CV guardados en {output_csv_path}")
    
    # Generate summary table
    summary_rows = []
    for model_name in models_dict.keys():
        for m_name in metrics_list:
            vals = fold_matrix[m_name][model_name]
            stats_dict = summarize_metric_distribution(vals)
            summary_rows.append({
                'model': model_name,
                'metric': m_name,
                **stats_dict
            })
    df_summary = pd.DataFrame(summary_rows)
    
    return df_cv, df_summary, fold_matrix
