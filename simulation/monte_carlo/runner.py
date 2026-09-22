"""
Monte Carlo Simulation Runner for Underground Mining Supply Chain.
Executes repeated stochastic runs (100, 500, 1000) over a 365-day horizon
to compute statistical confidence intervals and downtime distributions.
"""
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from simulation.system_dynamics.stocks_flows import SystemDynamicsModel

class MonteCarloRunner:
    @staticmethod
    def run_experiment(
        n_runs: int = 500,
        horizon_days: int = 365,
        base_seed: int = 42,
        scenario_type: str = "BASE",
        strategy_code: str = "ESTRATEGIA_C"
    ) -> Dict[str, Any]:
        """
        Runs Monte Carlo across Baseline and Selected Strategy to produce
        empirical distributions for statistical hypothesis testing.
        """
        lt_mult = 1.0
        dem_mult = 1.0
        supp_avail = 1.0
        if scenario_type == "CIERRE_FRONTERA":
            lt_mult = 3.0
        elif scenario_type == "FALLA_PROVEEDOR_UNICO":
            supp_avail = 0.05
        elif scenario_type == "DEMANDA_EXTREMA":
            dem_mult = 2.0

        # Strategy parameters
        strat_configs = {
            "ESTRATEGIA_A": {"init_s": 2, "ss": 1, "rop": 2, "max_s": 4, "lt_m": lt_mult, "dem_m": dem_mult, "supp_a": supp_avail, "rep": False, "3d": False},
            "ESTRATEGIA_B": {"init_s": 5, "ss": 3, "rop": 5, "max_s": 8, "lt_m": lt_mult, "dem_m": dem_mult, "supp_a": supp_avail, "rep": False, "3d": False},
            "ESTRATEGIA_C": {"init_s": 3, "ss": 2, "rop": 3, "max_s": 6, "lt_m": max(1.0, lt_mult * 0.55), "dem_m": dem_mult, "supp_a": max(0.65, supp_avail), "rep": False, "3d": False},
            "ESTRATEGIA_D": {"init_s": 2, "ss": 1, "rop": 2, "max_s": 4, "lt_m": lt_mult, "dem_m": dem_mult, "supp_a": supp_avail, "rep": True, "3d": False},
            "ESTRATEGIA_E": {"init_s": 2, "ss": 1, "rop": 2, "max_s": 4, "lt_m": lt_mult, "dem_m": dem_mult, "supp_a": supp_avail, "rep": False, "3d": True},
            "ESTRATEGIA_HIBRIDA": {"init_s": 3, "ss": 2, "rop": 4, "max_s": 6, "lt_m": max(1.0, lt_mult * 0.55), "dem_m": dem_mult, "supp_a": max(0.70, supp_avail), "rep": True, "3d": True}
        }
        
        cfg_baseline = strat_configs["ESTRATEGIA_A"]
        cfg_target = strat_configs.get(strategy_code, strat_configs["ESTRATEGIA_C"])

        baseline_downtimes = []
        strategy_downtimes = []
        baseline_stockouts = []
        strategy_stockouts = []

        for i in range(n_runs):
            run_seed = base_seed + i * 17
            
            # Baseline run
            m_base = SystemDynamicsModel(
                horizon_days=horizon_days,
                initial_stock=cfg_baseline["init_s"],
                safety_stock=cfg_baseline["ss"],
                reorder_point=cfg_baseline["rop"],
                target_max_stock=cfg_baseline["max_s"],
                lead_time_multiplier=cfg_baseline["lt_m"],
                demand_multiplier=cfg_baseline["dem_m"],
                supplier_availability=cfg_baseline["supp_a"],
                local_repair_active=cfg_baseline["rep"],
                local_3d_active=cfg_baseline["3d"],
                random_seed=run_seed
            )
            df_b = m_base.run()
            baseline_downtimes.append(df_b["cumulative_downtime_hours"].iloc[-1])
            baseline_stockouts.append(df_b["cumulative_stockouts"].iloc[-1])

            # Strategy run
            m_strat = SystemDynamicsModel(
                horizon_days=horizon_days,
                initial_stock=cfg_target["init_s"],
                safety_stock=cfg_target["ss"],
                reorder_point=cfg_target["rop"],
                target_max_stock=cfg_target["max_s"],
                lead_time_multiplier=cfg_target["lt_m"],
                demand_multiplier=cfg_target["dem_m"],
                supplier_availability=cfg_target["supp_a"],
                local_repair_active=cfg_target["rep"],
                local_3d_active=cfg_target["3d"],
                random_seed=run_seed
            )
            df_s = m_strat.run()
            strategy_downtimes.append(df_s["cumulative_downtime_hours"].iloc[-1])
            strategy_stockouts.append(df_s["cumulative_stockouts"].iloc[-1])

        b_dt = np.array(baseline_downtimes)
        s_dt = np.array(strategy_downtimes)

        reductions = ((b_dt - s_dt) / np.maximum(1.0, b_dt)) * 100.0

        mean_b = float(np.mean(b_dt))
        mean_s = float(np.mean(s_dt))
        mean_red = float(np.mean(reductions))
        ci95_red_inf = float(np.percentile(reductions, 2.5))
        ci95_red_sup = float(np.percentile(reductions, 97.5))

        return {
            "n_runs": n_runs,
            "scenario": scenario_type,
            "strategy": strategy_code,
            "baseline": {
                "downtime_mean": round(mean_b, 1),
                "downtime_std": round(float(np.std(b_dt)), 1),
                "downtime_median": round(float(np.median(b_dt)), 1),
                "downtime_p5": round(float(np.percentile(b_dt, 5)), 1),
                "downtime_p95": round(float(np.percentile(b_dt, 95)), 1),
                "stockouts_mean": round(float(np.mean(baseline_stockouts)), 1),
                "downtimes_raw": b_dt.tolist()
            },
            "strategy_resilient": {
                "downtime_mean": round(mean_s, 1),
                "downtime_std": round(float(np.std(s_dt)), 1),
                "downtime_median": round(float(np.median(s_dt)), 1),
                "downtime_p5": round(float(np.percentile(s_dt, 5)), 1),
                "downtime_p95": round(float(np.percentile(s_dt, 95)), 1),
                "stockouts_mean": round(float(np.mean(strategy_stockouts)), 1),
                "downtimes_raw": s_dt.tolist()
            },
            "reduction_stats": {
                "reduction_mean_pct": round(mean_red, 1),
                "reduction_ic95_inf": round(ci95_red_inf, 1),
                "reduction_ic95_sup": round(ci95_red_sup, 1),
                "meets_30_pct_threshold": bool(mean_red >= 30.0 and ci95_red_inf > 0.0)
            }
        }
