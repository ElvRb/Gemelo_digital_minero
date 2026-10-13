import os
import sys
import time
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
base = r"d:\SOFTWARE\SOFTWARE II\Gemelo Digital CD Minero\database\dataset\10. FEMTO Bearing\Training_set\Learning_set\Bearing1_1"

files = [os.path.join(base, f) for f in os.listdir(base) if f.endswith('.csv')][:200]
print(f"Testing pandas C-engine on {len(files)} files...")

t0 = time.time()
rows = []
for i, fp in enumerate(files):
    df = pd.read_csv(fp, header=None, usecols=[4, 5], engine='c')
    h = df[4].values
    v = df[5].values
    
    rms_h = np.sqrt(np.mean(h**2))
    rms_v = np.sqrt(np.mean(v**2))
    std_h = np.std(h)
    std_v = np.std(v)
    peak_h = np.max(np.abs(h))
    peak_v = np.max(np.abs(v))
    crest_h = peak_h / (rms_h + 1e-9)
    crest_v = peak_v / (rms_v + 1e-9)
    
elapsed = time.time() - t0
print(f"Processed {len(files)} files in {elapsed:.2f} seconds ({len(files)/elapsed:.1f} files/sec)")
print(f"Estimated time for 26,714 files: {26714 / (len(files)/elapsed):.1f} seconds")
