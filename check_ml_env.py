import sys

pkgs = ['sklearn', 'xgboost', 'lightgbm', 'shap', 'scipy', 'matplotlib', 'seaborn', 'statsmodels', 'joblib']
for pkg in pkgs:
    try:
        mod = __import__(pkg)
        print(f"  [OK] {pkg}: {getattr(mod, '__version__', 'installed')}")
    except ImportError as e:
        print(f"  [MISSING] {pkg}: {e}")
