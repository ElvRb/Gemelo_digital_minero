import os
import sys
import glob
import json
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
base = r"d:\SOFTWARE\SOFTWARE II\Gemelo Digital CD Minero\database\dataset"

print("=== INSPECTING FEMTO ===")
femto_base = os.path.join(base, "10. FEMTO Bearing")
femto_bearings = {}
for root, dirs, files in os.walk(femto_base):
    csvs = [f for f in files if f.endswith('.csv')]
    if csvs:
        rel = os.path.relpath(root, femto_base)
        femto_bearings[rel] = len(csvs)
print(f"Total bearing folders with CSVs: {len(femto_bearings)}")
for b, c in sorted(femto_bearings.items()):
    print(f"  {b}: {c} csv files")

# Inspect one FEMTO csv
sample_femto = None
for root, dirs, files in os.walk(femto_base):
    for f in files:
        if f.endswith('.csv'):
            sample_femto = os.path.join(root, f)
            break
    if sample_femto:
        break
print(f"Sample FEMTO file: {sample_femto}")
with open(sample_femto, 'r') as f:
    sample_lines = [f.readline().strip() for _ in range(5)]
print("Sample lines:")
for l in sample_lines:
    print("  ", l)

df_sample_femto = pd.read_csv(sample_femto, header=None)
print(f"Sample FEMTO shape: {df_sample_femto.shape}, cols: {df_sample_femto.columns.tolist()}")

print("\n=== INSPECTING XJTU-SY ===")
xjtu_base = os.path.join(base, "XJTU-SY")
for f in sorted(os.listdir(xjtu_base)):
    if f.endswith('.npy'):
        arr = np.load(os.path.join(xjtu_base, f), mmap_mode='r')
        print(f"  {f:12s}: shape={str(arr.shape):20s} dtype={arr.dtype}")

print("\n=== INSPECTING GLOBAL SUPPLY CHAIN XMLs ===")
gsc_base = os.path.join(base, "GlobalSupplyChain", "Global Supply Chain")
for xml_f in sorted(os.listdir(gsc_base)):
    if xml_f.endswith('.xml'):
        p = os.path.join(gsc_base, xml_f)
        try:
            tree = ET.parse(p)
            root = tree.getroot()
            tags = [child.tag for child in root[:3]]
            print(f"  {xml_f:35s}: root={root.tag:15s} child_count={len(root):5d} sample_tags={tags}")
        except Exception as e:
            print(f"  {xml_f:35s}: error={e}")

print("\n=== INSPECTING MAINTNORM COMBINED ===")
maintnorm_combined = os.path.join(base, "maintnorm-main", "data", "combined")
for split in ["train.norm", "val.norm", "test.norm"]:
    sp_path = os.path.join(maintnorm_combined, split)
    if os.path.exists(sp_path):
        record_count = 0
        with open(sp_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if line.endswith("<id>\n") or line.endswith("<id>"):
                    record_count += 1
        print(f"  {split}: {record_count} records")

print("\n=== INSPECTING MAINTIE DATA ===")
maintie_base = os.path.join(base, "maintie-main", "data")
for jf in ["gold_release.json", "silver_release.json", "scheme.json"]:
    jp = os.path.join(maintie_base, jf)
    if os.path.exists(jp):
        with open(jp, 'r', encoding='utf-8') as f:
            d = json.load(f)
            if isinstance(d, list):
                print(f"  {jf}: list with {len(d)} items")
            elif isinstance(d, dict):
                print(f"  {jf}: dict with {len(d)} keys: {list(d.keys())[:5]}")
