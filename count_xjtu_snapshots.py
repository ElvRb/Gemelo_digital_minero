import os
import sys
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
base = r"d:\SOFTWARE\SOFTWARE II\Gemelo Digital CD Minero\database\dataset\XJTU-SY"

x_files = sorted([f for f in os.listdir(base) if f.startswith('x') and f.endswith('.npy')])
total_snapshots = 0
for xf in x_files:
    arr = np.load(os.path.join(base, xf), mmap_mode='r')
    total_snapshots += arr.shape[0]
    print(f"{xf}: {arr.shape[0]} snapshots")
print(f"TOTAL SNAPSHOTS across all XJTU-SY: {total_snapshots}")
