# Resilience-Driven Digital Twin for Supply Chain Disruption in Underground Mining
## A System Dynamics and Multi-Agent Simulation of Critical Spare Parts Logistics

Plataforma científica e industrial integral para la gestión, simulación híbrida (Dinámica de Sistemas + Simulación Multi-Agente en SimPy), evaluación de resiliencia, analítica predictiva bajo metodología **CRISP-DM** y validación estadística formal de la cadena de suministro de repuestos críticos en minería subterránea.

---

## 🎯 Problema de Investigación e Hipótesis

Las operaciones mineras subterráneas dependen críticamente de repuestos de alto impacto y prolongados tiempos de reposición internacional (3 a 6 meses) para equipos pesados de producción:
* **Scooptrams (LHD)**
* **Jumbos de perforación frontal y radial**
* **Bombas multietapa de desagüe**
* **Ventiladores axiales principales de interior mina**
* **Palas / Shovels de carguío**
* **Perforadoras Long Hole**
* **Compresores estacionarios**
* **Fajas transportadoras (Conveyors)**

### Impacto Económico:
Una parada no planificada por quiebre de stock en un frente de producción subterráneo representa un costo operativo promedio de **\$14,500 USD por hora**.

### Hipótesis Principal:
* **$H_0$ (Hipótesis Nula):** El Gemelo Digital no identifica estrategias de resiliencia capaces de reducir significativamente el downtime causado por falta de repuestos críticos.
* **$H_1$ (Hipótesis Alternativa):** El Gemelo Digital identifica configuraciones de resiliencia que reducen el downtime causado por falta de repuestos críticos en al menos **30 % respecto a la estrategia actual** ($p < 0.05$).

---

## 🏗️ Arquitectura del Sistema

Clean Architecture en capas desacopladas:

1. **🖥️ Frontend React (Plataforma Principal - Puerto 3000):**
   * Desarrollado en **React 19 + Vite + Tailwind CSS + Recharts + Plotly 3D**.
   * **Gemelo Digital 3D**: Topología subterránea interactiva en 3D con 4 cotas de nivel (-120m, -240m, -360m, -480m), pique vertical y monitoreo de los 33 equipos en tiempo real.
   * **Inspector y BOM**: Despiece mecánico y eléctrico (*Bill of Materials*) por subsistemas con indicador de vulnerabilidad por proveedor único (*Single Sourcing*).
   * **Dinámica de Sistemas (SD)**: Ecuaciones diferenciales continuas con retardo de tercer orden ($DELAY3$) y sliders interactivos.
   * **Laboratorio de Resiliencia**: Escenarios de estrés del paper (**E0 Línea Base**, **E1 Quiebre de Proveedor Único**, **E2 Bloqueo de Vía de Acceso**, **E3 Demanda Extrema**) y benchmark de políticas (**P0 a P4**).
   * **Simulación Multi-Agente (SimPy ABM)**: Interacción de 5 clases de agentes autónomos y evaluación formal de hipótesis ($H_0$ vs $H_1$).
   * **Diseño Responsivo**: Barra lateral inteligente auto-plegable en tablets y dispositivos móviles con menú hamburguesa.

2. **⚙️ Backend FastAPI (API REST - Puerto 8000):**
   * Schemas Pydantic v2, servicios de negocio desacoplados y CORS habilitado.
   * Endpoints para telemetría, estado de la flota, snapshots, simulación SD, benchmark y evaluación estadística.
   * Documentación interactiva Swagger disponible en `/docs`.

3. **📊 Módulo de Machine Learning bajo Metodología CRISP-DM (Streamlit - Puerto 8501):**
   * Pipeline predictivo estructurado en las 6 fases de **CRISP-DM**.
   * Incorporación de datasets mineros públicos: **MSHA Equipment Failures** ($N=2,500$) y **Mining Supply Chain Benchmark** ($N=10,000$).
   * **8 Tablas numeradas** y **8 Figuras interactivas**, cada una con bloques estructurados obligatorios de:
     * **`1. INTERPRETACIÓN:`** Lectura cuantitativa y objetiva de las métricas observadas.
     * **`💡 2. EXPLICABILIDAD:`** Causalidad física en minería, costo de parada de \$14,500/h y decisión logística tomada.
   * **Suite de 3 Pruebas Estadísticas Robustas No Paramétricas**:
     1. **Test Omnibus de Friedman** ($\chi^2_F = 14.560, p = 0.00571 < 0.05$).
     2. **Test Pareado de Wilcoxon con Corrección Holm-Bonferroni** ($p < 0.05$ ajustado).
     3. **Test U de Mann-Whitney** ($U = 874,716.0, Z = 32.18, p = 1.25 \times 10^{-227} < 0.001$, Rank-Biserial $r = 0.8564$).
     4. **Inferencia Complementaria por Re-muestreo Bootstrap** (10,000 réplicas con Intervalo de Confianza al 95%).

