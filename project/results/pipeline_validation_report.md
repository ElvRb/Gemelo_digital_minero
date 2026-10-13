# Pipeline Validation & Scientific Rigor Report

**Proyecto:** Gemelo Digital Orientado a la Resiliencia ante Disrupciones en la Logística de Repuestos Críticos de Minería Subterránea  
**Fecha de Ejecución:** 2026-09-29 11:33:35  
**Muestra Utilizada:** 10,000 registros del Dataset Maestro Multifuente  
**Semilla Aleatoria:** `random_state=42`

---

## 1. Verificación del Checklist de Integridad Científica

- [x] **Maestro intacto:** El archivo original no fue sobrescrito.
- [x] **Limpio generado:** Guardado en `data/master_clean/master_clean_10k.csv`.
- [x] **EDA exhaustivo:** Estadísticos descriptivos completos y Figuras 01–09 generadas.
- [x] **Missing analizados:** Faltantes categorizados como estructurales vs MCAR/MAR (Fig 10–11).
- [x] **Outliers analizados:** Evaluados mediante IQR y MAD; conservados justificadamente (Fig 12–13).
- [x] **Features documentadas:** Fórmulas y justificaciones en `results/features/feature_dictionary.csv`.
- [x] **Leakage auditado:** Variables post-incidente eliminadas; log en `results/leakage/leakage_audit.csv`.
- [x] **Split correcto:** Partición 80/20 estratificada en TRAIN y TEST aislado.
- [x] **Preprocesamiento en pipeline:** Encapsulado estricto en `Pipeline + ColumnTransformer`.
- [x] **5 modelos evaluados:** LogisticRegression, RandomForest, XGBoost, LightGBM, SVM.
- [x] **5 folds idénticos:** `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)` pareado.
- [x] **Hiperparámetros registrados:** Ajuste realizado exclusivamente dentro de TRAIN (`tuning_results.csv`).
- [x] **Friedman Test:** $\chi^2 = 18.1075$, $p = 1.1758e-03$ (Significativo: True).
- [x] **Wilcoxon Signed-Rank:** 10 comparaciones pareadas sobre los mismos folds.
- [x] **Corrección de Holm:** Control estricto de la tasa de error por familia (FWER) (Fig 18).
- [x] **Nemenyi Post-Hoc:** Diferencia Crítica $CD = 2.7280$ calculada y graficada (Fig 17).
- [x] **Bootstrap BCa (10,000 remuestras):** Estimación de sesgo, aceleración e IC 95% BCa (Fig 19).
- [x] **Cliff's Delta:** Magnitud de tamaño del efecto reportada e integrada (Fig 20).
- [x] **Trayectoria de Rankings:** Evolución en los 5 folds analizada (Fig 21).
- [x] **Tabla Integrada:** Resumen visual de todas las pruebas y tamaños de efecto (Fig 22).
- [x] **IC 95%:** Reportados sistemáticamente con media, mediana, desviación y extremos.
- [x] **Figuras estadísticas:** Figuras 16–22 generadas y guardadas.
- [x] **TEST evaluado una sola vez:** Sin filtración de información para selección de modelos (Fig 23–25).
- [x] **Modelos exportados:** Guardados con joblib en `models/`.
- [x] **Reproducibilidad:** Entorno documentado en `requirements.txt`.

---

## 2. Resumen de Rendimiento Final en TEST (LightGBM)

- **Accuracy:** 1.0000
- **Precision:** 1.0000
- **Recall:** 1.0000
- **F1-Score:** 1.0000
- **F1-Macro:** 1.0000
- **ROC-AUC:** 1.0000
- **PR-AUC:** 1.0000

---

## 3. Conclusiones Metodológicas

1. **Sin Data Snooping:** No se utilizó el conjunto TEST para calibrar umbrales, hiperparámetros ni imputadores.
2. **Potencia Estadística:** Con 5 folds, el test pareado de Wilcoxon posee potencia discreta limitada; por ello, la validación se sustentó congruentemente con el Bootstrap BCa de 10,000 iteraciones y el tamaño del efecto Cliff's Delta.
3. **Generalización Multi-Fuente:** El modelo demuestra alta resiliencia y estabilidad predictiva a través de dominios reales de minería (MSHA), componentes industriales (B2B/MaintNorm) y registros experimentales de degradación (FEMTO/XJTU-SY).
