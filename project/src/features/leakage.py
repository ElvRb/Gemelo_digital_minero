"""
Module: leakage.py
Phase 10: Rigorous Data Leakage Audit.
Detects target derivatives, post-incident variables, and unconstrained identifiers.
Outputs results/leakage/leakage_audit.csv
"""

import os
import pandas as pd

def audit_and_clean_leakage(df, target_col='failure_label', audit_output_path=None):
    """
    Audits every column in df against leakage criteria.
    Removes post-event features and direct target derivatives.
    """
    audit_records = []
    
    # 1. Post-event / direct target derivatives
    direct_leakage_cols = [
        'failure_mode', 'failure_type', 'severity', 'downtime_hours',
        'recovery_time_days', 'degradation_index', 'rul', 'disruption_type',
        'maintenance_action', 'availability'
    ]
    
    # 2. Text / High-cardinality non-predictive identifiers
    identifier_cols = [
        'record_id', 'source_file', 'order_id', 'mine_name', 'supplier_name',
        'raw_text', 'normalized_text', 'sentence_text', 'token_span', 'event_name'
    ]
    
    # 3. Target column itself
    cols_to_drop = [target_col] + direct_leakage_cols + identifier_cols
    
    for col in df.columns:
        if col == target_col:
            risk = 'Target'
            reason = 'Columna objetivo a predecir'
            action = 'Separar en vector y'
        elif col in direct_leakage_cols:
            risk = 'HIGH_LEAKAGE'
            reason = 'Información posterior al evento (post-incident) o derivada directa del target'
            action = 'ELIMINAR DE PREDICTORES'
        elif col in identifier_cols:
            risk = 'OVERFITTING_RISK'
            reason = 'Identificador administrativo o texto bruto con riesgo de memorización espuria'
            action = 'ELIMINAR DE PREDICTORES'
        elif col in ['source_dataset', 'data_type', 'source_quality', 'conceptual_stage']:
            risk = 'METADATA'
            reason = 'Metadatos de trazabilidad; preservados para auditoría de fuentes y generalización'
            action = 'PRESERVAR'
        else:
            risk = 'LOW_CLEAN'
            reason = 'Variable observable ex-ante (pre-evento) válida para inferencia'
            action = 'PRESERVAR'
            
        audit_records.append({
            'variable': col,
            'leakage_risk_level': risk,
            'reason': reason,
            'action_taken': action
        })
        
    df_audit = pd.DataFrame(audit_records)
    if audit_output_path:
        os.makedirs(os.path.dirname(audit_output_path), exist_ok=True)
        df_audit.to_csv(audit_output_path, index=False)
        print(f"[OK] Auditoría de data leakage guardada en {audit_output_path}")
        
    # Valid predictor columns (excluding dropped)
    final_predictor_cols = [c for c in df.columns if c not in cols_to_drop]
    print(f"[OK] Columnas predictoras libres de leakage seleccionadas: {len(final_predictor_cols)}")
    
    return df_audit, final_predictor_cols
