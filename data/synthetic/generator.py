"""
High-fidelity synthetic dataset generator for underground mining supply chain.
Models realistic component failure rates, international lead times, supplier risks,
and produces 10,000+ reproducible records with random_state=42.
"""
import os
import numpy as np
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent
SYNTHETIC_DIR = DATA_DIR / "synthetic"
PROCESSED_DIR = DATA_DIR / "processed"

def generate_mining_dataset(n_samples: int = 10000, random_state: int = 42) -> pd.DataFrame:
    """
    Generates a realistic underground mining dataset with strict reproducibility.
    Avoids data leakage and follows empirical mining logistics distributions.
    """
    rng = np.random.RandomState(random_state)
    
    equipment_types = [
        "Scooptram (LHD)", "Jumbo de Perforación", "Ventilador Axial Principal",
        "Bomba de Desagüe Multietapa", "Shovel / Pala", "Perforadora Long Hole",
        "Compresor Estacionario", "Faja Transportadora"
    ]
    eq_weights = [0.25, 0.20, 0.12, 0.15, 0.08, 0.08, 0.06, 0.06]
    
    part_categories = [
        "Hidráulica de Alta Presión", "Transmisión y Tren de Potencia",
        "Electrónica y Control ECM", "Ventilación y Flujo de Aire",
        "Desagüe y Bombeo de Relaves", "Perforación y Rotación"
    ]
    part_weights = [0.28, 0.22, 0.15, 0.10, 0.13, 0.12]
    
    sample_eq = rng.choice(equipment_types, size=n_samples, p=eq_weights)
    sample_part = rng.choice(part_categories, size=n_samples, p=part_weights)
    
    # Lead time in days: Lognormal distribution (mean ~115 days, range 30-260)
    mu_log = np.log(110)
    sigma_log = 0.35
    lead_time = np.clip(rng.lognormal(mean=mu_log, sigma=sigma_log, size=n_samples), 25, 270)
    lead_time_variability = lead_time * rng.uniform(0.10, 0.35, size=n_samples)
    
    # Suppliers and dependency
    # 1 to 3 suppliers with higher probability of 1 (single sourcing issue)
    supplier_count = rng.choice([1, 2, 3], size=n_samples, p=[0.48, 0.38, 0.14])
    supplier_reliability = np.where(
        supplier_count == 1,
        rng.beta(a=8, b=2, size=n_samples) * 0.95,  # Single source: between 0.70 and 0.95
        rng.beta(a=12, b=1.5, size=n_samples) * 0.98 # Multiple: higher reliability
    )
    supplier_reliability = np.clip(supplier_reliability, 0.65, 0.99)
    
    # Supplier Dependency: Share of the primary supplier
    supplier_dependency = np.where(
        supplier_count == 1,
        1.0,
        rng.uniform(0.55, 0.92, size=n_samples)
    )
    
    # Demand and failure rates
    # Failure rate (events per month per machine): Exponential / Gamma
    failure_rate = rng.gamma(shape=2.5, scale=0.015, size=n_samples)
    failure_rate = np.clip(failure_rate, 0.005, 0.09)
    
    mtbf = np.clip(720.0 / (failure_rate * 30.0 + 1e-4), 120.0, 1800.0)
    mttr = rng.normal(loc=18.0, scale=5.0, size=n_samples)
    mttr = np.clip(mttr, 4.0, 48.0)
    
    # Monthly demand rate
    demand_rate = failure_rate * rng.uniform(8.0, 24.0, size=n_samples) + rng.poisson(lam=1.2, size=n_samples)
    demand_rate = np.clip(demand_rate, 0.2, 8.0)
    demand_variability = demand_rate * rng.uniform(0.15, 0.50, size=n_samples)
    
    # Stock levels
    safety_stock = rng.choice([0, 1, 2, 3], size=n_samples, p=[0.25, 0.40, 0.25, 0.10])
    reorder_point = np.maximum(1, np.round(safety_stock + demand_rate * (lead_time / 30.0) * 0.7)).astype(int)
    
    # Current stock level on site (can be 0 if depleted)
    stock_level = np.maximum(0, rng.poisson(lam=np.clip(reorder_point * 0.85, 0.5, 6.0), size=n_samples))
    
    # Criticality indices
    eq_crit_map = {
        "Ventilador Axial Principal": 3, "Bomba de Desagüe Multietapa": 3,
        "Shovel / Pala": 3, "Faja Transportadora": 3,
        "Scooptram (LHD)": 2, "Jumbo de Perforación": 2,
        "Perforadora Long Hole": 2, "Compresor Estacionario": 1
    }
    equipment_criticality = np.array([eq_crit_map[eq] for eq in sample_eq])
    
    part_crit_map = {
        "Hidráulica de Alta Presión": 3, "Electrónica y Control ECM": 3,
        "Ventilación y Flujo de Aire": 3, "Desagüe y Bombeo de Relaves": 3,
        "Perforación y Rotación": 2, "Transmisión y Tren de Potencia": 2
    }
    part_criticality = np.array([part_crit_map[p] for p in sample_part])
    
    # Logistical delays
    transport_delay = rng.exponential(scale=5.0, size=n_samples)
    customs_delay = rng.exponential(scale=6.0, size=n_samples)
    
    # Historical events
    historical_stockouts = rng.poisson(lam=1.5, size=n_samples)
    historical_downtime = historical_stockouts * rng.uniform(15.0, 75.0, size=n_samples)
    
    # --- TARGET DEFINITION ---
    # Lead time demand (pipeline demand expected during replenishment)
    expected_pipeline_demand = demand_rate * (lead_time / 30.0)
    stock_deficit = expected_pipeline_demand - (stock_level + safety_stock)
    
    # Latent risk score
    risk_score = (
        0.35 * (stock_deficit > 0).astype(float) * (stock_deficit / (expected_pipeline_demand + 1e-3))
        + 0.25 * (lead_time / 180.0)
        + 0.20 * supplier_dependency * (1.0 - supplier_reliability)
        + 0.15 * (failure_rate / 0.06)
        + 0.05 * (equipment_criticality / 3.0)
        + rng.normal(0, 0.08, size=n_samples)
    )
    
    # Stock-out Risk Target (Binary Classification)
    # 0 = Bajo riesgo, 1 = Alto riesgo
    risk_threshold = np.percentile(risk_score, 62) # ~38% high-risk (realistic class balance for critical parts)
    riesgo_stockout = (risk_score >= risk_threshold).astype(int)
    
    # Continuous Target (Expected Downtime Hours)
    # Downtime only surges when stockout risk is realized
    base_downtime = np.where(
        riesgo_stockout == 1,
        np.maximum(12.0, (lead_time * 0.25 + transport_delay + customs_delay) * (equipment_criticality / 2.0) + rng.normal(10, 8, size=n_samples)),
        np.maximum(0.0, rng.exponential(scale=4.0, size=n_samples))
    )
    downtime_esperado_horas = np.round(np.clip(base_downtime, 0.0, 480.0), 1)

    df = pd.DataFrame({
        "equipment_type": sample_eq,
        "part_category": sample_part,
        "lead_time": np.round(lead_time, 1),
        "lead_time_variability": np.round(lead_time_variability, 1),
        "supplier_count": supplier_count,
        "supplier_reliability": np.round(supplier_reliability, 3),
        "supplier_dependency": np.round(supplier_dependency, 3),
        "stock_level": stock_level,
        "safety_stock": safety_stock,
        "reorder_point": reorder_point,
        "demand_rate": np.round(demand_rate, 2),
        "demand_variability": np.round(demand_variability, 2),
        "failure_rate": np.round(failure_rate, 4),
        "MTBF": np.round(mtbf, 1),
        "MTTR": np.round(mttr, 1),
        "equipment_criticality": equipment_criticality,
        "part_criticality": part_criticality,
        "transport_delay": np.round(transport_delay, 1),
        "customs_delay": np.round(customs_delay, 1),
        "historical_stockouts": historical_stockouts,
        "historical_downtime": np.round(historical_downtime, 1),
        # Targets
        "riesgo_stockout": riesgo_stockout,
        "downtime_esperado_horas": downtime_esperado_horas
    })
    
    return df

def save_synthetic_dataset(n_samples: int = 10000, random_state: int = 42) -> Path:
    SYNTHETIC_DIR.mkdir(parents=True, exist_ok=True)
    df = generate_mining_dataset(n_samples=n_samples, random_state=random_state)
    target_path = SYNTHETIC_DIR / "mining_supply_chain_dataset.csv"
    df.to_csv(target_path, index=False)
    return target_path

def load_or_generate_dataset(n_samples: int = 10000, random_state: int = 42) -> pd.DataFrame:
    target_path = SYNTHETIC_DIR / "mining_supply_chain_dataset.csv"
    if target_path.exists():
        return pd.read_csv(target_path)
    df = generate_mining_dataset(n_samples=n_samples, random_state=random_state)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(target_path, index=False)
    return df

if __name__ == "__main__":
    p = save_synthetic_dataset()
    print(f"Synthetic dataset created at: {p}")
