import os
import sys
import time
import numpy as np
import pandas as pd
import scipy.stats as stats

sys.stdout.reconfigure(encoding='utf-8')

femto_base = r"d:\SOFTWARE\SOFTWARE II\Gemelo Digital CD Minero\database\dataset\10. FEMTO Bearing"
out_csv = r"d:\SOFTWARE\SOFTWARE II\Gemelo Digital CD Minero\FEMTO_processed.csv"

print("Starting feature extraction on FEMTO Bearing dataset...")

# Collect all bearing directories
bearing_dirs = []
for root, dirs, files in os.walk(femto_base):
    csvs = [f for f in files if f.endswith('.csv')]
    if csvs:
        bearing_dirs.append((root, sorted(csvs)))

print(f"Found {len(bearing_dirs)} bearing runs with CSVs.")

t0 = time.time()
first_batch = True
total_processed = 0

for b_idx, (b_dir, csv_list) in enumerate(bearing_dirs):
    rel_path = os.path.relpath(b_dir, femto_base)
    # determine set type
    parts = rel_path.split(os.sep)
    set_type = parts[0] if len(parts) > 0 else "Unknown"
    bearing_name = parts[-1]
    
    # Condition and bearing number from name e.g. Bearing1_3 -> cond 1, brg 3
    cond = bearing_name.replace("Bearing", "").split("_")[0] if "_" in bearing_name else "1"
    brg_num = bearing_name.replace("Bearing", "").split("_")[1] if "_" in bearing_name else "1"
    
    total_files_in_run = len(csv_list)
    print(f"\nProcessing [{b_idx+1}/{len(bearing_dirs)}] {rel_path} ({total_files_in_run} files)...")
    
    run_records = []
    for f_idx, fname in enumerate(csv_list):
        fp = os.path.join(b_dir, fname)
        try:
            # Read fast with open and split
            with open(fp, 'rb') as f:
                content = f.read().decode('latin1')
            lines = content.strip().split('\n')
            data = [line.rsplit(',', 2)[1:] for line in lines if ',' in line]
            arr = np.array(data, dtype=np.float32)
            if arr.shape[0] < 10 or arr.shape[1] < 2:
                continue
            
            sig_h = arr[:, 0]
            sig_v = arr[:, 1]
            
            rms_h = float(np.sqrt(np.mean(sig_h**2)))
            rms_v = float(np.sqrt(np.mean(sig_v**2)))
            std_h = float(np.std(sig_h))
            std_v = float(np.std(sig_v))
            mean_h = float(np.mean(sig_h))
            mean_v = float(np.mean(sig_v))
            var_h = float(np.var(sig_h))
            var_v = float(np.var(sig_v))
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
            
            # RUL calculation: remaining files * 10 seconds (or normalized %)
            remaining_files = total_files_in_run - f_idx - 1
            rul_val = float(remaining_files / total_files_in_run * 100.0)
            degradation_idx = float(max(0.0, min(1.0, 1.0 - (rul_val / 100.0))))
            failure_lbl = 1 if rul_val <= 10.0 else 0
            
            rec_id = f"FEMTO_{bearing_name}_{fname.replace('.csv', '')}"
            
            run_records.append({
                'record_id': rec_id,
                'source_dataset': 'FEMTO_Bearing',
                'source_file': fname,
                'data_type': 'real_experimental',
                'source_quality': 'experimental',
                'bearing_id': bearing_name,
                'set_type': set_type,
                'operating_condition': cond,
                'snapshot_index': f_idx + 1,
                'total_snapshots': total_files_in_run,
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
        except Exception as e:
            continue
            
    if run_records:
        df_run = pd.DataFrame(run_records)
        df_run.to_csv(out_csv, mode='w' if first_batch else 'a', header=first_batch, index=False)
        first_batch = False
        total_processed += len(run_records)
        print(f"  Saved {len(run_records)} records (Cum total: {total_processed})")

elapsed = time.time() - t0
print(f"\nFEMTO processing finished: {total_processed} files in {elapsed:.2f} s -> {out_csv}")
