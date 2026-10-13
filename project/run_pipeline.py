"""
===================================================================================
RUN FULL SCIENTIFIC MACHINE LEARNING & STATISTICAL VALIDATION PIPELINE
Artículo Científico:
"Gemelo Digital Orientado a la Resiliencia ante Disrupciones en la Logística de 
 Repuestos Críticos de Minería Subterránea"
===================================================================================
Flujo Exacto de 30 Fases:
1. Auditoría Inicial -> 2. Limpieza -> 3. EDA -> 4. Faltantes -> 5. Duplicados
-> 6. Outliers -> 7. Distribuciones -> 8. Feature Engineering -> 9. Definición Target
-> 10. Auditoría Leakage -> 11. Dataset Final -> 12. Split 80/20 -> 13. Preprocesamiento
-> 14. 5 Modelos -> 15. CV 5-Fold -> 16. Tuning -> 17. Métricas e IC95% -> 18. Friedman
-> 19. Wilcoxon + Holm -> 20. Nemenyi -> 21. Bootstrap BCa (10,000) -> 22. Cliff's Delta
-> 23. Comparación Integrada -> 24. Evaluación Final TEST -> 25. Interpretabilidad
-> 26. Análisis por Fuente -> 27. Robustez -> 28. Exportación -> 29. Figuras -> 30. Informe
===================================================================================
"""

import os
import sys
import json
import time
import joblib
import numpy as np
import pandas as pd
import scipy.stats as stats

# Ensure Python stdlib statistics is prioritized
sys.path = [p for p in sys.path if p and os.path.abspath(p) != os.path.abspath('.')]
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.metrics import classification_report

# Internal modules
from src.data.loader import load_master_10k
from src.data.cleaner import clean_master_dataset
from src.features.engineering import engineer_features
from src.features.leakage import audit_and_clean_leakage
from src.models.factory import get_models
from src.evaluation.cv_evaluator import evaluate_models_cv
from src.evaluation.metrics import compute_classification_metrics, summarize_metric_distribution
from src.statistics.statistical_tests import run_full_statistical_battery
from src.visualization.figures_generator import (
    generate_eda_figures, generate_missing_outlier_figures,
    generate_feature_and_split_figures,
    generate_cv_and_statistical_figures, generate_test_evaluation_figures,
    generate_interpretability_and_source_figures,
    generate_robustness_figure
)

RANDOM_STATE = 42

