"""
Notebook 04: Diseño de Pipelines Herméticos y Partición Train/Test
Artículo: "Gemelo Digital Orientado a la Resiliencia ante Disrupciones en la Logística de Repuestos Críticos de Minería Subterránea"
"""

import os
import sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.preprocessing.pipeline_builder import build_preprocessing_pipeline
from src.visualization.figures_generator import generate_feature_and_split_figures

def main():
    print("="*70)
    print("NOTEBOOK 04: DISEÑO DE PREPROCESAMIENTO Y PARTICIÓN TRAIN/TEST")
    print("="*70)
    
    final_data_dir = os.path.join(PROJECT_ROOT, "data", "final")
    x_train_path = os.path.join(final_data_dir, "X_train.csv")
    
    if not os.path.exists(x_train_path):
        print("Archivos de split no encontrados. Ejecute run_pipeline.py primero.")
        return
        
    X_train = pd.read_csv(x_train_path)
    X_test = pd.read_csv(os.path.join(final_data_dir, "X_test.csv"))
    y_train = pd.read_csv(os.path.join(final_data_dir, "y_train.csv")).squeeze()
    y_test = pd.read_csv(os.path.join(final_data_dir, "y_test.csv")).squeeze()
    
    num_cols = list(X_train.select_dtypes(include=[np.number]).columns)
    cat_cols = list(X_train.select_dtypes(include=['object', 'string']).columns)
    
    print(f"\n1. Conjunto TRAIN: {X_train.shape[0]} registros ({y_train.mean()*100:.1f}% positivos)")
    print(f"2. Conjunto TEST (Aislado): {X_test.shape[0]} registros ({y_test.mean()*100:.1f}% positivos)")
    print(f"3. Tipología de Variables Predictoras: {len(num_cols)} Numéricas | {len(cat_cols)} Categóricas")
    
    print("\n4. Ensamblado del ColumnTransformer:")
    preprocessor = build_preprocessing_pipeline(num_cols, cat_cols)
    print(preprocessor)
    
    print("\n5. Generando Figuras 14 y 15 (Correlación y Estratificación)...")
    figures_dir = os.path.join(PROJECT_ROOT, "results", "figures")
    generate_feature_and_split_figures(X_train, y_train, y_test, figures_dir)
    print("   Figuras generadas exitosamente en results/figures/")
    print("\n[OK] Notebook 04 completado exitosamente.")

if __name__ == '__main__':
    main()
