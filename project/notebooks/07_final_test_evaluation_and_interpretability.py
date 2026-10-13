"""
Notebook 07: Evaluación Final Imparcial en TEST e Interpretabilidad SHAP
Artículo: "Gemelo Digital Orientado a la Resiliencia ante Disrupciones en la Logística de Repuestos Críticos de Minería Subterránea"
"""

import os
import sys
import pandas as pd
import json

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def main():
    print("="*70)
    print("NOTEBOOK 07: EVALUACIÓN FINAL EN TEST E INTERPRETABILIDAD")
    print("="*70)
    
    test_metrics_path = os.path.join(PROJECT_ROOT, "results", "reports", "test_evaluation_metrics.csv")
    meta_path = os.path.join(PROJECT_ROOT, "models", "model_metadata.json")
    
    if not os.path.exists(test_metrics_path):
        print("Métricas de TEST no encontradas. Ejecute run_pipeline.py primero.")
        return
        
    df_metrics = pd.read_csv(test_metrics_path)
    print("\n1. Desempeño del Modelo Seleccionado en Conjunto TEST Aislado:")
    for col in df_metrics.columns:
        val = df_metrics[col].iloc[0]
        if isinstance(val, (int, float)):
            print(f"   - {col:15s}: {val:.4f}")
        else:
            print(f"   - {col:15s}: {val}")
            
    print("\n2. Metadatos de Exportación:")
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    print(f"   - Modelo Guardado: {meta['selected_model']}")
    print(f"   - Semilla: {meta['random_state']}")
    print(f"   - Variables Numéricas: {len(meta['features_numeric'])}")
    print(f"   - Variables Categóricas: {len(meta['features_categorical'])}")
    print(f"   - Timestamp: {meta['timestamp']}")
    
    print("\n[OK] Notebook 07 completado exitosamente.")

if __name__ == '__main__':
    main()
