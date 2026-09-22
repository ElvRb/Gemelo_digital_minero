"""
System Dynamics Model for Underground Mining Critical Spare Parts Logistics.
Formulates non-linear differential equations and discrete pipeline delays for
inventory stocks, in-transit replenishment, equipment availability, and downtime.
"""
from typing import Dict, Any, List
import numpy as np
import pandas as pd

class SystemDynamicsModel:
    def __init__(
        self,
        horizon_days: int = 365,
        dt_step: float = 1.0,
        initial_stock: int = 5,
        safety_stock: int = 2,
        reorder_point: int = 3,
        target_max_stock: int = 8,
        nominal_lead_time: float = 115.0,
        failure_rate_daily: float = 0.0014, # monthly ~0.042
        mttr_days: float = 0.75, # 18 hours
        total_equipment: int = 33,
        # Disruptions
        lead_time_multiplier: float = 1.0,
        demand_multiplier: float = 1.0,
        supplier_availability: float = 1.0,
        local_repair_active: bool = False,
        local_3d_active: bool = False,
        random_seed: int = 42
    ):
        self.horizon_days = horizon_days
        self.dt = dt_step
        self.initial_stock = initial_stock
        self.safety_stock = safety_stock
        self.reorder_point = reorder_point
        self.target_max_stock = target_max_stock
        self.nominal_lead_time = nominal_lead_time
        self.failure_rate_daily = failure_rate_daily
        self.mttr_days = mttr_days
        self.total_equipment = total_equipment
        
        self.lead_time_multiplier = lead_time_multiplier
        self.demand_multiplier = demand_multiplier
        self.supplier_availability = supplier_availability
        self.local_repair_active = local_repair_active
        self.local_3d_active = local_3d_active
        self.rng = np.random.RandomState(random_seed)

    def run(self) -> pd.DataFrame:
        """
        Executes numerical simulation of the System Dynamics differential model.
        Returns daily time-series of stocks, flows, delays, and cumulative downtime.
        """
        time_steps = int(self.horizon_days / self.dt)
        time_vec = np.linspace(0, self.horizon_days, time_steps)
        
        # State Stocks
        inventory = np.zeros(time_steps)
        in_transit = np.zeros(time_steps)
        oper_equipment = np.zeros(time_steps)
        down_equipment = np.zeros(time_steps)
        cum_downtime_hours = np.zeros(time_steps)
        cum_stockouts = np.zeros(time_steps)
        production_loss_usd = np.zeros(time_steps)

        # Pipeline delay array for orders in transit: index = arrival day
        pipeline_orders = np.zeros(int(self.horizon_days + 400))
        
        # Initial conditions
        inventory[0] = float(self.initial_stock)
        in_transit[0] = 1.0
        oper_equipment[0] = float(self.total_equipment - 2)
        down_equipment[0] = 2.0
        
        effective_lt = self.nominal_lead_time * self.lead_time_multiplier
        
        # Local 3D or repair modifications
        if self.local_3d_active:
            effective_lt = min(effective_lt, 4.0) # Rapid additive replacement
        elif self.local_repair_active:
            effective_lt = min(effective_lt, 16.0) # Local remanufacturing

        cost_per_hour = 14500.0

        for t in range(time_steps - 1):
            day = int(time_vec[t])
            
            # 1. Pipeline Delay Delivery (Receptions)
            deliveries_today = pipeline_orders[day]
            
            # 2. Equipment Failure and Parts Demand (Flows)
            daily_lambda = self.failure_rate_daily * self.demand_multiplier
            # Poisson arrival of failures
            num_failures = self.rng.poisson(lam=daily_lambda * oper_equipment[t])
            num_failures = min(num_failures, int(oper_equipment[t]))
            
            # 3. Inventory Dispatch and Stockout Check
            parts_demanded = num_failures
            current_inv = inventory[t] + deliveries_today
            
            if current_inv >= parts_demanded:
                parts_issued = parts_demanded
                unmet_demand = 0
            else:
                parts_issued = max(0, int(current_inv))
                unmet_demand = parts_demanded - parts_issued
                cum_stockouts[t + 1] = cum_stockouts[t] + unmet_demand

            new_inventory = max(0.0, current_inv - parts_issued)
            inventory[t + 1] = new_inventory

            # 4. Replenishment Policy (s, S)
            inventory_position = new_inventory + in_transit[t]
            if inventory_position <= self.reorder_point and self.supplier_availability > 0.05:
                order_qty = max(1, self.target_max_stock - int(inventory_position))
                # Disruption stochastic lead time
                stochastic_lt = max(1, int(self.rng.normal(effective_lt, effective_lt * 0.15)))
                arrival_day = min(len(pipeline_orders) - 1, day + stochastic_lt)
                pipeline_orders[arrival_day] += order_qty
                in_transit[t + 1] = in_transit[t] + order_qty - deliveries_today
            else:
                in_transit[t + 1] = max(0.0, in_transit[t] - deliveries_today)

            # 5. Equipment State Transitions (Operative vs Stopped)
            # Repaired equipment returning to service
            repairs_completed = 0
            if down_equipment[t] > 0 and parts_issued > 0:
                repairs_completed = min(int(down_equipment[t]), parts_issued)
            elif down_equipment[t] > 0 and new_inventory > 0 and self.rng.uniform() < (1.0 / self.mttr_days):
                repairs_completed = min(int(down_equipment[t]), 1)
                inventory[t + 1] = max(0.0, inventory[t + 1] - repairs_completed)

            new_down = down_equipment[t] + num_failures - repairs_completed
            new_down = max(0.0, min(float(self.total_equipment), new_down))
            down_equipment[t + 1] = new_down
            oper_equipment[t + 1] = float(self.total_equipment) - new_down

            # 6. Cumulative Downtime & Production Loss
            daily_dt_hours = new_down * 24.0
            cum_downtime_hours[t + 1] = cum_downtime_hours[t] + daily_dt_hours
            production_loss_usd[t + 1] = cum_downtime_hours[t + 1] * cost_per_hour

        df = pd.DataFrame({
            "day": time_vec,
            "inventory_level": np.round(inventory, 1),
            "in_transit": in_transit,
            "operative_equipment": oper_equipment,
            "stopped_equipment": down_equipment,
            "cumulative_downtime_hours": np.round(cum_downtime_hours, 1),
            "cumulative_stockouts": cum_stockouts,
            "production_loss_usd": np.round(production_loss_usd, 0)
        })
        return df
