"""
Notebook 01: Auditoría Inicial del Dataset Maestro y Muestreo Representativo
Artículo: "Gemelo Digital Orientado a la Resiliencia ante Disrupciones en la Logística de Repuestos Críticos de Minería Subterránea"
"""

import os
import sys
import pandas as pd
import numpy as np

# Set project path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.data.loader import load_master_10k

def main():
    print("="*70)
    print("NOTEBOOK 01: AUDITORÍA INICIAL Y CONTROL DE INTEGRIDAD DE LA MUESTRA")
    print("="*70)
    
    data_path = os.path.join(PROJECT_ROOT, "data", "master_original", "master_original_10k.csv")
    df = load_master_10k(data_path)
    
    print(f"\n1. Dimensiones de la Muestra: {df.shape[0]:,} filas x {df.shape[1]} columnas")
    print(f"2. Uso de Memoria: {df.memory_usage(deep=True).sum() / (1024*1024):.2f} MB")
    
    # Fuentes representadas
    print("\n3. Distribución por Dataset Fuente:")
    src_dist = df['source_dataset'].value_counts()
    for src, cnt in src_dist.items():
        print(f"   - {src:30s}: {cnt:5d} ({cnt/len(df)*100:.2f}%)")
        
    # Variables de identificación y trazabilidad
    print("\n4. Variables de Trazabilidad:")
    trace_cols = ['source_dataset', 'source_file', 'source_record_id', 'data_type', 'source_quality']
    for c in trace_cols:
        if c in df.columns:
            print(f"   - {c:20s}: {df[c].notna().sum():,} valores no nulos ({df[c].nunique():,} únicos)")
            
    # Estado inicial de valores faltantes
    missing_pct = df.isna().mean() * 100.0
    print(f"\n5. Promedio Global de Faltantes: {missing_pct.mean():.2f}%")
    print("   Top 5 variables con mayor completitud:")
    for c, pct in missing_pct.nsmallest(5).items():
        print(f"     * {c:25s}: {100-pct:.2f}% completo")
        
    print("\n[OK] Notebook 01 completado exitosamente.")

if __name__ == '__main__':
    main()
