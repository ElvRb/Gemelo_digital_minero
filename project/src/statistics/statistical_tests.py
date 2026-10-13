"""
Module: statistical_tests.py
Phase 19: Comprehensive Non-Parametric & Resampling Statistical Testing:
1. Friedman Test
2. Wilcoxon Signed-Rank + Holm-Bonferroni Correction (10 pairwise tests)
3. Nemenyi Post-Hoc Test & Critical Difference
4. Bias-Corrected and Accelerated (BCa) Bootstrap (10,000 resamples)
5. Cliff's Delta Non-Parametric Effect Size
6. Integrated Statistical Comparison Table
"""

import os
import itertools
import numpy as np
import pandas as pd
import scipy.stats as stats

# Critical values for two-tailed Nemenyi test (alpha=0.05)
# k=number of models (from Demsar, 2006)
NEMENYI_Q_005 = {2: 1.960, 3: 2.343, 4: 2.569, 5: 2.728, 6: 2.850, 7: 2.949, 8: 3.031}

def run_friedman_test(fold_matrix_metric):
    """
    Executes Friedman test across models on identical folds.
    fold_matrix_metric: dict of model_name -> list of fold values [v1..v5]
    """
    models = list(fold_matrix_metric.keys())
    data = np.array([fold_matrix_metric[m] for m in models]) # shape: (k_models, n_folds)
    k, n = data.shape
    
    # stats.friedmanchisquare expects arrays per model
    stat, p_value = stats.friedmanchisquare(*[fold_matrix_metric[m] for m in models])
    
    # Calculate average ranks per model (1 = best)
    # Higher metric is better, so negate values for rankdata
    ranks = np.zeros_like(data)
    for j in range(n):
        col = -data[:, j]
        ranks[:, j] = stats.rankdata(col)
    mean_ranks = {models[i]: float(np.mean(ranks[i, :])) for i in range(k)}
    
    res = {
        'test': 'Friedman',
        'statistic_chi2': float(stat),
        'degrees_of_freedom': k - 1,
        'p_value': float(p_value),
        'n_models': k,
        'n_folds': n,
        'alpha': 0.05,
        'significant': bool(p_value < 0.05),
        'mean_ranks': mean_ranks
    }
    return res

def run_wilcoxon_holm(fold_matrix_metric):
    """
    Executes pairwise Wilcoxon signed-rank tests with Holm-Bonferroni step-down correction.
    """
    models = list(fold_matrix_metric.keys())
    pairs = list(itertools.combinations(models, 2))
    
    pairwise_records = []
    for m_a, m_b in pairs:
        vals_a = np.array(fold_matrix_metric[m_a])
        vals_b = np.array(fold_matrix_metric[m_b])
        diff = vals_a - vals_b
        
        # If all differences are zero
        if np.all(diff == 0):
            w_stat, p_val = 0.0, 1.0
        else:
            try:
                # Wilcoxon signed-rank
                res = stats.wilcoxon(vals_a, vals_b, zero_method='pratt', alternative='two-sided')
                w_stat, p_val = float(res.statistic), float(res.pvalue)
            except Exception:
                w_stat, p_val = np.nan, 1.0
                
        pairwise_records.append({
            'model_A': m_a,
            'model_B': m_b,
            'wilcoxon_W': w_stat,
            'p_raw': p_val,
            'mean_diff': float(np.mean(diff)),
            'median_diff': float(np.median(diff))
        })
        
    df_pairs = pd.DataFrame(pairwise_records)
    # Sort by p_raw ascending for Holm correction
    df_pairs = df_pairs.sort_values('p_raw').reset_index(drop=True)
    m_tests = len(df_pairs)
    
    # Holm step-down adjusted p-values: p_adj_i = min(1, max_{j<=i} ((m - j + 1) * p_j))
    p_adj = []
    running_max = 0.0
    for i, row in df_pairs.iterrows():
        adjusted = (m_tests - i) * row['p_raw']
        adjusted = min(1.0, adjusted)
        running_max = max(running_max, adjusted)
        p_adj.append(running_max)
        
    df_pairs['p_holm'] = p_adj
    df_pairs['decision'] = np.where(df_pairs['p_holm'] < 0.05, 'Rechaza H0 (Diferencia Sig.)', 'No Rechaza H0 (Sin Dif. Sig.)')
    
    return df_pairs

