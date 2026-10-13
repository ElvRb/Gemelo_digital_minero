"""
Notebook 03: Ingeniería de Features Basada en Dominio y Auditoría Estricta de Data Leakage
Artículo: "Gemelo Digital Orientado a la Resiliencia ante Disrupciones en la Logística de Repuestos Críticos de Minería Subterránea"
"""

import os
import sys
import pandas as pd
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.features.engineering import engineer_features
from src.features.leakage import audit_and_clean_leakage

def main():
    print("="*70)
    print("NOTEBOOK 03: FEATURE ENGINEERING Y AUDITORÍA DE LEAKAGE")
    print("="*70)
    
    clean_path = os.path.join(PROJECT_ROOT, "data", "master_clean", "master_clean_10k.csv")
    feat_dict_path = os.path.join(PROJECT_ROOT, "results", "features", "feature_dictionary.csv")
    leakage_audit_path = os.path.join(PROJECT_ROOT, "results", "leakage", "leakage_audit.csv")
    
    if not os.path.exists(clean_path):
        print("Dataset limpio no encontrado. Ejecute Notebook 02 primero.")
        return
        
    df_clean = pd.read_csv(clean_path, low_memory=False)
    
    print("\n1. Construcción de Features de Dominio:")
    df_featured = engineer_features(df_clean, feat_dict_path)
    print(f"   Total de columnas tras ingeniería: {df_featured.shape[1]}")
    
    print("\n2. Auditoría Estricta Anti-Data Leakage:")
    target_col = 'failure_label'
    df_audited, predictor_cols = audit_and_clean_leakage(df_featured, target_col=target_col, audit_output_path=leakage_audit_path)
    
    print(f"   Variables predictoras válidas autorizadas: {len(predictor_cols)}")
    print("   Variables eliminadas por constituir información post-evento:")
    audit_df = pd.read_csv(leakage_audit_path)
    dropped = audit_df[audit_df['action'] == 'DROPPED']
    for _, r in dropped.iterrows():
        print(f"     * {r['column']:25s} [{r['leakage_risk']:12s}]: {r['reason']}")
        
    print("\n[OK] Notebook 03 completado exitosamente.")

if __name__ == '__main__':
    main()
