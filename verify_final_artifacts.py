import os
import sys
import pandas as pd
import pyarrow.parquet as pq

sys.stdout.reconfigure(encoding='utf-8')

maestro_dir = r"d:\SOFTWARE\SOFTWARE II\Gemelo Digital CD Minero\DATASETS_MAESTRO"
proc_dir = os.path.join(maestro_dir, "processed")

print("="*60)
print("AUDITORÍA FINAL DE ARTEFACTOS GENERADOS")
print("="*60)

files = sorted(os.listdir(proc_dir))
print(f"Total de archivos en processed/ ({len(files)}):")
for f in files:
    fp = os.path.join(proc_dir, f)
    sz_mb = os.path.getsize(fp) / (1024 * 1024)
    if f.endswith('.csv'):
        with open(fp, 'r', encoding='utf-8', errors='ignore') as fl:
            first_line = fl.readline().strip()
            cols = len(first_line.split(','))
            rows = sum(1 for _ in fl)
        print(f"  - {f:30s} | {rows:10,d} filas | {cols:3d} cols | {sz_mb:8.2f} MB")
    elif f.endswith('.parquet'):
        meta = pq.read_metadata(fp)
        print(f"  - {f:30s} | {meta.num_rows:10,d} filas | {meta.num_columns:3d} cols | {sz_mb:8.2f} MB")
    else:
        print(f"  - {f:30s} | {sz_mb:8.2f} MB")

print("\n" + "="*60)
print("CONTENIDO DE DATASET_REGISTRY.CSV")
print("="*60)
df_reg = pd.read_csv(os.path.join(proc_dir, "dataset_registry.csv"))
print(df_reg.to_string(index=False))

print("\n" + "="*60)
print("CONTENIDO DE INTEGRATION_SUMMARY.CSV")
print("="*60)
df_sum = pd.read_csv(os.path.join(proc_dir, "integration_summary.csv"))
print(df_sum.to_string(index=False))

print("\n" + "="*60)
print("CONTENIDO DE DATA_QUALITY_REPORT.CSV")
print("="*60)
df_qual = pd.read_csv(os.path.join(proc_dir, "data_quality_report.csv"))
print(df_qual.to_string(index=False))

print("\n" + "="*60)
print("RESUMEN DE MISSING_VALUES_REPORT.CSV (Top 20 y Clasificación)")
print("="*60)
df_miss = pd.read_csv(os.path.join(proc_dir, "missing_values_report.csv"))
print("Conteo por clasificación:")
print(df_miss['missing_classification'].value_counts())
print("\nMuestra de variables con faltante estructural vs calidad:")
print(df_miss[['column', 'missing_percentage', 'missing_classification', 'structural_reason']].head(15).to_string(index=False))
