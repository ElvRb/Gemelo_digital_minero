"""
Module: metrics.py
Phase 15: Evaluation metrics for classification and interval estimation.
Computes Accuracy, Precision, Recall, F1, F1-macro, ROC-AUC, PR-AUC.
Calculates mean, median, std, min, max, and 95% Confidence Intervals.
"""

import numpy as np
import scipy.stats as stats
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, average_precision_score
)

def compute_classification_metrics(y_true, y_pred, y_prob):
    """
    Computes all mandated classification metrics.
    """
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    f1_macro = f1_score(y_true, y_pred, average='macro', zero_division=0)
    
    # Probabilistic metrics
    if y_prob is not None and len(np.unique(y_true)) > 1:
        try:
            roc_auc = roc_auc_score(y_true, y_prob)
            pr_auc = average_precision_score(y_true, y_prob)
        except Exception:
            roc_auc = np.nan
            pr_auc = np.nan
    else:
        roc_auc = np.nan
        pr_auc = np.nan
        
    return {
        'accuracy': acc,
        'precision': prec,
        'recall': rec,
        'f1': f1,
        'f1_macro': f1_macro,
        'roc_auc': roc_auc,
        'pr_auc': pr_auc
    }

def summarize_metric_distribution(values):
    """
    Returns mean, median, std, min, max, and 95% Student-t confidence interval.
    """
    vals = np.array(values, dtype=float)
    vals = vals[~np.isnan(vals)]
    n = len(vals)
    if n == 0:
        return {'mean': np.nan, 'median': np.nan, 'std': np.nan, 'min': np.nan, 'max': np.nan, 'ci95_low': np.nan, 'ci95_high': np.nan}
    
    mean = float(np.mean(vals))
    median = float(np.median(vals))
    std = float(np.std(vals, ddof=1)) if n > 1 else 0.0
    min_v = float(np.min(vals))
    max_v = float(np.max(vals))
    
    if n > 1 and std > 0:
        t_crit = stats.t.ppf(0.975, df=n-1)
        se = std / np.sqrt(n)
        ci_low = mean - t_crit * se
        ci_high = mean + t_crit * se
    else:
        ci_low = mean
        ci_high = mean
        
    return {
        'mean': mean,
        'median': median,
        'std': std,
        'min': min_v,
        'max': max_v,
        'ci95_low': ci_low,
        'ci95_high': ci_high
    }
