import os
import pandas as pd

base = r"d:\SOFTWARE\SOFTWARE II\Gemelo Digital CD Minero\database\dataset"

def inspect_csv(path, sep=None, nrows=3):
    print("="*60)
    print(f"FILE: {os.path.basename(path)}")
    print(f"PATH: {path}")
    try:
        # Detect sep if not given
        if sep is None:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                first_line = f.readline()
                if '|' in first_line:
                    sep = '|'
                elif '\t' in first_line:
                    sep = '\t'
                elif ';' in first_line:
                    sep = ';'
                else:
                    sep = ','
        df = pd.read_csv(path, sep=sep, nrows=nrows, encoding='utf-8', encoding_errors='ignore', low_memory=False)
        print(f"Detected sep: '{sep}' | Columns ({len(df.columns)}): {list(df.columns[:15])}")
        print(f"Shape preview: {df.shape}")
        print("First row:")
        print(df.iloc[0].to_dict() if len(df) > 0 else "Empty")
    except Exception as e:
        print(f"Error reading {path}: {e}")

# 1. Accidents
inspect_csv(os.path.join(base, "Accidents", "Accidents.txt"))

# 2. Mines
inspect_csv(os.path.join(base, "Mines", "Mines.txt"))

# 3. MaintNorm
maintnorm_files = [os.path.join(base, "maintnorm-main", "data", "combined", f) for f in ["train.norm", "val.norm", "test.norm"]]
for mf in maintnorm_files:
    if os.path.exists(mf):
        inspect_csv(mf)
        break

# 4. MaintIE
maintie_dir = os.path.join(base, "maintie-main")
print("="*60)
print("MaintIE directory contents:")
for r, d, fs in os.walk(maintie_dir):
    for f in fs:
        if f.endswith(('.json', '.csv', '.tsv', '.txt', '.conll', '.norm', '.jsonl')):
            fp = os.path.join(r, f)
            print(f"  {os.path.relpath(fp, maintie_dir)} ({os.path.getsize(fp)/1024:.1f} KB)")

# 5. GlobalSupplyChain
gsc_dir = os.path.join(base, "GlobalSupplyChain", "Global Supply Chain")
if os.path.exists(gsc_dir):
    print("="*60)
    print("GlobalSupplyChain XML files:")
    for f in os.listdir(gsc_dir):
        if f.endswith(".xml"):
            print(f"  {f} ({os.path.getsize(os.path.join(gsc_dir, f))/1024:.1f} KB)")

# 6. obj1_synthetic_demand.csv
inspect_csv(os.path.join(base, "obj1_synthetic_demand.csv"))

# 7. 2024_full_anonymus_v2_final.csv
inspect_csv(os.path.join(base, "2024_full_anonymus_v2_final.csv"))

# 8. FEMTO
femto_dir = os.path.join(base, "10. FEMTO Bearing")
print("="*60)
print("FEMTO structure:")
for r, d, fs in os.walk(femto_dir):
    if fs:
        sample = fs[0]
        fp = os.path.join(r, sample)
        print(f"Folder: {os.path.relpath(r, femto_dir)} -> {len(fs)} files, sample: {sample}")
        with open(fp, 'r') as f:
            lines = [f.readline().strip() for _ in range(3)]
        print(f"   sample lines: {lines}")
        break

# 9. XJTU-SY
xjtu_dir = os.path.join(base, "XJTU-SY")
print("="*60)
print("XJTU-SY files:")
for f in os.listdir(xjtu_dir):
    fp = os.path.join(xjtu_dir, f)
    print(f"  {f} ({os.path.getsize(fp)/(1024*1024):.2f} MB)")

# 10. Backorder
inspect_csv(os.path.join(base, "backorder_prediction-master", "Kaggle_Training_Dataset_v2.csv"))

# 11. calendar.csv
inspect_csv(os.path.join(base, "calendar.csv"))
