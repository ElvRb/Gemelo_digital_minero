import os
import sys
import pandas as pd
import numpy as np
import pyarrow.parquet as pq

sys.stdout.reconfigure(encoding='utf-8')

# Ensure stdlib statistics is prioritized
sys.path = [p for p in sys.path if p and os.path.abspath(p) != os.path.abspath('.')]

parquet_path = r"d:\SOFTWARE\SOFTWARE II\Gemelo Digital CD Minero\DATASETS_MAESTRO\processed\dataset_maestro.parquet"
csv_path = r"d:\SOFTWARE\SOFTWARE II\Gemelo Digital CD Minero\DATASETS_MAESTRO\processed\dataset_maestro.csv"

print(f"Reading metadata from {parquet_path}...")
meta = pq.read_metadata(parquet_path)
print(f"Total rows in Master Parquet: {meta.num_rows:,} | Columns: {meta.num_columns}")

# Sample exactly 10,000 records using random_state=42
# We can read in chunks or sample across chunks to get a balanced/representative 10k sample
# Let's inspect source_dataset representation
df_meta = pd.read_parquet(parquet_path, columns=['source_dataset', 'data_type', 'source_quality', 'conceptual_stage', 'failure_label', 'stockout', 'demand', 'downtime_hours', 'rul'])

print("\n--- Source distribution in full dataset ---")
print(df_meta['source_dataset'].value_counts())

print("\n--- Data type distribution in full dataset ---")
print(df_meta['data_type'].value_counts())

print("\n--- Target Candidates Non-null and distributions ---")
for t in ['failure_label', 'stockout', 'demand', 'downtime_hours', 'rul']:
    valid = df_meta[t].dropna()
    print(f"\nTarget Candidate '{t}':")
    print(f"  Valid count: {len(valid):,} ({len(valid)/len(df_meta)*100:.2f}%)")
    if t in ['failure_label', 'stockout']:
        print(f"  Value counts:\n{valid.value_counts()}")
    else:
        print(f"  Summary: min={valid.min()}, max={valid.max()}, mean={valid.mean():.2f}, median={valid.median():.2f}")
