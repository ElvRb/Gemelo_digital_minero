"""
Notebook 06: Batería Estadística Pareada Rigurosa (Friedman, Wilcoxon-Holm, Nemenyi, Bootstrap BCa, Cliff's Delta)
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
    print("NOTEBOOK 06: BATERÍA ESTADÍSTICA PAREADA RIGUROSA")
    print("="*70)
    
    stat_dir = os.path.join(PROJECT_ROOT, "results", "statistics")
    integ_path = os.path.join(stat_dir, "integrated_statistical_comparison.csv")
    friedman_path = os.path.join(stat_dir, "friedman", "friedman.csv")
    
    if not os.path.exists(integ_path):
        print("Resultados estadísticos no encontrados. Ejecute run_pipeline.py primero.")
        return
        
    print("\n1. Test de Friedman:")
    df_f = pd.read_csv(friedman_path)
    print(df_f.to_string(index=False))
    
    print("\n2. Tabla Estadística Integrada (10 Pares de Modelos):")
    df_integ = pd.read_csv(integ_path)
    cols = ['model_A', 'model_B', 'delta_mean', 'p_holm', 'significant_holm', 'nemenyi_significant', 'ci95_bca', 'cliffs_delta', 'magnitude']
    print(df_integ[cols].to_string(index=False))
    
    print("\n[OK] Notebook 06 completado exitosamente.")

if __name__ == '__main__':
    main()
