import os
import sys
import pypdf

sys.stdout.reconfigure(encoding='utf-8')
base = r"d:\SOFTWARE\SOFTWARE II\Gemelo Digital CD Minero\database\dataset"

for pdf_name, folder in [("Original dataset desription.pdf", "GlobalSupplyChain"), ("Extended dataset description.pdf", "GlobalSupplyChainExtendedDataset")]:
    pfp = os.path.join(base, folder, pdf_name)
    print(f"=== {pdf_name} ===")
    reader = pypdf.PdfReader(pfp)
    for i, p in enumerate(reader.pages):
        print(f"--- Page {i+1} ---")
        print(p.extract_text()[:1500])