def run_nemenyi_test(fold_matrix_metric, friedman_res):
    """
    Computes Nemenyi Critical Difference and pairwise rank differences.
    """
    models = list(fold_matrix_metric.keys())
    k = len(models)
    n = len(fold_matrix_metric[models[0]])
    q_val = NEMENYI_Q_005.get(k, 2.728)
    
    cd = q_val * np.sqrt((k * (k + 1)) / (6.0 * n))
    mean_ranks = friedman_res['mean_ranks']
    
    records = []
    for m_a, m_b in itertools.combinations(models, 2):
        rank_diff = abs(mean_ranks[m_a] - mean_ranks[m_b])
        sig = rank_diff > cd
        records.append({
            'model_A': m_a,
            'model_B': m_b,
            'rank_A': round(mean_ranks[m_a], 3),
            'rank_B': round(mean_ranks[m_b], 3),
            'rank_diff': round(rank_diff, 4),
            'critical_difference': round(cd, 4),
            'significant_nemenyi': bool(sig)
        })
    return pd.DataFrame(records), cd, mean_ranks

def bootstrap_bca_pairwise(vals_a, vals_b, n_boot=10000, alpha=0.05, random_state=42):
    """
    Implements 10,000 resample Bias-Corrected and Accelerated (BCa) Bootstrap
    for pairwise differences Delta = metric_A - metric_B.
    """
    rng = np.random.default_rng(random_state)
    diff = np.array(vals_a) - np.array(vals_b)
    n = len(diff)
    theta_hat = float(np.mean(diff))
    
    # 1. Resample differences (preserving fold pairs)
    boot_indices = rng.integers(0, n, size=(n_boot, n))
    boot_diffs = diff[boot_indices]
    boot_thetas = np.mean(boot_diffs, axis=1)
    
    boot_mean = float(np.mean(boot_thetas))
    boot_median = float(np.median(boot_thetas))
    boot_se = float(np.std(boot_thetas, ddof=1))
    
    # 2. Bias-correction parameter z0
    prop_less = np.mean(boot_thetas < theta_hat)
    if prop_less == 0:
        prop_less = 1e-6
    elif prop_less == 1:
        prop_less = 1.0 - 1e-6
    z0 = stats.norm.ppf(prop_less)
    
    # 3. Acceleration parameter 'a' using Jackknife
    jack_thetas = np.zeros(n)
    for i in range(n):
        jack_thetas[i] = np.mean(np.delete(diff, i))
    jack_mean = np.mean(jack_thetas)
    num = np.sum((jack_mean - jack_thetas)**3)
    den = 6.0 * (np.sum((jack_mean - jack_thetas)**2))**1.5
    a = (num / den) if den > 1e-12 else 0.0
    
    # 4. Adjusted percentiles
    z_alpha_low = stats.norm.ppf(alpha / 2.0)
    z_alpha_high = stats.norm.ppf(1.0 - alpha / 2.0)
    
    def bca_percentile(z_val):
        denom = 1.0 - a * (z0 + z_val)
        if abs(denom) < 1e-6:
            denom = 1e-6
        arg = z0 + (z0 + z_val) / denom
        return stats.norm.cdf(arg)
        
    p_low = max(0.0, min(1.0, bca_percentile(z_alpha_low)))
    p_high = max(0.0, min(1.0, bca_percentile(z_alpha_high)))
    
    ci_low = float(np.percentile(boot_thetas, p_low * 100.0))
    ci_high = float(np.percentile(boot_thetas, p_high * 100.0))
    
    return {
        'delta_observed': theta_hat,
        'delta_boot_mean': boot_mean,
        'delta_boot_median': boot_median,
        'std_error': boot_se,
        'z0_bias': float(z0),
        'a_acceleration': float(a),
        'ci95_bca_low': ci_low,
        'ci95_bca_high': ci_high
    }

def compute_cliffs_delta(vals_a, vals_b):
    """
    Computes Cliff's Delta effect size:
    delta = sum(sign(a_i - b_j)) / (n * m)
    Magnitude thresholds:
    |delta| < 0.147: Negligible
    0.147 <= |delta| < 0.330: Small
    0.330 <= |delta| < 0.474: Medium
    |delta| >= 0.474: Large
    """
    a = np.array(vals_a)
    b = np.array(vals_b)
    n = len(a)
    m = len(b)
    
    diff_matrix = a[:, np.newaxis] - b[np.newaxis, :]
    delta = float(np.sum(np.sign(diff_matrix))) / (n * m)
    abs_d = abs(delta)
    
    if abs_d < 0.147:
        magnitude = 'Negligible'
    elif abs_d < 0.330:
        magnitude = 'Small'
    elif abs_d < 0.474:
        magnitude = 'Medium'
    else:
        magnitude = 'Large'
        
    return {
        'cliffs_delta': delta,
        'magnitude': magnitude
    }

