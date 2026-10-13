# Machine Learning Pipeline & Statistical Validation Framework: Mining Logistics Digital Twin

Este repositorio implementa el pipeline científico completo de **Machine Learning y Validación Estadística No Paramétrica Rigurosa** para el artículo científico:

> **"Gemelo Digital Orientado a la Resiliencia ante Disrupciones en la Logística de Repuestos Críticos de Minería Subterránea"**

---

## 1. Arquitectura del Proyecto

```text
project/
├── data/
│   ├── master_original/          # Dataset maestro original intacto (10,000 registros estratificados)
│   ├── master_clean/             # Dataset limpio y estandarizado con log de decisiones
│   └── final/                    # Conjuntos TRAIN (80%) y TEST aislado (20%)
├── src/
│   ├── data/                     # Módulos de carga (loader.py) y limpieza (cleaner.py)
│   ├── features/                 # Ingeniería de features (engineering.py) y auditoría de leakage (leakage.py)
│   ├── preprocessing/            # PipelineBuilder con ColumnTransformer hermético
│   ├── models/                   # Factoría de modelos: LR, RF, XGBoost, LightGBM, SVM
│   ├── evaluation/               # Métricas completas (metrics.py) y CV 5-Fold pareado (cv_evaluator.py)
│   ├── statistics/               # Batería estadística: Friedman, Wilcoxon+Holm, Nemenyi, BCa Bootstrap, Cliff's Delta
│   └── visualization/            # Generación de las 29 figuras científicas oficiales (300 DPI)
├── notebooks/                    # Scripts paso a paso modulares para exploración y docencia
├── models/                       # Modelos serializados (.joblib) y metadatos JSON
├── results/
│   ├── audit/                    # Reportes de auditoría inicial y gate de decisión
│   ├── cleaning/                 # Log de limpieza y auditoría de outliers (MAD/IQR)
│   ├── eda/                      # Tablas descriptivas de variables numéricas y categóricas
│   ├── leakage/                  # Auditoría rigurosa de fuga de información (data leakage)
│   ├── cross_validation/         # Resultados por fold, matrices de métricas e IC 95%
│   ├── hyperparameters/          # Historial de optimización en TRAIN
│   ├── statistics/               # Carpetas por prueba: friedman, wilcoxon_holm, nemenyi, bootstrap_bca, cliffs_delta
│   ├── figures/                  # 29 figuras científicas numeradas (fig01 a fig29)
│   └── reports/                  # Reporte de validación, checklist e informe de robustez
├── requirements.txt              # Especificación de dependencias del entorno
├── README.md                     # Guía de reproducción y documentación metodológica
└── run_pipeline.py               # Orquestador end-to-end de las 30 fases del pipeline
```

---

## 2. Garantías de Rigor Metodológico y Anti-Data Leakage

1. **Aislamiento Absoluto de TEST:** El conjunto TEST (20%, 1,439 registros) permanece completamente aislado. No se calculan medianas, frecuencias, correlaciones ni hiperparámetros utilizando este conjunto.
2. **Transformaciones en Pipeline:** Toda imputación, escalado robusto (`RobustScaler`) y codificación One-Hot se encapsula en un objeto `ColumnTransformer` dentro de un `Pipeline` de `scikit-learn`, entrenado exclusivamente dentro de cada split de validación.
3. **Auditoría de Post-Incidente (Leakage):** Se eliminaron todas las variables que representan consecuencias de la falla o disrupción (`downtime_hours`, `recovery_time_days`, `degradation_index`, `rul`, `severity`, etc.), así como identificadores unívocos no generalizables.
4. **Validación Cruzada Pareada:** Los 5 modelos se evalúan exactamente sobre los mismos 5 folds estratificados (`StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`).

---

## 3. Batería Estadística Pareada (Orden Mandatorio)

El pipeline ejecuta la secuencia de inferencia no paramétrica formal:
1. **Friedman Test:** Prueba global de orden de rangos sobre los $k=5$ modelos en $N=5$ bloques de folds.
2. **Wilcoxon Signed-Rank Test + Holm-Bonferroni:** Prueba pareada para las 10 combinaciones posibles de modelos, controlando la tasa de error por familia (FWER) con el ajuste escalonado de Holm.
3. **Nemenyi Post-Hoc Test:** Cálculo analítico de la Diferencia Crítica ($CD$) según Demšar (2006) y visualización gráfica.
4. **Bootstrap BCa (10,000 Remuestras):** Estimación de intervalos de confianza del 95% corregidos por sesgo ($z_0$) y aceleración ($a$ mediante jackknife) para la diferencia de desempeño $\Delta = \text{Métrica}_A - \text{Métrica}_B$.
5. **Cliff's Delta:** Estimación no paramétrica del tamaño del efecto ($\delta$) categorizada según umbrales estándar (Despreciable, Pequeño, Mediano, Grande).
6. **Tabla Estadística Integrada:** Consolidación de todos los contrastes para reporte directo en publicación científica.

---

## 4. Instrucciones de Reproducción

### Requisitos Previos
- Python 3.11+
- Virtualenv o Conda

### Instalación
```powershell
pip install -r requirements.txt
```

### Ejecución Completa End-to-End
Para reproducir todas las 30 fases del pipeline, generar las 29 figuras, tablas y modelos entrenados:
```powershell
python run_pipeline.py
```
El script reportará el progreso paso a paso y guardará todos los artefactos en `results/` y `models/`.
