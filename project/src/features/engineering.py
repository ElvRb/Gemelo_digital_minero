"""
Module: engineering.py
Phase 8: Feature Engineering based strictly on domain variables.
Generates results/features/feature_dictionary.csv documenting formula, variables, and rationale.
"""

import os
import numpy as np
import pandas as pd

def engineer_features(df_clean, dict_output_path):
    """
    Constructs domain features across temporal, inventory, vibration, and supplier echelons.
    """
    df = df_clean.copy()
    feature_dict = []
    
    # 1. Temporal features (from 'date')
    if 'date' in df.columns:
        dt = pd.to_datetime(df['date'], errors='coerce')
        df['temporal_month'] = dt.dt.month
        df['temporal_quarter'] = dt.dt.quarter
        df['temporal_dayofweek'] = dt.dt.dayofweek
        df['temporal_is_weekend'] = dt.dt.dayofweek.isin([5, 6]).astype(float)
        
        feature_dict.extend([
            {
                'feature_name': 'temporal_month',
                'formula': 'date.dt.month',
                'variables_used': 'date',
                'category': 'Temporal',
                'justificacion': 'Captura estacionalidad en la demanda de repuestos y condiciones climáticas en faenas mineras'
            },
            {
                'feature_name': 'temporal_quarter',
                'formula': 'date.dt.quarter',
                'variables_used': 'date',
                'category': 'Temporal',
                'justificacion': 'Captura ciclos presupuestarios y de mantenimiento mayor por trimestre'
            },
            {
                'feature_name': 'temporal_dayofweek',
                'formula': 'date.dt.dayofweek',
                'variables_used': 'date',
                'category': 'Temporal',
                'justificacion': 'Patrones operativos semanales y turnos de mantención preventiva'
            },
            {
                'feature_name': 'temporal_is_weekend',
                'formula': 'date.dt.dayofweek.isin([5, 6])',
                'variables_used': 'date',
                'category': 'Temporal',
                'justificacion': 'Disponibilidad reducida de despachos de proveedores en fines de semana'
            }
        ])
        
    # 2. Inventory and Supply Chain ratios
    if 'inventory_final' in df.columns and 'safety_stock' in df.columns:
        inv = pd.to_numeric(df['inventory_final'], errors='coerce')
        ss = pd.to_numeric(df['safety_stock'], errors='coerce')
        denom_ss = np.maximum(0.0, ss) + 1.0
        df['stock_buffer_ratio'] = np.maximum(0.0, inv) / denom_ss
        feature_dict.append({
            'feature_name': 'stock_buffer_ratio',
            'formula': 'max(0, inventory_final) / (max(0, safety_stock) + 1)',
            'variables_used': 'inventory_final, safety_stock',
            'category': 'Inventario',
            'justificacion': 'Mide la cobertura de seguridad del inventario ante quiebres inesperados'
        })
        
    if 'inventory_in_transit' in df.columns and 'inventory_final' in df.columns:
        it = pd.to_numeric(df['inventory_in_transit'], errors='coerce')
        inv = pd.to_numeric(df['inventory_final'], errors='coerce')
        denom_inv = np.maximum(0.0, inv) + 1.0
        df['pipeline_inventory_ratio'] = np.maximum(0.0, it) / denom_inv
        feature_dict.append({
            'feature_name': 'pipeline_inventory_ratio',
            'formula': 'max(0, inventory_in_transit) / (max(0, inventory_final) + 1)',
            'variables_used': 'inventory_in_transit, inventory_final',
            'category': 'Inventario',
        })
        
    if 'demand' in df.columns and 'forecast' in df.columns:
        dem = pd.to_numeric(df['demand'], errors='coerce')
        fc = pd.to_numeric(df['forecast'], errors='coerce')
        df['demand_forecast_error'] = np.abs(dem - fc)
        feature_dict.append({
            'feature_name': 'demand_forecast_error',
            'formula': 'abs(demand - forecast)',
            'variables_used': 'demand, forecast',
            'category': 'Demanda',
            'justificacion': 'Magnitud de la sorpresa o desvío de demanda no planificada'
        })
        
    # 3. Vibration & Prognostic Features
    if 'rms_horizontal' in df.columns and 'rms_vertical' in df.columns:
        rmsh = pd.to_numeric(df['rms_horizontal'], errors='coerce')
        rmsv = pd.to_numeric(df['rms_vertical'], errors='coerce')
        df['rms_magnitude_2d'] = np.sqrt(rmsh**2 + rmsv**2)
        feature_dict.append({
            'feature_name': 'rms_magnitude_2d',
            'formula': 'sqrt(rms_horizontal^2 + rms_vertical^2)',
            'variables_used': 'rms_horizontal, rms_vertical',
            'category': 'Vibración',
            'justificacion': 'Energía vibracional combinada del componente rotativo'
        })
        
    if 'kurtosis_horizontal' in df.columns and 'kurtosis_vertical' in df.columns:
        kh = pd.to_numeric(df['kurtosis_horizontal'], errors='coerce')
        kv = pd.to_numeric(df['kurtosis_vertical'], errors='coerce')
        df['kurtosis_mean'] = (kh + kv) / 2.0
        feature_dict.append({
            'feature_name': 'kurtosis_mean',
            'formula': '(kurtosis_horizontal + kurtosis_vertical) / 2',
            'variables_used': 'kurtosis_horizontal, kurtosis_vertical',
            'category': 'Vibración',
            'justificacion': 'Indicador temprano de impactos y discontinuidades en pistas de rodamiento'
        })
        
    # 4. Supplier & Logistics Risk
    if 'supplier_reliability' in df.columns:
        rel = pd.to_numeric(df['supplier_reliability'], errors='coerce')
        df['supplier_unreliability'] = 1.0 - rel
        feature_dict.append({
            'feature_name': 'supplier_unreliability',
            'formula': '1.0 - supplier_reliability',
            'variables_used': 'supplier_reliability',
            'category': 'Proveedor',
            'justificacion': 'Probabilidad histórica de incumplimiento o retraso del proveedor'
        })
        
    # Save feature dictionary
    os.makedirs(os.path.dirname(dict_output_path), exist_ok=True)
    pd.DataFrame(feature_dict).to_csv(dict_output_path, index=False)
    print(f"[OK] Feature Engineering completado: {len(feature_dict)} features creadas.")
    print(f"[OK] Diccionario guardado en {dict_output_path}")
    
    # Guarantee zero infinite values in any engineered or numeric columns
    num_cols = df.select_dtypes(include=[np.number]).columns
    df[num_cols] = df[num_cols].replace([np.inf, -np.inf], np.nan)
    
    return df
