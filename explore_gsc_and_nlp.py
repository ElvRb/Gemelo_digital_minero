import os
import sys
import json
import xml.etree.ElementTree as ET
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
base = r"d:\SOFTWARE\SOFTWARE II\Gemelo Digital CD Minero\database\dataset"

# 1. Check MaintIE vs MaintNorm
print("--- MAINTIE VS MAINTNORM ---")
maintnorm_train = os.path.join(base, "maintnorm-main", "data", "combined", "train.norm")
norm_ids = set()
with open(maintnorm_train, 'r', encoding='utf-8', errors='ignore') as f:
    for line in f:
        if line.endswith("<id>\n") or line.endswith("<id>"):
            norm_ids.add(line.split('\t')[0].strip())
print(f"MaintNorm combined train unique record IDs: {len(norm_ids)}")

maintie_gold = os.path.join(base, "maintie-main", "data", "gold_release.json")
with open(maintie_gold, 'r', encoding='utf-8') as f:
    gold = json.load(f)
print(f"MaintIE gold count: {len(gold)}")
gold_texts = [g.get('text', '') for g in gold[:5]]
print("Sample gold texts:")
for t in gold_texts:
    print("  ", t)

maintie_scheme = os.path.join(base, "maintie-main", "data", "scheme.json")
with open(maintie_scheme, 'r', encoding='utf-8') as f:
    scheme = json.load(f)
if isinstance(scheme, dict):
    for k, v in scheme.items():
        print(f"MaintIE scheme '{k}' count: {len(v)}: {v[:5] if isinstance(v, list) else list(v.keys())[:5]}")

# 2. Check Global Supply Chain XML files
print("\n--- GLOBAL SUPPLY CHAIN DETAILS ---")
gsc_path = os.path.join(base, "GlobalSupplyChain", "Global Supply Chain")
for xml_name in ["DemandSignalsFinal.xml", "ComponentsProductionCost.xml", "ComponentsProductionCapacity.xml", "20ft-PortToPortCost.xml", "GenericProductionCostAndCapacity.xml"]:
    xp = os.path.join(gsc_path, xml_name)
    if os.path.exists(xp):
        tree = ET.parse(xp)
        root = tree.getroot()
        print(f"\n{xml_name} (root: {root.tag}, len: {len(root)}):")
        for i, child in enumerate(root[:2]):
            print(f"  Item {i}: tag={child.tag}, attrib={child.attrib}")
            for sub in child[:5]:
                print(f"    {sub.tag}: {sub.text}")

# 3. Read PDF info if possible using PyPDF or simple extraction
for pdf_dir in ["GlobalSupplyChain", "GlobalSupplyChainExtendedDataset"]:
    pdf_files = [f for f in os.listdir(os.path.join(base, pdf_dir)) if f.endswith('.pdf')]
    for pf in pdf_files:
        pfp = os.path.join(base, pdf_dir, pf)
        print(f"\nPDF: {pf} ({os.path.getsize(pfp)/1024:.1f} KB)")
        try:
            import pypdf
            reader = pypdf.PdfReader(pfp)
            print(f"  Pages: {len(reader.pages)}")
            print("  Page 1 snippet:\n", reader.pages[0].extract_text()[:400])
        except Exception as e:
            print(f"  Could not read pdf with pypdf: {e}")
