import os
import sys
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
acc_path = r"d:\SOFTWARE\SOFTWARE II\Gemelo Digital CD Minero\database\dataset\Accidents\Accidents.txt"

df_sample = pd.read_csv(acc_path, sep='|', nrows=10, encoding='utf-8', encoding_errors='ignore', low_memory=False)
print("MSHA Accidents sample cols:")
for c in ['MINE_ID', 'DOCUMENT_NO', 'ACCIDENT_DT', 'DEGREE_INJURY', 'DAYS_LOST', 'MINING_EQUIP', 'EQUIP_MODEL_NO', 'CLASSIFICATION']:
    if c in df_sample.columns:
        print(f"  {c}: {df_sample[c].tolist()[:3]}")

# Check nulls and types on 1000 rows
df_1000 = pd.read_csv(acc_path, sep='|', nrows=1000, encoding='utf-8', encoding_errors='ignore', low_memory=False)
print("Injury degrees:", df_1000['DEGREE_INJURY'].value_counts().head(5).to_dict())
print("Equipments:", df_1000['MINING_EQUIP'].dropna().value_counts().head(5).to_dict())
