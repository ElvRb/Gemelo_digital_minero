import sys
import os

print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")

for pkg in ["pandas", "numpy", "scipy", "pyarrow", "fastparquet", "openpyxl"]:
    try:
        mod = __import__(pkg)
        print(f"  [OK] {pkg}: {getattr(mod, '__version__', 'installed')}")
    except ImportError as e:
        print(f"  [MISSING] {pkg}: {e}")
