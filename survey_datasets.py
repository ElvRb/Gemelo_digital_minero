import os
import glob
import pandas as pd

base_dir = r"d:\SOFTWARE\SOFTWARE II\Gemelo Digital CD Minero\database\dataset"

print(f"Scanning base directory: {base_dir}")
entries = os.listdir(base_dir)
for entry in entries:
    full_path = os.path.join(base_dir, entry)
    if os.path.isdir(full_path):
        # Count files inside
        files = []
        for root, dirs, filenames in os.walk(full_path):
            for f in filenames:
                files.append(os.path.join(root, f))
        print(f"\nDIR: {entry} (Total files: {len(files)})")
        # Print sample files (up to 10)
        for f in files[:10]:
            rel = os.path.relpath(f, full_path)
            size_mb = os.path.getsize(f) / (1024 * 1024)
            print(f"   - {rel} ({size_mb:.2f} MB)")
        if len(files) > 10:
            print(f"   ... and {len(files) - 10} more files")
    else:
        size_mb = os.path.getsize(full_path) / (1024 * 1024)
        print(f"\nFILE: {entry} ({size_mb:.2f} MB)")

# Also check if there's any data in other folders
other_dirs = [r"d:\SOFTWARE\SOFTWARE II\Gemelo Digital CD Minero\data"]
for od in other_dirs:
    if os.path.exists(od):
        print(f"\nScanning: {od}")
        for root, dirs, files in os.walk(od):
            for f in files:
                fp = os.path.join(root, f)
                print(f"   {os.path.relpath(fp, od)} ({os.path.getsize(fp)/(1024*1024):.2f} MB)")
