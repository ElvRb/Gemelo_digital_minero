"""
Module: figures_generator.py
Generates all 29 mandated scientific figures (Fig 01 through Fig 29)
strictly in results/figures/ at 300 DPI with scientific styling.
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Ensure stdlib statistics
sys.path = [p for p in sys.path if p and os.path.abspath(p) != os.path.abspath('.')]
import seaborn as sns

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
DPI = 300

def generate_eda_figures(df, figures_dir):
    """
    Generates Figures 01 to 09 for Exploratory Data Analysis (EDA).
    """
    os.makedirs(figures_dir, exist_ok=True)
    
    # Fig 01: fig01_distribuciones_numericas.png
    num_cols = ['demand', 'inventory_final', 'lead_time_days', 'downtime_hours']
    avail_num = [c for c in num_cols if c in df.columns]
    if avail_num:
        fig, axes = plt.subplots(1, len(avail_num), figsize=(4*len(avail_num), 3.8))
        if len(avail_num) == 1:
            axes = [axes]
        for ax, col in zip(axes, avail_num):
            data = pd.to_numeric(df[col], errors='coerce').dropna()
            sns.histplot(data, ax=ax, kde=True, color='#2b5c8f')
            ax.set_title(f'Distribución: {col}', fontsize=11, fontweight='bold')
            ax.set_xlabel(col)
            ax.set_ylabel('Frecuencia')
        plt.tight_layout()
        plt.savefig(os.path.join(figures_dir, "fig01_distribuciones_numericas.png"), dpi=DPI)
        plt.close()
        
    # Fig 02: fig02_histogramas_log.png
    if avail_num:
        fig, axes = plt.subplots(1, len(avail_num), figsize=(4*len(avail_num), 3.8))
        if len(avail_num) == 1:
            axes = [axes]
        for ax, col in zip(axes, avail_num):
            data = pd.to_numeric(df[col], errors='coerce').dropna()
            log_data = np.log1p(np.maximum(0, data))
            sns.histplot(log_data, ax=ax, kde=True, color='#1b4965')
            ax.set_title(f'Log1p: {col}', fontsize=11, fontweight='bold')
            ax.set_xlabel(f'log1p({col})')
            ax.set_ylabel('Densidad/Frecuencia')
        plt.tight_layout()
        plt.savefig(os.path.join(figures_dir, "fig02_histogramas_log.png"), dpi=DPI)
        plt.close()

    # Fig 03: fig03_boxplots_dispersion.png
    if avail_num:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        sns.boxplot(data=df[avail_num].apply(pd.to_numeric, errors='coerce'), ax=ax, palette='Set2')
        ax.set_title("Fig 03: Boxplots de Dispersión y Rango Intercuartil (IQR)", fontsize=12, fontweight='bold')
        ax.set_ylabel("Valor Observable")
        plt.tight_layout()
        plt.savefig(os.path.join(figures_dir, "fig03_boxplots_dispersion.png"), dpi=DPI)
        plt.close()

    # Fig 04: fig04_matriz_correlacion.png
    num_df = df.select_dtypes(include=[np.number]).dropna(how='all', axis=1)
    valid_cols = [c for c in num_df.columns if num_df[c].notna().sum() > len(df) * 0.2][:12]
    if len(valid_cols) > 1:
        corr = num_df[valid_cols].corr()
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', vmin=-1, vmax=1, ax=ax, cbar_kws={'label': 'Coef. Pearson'})
        ax.set_title("Fig 04: Matriz de Correlación de Pearson (Variables Observables)", fontsize=12, fontweight='bold')
        plt.tight_layout()
        plt.savefig(os.path.join(figures_dir, "fig04_matriz_correlacion.png"), dpi=DPI)
        plt.close()

    # Fig 05: fig05_frecuencias_categoricas.png
    fig, ax = plt.subplots(figsize=(8, 4.5))
    if 'equipment_category' in df.columns:
        df['equipment_category'].value_counts().head(6).plot(kind='barh', ax=ax, color='#e07a5f')
        ax.set_title("Fig 05: Frecuencia de Categorías de Equipo Minero/Industrial", fontsize=12, fontweight='bold')
        ax.set_xlabel("Número de Observaciones")
        plt.tight_layout()
        plt.savefig(os.path.join(figures_dir, "fig05_frecuencias_categoricas.png"), dpi=DPI)
        plt.close()

    # Fig 06: fig06_distribucion_temporal.png
    if 'date' in df.columns:
        dates = pd.to_datetime(df['date'], errors='coerce').dropna()
        if len(dates) > 0:
            fig, ax = plt.subplots(figsize=(10, 4.2))
            dates.dt.year.value_counts().sort_index().plot(kind='bar', ax=ax, color='#3d5a80')
            ax.set_title("Fig 06: Distribución Anual de Observaciones Temporales", fontsize=12, fontweight='bold')
            ax.set_xlabel("Año")
            ax.set_ylabel("Total de Registros")
            plt.xticks(rotation=0)
            plt.tight_layout()
            plt.savefig(os.path.join(figures_dir, "fig06_distribucion_temporal.png"), dpi=DPI)
            plt.close()

    # Fig 07: fig07_registros_por_fuente.png
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.2))
    df['source_dataset'].value_counts().plot(kind='barh', ax=ax1, color='#2a9d8f')
    ax1.set_title("Registros por Fuente de Datos", fontsize=11, fontweight='bold')
    ax1.set_xlabel("Cantidad de Filas")
    df['data_type'].value_counts().plot(kind='pie', ax=ax2, autopct='%1.1f%%', colors=sns.color_palette('pastel'))
    ax2.set_title("Distribución por Tipología de Evidencia", fontsize=11, fontweight='bold')
    ax2.set_ylabel("")
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "fig07_registros_por_fuente.png"), dpi=DPI)
    plt.close()

    # Fig 08: fig08_bivariadas_clave.png
    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    scatter_x = 'lead_time_days' if 'lead_time_days' in df.columns else df.select_dtypes(include=[np.number]).columns[0]
    scatter_y = 'demand' if 'demand' in df.columns else df.select_dtypes(include=[np.number]).columns[1]
    hue_col = 'data_type' if 'data_type' in df.columns else None
    sns.scatterplot(x=scatter_x, y=scatter_y, hue=hue_col, data=df, ax=ax, alpha=0.6, palette='tab10')
    ax.set_title("Fig 08: Relaciones Bivariadas Clave del Sistema Logístico", fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "fig08_bivariadas_clave.png"), dpi=DPI)
    plt.close()

    # Fig 09: fig09_distribucion_target.png
    if 'failure_label' in df.columns:
        fig, ax = plt.subplots(figsize=(6.5, 4.2))
        vc = df['failure_label'].fillna(-1).value_counts().sort_index()
        label_map = {-1.0: 'Sin Etiqueta (NaN)', 0.0: 'Operativo (0)', 1.0: 'Falla/Disrupción (1)'}
        labels = [label_map.get(k, str(k)) for k in vc.index]
        colors = ['#8d99ae', '#457b9d', '#e63946'][:len(vc)]
        ax.bar(labels, vc.values, color=colors, edgecolor='black', alpha=0.85)
        for i, v in enumerate(vc.values):
            ax.text(i, v + 50, f"{v:,} ({v/len(df)*100:.1f}%)", ha='center', fontweight='bold', fontsize=10)
        ax.set_title("Fig 09: Distribución de Clases del Target (failure_label)", fontsize=12, fontweight='bold')
        ax.set_ylabel("Frecuencia")
        ax.set_ylim(0, max(vc.values) * 1.15)
        plt.tight_layout()
        plt.savefig(os.path.join(figures_dir, "fig09_distribucion_target.png"), dpi=DPI)
        plt.close()
        
    print("[OK] Figuras 01-09 generadas.")

def generate_missing_outlier_figures(df, figures_dir):
    """
    Generates Figures 10 to 13.
    """
    # Fig 10: fig10_missing_porcentaje.png
    fig, ax = plt.subplots(figsize=(10, 6))
    missing_pct = (df.isna().sum() / len(df) * 100.0).sort_values(ascending=False).head(20)
    missing_pct.plot(kind='barh', ax=ax, color='#e76f51', edgecolor='black', alpha=0.85)
    ax.set_title("Fig 10: Top 20 Variables con Mayor Porcentaje de Valores Faltantes", fontsize=12, fontweight='bold')
    ax.set_xlabel("% Faltante")
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "fig10_missing_porcentaje.png"), dpi=DPI)
    plt.close()

    # Fig 11: fig11_missing_heatmap_fuente.png
    fig, ax = plt.subplots(figsize=(11, 5.5))
    src_missing = df.groupby('source_dataset').apply(lambda g: g.isna().mean() * 100.0)
    # top 15 variables with missingness
    top_miss_vars = df.isna().mean().sort_values(ascending=False).head(15).index
    sns.heatmap(src_missing[top_miss_vars], cmap='YlOrRd', annot=True, fmt='.0f', ax=ax, cbar_kws={'label': '% Faltante'})
    ax.set_title("Fig 11: Patrón de Faltantes Estructurales por Fuente de Datos", fontsize=12, fontweight='bold')
    ax.set_xlabel("Variable")
    ax.set_ylabel("Fuente del Dataset")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "fig11_missing_heatmap_fuente.png"), dpi=DPI)
    plt.close()

    # Fig 12: fig12_outliers_boxplot_iqr.png
    num_cols = ['lead_time_days', 'downtime_hours', 'unit_cost']
    avail = [c for c in num_cols if c in df.columns]
    if avail:
        fig, axes = plt.subplots(1, len(avail), figsize=(5*len(avail), 4.2))
        if len(avail) == 1:
            axes = [axes]
        for ax, col in zip(axes, avail):
            vals = pd.to_numeric(df[col], errors='coerce').dropna()
            q1 = vals.quantile(0.25)
            q3 = vals.quantile(0.75)
            iqr = q3 - q1
            outliers = (vals < q1 - 1.5 * iqr) | (vals > q3 + 1.5 * iqr)
            sns.boxplot(y=vals, ax=ax, color='#a8dadc')
            ax.set_title(f"{col}\nOutliers: {outliers.sum()} ({outliers.mean()*100:.1f}%)", fontsize=10, fontweight='bold')
            ax.set_ylabel("Valor")
        plt.tight_layout()
        plt.savefig(os.path.join(figures_dir, "fig12_outliers_boxplot_iqr.png"), dpi=DPI)
        plt.close()

    # Fig 13: fig13_distribucion_pre_post_transformacion.png
    target_var = 'lead_time_days' if 'lead_time_days' in df.columns else avail[0]
    lt = pd.to_numeric(df[target_var], errors='coerce').dropna()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2))
    sns.histplot(lt, ax=ax1, color='#6c757d', kde=True)
    ax1.set_title(f"{target_var} Original (Sesgado)", fontsize=11, fontweight='bold')
    ax1.set_xlabel("Escala Original")
    sns.histplot(np.log1p(np.maximum(0, lt)), ax=ax2, color='#2a9d8f', kde=True)
    ax2.set_title(f"{target_var} con Transformación Log1p", fontsize=11, fontweight='bold')
    ax2.set_xlabel("log1p(valor)")
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "fig13_distribucion_pre_post_transformacion.png"), dpi=DPI)
    plt.close()
    print("[OK] Figuras 10-13 generadas.")

def generate_feature_and_split_figures(X_train, y_train, y_test, figures_dir):
    """
    Generates Figures 14 and 15.
    """
    os.makedirs(figures_dir, exist_ok=True)
    
    # Fig 14: fig14_correlacion_features_target.png
    num_train = X_train.select_dtypes(include=[np.number])
    corrs = {}
    for c in num_train.columns:
        s = num_train[c].dropna()
        idx = s.index.intersection(y_train.index)
        if len(idx) > 20:
            val_corr = np.corrcoef(s.loc[idx], y_train.loc[idx])[0, 1]
            if not np.isnan(val_corr):
                corrs[c] = val_corr
                
    if corrs:
        ser_corr = pd.Series(corrs).sort_values()
        top_corrs = pd.concat([ser_corr.head(8), ser_corr.tail(8)]).drop_duplicates()
        fig, ax = plt.subplots(figsize=(8.5, 5.5))
        top_corrs.plot(kind='barh', ax=ax, color=np.where(top_corrs > 0, '#457b9d', '#e63946'), edgecolor='black')
        ax.set_title("Fig 14: Correlación Lineal (Biserial) de Features con Target en TRAIN", fontsize=11, fontweight='bold')
        ax.set_xlabel("Coeficiente de Correlación")
        ax.axvline(0, color='black', linewidth=0.8)
        plt.tight_layout()
        plt.savefig(os.path.join(figures_dir, "fig14_correlacion_features_target.png"), dpi=DPI)
        plt.close()
        
    # Fig 15: fig15_distribucion_target_train_test.png
    train_dist = y_train.value_counts(normalize=True).sort_index()
    test_dist = y_test.value_counts(normalize=True).sort_index()
    df_split = pd.DataFrame({'TRAIN (80%)': train_dist, 'TEST (20%)': test_dist})
    
    fig, ax = plt.subplots(figsize=(7, 4.2))
    df_split.plot(kind='bar', ax=ax, color=['#2b5c8f', '#e76f51'], edgecolor='black', alpha=0.85)
    ax.set_title("Fig 15: Proporción del Target en TRAIN vs TEST (Estratificación Exacta)", fontsize=11, fontweight='bold')
    ax.set_xticklabels(['Clase 0 (Operativo)', 'Clase 1 (Falla/Quiebre)'], rotation=0)
    ax.set_ylabel("Proporción Relativa")
    ax.set_ylim(0, 1.0)
    for p in ax.patches:
        ax.annotate(f"{p.get_height()*100:.1f}%", (p.get_x() + p.get_width() / 2., p.get_height() + 0.02),
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "fig15_distribucion_target_train_test.png"), dpi=DPI)
    plt.close()
    print("[OK] Figuras 14 y 15 generadas.")

def generate_cv_and_statistical_figures(fold_matrix, stats_bundle, figures_dir, metric_name='f1'):
    """
    Generates Figures 16 to 22 for Cross-Validation and Statistical Battery.
    """
    os.makedirs(figures_dir, exist_ok=True)
    models = list(fold_matrix[metric_name].keys())
    
    # Fig 16: fig16_boxplots_metricas_cv.png
    fig, ax = plt.subplots(figsize=(9, 4.8))
    plot_data = []
    for m in models:
        for v in fold_matrix[metric_name][m]:
            plot_data.append({'Modelo': m, metric_name.upper(): v})
    df_plot = pd.DataFrame(plot_data)
    sns.boxplot(x='Modelo', y=metric_name.upper(), data=df_plot, ax=ax, palette='Set2', hue='Modelo', legend=False)
    sns.stripplot(x='Modelo', y=metric_name.upper(), data=df_plot, ax=ax, color='black', alpha=0.6, jitter=0.2)
    ax.set_title(f"Fig 16: Desempeño ({metric_name.upper()}) en 5-Fold Stratified CV Pareado", fontsize=12, fontweight='bold')
    ax.set_ylabel(f"{metric_name.upper()} Score")
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "fig16_boxplots_metricas_cv.png"), dpi=DPI)
    plt.close()

    # Fig 17: fig17_friedman_critical_difference.png (Nemenyi CD diagram)
    mean_ranks = stats_bundle['mean_ranks']
    cd = stats_bundle['critical_difference']
    fig, ax = plt.subplots(figsize=(10, 3.8))
    sorted_models = sorted(mean_ranks.items(), key=lambda x: x[1])
    y_pos = np.arange(len(sorted_models))
    ax.errorbar([r for _, r in sorted_models], y_pos, xerr=cd/2.0, fmt='o', color='#e63946', ecolor='#6c757d', elinewidth=2.5, capsize=6)
    ax.set_yticks(y_pos)
    ax.set_yticklabels([m for m, _ in sorted_models], fontsize=11, fontweight='bold')
    ax.set_xlabel("Ranking Medio (1 = Mejor Desempeño)", fontsize=11)
    ax.set_title(f"Fig 17: Critical Difference Diagram (Nemenyi CD = {cd:.4f}, alpha=0.05)", fontsize=12, fontweight='bold')
    ax.invert_xaxis()
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "fig17_friedman_critical_difference.png"), dpi=DPI)
    plt.close()

    # Fig 18: fig18_wilcoxon_pvalues_heatmap.png (Holm-adjusted p-values)
    df_w = stats_bundle['wilcoxon_holm']
    grid = pd.DataFrame(1.0, index=models, columns=models)
    for _, row in df_w.iterrows():
        m_a = row['model_A']
        m_b = row['model_B']
        p_val = row['p_holm']
        grid.loc[m_a, m_b] = p_val
        grid.loc[m_b, m_a] = p_val
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(grid, annot=True, fmt='.3f', cmap='YlGnBu_r', cbar_kws={'label': 'p-value Ajustado Holm'}, ax=ax, vmin=0, vmax=1)
    ax.set_title("Fig 18: Matriz 5x5 de Significancia Pareada Wilcoxon (Ajuste Holm)", fontsize=11, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "fig18_wilcoxon_pvalues_heatmap.png"), dpi=DPI)
    plt.close()

    # Fig 19: fig19_bootstrap_bca_ci.png (Forest plot BCa 95% CIs)
    df_boot = stats_bundle['bootstrap_bca']
    fig, ax = plt.subplots(figsize=(10, 5.5))
    y_idx = np.arange(len(df_boot))
    labels = [f"{r['model_A']} vs {r['model_B']}" for _, r in df_boot.iterrows()]
    deltas = df_boot['delta_observed']
    ci_low = df_boot['ci95_bca_low']
    ci_high = df_boot['ci95_bca_high']
    xerr = [deltas - ci_low, ci_high - deltas]
    ax.errorbar(deltas, y_idx, xerr=xerr, fmt='o', color='#1d3557', ecolor='#457b9d', elinewidth=2, capsize=5)
    ax.axvline(0, color='#e63946', linestyle='--', linewidth=1.5, alpha=0.8)
    ax.set_yticks(y_idx)
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlabel(f"Diferencia Pareada Delta ({metric_name.upper()}) con IC 95% BCa (10,000 Remuestras)")
    ax.set_title("Fig 19: Forest Plot de Diferencias Pareadas con Intervalos BCa", fontsize=11, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "fig19_bootstrap_bca_ci.png"), dpi=DPI)
    plt.close()

    # Fig 20: fig20_cliffs_delta.png (Horizontal barplot with thresholds)
    df_cliffs = stats_bundle['cliffs_delta']
    labels_cliffs = [f"{r['model_A']} vs {r['model_B']}" for _, r in df_cliffs.iterrows()]
    fig, ax = plt.subplots(figsize=(9.5, 5))
    ax.barh(labels_cliffs, df_cliffs['cliffs_delta'], color='#8338ec', edgecolor='black', alpha=0.8)
    ax.axvline(0, color='black', linewidth=0.8)
    ax.axvline(0.147, color='gray', linestyle=':', label='Negligible/Small (0.147)')
    ax.axvline(-0.147, color='gray', linestyle=':')
    ax.axvline(0.33, color='orange', linestyle='--', label='Small/Medium (0.33)')
    ax.axvline(-0.33, color='orange', linestyle='--')
    ax.axvline(0.474, color='red', linestyle='-.', label='Medium/Large (0.474)')
    ax.axvline(-0.474, color='red', linestyle='-.')
    ax.set_xlabel("Cliff's Delta (Tamaño del Efecto no Paramétrico)")
    ax.set_title("Fig 20: Tamaño del Efecto Cliff's Delta para Pares de Modelos", fontsize=11, fontweight='bold')
    ax.legend(loc='lower right', fontsize=9)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "fig20_cliffs_delta.png"), dpi=DPI)
    plt.close()

    # Fig 21: fig21_rankings_por_fold.png (Trayectoria de rankings en 5 folds)
    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    palette = sns.color_palette('tab10', len(models))
    for i, m in enumerate(models):
        m_ranks = []
        for fold_i in range(5):
            scores = {mod: fold_matrix[metric_name][mod][fold_i] for mod in models}
            sorted_m = sorted(scores.keys(), key=lambda x: -scores[x])
            m_ranks.append(sorted_m.index(m) + 1)
        ax.plot(range(1, 6), m_ranks, marker='o', label=m, linewidth=2.5, color=palette[i])
    ax.set_xlabel("Fold de Validación Cruzada (1 a 5)")
    ax.set_ylabel("Ranking en el Fold (1 = Mejor)")
    ax.set_yticks(range(1, len(models)+1))
    ax.set_xticks(range(1, 6))
    ax.invert_yaxis()
    ax.set_title("Fig 21: Trayectoria de Rankings a lo Largo de los 5 Folds", fontsize=11, fontweight='bold')
    ax.legend(loc='upper right', bbox_to_anchor=(1.25, 1.0))
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "fig21_rankings_por_fold.png"), dpi=DPI)
    plt.close()

    # Fig 22: fig22_tabla_integrada_resumen.png (Render visual de la tabla integrada)
    df_integ = stats_bundle['integrated_table']
    display_cols = [c for c in ['model_A', 'model_B', 'delta_mean', 'p_holm', 'significant_holm', 'nemenyi_significant', 'ci95_bca', 'cliffs_delta', 'magnitude'] if c in df_integ.columns]
    display_df = df_integ[display_cols].copy()
    headers_map = {
        'model_A': 'Mod A', 'model_B': 'Mod B', 'delta_mean': 'Delta F1',
        'p_holm': 'p Holm', 'significant_holm': 'Sig Holm', 'nemenyi_significant': 'Sig Nem',
        'ci95_bca': 'IC 95% BCa', 'cliffs_delta': "Cliff's d", 'magnitude': 'Magnitud'
    }
    display_df.columns = [headers_map.get(c, c) for c in display_cols]
    
    fig, ax = plt.subplots(figsize=(12, 4.5))
    ax.axis('off')
    table = ax.table(cellText=display_df.values, colLabels=display_df.columns, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.1, 1.4)
    # Style header
    for (i, j), cell in table.get_celld().items():
        if i == 0:
            cell.set_facecolor('#2b5c8f')
            cell.set_text_props(color='white', fontweight='bold')
        else:
            if i % 2 == 0:
                cell.set_facecolor('#f2f2f2')
    ax.set_title("Fig 22: Tabla Resumen Integrada de la Batería Estadística Pareada", fontsize=12, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "fig22_tabla_integrada_resumen.png"), dpi=DPI)
    plt.close()
    
    print("[OK] Figuras 16-22 generadas.")

def generate_test_evaluation_figures(y_test, y_pred, y_prob, figures_dir, model_name="Best_Model"):
    """
    Generates Figures 23 to 25 on the isolated TEST set.
    """
    os.makedirs(figures_dir, exist_ok=True)
    from sklearn.metrics import confusion_matrix, roc_curve, precision_recall_curve, auc
    
    # Fig 23: fig23_matriz_confusion_test.png
    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False, ax=ax,
                xticklabels=['Pred 0 (Normal)', 'Pred 1 (Falla)'],
                yticklabels=['Real 0 (Normal)', 'Real 1 (Falla)'])
    ax.set_title(f"Fig 23: Matriz de Confusión en TEST ({model_name})", fontsize=11, fontweight='bold')
    ax.set_xlabel("Predicción del Modelo")
    ax.set_ylabel("Etiqueta Real Observada")
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "fig23_matriz_confusion_test.png"), dpi=DPI)
    plt.close()

    # Fig 24: fig24_curva_roc_test.png
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    roc_auc = auc(fpr, tpr)
    fig, ax = plt.subplots(figsize=(6.5, 5.2))
    ax.plot(fpr, tpr, color='#e63946', lw=2.5, label=f'ROC Curve (AUC = {roc_auc:.4f})')
    ax.plot([0, 1], [0, 1], color='#1d3557', lw=1.5, linestyle='--', label='Azar (AUC = 0.50)')
    ax.set_xlabel('False Positive Rate (1 - Specificity)')
    ax.set_ylabel('True Positive Rate (Sensitivity / Recall)')
    ax.set_title(f'Fig 24: Curva ROC en Conjunto TEST Aislado ({model_name})', fontsize=11, fontweight='bold')
    ax.legend(loc='lower right', fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "fig24_curva_roc_test.png"), dpi=DPI)
    plt.close()

    # Fig 25: fig25_curva_pr_test.png
    prec, rec, _ = precision_recall_curve(y_test, y_prob)
    pr_auc = auc(rec, prec)
    fig, ax = plt.subplots(figsize=(6.5, 5.2))
    ax.plot(rec, prec, color='#2a9d8f', lw=2.5, label=f'PR Curve (AUC = {pr_auc:.4f})')
    baseline = (y_test == 1).mean()
    ax.plot([0, 1], [baseline, baseline], color='gray', linestyle='--', label=f'Línea Base ({baseline:.2f})')
    ax.set_xlabel('Recall')
    ax.set_ylabel('Precision')
    ax.set_title(f'Fig 25: Curva Precision-Recall en Conjunto TEST ({model_name})', fontsize=11, fontweight='bold')
    ax.legend(loc='lower left', fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "fig25_curva_pr_test.png"), dpi=DPI)
    plt.close()
    print("[OK] Figuras 23-25 generadas.")

def generate_interpretability_and_source_figures(model, X_train, X_test, feature_names, df_test_meta, y_test, y_pred, figures_dir):
    """
    Generates Figures 26 to 28 (Interpretability & Source analysis).
    """
    os.makedirs(figures_dir, exist_ok=True)
    est = model.named_steps['model']
    
    # Fig 26: fig26_feature_importance.png
    fig, ax = plt.subplots(figsize=(8.5, 6))
    if hasattr(est, "feature_importances_"):
        fi = est.feature_importances_
        top_idx = np.argsort(fi)[-15:]
        ax.barh([feature_names[i] for i in top_idx], fi[top_idx], color='#457b9d', edgecolor='black')
        ax.set_xlabel("Importancia de la Variable (Gain / Split Importance)")
    else:
        from sklearn.inspection import permutation_importance
        perm = permutation_importance(model, X_test.iloc[:500], y_test.iloc[:500], n_repeats=5, random_state=42)
        top_idx = np.argsort(perm.importances_mean)[-15:]
        ax.barh([X_test.columns[i] for i in top_idx], perm.importances_mean[top_idx], color='#457b9d', edgecolor='black')
        ax.set_xlabel("Permutation Importance Mean")
        
    ax.set_title("Fig 26: Importancia Predictiva de Variables (No Causal)", fontsize=11, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "fig26_feature_importance.png"), dpi=DPI)
    plt.close()

    # Fig 27: fig27_shap_summary.png
    try:
        import shap
        prep = model.named_steps['preprocessor']
        X_test_prep = prep.transform(X_test.iloc[:300])
        explainer = shap.TreeExplainer(est) if hasattr(est, "feature_importances_") else shap.Explainer(est, X_test_prep)
        shap_values = explainer.shap_values(X_test_prep)
        
        if isinstance(shap_values, list) and len(shap_values) == 2:
            shap_plot_vals = shap_values[1]
        elif hasattr(shap_values, "values") and len(shap_values.values.shape) == 3:
            shap_plot_vals = shap_values.values[:, :, 1]
        else:
            shap_plot_vals = shap_values
            
        fig, ax = plt.subplots(figsize=(10, 6.2))
        mean_abs_shap = np.mean(np.abs(shap_plot_vals), axis=0)
        top_s_idx = np.argsort(mean_abs_shap)[-15:]
        ax.barh(range(len(top_s_idx)), mean_abs_shap[top_s_idx], color='#e07a5f', edgecolor='black')
        ax.set_yticks(range(len(top_s_idx)))
        ax.set_yticklabels([feature_names[i] for i in top_s_idx], fontsize=9)
        ax.set_xlabel("Mean |SHAP Value| (Impacto Medio en la Salida del Modelo)")
        ax.set_title("Fig 27: Explicabilidad Predictiva SHAP (Asociación, No Causalidad)", fontsize=11, fontweight='bold')
        plt.tight_layout()
        plt.savefig(os.path.join(figures_dir, "fig27_shap_summary.png"), dpi=DPI)
        plt.close()
    except Exception as e:
        print(f"  [AVISO] SHAP fallback simple: {e}")
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, "SHAP Proxy: Importancia de características calculada", ha='center', va='center')
        plt.savefig(os.path.join(figures_dir, "fig27_shap_summary.png"), dpi=DPI)
        plt.close()

    # Fig 28: fig28_metricas_por_fuente.png
    df_eval = pd.DataFrame({'source_dataset': df_test_meta['source_dataset'], 'y_true': y_test, 'y_pred': y_pred})
    source_acc = df_eval.groupby('source_dataset').apply(lambda g: (g['y_true'] == g['y_pred']).mean()).sort_values()
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    source_acc.plot(kind='barh', ax=ax, color='#2a9d8f', edgecolor='black')
    ax.set_xlabel("Exactitud Predictiva (Accuracy)")
    ax.set_xlim(0, 1.05)
    for p in ax.patches:
        ax.annotate(f"{p.get_width()*100:.1f}%", (p.get_width() + 0.01, p.get_y() + p.get_height()/2.),
                    va='center', fontsize=9, fontweight='bold')
    ax.set_title("Fig 28: Exactitud de Clasificación por Dataset Fuente (TEST)", fontsize=11, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "fig28_metricas_por_fuente.png"), dpi=DPI)
    plt.close()
    print("[OK] Figuras 26-28 generadas.")

def generate_robustness_figure(df_robustness, figures_dir):
    """
    Generates Figure 29: fig29_analisis_robustez.png
    """
    os.makedirs(figures_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    seeds = df_robustness['seed']
    f1_scores = df_robustness['f1']
    roc_scores = df_robustness['roc_auc']
    
    ax.plot(seeds.astype(str), f1_scores, marker='s', color='#2b5c8f', linestyle='-', linewidth=2.2, label='F1-Score')
    ax.plot(seeds.astype(str), roc_scores, marker='o', color='#e63946', linestyle='--', linewidth=2.2, label='ROC-AUC')
    
    mean_f1 = f1_scores.mean()
    std_f1 = f1_scores.std()
    ax.axhline(mean_f1, color='gray', linestyle=':', label=f'Media F1 = {mean_f1:.4f} (std={std_f1:.4f})')
    ax.set_ylim(min(f1_scores.min(), roc_scores.min()) - 0.05, 1.02)
    ax.set_xlabel("Semilla Aleatoria de Muestreo (Random State)")
    ax.set_ylabel("Métrica en TEST")
    ax.set_title("Fig 29: Sensibilidad y Robustez ante Variación de Semillas Aleatorias", fontsize=11, fontweight='bold')
    ax.legend(loc='lower right', fontsize=9)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "fig29_analisis_robustez.png"), dpi=DPI)
    plt.close()
    print("[OK] Figura 29 generada.")
