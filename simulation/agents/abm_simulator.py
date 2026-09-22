"""
Multi-Agent Simulation (ABM) using SimPy for Underground Mining Critical Spare Parts Logistics.
Implements interacting agents:
- EquipmentAgent: Operates, wears out according to Weibull/exponential MTBF, requests spare parts.
- WarehouseAgent: Manages buffer stocks, evaluates (s, S) policy, coordinates dispatch.
- SupplierAgent: Receives purchase orders, models production & international disruption.
- TransportAgent: Simulates logistics corridor transit and route blockages.
- MaintenanceAgent: Repairs and tests equipment upon spare part delivery.
"""
from typing import Dict, Any, List
import simpy
import numpy as np
import pandas as pd

class ABMSimulator:
    def __init__(
        self,
        horizon_days: int = 365,
        num_equipment: int = 33,
        initial_stock: int = 4,
        safety_stock: int = 2,
        reorder_point: int = 3,
        target_stock: int = 6,
        base_lead_time_days: float = 115.0,
        mtbf_days: float = 10.0, # Mean time between failures across fleet
        mttr_hours: float = 18.0,
        # Strategy toggles
        dual_sourcing: bool = False,
        local_repair: bool = False,
        local_3d: bool = False,
        # Disruption scenario
        lead_time_multiplier: float = 1.0,
        supplier_disruption: bool = False,
        random_seed: int = 42
    ):
        self.horizon_hours = horizon_days * 24.0
        self.num_equipment = num_equipment
        self.initial_stock = initial_stock
        self.safety_stock = safety_stock
        self.reorder_point = reorder_point
        self.target_stock = target_stock
        self.base_lead_time_hours = base_lead_time_days * 24.0
        self.mtbf_hours = mtbf_days * 24.0
        self.mttr_hours = mttr_hours
        
        self.dual_sourcing = dual_sourcing
        self.local_repair = local_repair
        self.local_3d = local_3d
        self.lead_time_multiplier = lead_time_multiplier
        self.supplier_disruption = supplier_disruption
        self.rng = np.random.RandomState(random_seed)

        # Metrics logged during ABM run
        self.total_failures = 0
        self.total_stockouts = 0
        self.cumulative_downtime_hours = 0.0
        self.history_records = []

    def run(self) -> Dict[str, Any]:
        """Executes the SimPy discrete-event simulation."""
        env = simpy.Environment()
        
        # Resources
        warehouse_stock = simpy.Container(env, capacity=100, init=self.initial_stock)
        maintenance_crews = simpy.Resource(env, capacity=4) # 4 maintenance squads
        
        # State trackers
        state = {
            "current_stock": self.initial_stock,
            "in_transit": 0,
            "stopped_machines": 0,
            "downtime_accum": 0.0,
            "stockouts_accum": 0
        }

        # 1. Warehouse Policy Process (Review inventory periodically)
        def warehouse_agent_process(env):
            while True:
                inv_pos = state["current_stock"] + state["in_transit"]
                if inv_pos <= self.reorder_point:
                    order_qty = max(1, self.target_stock - inv_pos)
                    state["in_transit"] += order_qty
                    env.process(procurement_and_transport_agent_process(env, order_qty))
                yield env.timeout(24.0) # Daily inventory review

        # 2. Supplier & Transport Agent Process
        def procurement_and_transport_agent_process(env, qty):
            # Calculate effective lead time
            lt_h = self.base_lead_time_hours * self.lead_time_multiplier
            
            if self.local_3d:
                lt_h = self.rng.uniform(72.0, 120.0) # 3 to 5 days
            elif self.local_repair:
                lt_h = self.rng.uniform(240.0, 480.0) # 10 to 20 days
            elif self.dual_sourcing:
                # 65% global, 35% local: blended stochastic LT
                if self.rng.uniform() < 0.35:
                    lt_h = self.rng.uniform(360.0, 720.0) # 15 to 30 days
                else:
                    lt_h = self.rng.normal(lt_h, lt_h * 0.15)
            else:
                if self.supplier_disruption:
                    lt_h += (120.0 * 24.0) # 120 days extra stoppage
                else:
                    lt_h = max(240.0, self.rng.normal(lt_h, lt_h * 0.20))

            yield env.timeout(max(24.0, lt_h))
            
            # Arrived at warehouse
            state["in_transit"] -= qty
            state["current_stock"] += qty
            yield warehouse_stock.put(qty)

        # 3. Equipment Agent Process
        def equipment_agent_process(env, eq_id):
            while True:
                # Machine operates until next failure
                op_time = self.rng.exponential(self.mtbf_hours)
                yield env.timeout(op_time)
                
                # Machine Fails
                self.total_failures += 1
                state["stopped_machines"] += 1
                failure_start = env.now
                
                # Request spare part from Warehouse
                if state["current_stock"] > 0:
                    yield warehouse_stock.get(1)
                    state["current_stock"] -= 1
                    part_wait_time = 0.0
                else:
                    self.total_stockouts += 1
                    state["stockouts_accum"] += 1
                    wait_start = env.now
                    yield warehouse_stock.get(1)
                    state["current_stock"] -= 1
                    part_wait_time = env.now - wait_start

                # Machine enters Maintenance with repair squad
                with maintenance_crews.request() as req:
                    yield req
                    repair_time = max(4.0, self.rng.normal(self.mttr_hours, 4.0))
                    yield env.timeout(repair_time)

                downtime_event = env.now - failure_start
                state["downtime_accum"] += downtime_event
                state["stopped_machines"] -= 1

        # 4. Logger Process
        def logger_process(env):
            while True:
                self.history_records.append({
                    "day": round(env.now / 24.0, 1),
                    "current_stock": state["current_stock"],
                    "in_transit": state["in_transit"],
                    "stopped_machines": state["stopped_machines"],
                    "cumulative_downtime_hours": round(state["downtime_accum"], 1),
                    "cumulative_stockouts": state["stockouts_accum"]
                })
                yield env.timeout(24.0)

        # Launch Agents in SimPy environment
        env.process(warehouse_agent_process(env))
        env.process(logger_process(env))
        for eq_id in range(self.num_equipment):
            env.process(equipment_agent_process(env, eq_id))

        # Run until horizon
        env.run(until=self.horizon_hours)

        df_history = pd.DataFrame(self.history_records)
        final_downtime = state["downtime_accum"]
        
        return {
            "total_failures": self.total_failures,
            "total_stockouts": state["stockouts_accum"],
            "cumulative_downtime_hours": round(final_downtime, 1),
            "production_loss_usd": round(final_downtime * 14500.0, 0),
            "history_df": df_history
        }