4. **🗄️ Base de Datos y Persistencia:**
   * SQLAlchemy con soporte dual: PostgreSQL (producción / Docker) y SQLite automático (`sqlite:///./mining_digital_twin.db`).
   * Modelos relacionales para Equipos, Tipos, Almacén, Repuestos, BOM, Fallas y Snapshots de estado.

---

## 📈 Catálogo del Módulo CRISP-DM (Streamlit)

### Tablas Generadas (8 Tablas con Interpretación y Explicabilidad):
* **Tabla 1**: Resumen Estadístico Descriptivo del Dataset Minero Público y Operacional (MSHA & Supply Chain).
* **Tabla 2**: Matriz Global de Rendimiento y Benchmark de los 5 Algoritmos (Accuracy, F1, ROC-AUC, Latencia).
* **Tabla 3**: Reporte de Clasificación Detallado y Matriz de Confusión del Modelo Ganador (Hybrid Voting).
* **Tabla 4**: Desglose de Rendimiento en Validación Cruzada Estratificada 5-Fold por Algoritmo.
* **Tabla 5**: Espacio de Búsqueda y Configuración Óptima de Hiperparámetros (GridSearchCV).
* **Tabla 6A**: Rankings Medios de los 5 Algoritmos (Prueba Omnibus de Friedman).
* **Tabla 6B**: Comparaciones Post-Hoc Pareadas de Wilcoxon con Corrección de Holm.
* **Tabla 7**: Estimación de Incertidumbre y Robustez por Remuestreo Bootstrap (10,000 Réplicas).
* **Tabla 8**: Resultados del Test U de Mann-Whitney (Separabilidad Estocástica de Clases y Detección de Quiebres Críticos).

### Figuras Generadas (8 Figuras Interactivas con Interpretación y Explicabilidad):
* **Figura 1**: Distribución y Balance de Clases de la Variable Objetivo (`riesgo_stockout`).
* **Figura 2**: Matriz de Correlación de Pearson entre Parámetros Logísticos y de Confiabilidad.
* **Figura 3**: Rendimiento Multimétrica Comparativo de los 5 Algoritmos.
* **Figura 4**: Mapas de Calor de las Matrices de Confusión en el Test Set ($N=2,000$).
* **Figura 5**: Radar Multidimensional de Competencias Técnicas del Algoritmo Ganador.
* **Figura 6**: Diagrama de Cajas (Boxplot) de Estabilidad y Varianza de F1-Macro en 5 Pliegues de CV.
* **Figura 7**: Superficie de Respuesta 2D de Hiperparámetros (Estimadores vs Profundidad).
* **Figura 7b**: Contribución Relativa en Ganancia de Rendimiento (ANOVA Hiperparámetros).
* **Figura 8**: Distribución Empírica por Remuestreo Bootstrap (10,000 Réplicas) con Intervalo de Confianza al 95%.

---

## 🚀 Puesta en Marcha Rápida

### 1. Clonar el Repositorio
```bash
git clone https://github.com/ElvRb/Gemelo_digital_minero.git
cd Gemelo_digital_minero
```

### 2. Configurar el Backend (Python)
Requisitos: Python 3.10 o superior.

```bash
# Crear y activar entorno virtual
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# Instalar dependencias de Python
pip install -r requirements.txt

# Inicializar y poblar la base de datos
python -m database.seed.data_seeder

# Iniciar servidor backend FastAPI
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
> La API estará disponible en `http://localhost:8000` y la documentación Swagger en `http://localhost:8000/docs`.

### 3. Configurar el Frontend (React + Vite)
Requisitos: Node.js 18 o superior y npm.

```bash
# Navegar al directorio del frontend
cd frontend

# Instalar dependencias
npm install --legacy-peer-deps

# Iniciar servidor de desarrollo
npm run dev -- --port 3000 --host 0.0.0.0
```
> Abre tu navegador en **`http://localhost:3000`**.

### 4. Ejecutar el Frontend Streamlit (Suite CRISP-DM)
```bash
python -m streamlit run app/streamlit_app.py --server.port 8501
```
> Abre tu navegador en **`http://localhost:8501`** y navega a *"⚙️ Motor de Inteligencia Artificial"*.

---

## 🧪 Pruebas Automatizadas

Para ejecutar la suite de pruebas completa:

```bash
pytest tests/ -v
```

Cubre:
* Integridad referencial de BD y cálculo de SDI (`test_database.py`)
* Solucionadores de System Dynamics, SimPy ABM y Monte Carlo (`test_simulation.py`)
* Entrenamiento de los 5 modelos de ML y 5-Fold CV (`test_ml_models.py`)
* Suite de pruebas estadísticas y evaluación formal de hipótesis (`test_statistics.py`)

---

## 🐳 Despliegue con Docker Compose

```bash
docker-compose up --build
```

---

## 👤 Credenciales de Acceso por Defecto

| Rol | Usuario | Contraseña | Nombre Registrado |
| :--- | :--- | :--- | :--- |
| **Administrador** | `admin` | `admin123` | **Sofia Contreras** |
| **Ingeniero** | `ingeniero` | `ing123` | Carlos Mendoza |
| **Operador** | `operador` | `op123` | Juan Pérez |

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.
