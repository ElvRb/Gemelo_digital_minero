"""
Module: cleaner.py
Performs Phase 2: Systematic, auditable data cleaning without data snooping.
All decisions are logged in results/cleaning/cleaning_log.csv
"""

import os
import numpy as np
import pandas as pd

def clean_master_dataset(df_raw, output_clean_path, log_path):
    """
    Standardizes column formats, cleans infinite and pseudo-null strings,
    ensures proper typing, and generates an auditable cleaning log.
    """
    df = df_raw.copy()
    cleaning_records = []
    
    # 1. Column name standardization (snake_case)
    orig_cols = list(df.columns)
    df.columns = [c.strip().lower().replace(" ", "_").replace("-", "_") for c in df.columns]
    renamed_count = sum(1 for o, n in zip(orig_cols, df.columns) if o != n)
    cleaning_records.append({
        'variable': 'all_columns',
        'transformation': 'standardize_snake_case',
        'cantidad_afectada': renamed_count,
        'justificacion': 'Garantizar consistencia lexicográfica y evitar fallos por espacios o mayúsculas'
    })
    
    # 2. Reemplazo de infinitos por NaN
    inf_count = 0
    num_cols = df.select_dtypes(include=[np.number]).columns
    for col in num_cols:
        col_inf = np.isinf(df[col]).sum()
        if col_inf > 0:
            df[col] = df[col].replace([np.inf, -np.inf], np.nan)
            inf_count += col_inf
            cleaning_records.append({
                'variable': col,
                'transformation': 'replace_inf_with_nan',
                'cantidad_afectada': int(col_inf),
                'justificacion': 'Valores infinitos no son computables en modelos de ML y representan anomalías de división'
            })
            
    # 3. Tratamiento de pseudo-nulos en strings ('nan', 'None', 'null', 'N/A', '')
    str_cols = df.select_dtypes(include=['object', 'string']).columns
    pseudo_null_count = 0
    pseudo_nulls = {'nan', 'none', 'null', 'n/a', 'na', '', 'unknown', '?', 'none'}
    for col in str_cols:
        mask = df[col].astype(str).str.strip().str.lower().isin(pseudo_nulls)
        n_affected = mask.sum()
        if n_affected > 0:
            df.loc[mask, col] = np.nan
            pseudo_null_count += n_affected
            cleaning_records.append({
                'variable': col,
                'transformation': 'standardize_string_nulls',
                'cantidad_afectada': int(n_affected),
                'justificacion': 'Homogeneizar representaciones dispares de valores faltantes textuales a np.nan'
            })
            
    # 4. Normalización de fechas a datetime ISO
    date_cols = [c for c in df.columns if 'date' in c or c in ['expected_delivery', 'actual_delivery']]
    for col in date_cols:
        orig_na = df[col].isna().sum()
        df[col] = pd.to_datetime(df[col], errors='coerce')
        new_na = df[col].isna().sum()
        invalid_dates = new_na - orig_na
        cleaning_records.append({
            'variable': col,
            'transformation': 'convert_to_datetime',
            'cantidad_afectada': int(invalid_dates),
            'justificacion': 'Casteo riguroso a formato datetime ISO para habilitar ingeniería temporal'
        })
        
    # 5. Corrección de valores negativos no físicos en inventario y lead time
    non_negative_vars = ['lead_time_days', 'downtime_hours', 'unit_cost', 'recovery_time_days']
    for col in non_negative_vars:
        if col in df.columns:
            neg_mask = (df[col] < 0) & df[col].notna()
            n_neg = neg_mask.sum()
            if n_neg > 0:
                # -99.0 en backorders indica dato faltante en performance
                df.loc[neg_mask, col] = np.nan
                cleaning_records.append({
                    'variable': col,
                    'transformation': 'replace_negative_with_nan',
                    'cantidad_afectada': int(n_neg),
                    'justificacion': 'Valores negativos en variables estrictamente no negativas corresponden a códigos de ausencia (-99) o error de registro'
                })
                
    # 6. Duplicados exactos completos
    exact_dups = df.duplicated().sum()
    if exact_dups > 0:
        df = df.drop_duplicates().reset_index(drop=True)
    cleaning_records.append({
        'variable': 'all_rows',
        'transformation': 'drop_exact_duplicates',
        'cantidad_afectada': int(exact_dups),
        'justificacion': 'Eliminación exclusiva de filas 100% redundantes en todos sus campos para evitar sesgo en el muestreo'
    })
    
    # Guardar maestro limpio
    os.makedirs(os.path.dirname(output_clean_path), exist_ok=True)
    df.to_csv(output_clean_path, index=False)
    
    # Guardar log de limpieza
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    df_log = pd.DataFrame(cleaning_records)
    df_log.to_csv(log_path, index=False)
    
    print(f"[OK] Limpieza finalizada: {len(df)} registros limpios guardados en {output_clean_path}")
    print(f"[OK] Log de decisiones de limpieza guardado en {log_path} ({len(df_log)} registros)")
    return df, df_log
