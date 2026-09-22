"""
Unit tests for all statistical validation methods:
Friedman, Wilcoxon-Holm, Bootstrap 10k, KS test, Mann-Whitney U, Sobol, Hypothesis Evaluator.
"""
import pytest
import numpy as np
from statistics.friedman import FriedmanTest
from statistics.wilcoxon import WilcoxonHolmTest
from statistics.bootstrap import BootstrapEstimator
from statistics.ks_test import DigitalTwinValidator
from statistics.mann_whitney import MannWhitneyTest
from statistics.sobol import SobolSensitivityAnalyzer
from statistics.hypothesis_evaluator import HypothesisEvaluator

def test_friedman_test():
    cv_data = {
        "Model A": {"f1_macro": [0.85, 0.86, 0.84, 0.87, 0.85]},
        "Model B": {"f1_macro": [0.92, 0.93, 0.91, 0.94, 0.92]},
        "Model C": {"f1_macro": [0.75, 0.76, 0.74, 0.77, 0.75]},
        "Model D": {"f1_macro": [0.89, 0.90, 0.88, 0.91, 0.89]},
        "Model E": {"f1_macro": [0.82, 0.83, 0.81, 0.84, 0.82]}
    }
    res = FriedmanTest.evaluate(cv_data, metric="f1_macro")
    assert res["is_significant"] is True
    assert res["p_value"] < 0.05

def test_wilcoxon_holm_test():
    cv_data = {
        "Best Model": {"f1_macro": [0.93, 0.94, 0.92, 0.95, 0.93]},
        "Model 2": {"f1_macro": [0.85, 0.86, 0.84, 0.87, 0.85]},
        "Model 3": {"f1_macro": [0.78, 0.79, 0.77, 0.80, 0.78]}
    }
    res = WilcoxonHolmTest.evaluate(cv_data, best_model_name="Best Model", metric="f1_macro")
    assert len(res["table_df"]) == 2
    assert "p_value_ajustado" in res["table_df"].columns

def test_bootstrap_estimator():
    y_true = np.array([0, 1, 0, 1, 1, 0, 1, 0] * 10)
    p_a = np.array([0, 1, 0, 1, 1, 0, 1, 0] * 10) # perfect
    p_b = np.array([1, 0, 1, 0, 0, 1, 0, 1] * 10) # poor
    res = BootstrapEstimator.estimate_metric_difference(y_true, p_a, p_b, n_bootstraps=1000)
    assert res["is_significant"] is True
    assert res["mean_difference"] > 0

def test_ks_test():
    d1 = {"downtime": [100, 120, 110, 130, 115], "lead_time": [90, 95, 92, 88, 91], "stockouts": [1, 2, 1, 0, 1]}
    d2 = {"downtime": [102, 118, 112, 128, 114], "lead_time": [91, 94, 91, 89, 92], "stockouts": [1, 2, 1, 1, 0]}
    res = DigitalTwinValidator.validate_distributions(d1, d2)
    assert "all_passed" in res

def test_mann_whitney_and_hypothesis():
    baseline = [420.0, 435.0, 410.0, 440.0, 415.0] * 10
    strategy = [210.0, 220.0, 205.0, 225.0, 215.0] * 10 # ~50% reduction
    res = HypothesisEvaluator.test_hypothesis(baseline, strategy, alpha=0.05, threshold_reduction_pct=30.0)
    assert res["reject_h0"] is True
    assert res["reduccion_estimada_pct"] >= 30.0

def test_sobol_sensitivity():
    df_sobol = SobolSensitivityAnalyzer.calculate_indices(n_samples=64, random_seed=42)
    assert len(df_sobol) == 6
    assert "S1 (Primer Orden)" in df_sobol.columns
    assert "ST (Efecto Total)" in df_sobol.columns
