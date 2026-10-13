import os
import sys
import glob
import json
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

base = r"d:\SOFTWARE\SOFTWARE II\Gemelo Digital CD Minero\database\dataset"

print("--- 1. MSHA ACCIDENTS ---")
acc_path = os.path.join(base, "Accidents", "Accidents.txt")
with open(acc_path, 'r', encoding='utf-8', errors='ignore') as f:
    acc_cols = f.readline().strip().split('|')
print(f"Accidents cols ({len(acc_cols)}): {acc_cols[:15]}")
print(f"Accidents file size: {os.path.getsize(acc_path)/(1024*1024):.2f} MB")

print("\n--- 2. MSHA MINES ---")
mines_path = os.path.join(base, "Mines", "Mines.txt")
with open(mines_path, 'r', encoding='utf-8', errors='ignore') as f:
    mines_cols = f.readline().strip().split('|')
print(f"Mines cols ({len(mines_cols)}): {mines_cols[:15]}")
print(f"Mines file size: {os.path.getsize(mines_path)/(1024*1024):.2f} MB")

print("\n--- 3. MAINTNORM ---")
maintnorm_dir = os.path.join(base, "maintnorm-main")
for f in ["README.md", "DATA.md"]:
    fp = os.path.join(maintnorm_dir, f)
    if os.path.exists(fp):
        print(f"[{f} snippet]:")
        with open(fp, 'r', encoding='utf-8', errors='ignore') as mf:
            lines = [mf.readline() for _ in range(8)]
            print("".join(lines))

norm_files = glob.glob(os.path.join(maintnorm_dir, "**", "*.norm"), recursive=True)
print(f"Norm files found: {norm_files}")
for nf in norm_files[:2]:
    with open(nf, 'r', encoding='utf-8', errors='ignore') as f:
        print(f"Sample from {os.path.basename(nf)}:")
        for _ in range(5):
            print("  ", repr(f.readline()))

print("\n--- 4. MAINTIE ---")
maintie_gold = os.path.join(base, "maintie-main", "data", "gold_release.json")
if os.path.exists(maintie_gold):
    with open(maintie_gold, 'r', encoding='utf-8') as f:
        gold_data = json.load(f)
    print(f"Gold records count: {len(gold_data)}")
    print(f"Gold sample keys: {list(gold_data[0].keys()) if len(gold_data) > 0 else 'None'}")
    if len(gold_data) > 0:
        sample = gold_data[0]
        print(f"Sample gold entry tokens: {sample.get('tokens')[:10] if 'tokens' in sample else sample}")
        print(f"Sample gold entities: {sample.get('entities')[:3] if 'entities' in sample else 'None'}")

print("\n--- 5. GLOBAL SUPPLY CHAIN ---")
gsc_dir = os.path.join(base, "GlobalSupplyChain", "Global Supply Chain")
demand_xml = os.path.join(gsc_dir, "DemandSignalsFinal.xml")
if os.path.exists(demand_xml):
    tree = ET.parse(demand_xml)
    root = tree.getroot()
    print(f"DemandSignalsFinal root tag: {root.tag}, children count: {len(root)}")
    if len(root) > 0:
        sample_elem = root[0]
        print(f"Sample elem tag: {sample_elem.tag}, attrib: {sample_elem.attrib}")
        print(f"Sample subelements: {[(child.tag, child.text) for child in sample_elem[:5]]}")

print("\n--- 6. AVIATION SPARE PARTS ---")
av_path = os.path.join(base, "obj1_synthetic_demand.csv")
df_av = pd.read_csv(av_path, nrows=5)
print(f"Aviation columns: {list(df_av.columns)}")
print(f"Aviation rows approx: {sum(1 for _ in open(av_path))} lines")

print("\n--- 7. B2B-PARTS-REC ---")
b2b_files = sorted(glob.glob(os.path.join(base, "202*_full_anonymus_v2_final.csv")))
print(f"B2B files ({len(b2b_files)}): {[os.path.basename(x) for x in b2b_files]}")

print("\n--- 8. FEMTO BEARING ---")
femto_dir = os.path.join(base, "10. FEMTO Bearing")
subdirs = [d for d in os.listdir(femto_dir) if os.path.isdir(os.path.join(femto_dir, d))]
print(f"FEMTO subdirs: {subdirs}")
for sd in subdirs:
    sd_path = os.path.join(femto_dir, sd)
    bearings = [b for b in os.listdir(sd_path) if os.path.isdir(os.path.join(sd_path, b))]
    print(f"  {sd}: {bearings}")

print("\n--- 9. XJTU-SY BEARING ---")
xjtu_dir = os.path.join(base, "XJTU-SY")
npy_files = [f for f in os.listdir(xjtu_dir) if f.endswith(".npy")]
print(f"XJTU-SY .npy files count: {len(npy_files)}")
# Inspect first couple .npy
for nf in npy_files[:4]:
    arr = np.load(os.path.join(xjtu_dir, nf), mmap_mode='r')
    print(f"  {nf}: shape={arr.shape}, dtype={arr.dtype}")

print("\n--- 10. BACKORDERS ---")
bo_path = os.path.join(base, "backorder_prediction-master", "Kaggle_Training_Dataset_v2.csv")
df_bo = pd.read_csv(bo_path, nrows=5)
print(f"Backorders cols: {list(df_bo.columns)}")

print("\n--- 11. M5 FORECASTING ---")
cal_path = os.path.join(base, "calendar.csv")
df_cal = pd.read_csv(cal_path, nrows=5)
print(f"Calendar cols: {list(df_cal.columns)}")
print(f"Calendar lines: {sum(1 for _ in open(cal_path))} lines")
