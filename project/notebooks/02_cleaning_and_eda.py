"""
Notebook 02: Limpieza de Datos y Análisis Exploratorio Exhaustivo (EDA)
Artículo: "Gemelo Digital Orientado a la Resiliencia ante Disrupciones en la Logística de Repuestos Críticos de Minería Subterránea"
"""

import os
import sys
import pandas as pd
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.data.loader import load_master_10k
from src.data.cleaner import clean_master_dataset
from src.visualization.figures_generator import generate_eda_figures, generate_missing_outlier_figures

def main():
    print("="*70)
    print("NOTEBOOK 02: LIMPIEZA DE DATOS Y ANÁLISIS EXPLORATORIO (EDA)")
    print("="*70)
    
    raw_path = os.path.join(PROJECT_ROOT, "data", "master_original", "master_original_10k.csv")
    clean_path = os.path.join(PROJECT_ROOT, "data", "master_clean", "master_clean_10k.csv")
    log_path = os.path.join(PROJECT_ROOT, "results", "cleaning", "cleaning_log.csv")
    figures_dir = os.path.join(PROJECT_ROOT, "results", "figures")
    
    df_raw = load_master_10k(raw_path)
    df_clean, cleaning_log = clean_master_dataset(df_raw, clean_path, log_path)
    
    print("\n1. Limpieza completada:")
    print(f"   - Filas procesadas: {len(df_clean):,}")
    print(f"   - Decisiones registradas en log: {len(cleaning_log)}")
    
    print("\n2. Resumen Estadístico de Variables Clave:")
    num_cols = ['lead_time_days', 'downtime_hours', 'demand', 'inventory_final']
    avail = [c for c in num_cols if c in df_clean.columns]
    print(df_clean[avail].describe().T[['count', 'mean', 'std', 'min', '50%', 'max']].to_string())
    
    print("\n3. Generación de Figuras de EDA (Fig 01 a 13)...")
    generate_eda_figures(df_clean, figures_dir)
    generate_missing_outlier_figures(df_clean, figures_dir)
    print("   Figuras generadas exitosamente en results/figures/")
    print("\n[OK] Notebook 02 completado exitosamente.")

if __name__ == '__main__':
    main()
