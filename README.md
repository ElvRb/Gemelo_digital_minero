# Resilience-Driven Digital Twin for Supply Chain Disruption in Underground Mining
## A System Dynamics and Multi-Agent Simulation of Critical Spare Parts Logistics

Plataforma científica e industrial integral para la gestión, simulación híbrida (Dinámica de Sistemas + Simulación Multi-Agente en SimPy), evaluación de resiliencia y validación estadística formal de la cadena de suministro de repuestos críticos en minería subterránea.

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

### Hipótesis Principal:
* **$H_0$ (Hipótesis Nula):** El Gemelo Digital no identifica estrategias de resiliencia capaces de reducir significativamente el downtime causado por falta de repuestos críticos.
* **$H_1$ (Hipótesis Alternativa):** El Gemelo Digital identifica configuraciones de resiliencia que reducen el downtime causado por falta de repuestos críticos en al menos **30 % respecto a la estrategia actual** ($p < 0.05$).

---

## 🏗️ Arquitectura del Sistema

Clean Architecture en capas desacopladas:

1. **🖥️ Frontend React (Plataforma Principal - Puerto 3000):**
   * Desarrollado en **React 19 + Vite + Tailwind CSS + Recharts + Plotly 3D**.
   * **Gemelo Digital 3D**: Topología subterránea interactiva en 3D con 4 cotas de nivel (-120m, -240m, -360m, -480m), pique vertical y monitoreo de los 33 equipos.
   * **Inspector y BOM**: Despiece mecánico y eléctrico (Bill of Materials) por subsistemas con indicador de quiebre de stock.
   * **Dinámica de Sistemas (SD)**: Ecuaciones diferenciales continuas con retardo $DELAY3$ y sliders interactivos.
   * **Laboratorio de Resiliencia**: Escenarios de estrés del paper (**E0 Línea Base**, **E1 Quiebre de Proveedor Único**, **E2 Bloqueo de Vía de Acceso**, **E3 Demanda Extrema**) y benchmark de políticas (**P0 a P4**).
   * **Simulación Multi-Agente (SimPy ABM)**: Interacción de 5 clases de agentes autónomos y evaluación formal de hipótesis ($H_0$ vs $H_1$).
   * **Diseño Responsivo**: Barra lateral inteligente auto-plegable en tablets y dispositivos móviles con menú hamburguesa.

2. **⚙️ Backend FastAPI (API REST - Puerto 8000):**
   * Schemas Pydantic v2, servicios de negocio desacoplados y CORS habilitado.
   * Endpoints para telemetría, estado de la flota, snapshots, simulación SD, benchmark y evaluación estadística.
   * Documentación interactiva Swagger disponible en `/docs`.

3. **📊 Frontend Analítico Streamlit (Puerto 8501):**
   * Plataforma de soporte analítico con motor de Machine Learning y benchmarking de algoritmos supervisados.

4. **🗄️ Base de Datos y Persistencia:**
   * SQLAlchemy con soporte dual: PostgreSQL (producción / Docker) y SQLite automático (`sqlite:///./mining_digital_twin.db`).
   * Modelos relacionales para Equipos, Tipos, Almacén, Repuestos, BOM, Fallas y Snapshots de estado.

5. **🔬 Rigor Científico y Pruebas Estadísticas:**
   * **Mann-Whitney U**, **Test de Friedman**, **Wilcoxon Signed-Rank** con corrección Holm-Bonferroni.
   * **Remuestreo Bootstrap** (10,000 réplicas con Intervalo de Confianza al 95%).
   * Análisis de Sensibilidad Global de Sobol ($S_1, S_T$).

---

## 🚀 Puesta en Marcha Rápida

### 1. Clonar el Repositorio
```bash
git clone https://github.com/TU_USUARIO/TU_REPOSITORIO.git
cd "Gemelo Digital CD Minero"
```

### 2. Configurar el Backend (Python)
Requisitos: Python 3.10 o superior.

```bash
# Crear y activar entorno virtual (opcional pero recomendado)
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

### 4. (Opcional) Ejecutar el Frontend Streamlit
```bash
streamlit run app/streamlit_app.py --server.port 8501
```

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
