import os
import sys
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
mines_path = r"d:\SOFTWARE\SOFTWARE II\Gemelo Digital CD Minero\database\dataset\Mines\Mines.txt"

df_sample = pd.read_csv(mines_path, sep='|', nrows=10, encoding='utf-8', encoding_errors='ignore', low_memory=False)
print("MSHA Mines sample cols:")
for c in ['MINE_ID', 'CURRENT_MINE_NAME', 'CURRENT_OPERATOR_NAME', 'CURRENT_CONTROLLER_NAME', 'COAL_METAL_IND', 'STATE', 'LATITUDE', 'LONGITUDE', 'CURRENT_MINE_STATUS']:
    if c in df_sample.columns:
        print(f"  {c}: {df_sample[c].tolist()[:3]}")
