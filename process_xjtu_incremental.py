import os
import sys
import time
import numpy as np
import pandas as pd
import scipy.stats as stats

sys.stdout.reconfigure(encoding='utf-8')

xjtu_dir = r"d:\SOFTWARE\SOFTWARE II\Gemelo Digital CD Minero\database\dataset\XJTU-SY"
out_csv = r"d:\SOFTWARE\SOFTWARE II\Gemelo Digital CD Minero\XJTU_SY_processed.csv"

print("Starting incremental processing of XJTU-SY Bearing dataset...")
x_files = sorted([f for f in os.listdir(xjtu_dir) if f.startswith('x') and f.endswith('.npy')])

t0 = time.time()
first_batch = True
total_processed = 0

for xf in x_files:
    prefix = xf.replace('.npy', '')
    yf = 'y' + xf[1:]
    yp = os.path.join(xjtu_dir, yf)
    xp = os.path.join(xjtu_dir, xf)
    
    # Load labels
    if os.path.exists(yp):
        y_arr = np.load(yp)
    else:
        y_arr = None
        
    # Memory-mapped read for X - zero full load into RAM
    x_arr = np.load(xp, mmap_mode='r')
    n_snapshots = x_arr.shape[0]
    
    # Extract condition and bearing ID
    # e.g. xte1_3 -> condition 1, bearing 3, split test
    condition = prefix[3] if len(prefix) > 3 else "1"
    bearing = prefix[4:] if len(prefix) > 4 else "unknown"
    split = "train" if "tr" in prefix else "test"
    
    # Process in chunks of 50 snapshots
    chunk_size = 50
    for start_idx in range(0, n_snapshots, chunk_size):
        end_idx = min(start_idx + chunk_size, n_snapshots)
        # Read only slice into memory
        chunk_x = np.array(x_arr[start_idx:end_idx])  # shape: (chunk_len, 32768, 2)
        
        chunk_records = []
        for i in range(chunk_x.shape[0]):
            snap_idx = start_idx + i
            sig_h = chunk_x[i, :, 0]
            sig_v = chunk_x[i, :, 1]
            
            # Feature calculations
            mean_h = float(np.mean(sig_h))
            mean_v = float(np.mean(sig_v))
            std_h = float(np.std(sig_h))
            std_v = float(np.std(sig_v))
            var_h = float(np.var(sig_h))
            var_v = float(np.var(sig_v))
            rms_h = float(np.sqrt(np.mean(sig_h**2)))
            rms_v = float(np.sqrt(np.mean(sig_v**2)))
            peak_h = float(np.max(np.abs(sig_h)))
            peak_v = float(np.max(np.abs(sig_v)))
            p2p_h = float(np.ptp(sig_h))
            p2p_v = float(np.ptp(sig_v))
            crest_h = float(peak_h / (rms_h + 1e-9))
            crest_v = float(peak_v / (rms_v + 1e-9))
            crest_factor = (crest_h + crest_v) / 2.0
            kurt_h = float(stats.kurtosis(sig_h))
            kurt_v = float(stats.kurtosis(sig_v))
            skew_h = float(stats.skew(sig_h))
            skew_v = float(stats.skew(sig_v))
            spec_energy_h = float(np.sum(sig_h**2) / len(sig_h))
            spec_energy_v = float(np.sum(sig_v**2) / len(sig_v))
            
            # RUL & Failure Label
            if y_arr is not None and snap_idx < len(y_arr):
                rul_val = float(y_arr[snap_idx, 0])
            else:
                rul_val = float((n_snapshots - snap_idx - 1) / n_snapshots * 100.0)
            
            degradation_idx = float(max(0.0, min(1.0, 1.0 - (rul_val / 100.0))))
            failure_lbl = 1 if rul_val <= 10.0 else 0
            
            rec_id = f"XJTU_{prefix}_s{snap_idx:04d}"
            
            chunk_records.append({
                'record_id': rec_id,
                'source_dataset': 'XJTU_SY_Bearing',
                'source_file': xf,
                'data_type': 'real_experimental',
                'source_quality': 'experimental',
                'bearing_id': f"Bearing_{prefix}",
                'operating_condition': condition,
                'snapshot_index': snap_idx,
                'split': split,
                'component': 'bearing',
                'component_type': 'Mechanical',
                'rms_horizontal': round(rms_h, 6),
                'rms_vertical': round(rms_v, 6),
                'std_horizontal': round(std_h, 6),
                'std_vertical': round(std_v, 6),
                'mean_horizontal': round(mean_h, 6),
                'mean_vertical': round(mean_v, 6),
                'variance_horizontal': round(var_h, 6),
                'variance_vertical': round(var_v, 6),
                'peak_horizontal': round(peak_h, 6),
                'peak_vertical': round(peak_v, 6),
                'peak_to_peak_horizontal': round(p2p_h, 6),
                'peak_to_peak_vertical': round(p2p_v, 6),
                'crest_factor': round(crest_factor, 6),
                'crest_factor_horizontal': round(crest_h, 6),
                'crest_factor_vertical': round(crest_v, 6),
                'kurtosis_horizontal': round(kurt_h, 6),
                'kurtosis_vertical': round(kurt_v, 6),
                'skewness_horizontal': round(skew_h, 6),
                'skewness_vertical': round(skew_v, 6),
                'spectral_energy_horizontal': round(spec_energy_h, 6),
                'spectral_energy_vertical': round(spec_energy_v, 6),
                'degradation_index': round(degradation_idx, 6),
                'rul': round(rul_val, 4),
                'failure_label': failure_lbl
            })
        
        # Intermediate write to CSV
        df_chunk = pd.DataFrame(chunk_records)
        df_chunk.to_csv(out_csv, mode='w' if first_batch else 'a', header=first_batch, index=False)
        first_batch = False
        total_processed += len(chunk_records)
        
    print(f"  Processed {xf}: {n_snapshots} snapshots (Cum total: {total_processed})")

elapsed = time.time() - t0
print(f"Incremental processing completed: {total_processed} snapshots in {elapsed:.2f} s -> {out_csv}")
