import os
import sys
import time
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
base = r"d:\SOFTWARE\SOFTWARE II\Gemelo Digital CD Minero\database\dataset\10. FEMTO Bearing\Training_set\Learning_set\Bearing1_1"
files = [os.path.join(base, f) for f in os.listdir(base) if f.endswith('.csv')][:200]

# Method 1: pandas
t0 = time.time()
for fp in files:
    df = pd.read_csv(fp, header=None, usecols=[4, 5], engine='c')
    h = df[4].values
    v = df[5].values
    _ = np.sqrt(np.mean(h**2))
t_pd = time.time() - t0
print(f"Pandas read_csv: {t_pd:.2f} s ({len(files)/t_pd:.1f} files/sec)")

# Method 2: fast binary read + split
t0 = time.time()
for fp in files:
    with open(fp, 'rb') as f:
        content = f.read().decode('latin1')
    # parse cols 4 and 5
    lines = content.strip().split('\n')
    # each line has 6 commas
    data = [line.rsplit(',', 2)[1:] for line in lines if ',' in line]
    arr = np.array(data, dtype=np.float32)
    h = arr[:, 0]
    v = arr[:, 1]
    _ = np.sqrt(np.mean(h**2))
t_str = time.time() - t0
print(f"String split + float32: {t_str:.2f} s ({len(files)/t_str:.1f} files/sec)")
