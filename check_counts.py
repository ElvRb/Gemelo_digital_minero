import os
import sys
import glob
import pandas as pd
import json

sys.stdout.reconfigure(encoding='utf-8')
base = r"d:\SOFTWARE\SOFTWARE II\Gemelo Digital CD Minero\database\dataset"

print("--- 1. MSHA ACCIDENTS ---")
acc_path = os.path.join(base, "Accidents", "Accidents.txt")
# Count rows quickly
count = 0
with open(acc_path, 'r', encoding='utf-8', errors='ignore') as f:
    header = f.readline().strip().split('|')
    for _ in f:
        count += 1
print(f"Total records in Accidents.txt: {count}")
print(f"Header ({len(header)} cols): {header}")

print("\n--- 2. MSHA MINES ---")
mines_path = os.path.join(base, "Mines", "Mines.txt")
count_mines = 0
with open(mines_path, 'r', encoding='utf-8', errors='ignore') as f:
    header_mines = f.readline().strip().split('|')
    for _ in f:
        count_mines += 1
print(f"Total records in Mines.txt: {count_mines}")
print(f"Header ({len(header_mines)} cols): {header_mines}")

print("\n--- 3. MAINTNORM ---")
maintnorm_dir = os.path.join(base, "maintnorm-main")
# Check how maintnorm records are structured
train_norm = os.path.join(maintnorm_dir, "data", "combined", "train.norm")
lines = []
with open(train_norm, 'r', encoding='utf-8', errors='ignore') as f:
    for i in range(30):
        lines.append(f.readline())
print("First 30 lines of train.norm:")
for l in lines:
    print(repr(l))

print("\n--- 6. AVIATION SPARE PARTS ---")
av_path = os.path.join(base, "obj1_synthetic_demand.csv")
df_av = pd.read_csv(av_path)
print(f"Aviation shape: {df_av.shape}")
print(df_av.head(2))

print("\n--- 7. B2B-PARTS-REC ---")
b2b_files = sorted(glob.glob(os.path.join(base, "202*_full_anonymus_v2_final.csv")))
for bf in b2b_files:
    # count lines
    with open(bf, 'r', encoding='utf-8', errors='ignore') as f:
        c = sum(1 for _ in f) - 1
    print(f"{os.path.basename(bf)}: {c} records")

print("\n--- 10. BACKORDERS ---")
for bo_f in ["Kaggle_Training_Dataset_v2.csv", "Kaggle_Test_Dataset_v2.csv"]:
    p = os.path.join(base, "backorder_prediction-master", bo_f)
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8', errors='ignore') as f:
            c = sum(1 for _ in f) - 1
        print(f"{bo_f}: {c} records")

print("\n--- 11. M5 FORECASTING ---")
cal_path = os.path.join(base, "calendar.csv")
df_cal = pd.read_csv(cal_path)
print(f"Calendar shape: {df_cal.shape}")
print(df_cal.head(2))
