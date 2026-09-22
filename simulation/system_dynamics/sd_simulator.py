"""
Runner and Scenario Comparator for System Dynamics.
Executes baseline vs disrupted vs resilient strategy comparisons.
"""
from typing import Dict, Any, List
import pandas as pd
from simulation.system_dynamics.stocks_flows import SystemDynamicsModel

class SDSimulator:
    @staticmethod
    def run_strategy_comparison(
        horizon_days: int = 365,
        scenario_type: str = "BASE",
        random_seed: int = 42
    ) -> Dict[str, Any]:
        """
        Runs System Dynamics across Strategies A, B, C, D, E under a specified scenario.
        """
        # Scenario configuration
        lt_mult = 1.0
        dem_mult = 1.0
        supp_avail = 1.0
        
        if scenario_type == "CIERRE_FRONTERA":
            lt_mult = 3.0
        elif scenario_type == "FALLA_PROVEEDOR_UNICO":
            supp_avail = 0.05
        elif scenario_type == "DEMANDA_EXTREMA":
            dem_mult = 2.0
            
        strategies_config = {
            "Estrategia A (Baseline)": {
                "initial_stock": 2, "safety_stock": 1, "reorder_point": 2, "target_max": 4,
                "lt_mult": lt_mult, "dem_mult": dem_mult, "supp_avail": supp_avail,
                "local_repair": False, "local_3d": False
            },
            "Estrategia B (Safety Stock +100%)": {
                "initial_stock": 5, "safety_stock": 3, "reorder_point": 5, "target_max": 8,
                "lt_mult": lt_mult, "dem_mult": dem_mult, "supp_avail": supp_avail,
                "local_repair": False, "local_3d": False
            },
            "Estrategia C (Dual Sourcing)": {
                "initial_stock": 3, "safety_stock": 2, "reorder_point": 3, "target_max": 6,
                "lt_mult": max(1.0, lt_mult * 0.55), # Local secondary supplier reduces average LT
                "dem_mult": dem_mult, "supp_avail": max(0.65, supp_avail),
                "local_repair": False, "local_3d": False
            },
            "Estrategia D (Reparación Local)": {
                "initial_stock": 2, "safety_stock": 1, "reorder_point": 2, "target_max": 4,
                "lt_mult": lt_mult, "dem_mult": dem_mult, "supp_avail": supp_avail,
                "local_repair": True, "local_3d": False
            },
            "Estrategia E (Impresión 3D Local)": {
                "initial_stock": 2, "safety_stock": 1, "reorder_point": 2, "target_max": 4,
                "lt_mult": lt_mult, "dem_mult": dem_mult, "supp_avail": supp_avail,
                "local_repair": False, "local_3d": True
            }
        }
        
        results = {}
        summary_rows = []
        baseline_dt = 1.0
        
        for strat_name, cfg in strategies_config.items():
            model = SystemDynamicsModel(
                horizon_days=horizon_days,
                initial_stock=cfg["initial_stock"],
                safety_stock=cfg["safety_stock"],
                reorder_point=cfg["reorder_point"],
                target_max_stock=cfg["target_max"],
                lead_time_multiplier=cfg["lt_mult"],
                demand_multiplier=cfg["dem_mult"],
                supplier_availability=cfg["supp_avail"],
                local_repair_active=cfg["local_repair"],
                local_3d_active=cfg["local_3d"],
                random_seed=random_seed
            )
            df = model.run()
            final_downtime = df["cumulative_downtime_hours"].iloc[-1]
            final_stockouts = df["cumulative_stockouts"].iloc[-1]
            final_loss = df["production_loss_usd"].iloc[-1]
            avg_inv = df["inventory_level"].mean()
            
            if "Baseline" in strat_name:
                baseline_dt = max(1.0, final_downtime)
                red_pct = 0.0
            else:
                red_pct = round(((baseline_dt - final_downtime) / baseline_dt) * 100.0, 1)
                
            results[strat_name] = df
            summary_rows.append({
                "Estrategia": strat_name,
                "Downtime_Total_Horas": round(final_downtime, 1),
                "Reduccion_Downtime_Pct": red_pct,
                "Total_Stockouts": int(final_stockouts),
                "Inventario_Promedio": round(avg_inv, 1),
                "Perdida_Produccion_USD": round(final_loss, 0)
            })
            
        summary_df = pd.DataFrame(summary_rows)
        return {
            "summary": summary_df,
            "time_series": results
        }
