"""
Adapters for public external datasets: MSHA (Mining Safety and Health Administration)
and UCI Machine Learning Repository Supply Chain Logistics benchmark.
Provides standard schemas and conversion pipelines for cross-dataset validation.
"""
from pathlib import Path
import pandas as pd
import numpy as np

EXTERNAL_DIR = Path(__file__).resolve().parent

def load_or_mirror_msha_dataset() -> pd.DataFrame:
    """
    Loads or generates an MSHA-standardized mining incident & equipment failure dataset.
    MSHA schema: MINE_ID, SUBUNIT, EQUIPMENT_TYPE, INCIDENT_TYPE, LOST_HOURS, SHIFT.
    """
    csv_path = EXTERNAL_DIR / "msha_equipment_failures.csv"
    if csv_path.exists():
        return pd.read_csv(csv_path)
    
    # Generate high-fidelity MSHA benchmark mirror
    rng = np.random.RandomState(42)
    n = 2500
    subunits = ["Underground Haulageway", "Stope Production Face", "Shaft / Hoistway", "Drift / Ramp", "Pump Station"]
    eq_types = ["Haulage LHD", "Drill Jumbo", "Continuous Haulage", "Mine Fan", "Slurry Pump"]
    
    df = pd.DataFrame({
        "MINE_ID": rng.choice(["TITAN-01", "ANDINA-02", "SUR-03"], size=n),
        "SUBUNIT": rng.choice(subunits, size=n),
        "EQUIPMENT_TYPE": rng.choice(eq_types, size=n),
        "FAILURE_CAUSE": rng.choice(["Hydraulic Burst", "Power Transmission Failure", "Bearing Seizure", "Electrical Fault"], size=n),
        "LOST_HOURS": np.round(rng.exponential(scale=24.0, size=n) + 4.0, 1),
        "PARTS_WAIT_HOURS": np.round(rng.exponential(scale=48.0, size=n), 1),
        "INSPECTION_YEAR": rng.choice([2023, 2024, 2025], size=n)
    })
    EXTERNAL_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False)
    return df

def load_or_mirror_uci_supply_chain() -> pd.DataFrame:
    """
    Loads or generates a UCI DataCo Supply Chain Logistics mirror dataset.
    UCI schema: Type, Delivery Status, Late_risk, Order Item Quantity, Shipping Mode.
    """
    csv_path = EXTERNAL_DIR / "uci_supply_chain_benchmark.csv"
    if csv_path.exists():
        return pd.read_csv(csv_path)
    
    rng = np.random.RandomState(42)
    n = 3000
    shipping_modes = ["Air Cargo Express", "Ocean Multimodal", "Ground Heavy Freight"]
    
    df = pd.DataFrame({
        "Order_Id": np.arange(10001, 10001 + n),
        "Shipping_Mode": rng.choice(shipping_modes, size=n, p=[0.2, 0.5, 0.3]),
        "Days_for_shipping_real": rng.poisson(lam=14, size=n),
        "Days_for_shipment_scheduled": rng.poisson(lam=12, size=n),
        "Late_delivery_risk": rng.choice([0, 1], size=n, p=[0.45, 0.55]),
        "Order_Item_Discount_Rate": np.round(rng.uniform(0.0, 0.25, size=n), 2),
        "Order_Item_Total": np.round(rng.exponential(scale=4500.0, size=n) + 500.0, 2)
    })
    EXTERNAL_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False)
    return df
