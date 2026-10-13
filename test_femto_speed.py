import os
import sys
import time
import numpy as np
import scipy.stats as stats

sys.stdout.reconfigure(encoding='utf-8')
base = r"d:\SOFTWARE\SOFTWARE II\Gemelo Digital CD Minero\database\dataset\10. FEMTO Bearing\Training_set\Learning_set\Bearing1_1"

files = [os.path.join(base, f) for f in os.listdir(base) if f.endswith('.csv')][:200]
print(f"Testing feature extraction on {len(files)} FEMTO files...")

t0 = time.time()
rows = []
for i, fp in enumerate(files):
    # Fast load: only cols 4 and 5 (0-indexed: 4 is horiz, 5 is vert)
    data = np.loadtxt(fp, delimiter=',', usecols=(4, 5))
    h = data[:, 0]
    v = data[:, 1]
    
    rms_h = np.sqrt(np.mean(h**2))
    rms_v = np.sqrt(np.mean(v**2))
    std_h = np.std(h)
    std_v = np.std(v)
    peak_h = np.max(np.abs(h))
    peak_v = np.max(np.abs(v))
    crest_h = peak_h / (rms_h + 1e-9)
    crest_v = peak_v / (rms_v + 1e-9)
    kurt_h = float(stats.kurtosis(h))
    kurt_v = float(stats.kurtosis(v))
    
    rows.append((rms_h, rms_v, std_h, std_v, peak_h, peak_v, crest_h, kurt_h))

elapsed = time.time() - t0
print(f"Processed {len(files)} files in {elapsed:.2f} seconds ({len(files)/elapsed:.1f} files/sec)")
print(f"Estimated time for 26,714 files: {26714 / (len(files)/elapsed):.1f} seconds")
