"""
Notebook 05: Entrenamiento de 5 Modelos y Validación Cruzada 5-Fold Pareada
Artículo: "Gemelo Digital Orientado a la Resiliencia ante Disrupciones en la Logística de Repuestos Críticos de Minería Subterránea"
"""

import os
import sys
import pandas as pd
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def main():
    print("="*70)
    print("NOTEBOOK 05: VALIDACIÓN CRUZADA ESTRATIFICADA PAREADA (5 MODELOS)")
    print("="*70)
    
    cv_summary_path = os.path.join(PROJECT_ROOT, "results", "cross_validation", "cv_summary_metrics.csv")
    cv_results_path = os.path.join(PROJECT_ROOT, "results", "cross_validation", "cv_results.csv")
    
    if not os.path.exists(cv_summary_path):
        print("Resultados de CV no encontrados. Ejecute run_pipeline.py primero.")
        return
        
    df_summary = pd.read_csv(cv_summary_path)
    df_cv = pd.read_csv(cv_results_path)
    
    print("\n1. Modelos Evaluados sobre Folds Idénticos:")
    for m in df_cv['model'].unique():
        print(f"   - {m}")
        
    print("\n2. Resumen de F1-Score en Validación Cruzada (Media, Mediana, Desviación, IC 95%):")
    f1_df = df_summary[df_summary['metric'] == 'f1'][['model', 'mean', 'median', 'std', 'min', 'max', 'ci95_low', 'ci95_high']]
    print(f1_df.to_string(index=False))
    
    print("\n3. Resumen de ROC-AUC en Validación Cruzada:")
    auc_df = df_summary[df_summary['metric'] == 'roc_auc'][['model', 'mean', 'median', 'std', 'ci95_low', 'ci95_high']]
    print(auc_df.to_string(index=False))
    
    print("\n[OK] Notebook 05 completado exitosamente.")

if __name__ == '__main__':
    main()
