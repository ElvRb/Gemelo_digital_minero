"""
Simulation Engine Facade: Unifies System Dynamics, Multi-Agent Simulation (ABM),
and Monte Carlo stochastic exploration.
"""
from typing import Dict, Any
from simulation.system_dynamics.sd_simulator import SDSimulator
from simulation.agents.abm_simulator import ABMSimulator
from simulation.monte_carlo.runner import MonteCarloRunner

class SimulationEngine:
    @staticmethod
    def run_sd_comparison(horizon_days: int = 365, scenario_type: str = "BASE", random_seed: int = 42):
        return SDSimulator.run_strategy_comparison(horizon_days, scenario_type, random_seed)

    @staticmethod
    def run_abm_single(
        horizon_days: int = 365,
        strategy_code: str = "ESTRATEGIA_A",
        scenario_type: str = "BASE",
        random_seed: int = 42
    ):
        dual = strategy_code in ("ESTRATEGIA_C", "ESTRATEGIA_HIBRIDA")
        local_rep = strategy_code in ("ESTRATEGIA_D", "ESTRATEGIA_HIBRIDA")
        local_3d = strategy_code in ("ESTRATEGIA_E", "ESTRATEGIA_HIBRIDA")
        lt_m = 3.0 if scenario_type == "CIERRE_FRONTERA" else 1.0
        supp_disrupt = scenario_type == "FALLA_PROVEEDOR_UNICO"

        sim = ABMSimulator(
            horizon_days=horizon_days,
            dual_sourcing=dual,
            local_repair=local_rep,
            local_3d=local_3d,
            lead_time_multiplier=lt_m,
            supplier_disruption=supp_disrupt,
            random_seed=random_seed
        )
        return sim.run()

    @staticmethod
    def run_monte_carlo(
        n_runs: int = 500,
        horizon_days: int = 365,
        base_seed: int = 42,
        scenario_type: str = "BASE",
        strategy_code: str = "ESTRATEGIA_C"
    ):
        return MonteCarloRunner.run_experiment(
            n_runs=n_runs,
            horizon_days=horizon_days,
            base_seed=base_seed,
            scenario_type=scenario_type,
            strategy_code=strategy_code
        )