def run_full_statistical_battery(fold_matrix_metric, metric_name='f1'):
    """
    Executes the entire sequential statistical pipeline:
    Friedman -> Wilcoxon+Holm -> Nemenyi -> Bootstrap BCa (10,000) -> Cliff's Delta
    -> Integrated Table
    """
    print(f"\n[+] Ejecutando Batería Estadística Rigurosa sobre métrica '{metric_name}'...")
    
    # 1. Friedman
    friedman_res = run_friedman_test(fold_matrix_metric)
    print(f"  [1/5] Friedman Test: Chi2={friedman_res['statistic_chi2']:.4f}, df={friedman_res['degrees_of_freedom']}, p={friedman_res['p_value']:.4e} (Significativo: {friedman_res['significant']})")
    
    # 2. Wilcoxon + Holm
    df_wilcoxon = run_wilcoxon_holm(fold_matrix_metric)
    print(f"  [2/5] Wilcoxon Signed-Rank + Holm: 10 comparaciones pareadas calculadas.")
    
    # 3. Nemenyi
    df_nemenyi, cd_val, mean_ranks = run_nemenyi_test(fold_matrix_metric, friedman_res)
    print(f"  [3/5] Nemenyi Post-Hoc: Critical Difference (CD) = {cd_val:.4f}")
    
    # 4. Bootstrap BCa 10,000 resamples
    print("  [4/5] Ejecutando Bootstrap BCa con 10,000 remuestras pareadas...")
    models = list(fold_matrix_metric.keys())
    pairs = list(itertools.combinations(models, 2))
    boot_records = []
    
    for m_a, m_b in pairs:
        v_a = fold_matrix_metric[m_a]
        v_b = fold_matrix_metric[m_b]
        bca_res = bootstrap_bca_pairwise(v_a, v_b, n_boot=10000, alpha=0.05, random_state=42)
        boot_records.append({
            'model_A': m_a,
            'model_B': m_b,
            **bca_res
        })
    df_bootstrap = pd.DataFrame(boot_records)
    print("        Bootstrap BCa completado.")
    
    # 5. Cliff's Delta
    print("  [5/5] Calculando Cliff's Delta y magnitudes de tamaño del efecto...")
    cliffs_records = []
    for m_a, m_b in pairs:
        v_a = fold_matrix_metric[m_a]
        v_b = fold_matrix_metric[m_b]
        cd_res = compute_cliffs_delta(v_a, v_b)
        cliffs_records.append({
            'model_A': m_a,
            'model_B': m_b,
            **cd_res
        })
    df_cliffs = pd.DataFrame(cliffs_records)
    
    # 6. Integrated Table
    df_nem_sub = df_nemenyi[['model_A', 'model_B', 'significant_nemenyi', 'rank_diff']].rename(
        columns={'significant_nemenyi': 'nemenyi_significant'}
    )
    integrated_df = (
        df_wilcoxon
        .merge(df_bootstrap, on=['model_A', 'model_B'], how='left')
        .merge(df_cliffs, on=['model_A', 'model_B'], how='left')
        .merge(df_nem_sub, on=['model_A', 'model_B'], how='left')
    )
    
    integrated_df['delta_mean'] = integrated_df['delta_observed'].round(4)
    integrated_df['significant_holm'] = integrated_df['p_holm'] < 0.05
    integrated_df['ci95_bca'] = integrated_df.apply(
        lambda r: f"[{r['ci95_bca_low']:.4f}, {r['ci95_bca_high']:.4f}]", axis=1
    )
    integrated_df['p_holm'] = integrated_df['p_holm'].round(4)
    integrated_df['cliffs_delta'] = integrated_df['cliffs_delta'].round(4)
    
    # Add conclusion
    conclusions = []
    for _, row in integrated_df.iterrows():
        p_h = row['p_holm']
        ci_l = row['ci95_bca_low']
        ci_h = row['ci95_bca_high']
        mag = row['magnitude']
        m_a = row['model_A']
        m_b = row['model_B']
        
        # Check if 0 is included in BCa CI
        zero_in_ci = (ci_l <= 0 <= ci_h)
        if p_h < 0.05 and not zero_in_ci:
            winner = m_a if row['delta_observed'] > 0 else m_b
            conc = f"Diferencia estadísticamente significativa a favor de {winner} (Efecto: {mag})"
        elif not zero_in_ci:
            conc = f"Efecto {mag} con IC95% que excluye cero, sin sig. tras Holm"
        else:
            conc = "Rendimiento estadísticamente equivalente (IC95% incluye cero)"
        conclusions.append(conc)
        
    integrated_df['conclusion'] = conclusions
    
    return {
        'friedman': friedman_res,
        'wilcoxon_holm': df_wilcoxon,
        'nemenyi': df_nemenyi,
        'bootstrap_bca': df_bootstrap,
        'cliffs_delta': df_cliffs,
        'integrated_table': integrated_df,
        'critical_difference': cd_val,
        'mean_ranks': mean_ranks
    }
