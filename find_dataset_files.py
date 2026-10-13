import os

workspace = r"d:\SOFTWARE\SOFTWARE II\Gemelo Digital CD Minero"

print("Searching for files across workspace...")
matches = []
for root, dirs, files in os.walk(workspace):
    # Skip .git, venv
    if ".git" in root or "venv" in root or ".pytest_cache" in root:
        continue
    for f in files:
        fl = f.lower()
        if any(k in fl for k in ["m5", "aviation", "b2b", "obj1", "calendar", "spare", "demand", "stockout", "backorder", "maint", "msha", "femto", "xjtu", "supply"]):
            matches.append(os.path.join(root, f))

for m in sorted(matches):
    rel = os.path.relpath(m, workspace)
    sz = os.path.getsize(m) / (1024*1024)
    print(f"{rel} ({sz:.3f} MB)")
