"""
Feature Engineering Pipeline for Mining Spare Parts Logistics.
Derives domain-specific risk indices while avoiding data leakage.
"""
from typing import Tuple, List
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

class MiningFeaturePipeline:
    FEATURE_COLUMNS = [
        "lead_time", "lead_time_variability", "supplier_count",
        "supplier_reliability", "supplier_dependency", "stock_level",
        "safety_stock", "reorder_point", "demand_rate", "demand_variability",
        "failure_rate", "MTBF", "MTTR", "equipment_criticality",
        "part_criticality", "transport_delay", "customs_delay",
        "historical_stockouts", "historical_downtime",
        # Engineered Features
        "lead_time_demand", "stock_coverage_ratio", "supplier_vulnerability",
        "criticality_index", "safety_buffer_ratio"
    ]

    @staticmethod
    def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
        """Computes derived domain-specific risk indicators."""
        df_feat = df.copy()
        
        # Expected demand during replenishment pipeline
        df_feat["lead_time_demand"] = np.round(df_feat["demand_rate"] * (df_feat["lead_time"] / 30.0), 2)
        
        # Stock coverage: How many times does available stock cover pipeline demand?
        df_feat["stock_coverage_ratio"] = np.round(
            df_feat["stock_level"] / np.maximum(0.1, df_feat["lead_time_demand"]), 3
        )
        
        # Supplier vulnerability index
        df_feat["supplier_vulnerability"] = np.round(
            df_feat["supplier_dependency"] * (1.0 - df_feat["supplier_reliability"]), 3
        )
        
        # Asset x Spare part criticality interaction
        df_feat["criticality_index"] = df_feat["equipment_criticality"] * df_feat["part_criticality"]
        
        # Safety buffer ratio vs ROP
        df_feat["safety_buffer_ratio"] = np.round(
            (df_feat["stock_level"] + df_feat["safety_stock"]) / np.maximum(1.0, df_feat["reorder_point"]), 3
        )
        
        return df_feat

    @classmethod
    def prepare_train_test(
        cls,
        df: pd.DataFrame,
        target_col: str = "riesgo_stockout",
        test_size: float = 0.20,
        random_state: int = 42
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, StandardScaler, List[str]]:
        """Splits into stratified train/test and fits scaler strictly on train set to prevent leakage."""
        df_feat = cls.engineer_features(df)
        X = df_feat[cls.FEATURE_COLUMNS].values
        y = df_feat[target_col].values

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        return X_train_scaled, X_test_scaled, y_train, y_test, scaler, cls.FEATURE_COLUMNS