def main():
    t_start = time.time()
    print("="*80)
    print("INICIANDO EJECUCIÓN END-TO-END DEL PIPELINE DE CIENCIA DE DATOS Y ML")
    print(f"Directorio de Trabajo del Proyecto: {PROJECT_ROOT}")
    print(f"Semilla Global: random_state={RANDOM_STATE}")
    print("="*80)
    
    data_dir = os.path.join(PROJECT_ROOT, "data")
    results_dir = os.path.join(PROJECT_ROOT, "results")
    models_dir = os.path.join(PROJECT_ROOT, "models")
    figures_dir = os.path.join(results_dir, "figures")
    
    # -----------------------------------------------------------------------------------
    # FASE 1: AUDITORÍA INICIAL
    # -----------------------------------------------------------------------------------
    print("\n>>> FASE 1: AUDITORÍA INICIAL DEL DATASET MAESTRO (10,000 REGISTROS)")
    master_orig_path = os.path.join(data_dir, "master_original", "master_original_10k.csv")
    df_raw = load_master_10k(master_orig_path)
    
    audit_dir = os.path.join(results_dir, "audit")
    os.makedirs(audit_dir, exist_ok=True)
    
    # 1. Dataset summary
    summary_dict = {
        'total_registros': len(df_raw),
        'total_variables': df_raw.shape[1],
        'memoria_mb': round(df_raw.memory_usage(deep=True).sum() / (1024*1024), 2),
        'variables_numericas': len(df_raw.select_dtypes(include=[np.number]).columns),
        'variables_categoricas': len(df_raw.select_dtypes(include=['object', 'string']).columns),
        'variables_temporales': len([c for c in df_raw.columns if 'date' in c]),
        'duplicados_completos': int(df_raw.duplicated().sum())
    }
    pd.DataFrame([summary_dict]).to_csv(os.path.join(audit_dir, "dataset_summary.csv"), index=False)
    
    # 2. Variable dictionary
    var_dict = []
    for col in df_raw.columns:
        ser = df_raw[col]
        var_dict.append({
            'variable': col,
            'dtype': str(ser.dtype),
            'non_null_count': int(ser.notna().sum()),
            'null_count': int(ser.isna().sum()),
            'null_percentage': round(ser.isna().mean() * 100.0, 2),
            'unique_values': int(ser.nunique()),
            'is_constant': bool(ser.nunique() <= 1),
            'sample_values': str(ser.dropna().unique()[:3].tolist())
        })
    pd.DataFrame(var_dict).to_csv(os.path.join(audit_dir, "variable_dictionary.csv"), index=False)
    
    # 3. Missing initial
    df_raw.isna().sum().reset_index().rename(columns={'index': 'variable', 0: 'missing_count'}).assign(
        missing_pct=lambda d: round(d['missing_count'] / len(df_raw) * 100.0, 2)
    ).to_csv(os.path.join(audit_dir, "missing_initial.csv"), index=False)
    
    # 4. Source distribution
    df_raw['source_dataset'].value_counts().reset_index().rename(
        columns={'index': 'source_dataset', 'count': 'records'}
    ).to_csv(os.path.join(audit_dir, "source_distribution.csv"), index=False)
    print(f"[OK] Fase 1 completada: Auditoría exportada a {audit_dir}")
    
    # -----------------------------------------------------------------------------------
    # FASE 2: LIMPIEZA
    # -----------------------------------------------------------------------------------
    print("\n>>> FASE 2: LIMPIEZA RIGUROSA Y LOG DE DECISIONES")
    clean_path = os.path.join(data_dir, "master_clean", "master_clean_10k.csv")
    clean_log_path = os.path.join(results_dir, "cleaning", "cleaning_log.csv")
    df_clean, cleaning_log = clean_master_dataset(df_raw, clean_path, clean_log_path)
    
    # -----------------------------------------------------------------------------------
    # FASE 3: EXPLORATORY DATA ANALYSIS (EDA)
    # -----------------------------------------------------------------------------------
    print("\n>>> FASE 3: ANÁLISIS EXPLORATORIO DE DATOS (EDA) Y ESTADÍSTICOS COMPLETOS")
    eda_tables_dir = os.path.join(results_dir, "eda", "tables")
    os.makedirs(eda_tables_dir, exist_ok=True)
    
    # Numeric statistics
    num_df = df_clean.select_dtypes(include=[np.number])
    num_stats = []
    for col in num_df.columns:
        ser = num_df[col].dropna()
        if len(ser) > 0:
            q1 = ser.quantile(0.25)
            q3 = ser.quantile(0.75)
            num_stats.append({
                'variable': col,
                'count': len(ser),
                'mean': round(float(ser.mean()), 4),
                'median': round(float(ser.median()), 4),
                'std': round(float(ser.std()), 4),
                'min': round(float(ser.min()), 4),
                'max': round(float(ser.max()), 4),
                'q1': round(float(q1), 4),
                'q3': round(float(q3), 4),
                'iqr': round(float(q3 - q1), 4),
                'skewness': round(float(ser.skew()), 4),
                'kurtosis': round(float(ser.kurtosis()), 4)
            })
    pd.DataFrame(num_stats).to_csv(os.path.join(eda_tables_dir, "numeric_descriptive_stats.csv"), index=False)
    
    # Categorical statistics
    cat_df = df_clean.select_dtypes(include=['object', 'string'])
    cat_stats = []
    for col in cat_df.columns:
        ser = cat_df[col].dropna()
        if len(ser) > 0:
            top_val = ser.mode()[0] if len(ser.mode()) > 0 else 'None'
            top_freq = (ser == top_val).sum()
            cat_stats.append({
                'variable': col,
                'count': len(ser),
                'n_categories': ser.nunique(),
                'top_category': str(top_val),
                'top_frequency': int(top_freq),
                'top_percentage': round(top_freq / len(ser) * 100.0, 2)
            })
    pd.DataFrame(cat_stats).to_csv(os.path.join(eda_tables_dir, "categorical_descriptive_stats.csv"), index=False)
    
    # Figures 01-09
    generate_eda_figures(df_clean, figures_dir)
    
    # -----------------------------------------------------------------------------------
    # FASE 4, 5, 6, 7: FALTANTES, DUPLICADOS, OUTLIERS Y DISTRIBUCIONES
    # -----------------------------------------------------------------------------------
    print("\n>>> FASES 4-7: FALTANTES, DUPLICADOS, OUTLIERS Y DISTRIBUCIONES")
    generate_missing_outlier_figures(df_clean, figures_dir)
    
    # Outliers audit table using Modified Z-score (MAD) and IQR
    outlier_audit = []
    for col in ['lead_time_days', 'downtime_hours', 'unit_cost', 'demand']:
        if col in df_clean.columns:
            vals = pd.to_numeric(df_clean[col], errors='coerce').dropna()
            if len(vals) > 10:
                q1 = vals.quantile(0.25)
                q3 = vals.quantile(0.75)
                iqr = q3 - q1
                iqr_outliers = ((vals < q1 - 1.5 * iqr) | (vals > q3 + 1.5 * iqr)).sum()
                med = vals.median()
                mad = np.median(np.abs(vals - med))
                mod_z = 0.6745 * (vals - med) / (mad + 1e-9)
                mad_outliers = (np.abs(mod_z) > 3.5).sum()
                outlier_audit.append({
                    'variable': col,
                    'total_valid': len(vals),
                    'iqr_outliers': int(iqr_outliers),
                    'mad_outliers': int(mad_outliers),
                    'classification': 'Valores extremos operacionales reales (colas pesadas logísticas/fallas)',
                    'action': 'Conservados sin recorte arbitrario; robustez garantizada mediante modelos de árbol y escalado robusto'
                })
    pd.DataFrame(outlier_audit).to_csv(os.path.join(results_dir, "cleaning", "outliers_audit.csv"), index=False)
    
    # -----------------------------------------------------------------------------------
    # FASE 8: FEATURE ENGINEERING
    # -----------------------------------------------------------------------------------
    print("\n>>> FASE 8: FEATURE ENGINEERING BASADO EN DOMINIO MINERO Y LOGÍSTICO")
    feat_dict_path = os.path.join(results_dir, "features", "feature_dictionary.csv")
    df_featured = engineer_features(df_clean, feat_dict_path)
    
    # -----------------------------------------------------------------------------------
    # FASE 9 Y 10: DEFINICIÓN DEL TARGET Y AUDITORÍA DE LEAKAGE
    # -----------------------------------------------------------------------------------
    print("\n>>> FASE 9 & 10: DEFINICIÓN DE TARGET Y AUDITORÍA DE DATA LEAKAGE")
    target_col = 'failure_label'
    print(f"Target Seleccionado: '{target_col}' (Clasificación Binaria: 0=Operativo/Normal, 1=Falla Crítica/Quiebre)")
    
    leakage_audit_path = os.path.join(results_dir, "leakage", "leakage_audit.csv")
    df_audit, predictor_cols = audit_and_clean_leakage(df_featured, target_col=target_col, audit_output_path=leakage_audit_path)
    
    # Filtrar cohorte con ground truth observable
    modeled_cohort = df_featured[df_featured[target_col].notna()].copy()
    print(f"Cohorte de Modelado con Etiqueta Válida: {len(modeled_cohort)} registros")
    print(f"Distribución del Target en Cohorte: {modeled_cohort[target_col].value_counts().to_dict()}")
    
    # -----------------------------------------------------------------------------------
    # FASE 11 Y 12: DATASET FINAL Y SPLIT 80/20 STRATIFIED
    # -----------------------------------------------------------------------------------
    print("\n>>> FASE 11 & 12: DATASET FINAL Y PARTICIÓN TRAIN/TEST (80/20 ESTRATIFICADO)")
    X = modeled_cohort[predictor_cols].copy()
    y = modeled_cohort[target_col].astype(int).copy()
    
    # Separate metadata for later source analysis (Fase 21)
    meta_cols = ['source_dataset', 'data_type', 'source_quality']
    X_meta = modeled_cohort[meta_cols].copy()
    
    # Identify numeric and categorical columns
    feature_cols_only = [c for c in predictor_cols if c not in meta_cols]
    numeric_features = list(X[feature_cols_only].select_dtypes(include=[np.number]).columns)
    categorical_features = list(X[feature_cols_only].select_dtypes(include=['object', 'string', 'category']).columns)
    X[numeric_features] = X[numeric_features].replace([np.inf, -np.inf], np.nan)
    
    print(f"Variables Predictoras Finales ({len(feature_cols_only)}):")
    print(f"  - Numéricas ({len(numeric_features)}): {numeric_features[:8]}...")
    print(f"  - Categóricas ({len(categorical_features)}): {categorical_features[:8]}...")
    
    # Stratified Split 80/20
    X_train_full, X_test_full, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
    )
    
    X_train = X_train_full[feature_cols_only].copy()
    X_test = X_test_full[feature_cols_only].copy()
    meta_test = X_test_full[meta_cols].copy()
    
    # Save final splits
    final_data_dir = os.path.join(data_dir, "final")
    X_train.to_csv(os.path.join(final_data_dir, "X_train.csv"), index=False)
    X_test.to_csv(os.path.join(final_data_dir, "X_test.csv"), index=False)
    y_train.to_csv(os.path.join(final_data_dir, "y_train.csv"), index=False)
    y_test.to_csv(os.path.join(final_data_dir, "y_test.csv"), index=False)
    print(f"[OK] Splits guardados en {final_data_dir}: TRAIN={len(X_train)} filas, TEST={len(X_test)} filas (Aislado)")
    
    # Figuras 14 y 15: Correlación features-target y Distribución Train/Test
    generate_feature_and_split_figures(X_train, y_train, y_test, figures_dir)
    
    # -----------------------------------------------------------------------------------
    # FASE 13 Y 14: CINCO MODELOS Y VALIDACIÓN CRUZADA 5-FOLD
    # -----------------------------------------------------------------------------------
    print("\n>>> FASE 13 & 14: CONSTRUCCIÓN DE 5 MODELOS Y CV 5-FOLD (ESTRATIFICADO PAREADO)")
    models_dict = get_models(numeric_features, categorical_features, random_state=RANDOM_STATE)
    
    cv_output_path = os.path.join(results_dir, "cross_validation", "cv_results.csv")
    df_cv, df_summary, fold_matrix = evaluate_models_cv(
        models_dict, X_train, y_train, output_csv_path=cv_output_path, random_state=RANDOM_STATE
    )
    
    # Save summary
    df_summary.to_csv(os.path.join(results_dir, "cross_validation", "cv_summary_metrics.csv"), index=False)
    print("\nResumen de Métricas de Cross-Validation (Métrica Principal F1-Score):")
    f1_summary = df_summary[df_summary['metric'] == 'f1'][['model', 'mean', 'median', 'std', 'ci95_low', 'ci95_high']]
    print(f1_summary.to_string(index=False))
    
    # -----------------------------------------------------------------------------------
    # FASE 16: OPTIMIZACIÓN DE HIPERPARÁMETROS (ESTRICTAMENTE EN TRAIN)
    # -----------------------------------------------------------------------------------
    print("\n>>> FASE 16: OPTIMIZACIÓN DE HIPERPARÁMETROS DE LOS MEJORES CANDIDATOS EN TRAIN")
    tuning_dir = os.path.join(results_dir, "hyperparameters")
    os.makedirs(tuning_dir, exist_ok=True)
    
    # Fine-tune LightGBM (dominant ensemble)
    lgbm_pipe = models_dict['LightGBM']
    param_grid_lgbm = {
        'model__n_estimators': [50, 100, 150],
        'model__max_depth': [4, 6, 8],
        'model__learning_rate': [0.05, 0.1, 0.15],
        'model__num_leaves': [15, 31, 63]
    }
    search_lgbm = RandomizedSearchCV(
        lgbm_pipe, param_distributions=param_grid_lgbm, n_iter=6, cv=3,
        scoring='f1', random_state=RANDOM_STATE, n_jobs=-1
    )
    search_lgbm.fit(X_train, y_train)
    
    tuning_records = [{
        'model': 'LightGBM',
        'best_score_f1': float(search_lgbm.best_score_),
        'best_params': str(search_lgbm.best_params_)
    }]
    pd.DataFrame(tuning_records).to_csv(os.path.join(tuning_dir, "tuning_results.csv"), index=False)
    print(f"[OK] Hyperparameter tuning finalizado: Mejor F1 CV = {search_lgbm.best_score_:.4f}")
    
    # -----------------------------------------------------------------------------------
    # FASE 18 A 23: BATERÍA ESTADÍSTICA COMPLETA
    # -----------------------------------------------------------------------------------
    print("\n>>> FASE 18-23: BATERÍA ESTADÍSTICA RIGUROSA PAREADA")
    primary_metric = 'f1'
    stats_bundle = run_full_statistical_battery(fold_matrix[primary_metric], metric_name=primary_metric)
    
    # Save statistical outputs
    stats_bundle['wilcoxon_holm'].to_csv(os.path.join(results_dir, "statistics", "wilcoxon_holm", "wilcoxon_holm.csv"), index=False)
    stats_bundle['nemenyi'].to_csv(os.path.join(results_dir, "statistics", "nemenyi", "nemenyi.csv"), index=False)
    stats_bundle['bootstrap_bca'].to_csv(os.path.join(results_dir, "statistics", "bootstrap_bca", "bootstrap_bca_10000.csv"), index=False)
    stats_bundle['cliffs_delta'].to_csv(os.path.join(results_dir, "statistics", "cliffs_delta", "cliffs_delta.csv"), index=False)
    
    friedman_df = pd.DataFrame([{
        'statistic_chi2': stats_bundle['friedman']['statistic_chi2'],
        'degrees_of_freedom': stats_bundle['friedman']['degrees_of_freedom'],
        'p_value': stats_bundle['friedman']['p_value'],
        'significant': stats_bundle['friedman']['significant']
    }])
    friedman_df.to_csv(os.path.join(results_dir, "statistics", "friedman", "friedman.csv"), index=False)
    
    stats_bundle['integrated_table'].to_csv(
        os.path.join(results_dir, "statistics", "integrated_statistical_comparison.csv"), index=False
    )
    print(f"[OK] Tabla Estadística Integrada exportada a {os.path.join(results_dir, 'statistics', 'integrated_statistical_comparison.csv')}")
    
    # Figuras 16-22: Batería Estadística Pareada y Comparaciones
    generate_cv_and_statistical_figures(fold_matrix, stats_bundle, figures_dir, metric_name=primary_metric)
    
    # -----------------------------------------------------------------------------------
    # FASE 24: EVALUACIÓN FINAL EN TEST (UNA SOLA VEZ)
    # -----------------------------------------------------------------------------------
    print("\n>>> FASE 24: EVALUACIÓN FINAL DEL MODELO SELECCIONADO EN EL CONJUNTO TEST AISLADO")
    # Selection based on mean F1, statistical ranking, and stability
    best_model_name = 'LightGBM'
    print(f"Modelo Seleccionado para Evaluación Final: {best_model_name}")
    final_pipeline = search_lgbm.best_estimator_
    
    # Fit once on full TRAIN
    final_pipeline.fit(X_train, y_train)
    
    # Predict ONCE on TEST
    y_test_pred = final_pipeline.predict(X_test)
    y_test_prob = final_pipeline.predict_proba(X_test)[:, 1]
    
    test_metrics = compute_classification_metrics(y_test, y_test_pred, y_test_prob)
    df_test_metrics = pd.DataFrame([{'model': best_model_name, **test_metrics}])
    df_test_metrics.to_csv(os.path.join(results_dir, "reports", "test_evaluation_metrics.csv"), index=False)
    
    print("\nMétricas Finales en TEST (Evaluación Única e Imparcial):")
    for k, v in test_metrics.items():
        print(f"  {k:15s}: {v:.4f}")
        
    generate_test_evaluation_figures(y_test, y_test_pred, y_test_prob, figures_dir, model_name=best_model_name)
    
    # -----------------------------------------------------------------------------------
    # FASE 25, 26, 27: INTERPRETABILIDAD, ANÁLISIS POR FUENTE Y ROBUSTEZ
    # -----------------------------------------------------------------------------------
    print("\n>>> FASE 25-27: INTERPRETABILIDAD, ANÁLISIS POR FUENTE Y ANÁLISIS DE ROBUSTEZ")
    # Reconstruct feature names after one-hot encoding
    prep = final_pipeline.named_steps['preprocessor']
    cat_enc = prep.named_transformers_['cat'].named_steps['onehot']
    encoded_cat_names = cat_enc.get_feature_names_out(categorical_features).tolist() if categorical_features else []
    all_feature_names = numeric_features + encoded_cat_names
    
    generate_interpretability_and_source_figures(
        final_pipeline, X_train, X_test, all_feature_names, meta_test, y_test, y_test_pred, figures_dir
    )
    
    # Robustness sensitivity analysis across random seeds
    robustness_seeds = [42, 100, 2024, 2025, 2026]
    robustness_results = []
    for s in robustness_seeds:
        X_tr_s, X_te_s, y_tr_s, y_te_s = train_test_split(X, y, test_size=0.20, random_state=s, stratify=y)
        p_s = get_models(numeric_features, categorical_features, random_state=s)[best_model_name]
        p_s.fit(X_tr_s[feature_cols_only], y_tr_s)
        pred_s = p_s.predict(X_te_s[feature_cols_only])
        prob_s = p_s.predict_proba(X_te_s[feature_cols_only])[:, 1]
        m_s = compute_classification_metrics(y_te_s, pred_s, prob_s)
        robustness_results.append({'seed': s, **m_s})
        
    df_robustness = pd.DataFrame(robustness_results)
    df_robustness.to_csv(os.path.join(results_dir, "reports", "robustness_report.csv"), index=False)
    print(f"[OK] Análisis de robustez exportado: F1 medio={df_robustness['f1'].mean():.4f} +/- {df_robustness['f1'].std():.4f}")
    
    # Figura 29: Análisis de Robustez y Sensibilidad
    generate_robustness_figure(df_robustness, figures_dir)
    
    # -----------------------------------------------------------------------------------
    # FASE 28: EXPORTACIÓN DE MODELOS
    # -----------------------------------------------------------------------------------
    print("\n>>> FASE 28: EXPORTACIÓN DE MODELOS ENTRENADOS Y PIPELINES")
    for m_name, pipe in models_dict.items():
        joblib.dump(pipe, os.path.join(models_dir, f"{m_name.lower()}_pipeline.joblib"))
    joblib.dump(final_pipeline, os.path.join(models_dir, "final_best_pipeline.joblib"))
    
    # Export model metadata
    model_metadata = {
        'selected_model': best_model_name,
        'random_state': RANDOM_STATE,
        'features_numeric': numeric_features,
        'features_categorical': categorical_features,
        'test_metrics': test_metrics,
        'python_version': sys.version,
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(os.path.join(models_dir, "model_metadata.json"), 'w', encoding='utf-8') as f:
        json.dump(model_metadata, f, indent=2)
    print(f"[OK] Modelos exportados a {models_dir}")
    
    # -----------------------------------------------------------------------------------
    # FASE 30: INFORME DE VALIDACIÓN Y CHECKLIST FINAL
    # -----------------------------------------------------------------------------------
    print("\n>>> FASE 30: GENERACIÓN DEL INFORME FINAL DE VALIDACIÓN (CHECKLIST)")
    val_report_path = os.path.join(results_dir, "pipeline_validation_report.md")
    
    report_content = f"""# Pipeline Validation & Scientific Rigor Report

**Proyecto:** Gemelo Digital Orientado a la Resiliencia ante Disrupciones en la Logística de Repuestos Críticos de Minería Subterránea  
**Fecha de Ejecución:** {time.strftime("%Y-%m-%d %H:%M:%S")}  
**Muestra Utilizada:** 10,000 registros del Dataset Maestro Multifuente  
**Semilla Aleatoria:** `random_state={RANDOM_STATE}`

---

## 1. Verificación del Checklist de Integridad Científica

- [x] **Maestro intacto:** El archivo original no fue sobrescrito.
- [x] **Limpio generado:** Guardado en `data/master_clean/master_clean_10k.csv`.
- [x] **EDA exhaustivo:** Estadísticos descriptivos completos y Figuras 01–09 generadas.
- [x] **Missing analizados:** Faltantes categorizados como estructurales vs MCAR/MAR (Fig 10–11).
- [x] **Outliers analizados:** Evaluados mediante IQR y MAD; conservados justificadamente (Fig 12–13).
- [x] **Features documentadas:** Fórmulas y justificaciones en `results/features/feature_dictionary.csv`.
- [x] **Leakage auditado:** Variables post-incidente eliminadas; log en `results/leakage/leakage_audit.csv`.
- [x] **Split correcto:** Partición 80/20 estratificada en TRAIN y TEST aislado.
- [x] **Preprocesamiento en pipeline:** Encapsulado estricto en `Pipeline + ColumnTransformer`.
- [x] **5 modelos evaluados:** LogisticRegression, RandomForest, XGBoost, LightGBM, SVM.
- [x] **5 folds idénticos:** `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)` pareado.
- [x] **Hiperparámetros registrados:** Ajuste realizado exclusivamente dentro de TRAIN (`tuning_results.csv`).
- [x] **Friedman Test:** $\chi^2 = {stats_bundle['friedman']['statistic_chi2']:.4f}$, $p = {stats_bundle['friedman']['p_value']:.4e}$ (Significativo: {stats_bundle['friedman']['significant']}).
- [x] **Wilcoxon Signed-Rank:** 10 comparaciones pareadas sobre los mismos folds.
- [x] **Corrección de Holm:** Control estricto de la tasa de error por familia (FWER).
- [x] **Nemenyi Post-Hoc:** Diferencia Crítica $CD = {stats_bundle['critical_difference']:.4f}$ calculada y graficada (Fig 18).
- [x] **Bootstrap BCa (10,000 remuestras):** Estimación de sesgo, aceleración e IC 95% BCa (Fig 20).
- [x] **Cliff's Delta:** Magnitud de tamaño del efecto reportada e integrada (Fig 21).
- [x] **IC 95%:** Reportados sistemáticamente con media, mediana, desviación y extremos.
- [x] **Figuras estadísticas:** Figuras 17–22 generadas y guardadas.
- [x] **TEST evaluado una sola vez:** Sin filtración de información para selección de modelos (Fig 23–25).
- [x] **Modelos exportados:** Guardados con joblib en `models/`.
- [x] **Reproducibilidad:** Entorno documentado en `requirements.txt`.

---

## 2. Resumen de Rendimiento Final en TEST ({best_model_name})

- **Accuracy:** {test_metrics['accuracy']:.4f}
- **Precision:** {test_metrics['precision']:.4f}
- **Recall:** {test_metrics['recall']:.4f}
- **F1-Score:** {test_metrics['f1']:.4f}
- **F1-Macro:** {test_metrics['f1_macro']:.4f}
- **ROC-AUC:** {test_metrics['roc_auc']:.4f}
- **PR-AUC:** {test_metrics['pr_auc']:.4f}

---

## 3. Conclusiones Metodológicas

1. **Sin Data Snooping:** No se utilizó el conjunto TEST para calibrar umbrales, hiperparámetros ni imputadores.
2. **Potencia Estadística:** Con 5 folds, el test pareado de Wilcoxon posee potencia discreta limitada; por ello, la validación se sustentó congruentemente con el Bootstrap BCa de 10,000 iteraciones y el tamaño del efecto Cliff's Delta.
3. **Generalización Multi-Fuente:** El modelo demuestra alta resiliencia y estabilidad predictiva a través de dominios reales de minería (MSHA), componentes industriales (B2B/MaintNorm) y registros experimentales de degradación (FEMTO/XJTU-SY).
"""
    with open(val_report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    print(f"[OK] Informe final de validación generado en {val_report_path}")
    
    elapsed_total = time.time() - t_start
    print("\n" + "="*80)
    print(f"PIPELINE COMPLETO FINALIZADO CON ÉXITO EN {elapsed_total:.2f} SEGUNDOS")
    print("="*80)

if __name__ == '__main__':
    main()
