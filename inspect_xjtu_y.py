import os
import sys
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
base = r"d:\SOFTWARE\SOFTWARE II\Gemelo Digital CD Minero\database\dataset\XJTU-SY"

y_files = sorted([f for f in os.listdir(base) if f.startswith('y') and f.endswith('.npy')])
print(f"Total Y files: {len(y_files)}")
for yf in y_files[:5]:
    arr = np.load(os.path.join(base, yf))
    print(f"{yf}: shape={arr.shape}, min={arr.min()}, max={arr.max()}, first 5={arr[:5].flatten()}")
