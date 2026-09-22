"""
Unit and integration tests for System Dynamics, ABM, and Monte Carlo simulation engines.
"""
import pytest
from simulation.system_dynamics.stocks_flows import SystemDynamicsModel
from simulation.system_dynamics.sd_simulator import SDSimulator
from simulation.agents.abm_simulator import ABMSimulator
from simulation.monte_carlo.runner import MonteCarloRunner

def test_system_dynamics_execution():
    model = SystemDynamicsModel(horizon_days=60, random_seed=42)
    df = model.run()
    assert len(df) == 60
    assert "cumulative_downtime_hours" in df.columns
    assert "inventory_level" in df.columns
    assert df["cumulative_downtime_hours"].iloc[-1] >= 0

def test_sd_strategy_comparison():
    res = SDSimulator.run_strategy_comparison(horizon_days=90, scenario_type="BASE", random_seed=42)
    assert "summary" in res
    df_sum = res["summary"]
    assert len(df_sum) == 5 # 5 strategies
    assert "Downtime_Total_Horas" in df_sum.columns

def test_abm_simulation():
    sim = ABMSimulator(horizon_days=30, num_equipment=10, random_seed=42)
    res = sim.run()
    assert res["total_failures"] >= 0
    assert "history_df" in res
    assert not res["history_df"].empty

def test_monte_carlo_runner():
    res = MonteCarloRunner.run_experiment(n_runs=20, horizon_days=45, base_seed=42, scenario_type="BASE", strategy_code="ESTRATEGIA_C")
    assert res["n_runs"] == 20
    assert "reduction_stats" in res
    assert "reduction_mean_pct" in res["reduction_stats"]
