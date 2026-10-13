import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
base = r"d:\SOFTWARE\SOFTWARE II\Gemelo Digital CD Minero\database\dataset\10. FEMTO Bearing"

total_files = 0
for root, dirs, files in os.walk(base):
    csvs = [f for f in files if f.endswith('.csv')]
    if csvs:
        rel = os.path.relpath(root, base)
        total_files += len(csvs)
        print(f"  {rel:40s}: {len(csvs):5d} files")
print(f"TOTAL CSV FILES IN FEMTO: {total_files}")
