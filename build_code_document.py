import os
import sys
import time
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

EXCLUDE_DIRS = {
    'venv', '.venv', '__pycache__', 'node_modules', '.git', '.pytest_cache',
    'dist', 'build', '.idea', '.vscode', 'DATASETS_MAESTRO', 'dataset', 'datasets',
    'maintie-main', 'artifacts', 'logs', 'reports_output'
}

VALID_EXTS = {'.py', '.js', '.jsx', '.ts', '.tsx', '.html', '.css', '.sql', '.yaml', '.yml', 'Dockerfile'}

EXCLUDE_FILES = {
    'generate_code_docx.py', 'test_categorization.py', 'test_style.py', 
    'test_render.py', 'test_perf.py', 'test_table.py', 'benchmark_docx.py',
    'build_code_document.py'
}

MODULE_INFO = {
    '01. Arquitectura, Configuración & Docker': {
        'desc': 'Archivos de configuración de infraestructura, contenedores Docker y orquestación de servicios para el despliegue del sistema.',
        'tech': 'Docker, Docker Compose, YAML'
    },
    '02. Backend API & Servicios (FastAPI)': {
        'desc': 'Servidor backend basado en FastAPI, middleware, autenticación JWT, configuración y servicios de lógica de negocio (Gemelo Digital, Cadena de Suministro, Recomendaciones).',
        'tech': 'Python, FastAPI, Pydantic, JWT'
    },
    '03. Base de Datos & Modelos ORM (SQLAlchemy)': {
        'desc': 'Definición de modelos relacionales ORM (equipos, sensores, simulación, fallas, repuestos, usuarios), conexión pooling y sembrador de datos sintéticos.',
        'tech': 'Python, SQLAlchemy, SQLite/PostgreSQL'
    },
    '04. Motor de Simulación (ABM, Monte Carlo, SD)': {
        'desc': 'Motores de simulación híbrida: Modelo Basado en Agentes (ABM) para despacho minero, Simulación Estocástica Monte Carlo y Dinámica de Sistemas (stocks y flujos).',
        'tech': 'Python, Mesa, SimPy, NumPy, SciPy'
    },
    '05. Machine Learning & Modelos Predictivos': {
        'desc': 'Modelos de predicción de fallas y RUL (Vida Útil Remanente), ingeniería de características, pipeline de entrenamiento y explicabilidad con SHAP.',
        'tech': 'Python, Scikit-learn, XGBoost, SHAP'
    },
    '06. Batería de Análisis Estadístico e Hipótesis': {
        'desc': 'Pruebas estadísticas rigurosas para validación de hipótesis: Bootstrap, Friedman, Wilcoxon, Mann-Whitney, Kolmogorov-Smirnov y sensibilidad Sobol.',
        'tech': 'Python, SciPy, Statsmodels, SALib'
    },
    '07. Dashboard & Aplicación Interactiva (Streamlit)': {
        'desc': 'Aplicación principal de usuario en Streamlit: vistas operacionales, tableros ejecutivos de KPIs, análisis EDA, monitoreo 3D y control de escenarios.',
        'tech': 'Python, Streamlit, Plotly, Altair, CSS'
    },
    '08. Frontend Web & Visualización 3D (React & Three.js)': {
        'desc': 'Interfaz web moderna con visualización tridimensional de la mina en Three.js, vista de agentes autónomos, laboratorio de resiliencia e inspector de equipos.',
        'tech': 'React, Three.js, Vite, Tailwind CSS, JavaScript'
    },
    '09. Pipeline de Datos & Experimentación ML': {
        'desc': 'Pipeline experimental estructurado: notebooks reproducibles de auditoría, limpieza, feature engineering, validación cruzada y generación de figuras científicas.',
        'tech': 'Python, Pandas, Matplotlib, Seaborn'
    },
    '10. Pruebas Automatizadas (Unit & Integration)': {
        'desc': 'Suite de pruebas de software para verificar integridad de base de datos, modelos de Machine Learning, simulador y análisis estadístico.',
        'tech': 'Python, Pytest'
    },
    '11. Generación de Reportes': {
        'desc': 'Módulo de generación de informes técnicos, resúmenes operativos y exportación de métricas.',
        'tech': 'Python, FPDF/ReportLab/Markdown'
    },
    '12. Scripts de Procesamiento, Auditoría y Utilidades': {
        'desc': 'Scripts de soporte para ingesta, muestreo, verificación de datasets (FEMTO, XJTU-SY, MSHA) y validación de artefactos finales.',
        'tech': 'Python, Pandas, CLI Tools'
    }
}

FILE_DESCRIPTIONS = {
    'Dockerfile': 'Definición de contenedor Docker para construcción y empaquetado del entorno de producción.',
    'docker-compose.yml': 'Orquestación de servicios multicontenedor (backend, app, base de datos).',
    'backend/__init__.py': 'Inicializador de paquete para el módulo de backend.',
    'backend/config.py': 'Configuración global del backend, variables de entorno y parámetros de red.',
    'backend/main.py': 'Punto de entrada FastAPI, middlewares CORS, configuración de endpoints y ciclo de vida.',
    'backend/services/auth_service.py': 'Servicio de autenticación, hash de credenciales y generación/validación de tokens JWT.',
    'backend/services/digital_twin_service.py': 'Servicio principal de lógica del gemelo digital, sincronización de telemetría y estado de flota.',
    'backend/services/recommendation_service.py': 'Servicio de recomendaciones prescriptivas de mantenimiento basadas en riesgo.',
    'backend/services/supply_chain_service.py': 'Servicio de optimización logística, disponibilidad de repuestos y órdenes de compra.',
    'database/__init__.py': 'Inicializador del paquete database con exportación de modelos y conexiones.',
    'database/connection.py': 'Gestor de conexión SQLAlchemy, configuración del motor SQLite y sesiones contextuales.',
    'database/models/__init__.py': 'Punto centralizado de importación de todos los modelos relacionales del sistema.',
    'database/models/digital_twin.py': 'Modelo ORM para estados operacionales, variables ambientales y telemetría de activos.',
    'database/models/equipment.py': 'Modelo ORM de equipos mineros (camiones, palas, perforadoras) y sus especificaciones.',
    'database/models/inventory.py': 'Modelo ORM para control de stock en almacén, niveles mínimos y rotación de repuestos.',
    'database/models/logistics.py': 'Modelo ORM para rutas de transporte, asignación de viajes y estados de despacho.',
    'database/models/mine.py': 'Modelo ORM de infraestructura minera, tajos, bancos, talleres y botaderos.',
    'database/models/ml.py': 'Modelo ORM para registro de experimentos de Machine Learning, métricas y predicciones.',
    'database/models/simulation.py': 'Modelo ORM para persistencia de escenarios y corridas de simulación estocástica.',
    'database/models/spare_part.py': 'Modelo ORM para catálogo maestro de repuestos, criticidad y tiempos de reposición.',
    'database/models/statistics.py': 'Modelo ORM para almacenamiento de pruebas de hipótesis e intervalos estadísticos.',
    'database/models/supplier.py': 'Modelo ORM para gestión de proveedores de partes mineras y acuerdos de servicio (SLA).',
    'database/models/user.py': 'Modelo ORM de usuarios, roles de acceso, permisos y auditoría de seguridad.',
    'database/seed/data_seeder.py': 'Módulo sembrador de datos sintéticos realistas para inicialización completa de la base de datos.',
    'simulation/engine.py': 'Motor unificado de orquestación para simulación híbrida (agentes y dinámica continua).',
    'simulation/agents/abm_simulator.py': 'Simulador multiagente (ABM) para interacción autónoma entre camiones de acarreo y palas.',
    'simulation/monte_carlo/runner.py': 'Ejecutor de simulaciones Monte Carlo para evaluación probabilística de riesgo operacional.',
    'simulation/system_dynamics/sd_simulator.py': 'Simulador de Dinámica de Sistemas para análisis macroscópico de flujos y desgaste acumulado.',
    'simulation/system_dynamics/stocks_flows.py': 'Definición de ecuaciones diferenciales, stocks, flujos y lazos de retroalimentación.',
    'ml/explainability/explainer.py': 'Módulo de explicabilidad de modelos con cálculo de valores SHAP e impacto de features.',
    'ml/feature_engineering/pipeline.py': 'Pipeline de preprocesamiento, escalado y derivación de indicadores de condición de maquinaria.',
    'ml/models/models_suite.py': 'Suite de algoritmos de Machine Learning: Random Forest, Gradient Boosting, XGBoost y regresión.',
    'ml/training/trainer.py': 'Entrenador sistemático con validación cruzada estratificada y serialización de modelos.',
    'statistics/__init__.py': 'Inicializador del paquete de análisis estadístico.',
    'statistics/bootstrap.py': 'Implementación de remuestreo Bootstrap para intervalos de confianza no paramétricos.',
    'statistics/friedman.py': 'Prueba de Friedman para comparación no paramétrica de múltiples algoritmos predictivos.',
    'statistics/hypothesis_evaluator.py': 'Evaluador central de hipótesis científicas del proyecto con criterios de decisión.',
    'statistics/ks_test.py': 'Prueba de Kolmogorov-Smirnov de dos muestras para comparar distribuciones de falla.',
    'statistics/mann_whitney.py': 'Prueba U de Mann-Whitney para validación de diferencias en muestras independientes.',
    'statistics/sobol.py': 'Análisis de sensibilidad global de Sobol para descomposición de varianza de parámetros clave.',
    'statistics/wilcoxon.py': 'Prueba de rangos con signo de Wilcoxon para análisis comparativo pareado de modelos.',
    'app/streamlit_app.py': 'Aplicación principal Streamlit con configuración de navegación multipágina y sesión.',
    'app/components/kpi_cards.py': 'Componentes reutilizables para tarjetas de indicadores clave de rendimiento (KPIs).',
    'app/components/mine_3d.py': 'Componente de renderizado 3D de la topografía minera y ubicación de maquinaria pesada.',
    'app/styles/custom.css': 'Estilos CSS personalizados para interfaz oscura (Dark UI) temática de ingeniería minera.',
    'app/views/dashboard_view.py': 'Vista de tablero de mando general con disponibilidad de flota, OEE y alertas urgentes.',
    'app/views/digital_twin_view.py': 'Vista interactiva del Gemelo Digital con telemetría en tiempo real y estado por equipo.',
    'app/views/eda_view.py': 'Vista de análisis exploratorio de datos, matrices de correlación y perfiles de sensores.',
    'app/views/hypothesis_view.py': 'Vista de validación empírica de hipótesis científicas con gráficos de p-valor.',
    'app/views/log_view.py': 'Vista de registro de eventos del sistema, trazas de ejecución y auditoría de cambios.',
    'app/views/login_view.py': 'Vista de interfaz de inicio de sesión con control de credenciales y roles.',
    'app/views/mine_view.py': 'Vista de visualización geoespacial de sectores de la mina, botaderos y trituradoras.',
    'app/views/ml_view.py': 'Vista de métricas de modelos de Machine Learning, curvas de precisión-recall y matriz de confusión.',
    'app/views/recommendations_view.py': 'Vista de recomendaciones prescriptivas con estimación de costos y priorización de órdenes.',
    'app/views/reports_view.py': 'Vista de generación y descarga de informes técnicos en formatos ejecutivos.',
    'app/views/resilience_view.py': 'Vista de laboratorio de resiliencia para prueba de estrés ante bloqueos o fallos simultáneos.',
    'app/views/simulation_view.py': 'Vista de ejecución interactiva de simulaciones ABM y escenarios de contingencia.',
    'app/views/statistics_view.py': 'Vista analítica de la batería estadística con distribuciones y tests no paramétricos.',
    'app/views/supply_chain_view.py': 'Vista de cadena de suministro con monitoreo de stock de repuestos y órdenes a proveedores.',
    'app/views/users_view.py': 'Vista de gestión de usuarios, asignación de perfiles técnicos y permisos administrativos.',
    'frontend/index.html': 'Plantilla HTML base de la aplicación React con montura del DOM principal.',
    'frontend/vite.config.js': 'Configuración de compilación ultrarrápida con Vite y plugins de React.',
    'frontend/src/main.jsx': 'Punto de entrada de renderizado React con StrictMode y hoja de estilos global.',
    'frontend/src/App.jsx': 'Componente raíz React con navegación, barra superior, menú lateral y vistas activas.',
    'frontend/src/App.css': 'Estilos CSS específicos de la aplicación React y transiciones de componentes.',
    'frontend/src/index.css': 'Estilos base, reset CSS y variables de diseño del frontend.',
    'frontend/src/api/client.js': 'Cliente de conexión API con interceptores de peticiones, endpoints y manejo de errores.',
    'frontend/src/components/Navbar.jsx': 'Barra superior con información del operador, estado del socket y notificaciones.',
    'frontend/src/components/Sidebar.jsx': 'Menú lateral de selección de módulos y estado de los servicios del sistema.',
    'frontend/src/components/DigitalTwinView.jsx': 'Componente de monitoreo del Gemelo Digital con telemetría visual de equipos.',
    'frontend/src/components/EquipmentInspector.jsx': 'Inspector detallado de parámetros mecánicos, hidráulicos y térmicos por máquina.',
    'frontend/src/components/Mine3DViewer.jsx': 'Visor 3D en Three.js con animación interactiva de topografía, tajos y camiones mineros.',
    'frontend/src/components/MultiAgentView.jsx': 'Visualizador del sistema multiagente con trayectorias de camiones y tiempos de ciclo.',
    'frontend/src/components/ResilienceLabView.jsx': 'Panel interactivo para inyección de perturbaciones y pruebas de resiliencia operacional.',
    'frontend/src/components/SystemDynamicsView.jsx': 'Diagrama de causalidad y simulación gráfica interactiva de dinámica de sistemas.',
    'project/run_pipeline.py': 'Orquestador principal que ejecuta de forma secuencial todo el pipeline experimental.',
    'project/notebooks/01_data_audit_and_sampling.py': 'Fase 1: Auditoría de integridad de datos y muestreo estratificado de fuentes.',
    'project/notebooks/02_cleaning_and_eda.py': 'Fase 2: Limpieza de registros, imputación y análisis exploratorio de señales.',
    'project/notebooks/03_feature_engineering_and_leakage_audit.py': 'Fase 3: Ingeniería de características temporales y prevención de data leakage.',
    'project/notebooks/04_preprocessing_and_pipeline_design.py': 'Fase 4: Diseño de transformadores y pipelines reproducibles con Scikit-learn.',
    'project/notebooks/05_model_training_and_cross_validation.py': 'Fase 5: Entrenamiento masivo de modelos con validación cruzada temporal.',
    'project/notebooks/06_statistical_battery_and_comparisons.py': 'Fase 6: Ejecución de batería estadística para comparación de significancia entre modelos.',
    'project/notebooks/07_final_test_evaluation_and_interpretability.py': 'Fase 7: Evaluación en conjunto de prueba final y análisis de explicabilidad con SHAP.',
    'project/notebooks/08_source_generalization_and_robustness.py': 'Fase 8: Pruebas de generalización entre fuentes cruzadas y evaluación de robustez.',
    'project/src/data/cleaner.py': 'Módulo de limpieza de datos de mantenimiento, descarte de anomalías y estandarización.',
    'project/src/data/loader.py': 'Cargador de datos desde repositorios locales y bases de datos estructuradas.',
    'project/src/evaluation/cv_evaluator.py': 'Evaluador de validación cruzada respetando dependencias temporales de fallas.',
    'project/src/evaluation/metrics.py': 'Cálculo de métricas de precisión, exhaustividad, ROC-AUC, PR-AUC y error cuadrático.',
    'project/src/features/engineering.py': 'Extracción de indicadores de desgaste, ventanas móviles y métricas estadísticas de vibración.',
    'project/src/features/leakage.py': 'Herramientas de inspección para garantizar la ausencia de filtración de datos futuros.',
    'project/src/models/factory.py': 'Patrón Factory para instanciación estandarizada de algoritmos de clasificación y regresión.',
    'project/src/preprocessing/pipeline_builder.py': 'Construcción modular de pipelines de transformación compatibles con Scikit-learn.',
    'project/src/statistics/statistical_tests.py': 'Funciones matemáticas para cálculo de pruebas de hipótesis estadísticas del pipeline.',
    'project/src/visualization/figures_generator.py': 'Generación automatizada de gráficos en alta resolución para reportes y publicaciones.',
    'tests/test_database.py': 'Pruebas unitarias de esquemas ORM, inserciones, relaciones y consultas de BD.',
    'tests/test_ml_models.py': 'Pruebas unitarias para verificar convergencia y salidas de modelos de Machine Learning.',
    'tests/test_simulation.py': 'Pruebas unitarias de invariantes del motor de simulación y comportamiento de agentes.',
    'tests/test_statistics.py': 'Pruebas unitarias para validar exactitud numérica de la batería de tests estadísticos.',
    'reports/generator.py': 'Generador programático de reportes técnicos con consolidación de métricas y hallazgos.',
    'check_counts.py': 'Script de verificación de conteo de registros en tablas maestras y procesadas.',
    'check_ml_env.py': 'Script de verificación de dependencias y compatibilidad del entorno de Machine Learning.',
    'count_femto_files.py': 'Utilidad para cuantificar archivos y acelerometría del dataset FEMTO Bearing.',
    'count_xjtu_snapshots.py': 'Utilidad para contar instantáneas y series de vibración del dataset XJTU-SY.',
    'deep_inspect_sources.py': 'Inspección profunda de consistencia en fuentes de datos heterogéneas.',
    'explore_gsc_and_nlp.py': 'Exploración de reportes textuales mineros con técnicas de Procesamiento de Lenguaje Natural.',
    'explore_master_for_ml.py': 'Análisis exploratorio de la tabla consolidada para preparación de datasets de ML.',
    'find_dataset_files.py': 'Búsqueda e indexación de archivos de datos disponibles en el almacenamiento local.',
    'gate_and_sample.py': 'Filtrado de calidad y muestreo balanceado de registros para entrenamiento ágil.',
    'inspect_details.py': 'Inspección de atributos detallados y metadatos de activos del gemelo digital.',
    'inspect_environment.py': 'Comprobación de variables del sistema operativo, versión de Python y paquetes.',
    'inspect_msha_acc.py': 'Inspección y categorización de registros de accidentes de la base de datos MSHA.',
    'inspect_msha_mines.py': 'Inspección del padrón general de minas registradas en MSHA y sus características.',
    'inspect_sources.py': 'Revisión preliminar de fuentes de datos disponibles para el proyecto.',
    'inspect_xjtu_y.py': 'Inspección de etiquetas y variables objetivo en el dataset XJTU-SY.',
    'process_femto.py': 'Pipeline de extracción, procesamiento y agregación de señales del dataset FEMTO.',
    'process_xjtu_incremental.py': 'Procesamiento incremental eficiente de acelerometría continua del dataset XJTU-SY.',
    'read_gsc_pdfs.py': 'Extractor de información de documentos PDF técnicos y manuales de mantenimiento.',
    'survey_datasets.py': 'Censo descriptivo de datasets y volumetría disponible en el repositorio.',
    'test_femto_optimization.py': 'Prueba de rendimiento y optimización para lectura vectorial de señales FEMTO.',
    'test_femto_pd.py': 'Validación de transformaciones en Pandas para series de tiempo de vibración.',
    'test_femto_speed.py': 'Benchmark de velocidad de procesamiento para series temporales de alta frecuencia.',
    'test_maintnorm_parse.py': 'Pruebas de parseo y normalización de textos de órdenes de trabajo de mantenimiento.',
    'verify_final_artifacts.py': 'Script de verificación de completitud e integridad de todos los artefactos generados.'
}

def get_category(rel_path):
    parts = rel_path.replace('\\', '/').split('/')
    top = parts[0]
    if top == 'backend':
        return '02. Backend API & Servicios (FastAPI)'
    elif top == 'database':
        return '03. Base de Datos & Modelos ORM (SQLAlchemy)'
    elif top == 'simulation':
        return '04. Motor de Simulación (ABM, Monte Carlo, SD)'
    elif top == 'ml':
        return '05. Machine Learning & Modelos Predictivos'
    elif top == 'statistics':
        return '06. Batería de Análisis Estadístico e Hipótesis'
    elif top == 'app':
        return '07. Dashboard & Aplicación Interactiva (Streamlit)'
    elif top == 'frontend':
        return '08. Frontend Web & Visualización 3D (React & Three.js)'
    elif top == 'project':
        return '09. Pipeline de Datos & Experimentación ML'
    elif top == 'tests':
        return '10. Pruebas Automatizadas (Unit & Integration)'
    elif top == 'reports':
        return '11. Generación de Reportes'
    elif top in {'Dockerfile', 'docker-compose.yml'}:
        return '01. Arquitectura, Configuración & Docker'
    else:
        return '12. Scripts de Procesamiento, Auditoría y Utilidades'

def get_lang(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    mapping = {
        '.py': 'Python',
        '.jsx': 'React (JSX)',
        '.js': 'JavaScript',
        '.html': 'HTML5',
        '.css': 'CSS3',
        '.yml': 'YAML',
        '.yaml': 'YAML',
        '.sql': 'SQL'
    }
    if os.path.basename(file_path) == 'Dockerfile':
        return 'Dockerfile'
    return mapping.get(ext, 'Texto')

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    ''')
    tcPr.append(tcMar)

def set_cell_borders(cell, top='CBD5E1', bottom='CBD5E1', left='CBD5E1', right='CBD5E1', sz='4'):
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{top}"/>
            <w:left w:val="single" w:sz="{sz}" w:space="0" w:color="{left}"/>
            <w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{bottom}"/>
            <w:right w:val="single" w:sz="{sz}" w:space="0" w:color="{right}"/>
        </w:tcBorders>
    ''')
    tcPr.append(borders)

def add_header_footer(doc):
    for s in doc.sections:
        s.different_first_page_header_footer = True
        
        # Header
        header = s.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("GEMELO DIGITAL MINERO  |  CÓDIGO FUENTE DEL SISTEMA")
        hrun.font.name = 'Segoe UI'
        hrun.font.size = Pt(8.0)
        hrun.font.color.rgb = RGBColor(100, 116, 139)
        
        # Footer
        footer = s.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        frun = fp.add_run("Documentación Técnica de Software  —  Confidencial y de Uso Exclusivo")
        frun.font.name = 'Segoe UI'
        frun.font.size = Pt(8.0)
        frun.font.color.rgb = RGBColor(148, 163, 184)

def main():
    print("Iniciando escaneo y catalogación de archivos de código...")
    all_files = []
    by_category = {}

    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith('.')]
        parts = set(os.path.normpath(root).split(os.sep))
        if parts.intersection(EXCLUDE_DIRS):
            continue

        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if (ext in VALID_EXTS or f == 'Dockerfile') and f not in EXCLUDE_FILES:
                rel_path = os.path.relpath(os.path.join(root, f), '.')
                rel_clean = rel_path.replace('\\', '/')
                if rel_clean.startswith('data/') or 'database/dataset' in rel_clean:
                    continue
                cat = get_category(rel_path)
                by_category.setdefault(cat, []).append(rel_path)
                all_files.append(rel_path)

    all_files.sort()
    for cat in by_category:
        by_category[cat].sort()

    total_files = len(all_files)
    total_lines = 0
    file_metadata = {}

    for fp in all_files:
        try:
            with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                total_lines += len(lines)
                size_kb = os.path.getsize(fp) / 1024.0
                file_metadata[fp] = {
                    'lines': len(lines),
                    'content': "".join(lines),
                    'size_kb': size_kb
                }
        except Exception as e:
            file_metadata[fp] = {'lines': 0, 'content': '', 'size_kb': 0}

    print(f"Total archivos detectados: {total_files}")
    print(f"Total líneas de código: {total_lines}")

    doc = docx.Document()
    
    # Page setup
    for section in doc.sections:
        section.top_margin = Inches(0.7)
        section.bottom_margin = Inches(0.7)
        section.left_margin = Inches(0.7)
        section.right_margin = Inches(0.7)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)

    add_header_footer(doc)

    # Styles
    styles = doc.styles
    
    # Code style
    code_style = styles.add_style('SourceCodeBlock', docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
    code_style.font.name = 'Consolas'
    code_style.font.size = Pt(7.5)
    code_style.font.color.rgb = RGBColor(30, 41, 59)
    code_style.paragraph_format.space_before = Pt(0)
    code_style.paragraph_format.space_after = Pt(0)
    code_style.paragraph_format.line_spacing = 1.0
    code_style.paragraph_format.left_indent = Inches(0.12)
    code_style.paragraph_format.right_indent = Inches(0.12)
    
    # Paragraph shading and left border
    pPr = code_style._element.get_or_add_pPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F8FAFC"/>')
    pPr.append(shd)
    bdr = parse_xml(f'''
        <w:pBdr {nsdecls("w")}>
            <w:top w:val="none" w:sz="0" w:space="0" w:color="auto"/>
            <w:left w:val="single" w:sz="18" w:space="6" w:color="2563EB"/>
            <w:bottom w:val="none" w:sz="0" w:space="0" w:color="auto"/>
            <w:right w:val="none" w:sz="0" w:space="0" w:color="auto"/>
        </w:pBdr>
    ''')
    pPr.append(bdr)

    # =========================================================================
    # 1. PORTADA
    # =========================================================================
    print("Generando portada...")
    p_pre = doc.add_paragraph()
    p_pre.paragraph_format.space_before = Pt(36)
    
    # Tag
    p_tag = doc.add_paragraph()
    r_tag = p_tag.add_run("ARQUITECTURA DE SOFTWARE  •  REPOSITORIO COMPLETO")
    r_tag.font.name = 'Segoe UI'
    r_tag.font.size = Pt(10)
    r_tag.font.bold = True
    r_tag.font.color.rgb = RGBColor(37, 99, 235) # Blue 600
    p_tag.paragraph_format.space_after = Pt(12)

    # Main Title
    p_title = doc.add_paragraph()
    r_title = p_title.add_run("CÓDIGO FUENTE DEL SISTEMA")
    r_title.font.name = 'Segoe UI'
    r_title.font.size = Pt(30)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(15, 23, 42) # Slate 900
    p_title.paragraph_format.space_after = Pt(6)

    # Subtitle
    p_sub = doc.add_paragraph()
    r_sub = p_sub.add_run("Gemelo Digital para la Gestión, Simulación y Mantenimiento Predictivo en Minería")
    r_sub.font.name = 'Segoe UI'
    r_sub.font.size = Pt(16)
    r_sub.font.color.rgb = RGBColor(51, 65, 85) # Slate 700
    p_sub.paragraph_format.space_after = Pt(28)

    # Divider bar
    tbl_bar = doc.add_table(rows=1, cols=1)
    tbl_bar.autofit = False
    tbl_bar.columns[0].width = Inches(7.1)
    c_bar = tbl_bar.cell(0, 0)
    set_cell_background(c_bar, "2563EB")
    set_cell_margins(c_bar, top=20, bottom=20, left=0, right=0)
    set_cell_borders(c_bar, top='2563EB', bottom='2563EB', left='2563EB', right='2563EB', sz='12')
    p_in_bar = c_bar.paragraphs[0]
    p_in_bar.paragraph_format.space_before = Pt(0)
    p_in_bar.paragraph_format.space_after = Pt(0)
    p_bar_space = doc.add_paragraph()
    p_bar_space.paragraph_format.space_after = Pt(24)

    # Overview text
    p_desc = doc.add_paragraph()
    r_desc = p_desc.add_run(
        "El presente documento técnico recopila de forma exhaustiva y estructurada la totalidad "
        "del código fuente del ecosistema de Gemelo Digital Minero. Comprende la arquitectura de "
        "servicios backend en FastAPI, modelos relacionales ORM en SQLAlchemy, algoritmos predictivos "
        "de Machine Learning con explicabilidad SHAP, motor de simulación multiagente (ABM) y dinámica "
        "de sistemas, batería de validación estadística de hipótesis, aplicación interactiva en Streamlit "
        "y componentes web con visualización 3D en Three.js."
    )
    r_desc.font.name = 'Segoe UI'
    r_desc.font.size = Pt(10.5)
    r_desc.font.color.rgb = RGBColor(71, 85, 105)
    p_desc.paragraph_format.space_after = Pt(36)

    # Metadata card table
    meta_table = doc.add_table(rows=6, cols=2)
    meta_table.autofit = False
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.columns[0].width = Inches(2.3)
    meta_table.columns[1].width = Inches(4.8)

    meta_items = [
        ("Proyecto:", "Gemelo Digital CD Minero"),
        ("Stack Tecnológico:", "FastAPI, React Three.js, Streamlit, SQLAlchemy, Mesa ABM, Scikit-learn"),
        ("Estructura Modular:", f"12 Módulos / Subsistemas Funcionales"),
        ("Volumetría de Código:", f"{total_files} archivos fuente  |  {total_lines:,} líneas de código"),
        ("Fecha de Emisión:", "29 de Septiembre de 2026"),
        ("Clasificación:", "Documentación Técnica y Código Fuente Completo")
    ]

    for idx, (label, val) in enumerate(meta_items):
        c0 = meta_table.cell(idx, 0)
        c1 = meta_table.cell(idx, 1)
        bg = "F8FAFC" if idx % 2 == 0 else "FFFFFF"
        set_cell_background(c0, bg)
        set_cell_background(c1, bg)
        set_cell_margins(c0, top=90, bottom=90, left=120, right=100)
        set_cell_margins(c1, top=90, bottom=90, left=120, right=100)
        set_cell_borders(c0, top='E2E8F0', bottom='E2E8F0', left='CBD5E1', right='E2E8F0', sz='4')
        set_cell_borders(c1, top='E2E8F0', bottom='E2E8F0', left='E2E8F0', right='CBD5E1', sz='4')

        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_before = Pt(0)
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(label)
        r0.font.name = 'Segoe UI'
        r0.font.size = Pt(9.5)
        r0.font.bold = True
        r0.font.color.rgb = RGBColor(30, 41, 59)

        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_before = Pt(0)
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(val)
        r1.font.name = 'Segoe UI'
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = RGBColor(51, 65, 85)

    doc.add_page_break()

    # =========================================================================
    # 2. RESUMEN EJECUTIVO Y MAPA DE MÓDULOS
    # =========================================================================
    print("Generando mapa de módulos y resumen...")
    h1 = doc.add_heading(level=1)
    rh1 = h1.add_run("1. Mapa de Arquitectura y Volumetría Modular")
    rh1.font.name = 'Segoe UI'
    rh1.font.size = Pt(18)
    rh1.font.bold = True
    rh1.font.color.rgb = RGBColor(15, 23, 42)
    h1.paragraph_format.space_before = Pt(12)
    h1.paragraph_format.space_after = Pt(12)

    p_map_intro = doc.add_paragraph()
    r_map = p_map_intro.add_run(
        "El sistema se organiza en 12 subsistemas complementarios que articulan desde la infraestructura "
        "y base de datos hasta los algoritmos avanzados de simulación, predicción y frontend 3D:"
    )
    r_map.font.name = 'Segoe UI'
    r_map.font.size = Pt(10)
    p_map_intro.paragraph_format.space_after = Pt(14)

    # Summary table
    sum_table = doc.add_table(rows=len(MODULE_INFO) + 2, cols=5)
    sum_table.autofit = False
    sum_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    col_widths = [Inches(2.0), Inches(2.6), Inches(1.1), Inches(0.7), Inches(0.7)]
    for row in sum_table.rows:
        for idx, w in enumerate(col_widths):
            row.cells[idx].width = w

    # Header Row
    headers = ["Módulo / Subsistema", "Propósito en el Gemelo Digital", "Tecnologías", "Archivos", "Líneas"]
    for idx, h_text in enumerate(headers):
        cell = sum_table.cell(0, idx)
        set_cell_background(cell, "1E3A8A")
        set_cell_margins(cell, top=120, bottom=120, left=100, right=100)
        set_cell_borders(cell, top='1E3A8A', bottom='1E3A8A', left='1E3A8A', right='1E3A8A', sz='6')
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        if idx in [3, 4]:
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r = p.add_run(h_text)
        r.font.name = 'Segoe UI'
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    row_idx = 1
    total_files_sum = 0
    total_lines_sum = 0

    for cat_name in sorted(MODULE_INFO.keys()):
        files_in_cat = by_category.get(cat_name, [])
        cat_lines = sum(file_metadata.get(f, {}).get('lines', 0) for f in files_in_cat)
        total_files_sum += len(files_in_cat)
        total_lines_sum += cat_lines

        c_name = sum_table.cell(row_idx, 0)
        c_desc = sum_table.cell(row_idx, 1)
        c_tech = sum_table.cell(row_idx, 2)
        c_cnt = sum_table.cell(row_idx, 3)
        c_lns = sum_table.cell(row_idx, 4)

        bg = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
        for c in [c_name, c_desc, c_tech, c_cnt, c_lns]:
            set_cell_background(c, bg)
            set_cell_margins(c, top=80, bottom=80, left=90, right=90)
            set_cell_borders(c, top='E2E8F0', bottom='E2E8F0', left='E2E8F0', right='E2E8F0', sz='4')

        # Cell 0
        p0 = c_name.paragraphs[0]
        p0.paragraph_format.space_before = Pt(0)
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(cat_name)
        r0.font.name = 'Segoe UI'
        r0.font.size = Pt(8.0)
        r0.font.bold = True
        r0.font.color.rgb = RGBColor(15, 23, 42)

        # Cell 1
        p1 = c_desc.paragraphs[0]
        p1.paragraph_format.space_before = Pt(0)
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(MODULE_INFO[cat_name]['desc'])
        r1.font.name = 'Segoe UI'
        r1.font.size = Pt(7.5)
        r1.font.color.rgb = RGBColor(71, 85, 105)

        # Cell 2
        p2 = c_tech.paragraphs[0]
        p2.paragraph_format.space_before = Pt(0)
        p2.paragraph_format.space_after = Pt(0)
        r2 = p2.add_run(MODULE_INFO[cat_name]['tech'])
        r2.font.name = 'Segoe UI'
        r2.font.size = Pt(7.5)
        r2.font.color.rgb = RGBColor(37, 99, 235)

        # Cell 3
        p3 = c_cnt.paragraphs[0]
        p3.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p3.paragraph_format.space_before = Pt(0)
        p3.paragraph_format.space_after = Pt(0)
        r3 = p3.add_run(str(len(files_in_cat)))
        r3.font.name = 'Segoe UI'
        r3.font.size = Pt(8.0)
        r3.font.color.rgb = RGBColor(30, 41, 59)

        # Cell 4
        p4 = c_lns.paragraphs[0]
        p4.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p4.paragraph_format.space_before = Pt(0)
        p4.paragraph_format.space_after = Pt(0)
        r4 = p4.add_run(f"{cat_lines:,}")
        r4.font.name = 'Segoe UI'
        r4.font.size = Pt(8.0)
        r4.font.bold = True
        r4.font.color.rgb = RGBColor(30, 41, 59)

        row_idx += 1

    # Total Row
    tot_row = row_idx
    for c_idx in range(5):
        c = sum_table.cell(tot_row, c_idx)
        set_cell_background(c, "E2E8F0")
        set_cell_margins(c, top=90, bottom=90, left=90, right=90)
        set_cell_borders(c, top='94A3B8', bottom='94A3B8', left='94A3B8', right='94A3B8', sz='6')
    
    p_tot0 = sum_table.cell(tot_row, 0).paragraphs[0]
    p_tot0.paragraph_format.space_before = Pt(0)
    p_tot0.paragraph_format.space_after = Pt(0)
    r_tot0 = p_tot0.add_run("TOTAL GENERAL")
    r_tot0.font.name = 'Segoe UI'
    r_tot0.font.size = Pt(8.5)
    r_tot0.font.bold = True
    r_tot0.font.color.rgb = RGBColor(15, 23, 42)

    p_tot3 = sum_table.cell(tot_row, 3).paragraphs[0]
    p_tot3.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_tot3.paragraph_format.space_before = Pt(0)
    p_tot3.paragraph_format.space_after = Pt(0)
    r_tot3 = p_tot3.add_run(str(total_files_sum))
    r_tot3.font.name = 'Segoe UI'
    r_tot3.font.size = Pt(8.5)
    r_tot3.font.bold = True
    r_tot3.font.color.rgb = RGBColor(15, 23, 42)

    p_tot4 = sum_table.cell(tot_row, 4).paragraphs[0]
    p_tot4.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_tot4.paragraph_format.space_before = Pt(0)
    p_tot4.paragraph_format.space_after = Pt(0)
    r_tot4 = p_tot4.add_run(f"{total_lines_sum:,}")
    r_tot4.font.name = 'Segoe UI'
    r_tot4.font.size = Pt(8.5)
    r_tot4.font.bold = True
    r_tot4.font.color.rgb = RGBColor(15, 23, 42)

    doc.add_page_break()

    # =========================================================================
    # 3. ÍNDICE DETALLADO DE ARCHIVOS
    # =========================================================================
    print("Generando inventario detallado de archivos...")
    h2 = doc.add_heading(level=1)
    rh2 = h2.add_run("2. Inventario Detallado de Archivos Fuente")
    rh2.font.name = 'Segoe UI'
    rh2.font.size = Pt(18)
    rh2.font.bold = True
    rh2.font.color.rgb = RGBColor(15, 23, 42)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(12)

    p_inv_intro = doc.add_paragraph()
    r_inv = p_inv_intro.add_run(
        "A continuación se lista la totalidad de los 123 archivos de código fuente que integran el sistema, "
        "con su ruta relativa, lenguaje, recuento de líneas y rol funcional:"
    )
    r_inv.font.name = 'Segoe UI'
    r_inv.font.size = Pt(10)
    p_inv_intro.paragraph_format.space_after = Pt(14)

    # Inventory table
    inv_table = doc.add_table(rows=total_files + 1, cols=5)
    inv_table.autofit = False
    inv_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    inv_col_widths = [Inches(0.4), Inches(2.3), Inches(0.9), Inches(0.6), Inches(2.9)]
    for row in inv_table.rows:
        for idx, w in enumerate(inv_col_widths):
            row.cells[idx].width = w

    inv_headers = ["#", "Archivo / Ruta Relativa", "Lenguaje", "Líneas", "Descripción Funcional"]
    for idx, h_text in enumerate(inv_headers):
        cell = inv_table.cell(0, idx)
        set_cell_background(cell, "0F172A")
        set_cell_margins(cell, top=100, bottom=100, left=80, right=80)
        set_cell_borders(cell, top='0F172A', bottom='0F172A', left='0F172A', right='0F172A', sz='6')
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        if idx in [0, 3]:
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r = p.add_run(h_text)
        r.font.name = 'Segoe UI'
        r.font.size = Pt(8.0)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    inv_row_idx = 1
    file_number = 1

    for cat_name in sorted(MODULE_INFO.keys()):
        files_in_cat = by_category.get(cat_name, [])
        for rel_f in files_in_cat:
            c0 = inv_table.cell(inv_row_idx, 0)
            c1 = inv_table.cell(inv_row_idx, 1)
            c2 = inv_table.cell(inv_row_idx, 2)
            c3 = inv_table.cell(inv_row_idx, 3)
            c4 = inv_table.cell(inv_row_idx, 4)

            bg = "F8FAFC" if inv_row_idx % 2 == 1 else "FFFFFF"
            for c in [c0, c1, c2, c3, c4]:
                set_cell_background(c, bg)
                set_cell_margins(c, top=60, bottom=60, left=70, right=70)
                set_cell_borders(c, top='E2E8F0', bottom='E2E8F0', left='E2E8F0', right='E2E8F0', sz='4')

            clean_path = rel_f.replace('\\', '/')
            lns = file_metadata.get(rel_f, {}).get('lines', 0)
            lang = get_lang(rel_f)
            desc = FILE_DESCRIPTIONS.get(clean_path, f"Módulo de soporte y lógica para {clean_path}.")

            # c0: #
            p0 = c0.paragraphs[0]
            p0.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            p0.paragraph_format.space_before = Pt(0)
            p0.paragraph_format.space_after = Pt(0)
            r0 = p0.add_run(str(file_number))
            r0.font.name = 'Segoe UI'
            r0.font.size = Pt(7.5)
            r0.font.color.rgb = RGBColor(100, 116, 139)

            # c1: Path
            p1 = c1.paragraphs[0]
            p1.paragraph_format.space_before = Pt(0)
            p1.paragraph_format.space_after = Pt(0)
            r1 = p1.add_run(clean_path)
            r1.font.name = 'Consolas'
            r1.font.size = Pt(7.0)
            r1.font.bold = True
            r1.font.color.rgb = RGBColor(15, 23, 42)

            # c2: Lang
            p2 = c2.paragraphs[0]
            p2.paragraph_format.space_before = Pt(0)
            p2.paragraph_format.space_after = Pt(0)
            r2 = p2.add_run(lang)
            r2.font.name = 'Segoe UI'
            r2.font.size = Pt(7.5)
            r2.font.color.rgb = RGBColor(37, 99, 235)

            # c3: Lines
            p3 = c3.paragraphs[0]
            p3.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            p3.paragraph_format.space_before = Pt(0)
            p3.paragraph_format.space_after = Pt(0)
            r3 = p3.add_run(f"{lns:,}")
            r3.font.name = 'Segoe UI'
            r3.font.size = Pt(7.5)
            r3.font.color.rgb = RGBColor(30, 41, 59)

            # c4: Desc
            p4 = c4.paragraphs[0]
            p4.paragraph_format.space_before = Pt(0)
            p4.paragraph_format.space_after = Pt(0)
            r4 = p4.add_run(desc)
            r4.font.name = 'Segoe UI'
            r4.font.size = Pt(7.0)
            r4.font.color.rgb = RGBColor(71, 85, 105)

            inv_row_idx += 1
            file_number += 1

    doc.add_page_break()

    # =========================================================================
    # 4. CÓDIGO FUENTE POR MÓDULOS (01 AL 12)
    # =========================================================================
    print("Iniciando inclusión de código fuente por módulos...")
    global_file_counter = 1

    for cat_idx, cat_name in enumerate(sorted(MODULE_INFO.keys()), start=1):
        files_in_cat = by_category.get(cat_name, [])
        cat_lines = sum(file_metadata.get(f, {}).get('lines', 0) for f in files_in_cat)
        print(f"  Procesando {cat_name} ({len(files_in_cat)} archivos, {cat_lines} líneas)...")

        # Module Heading
        mod_h = doc.add_heading(level=1)
        rmod = mod_h.add_run(f"Capítulo {cat_idx}: {cat_name}")
        rmod.font.name = 'Segoe UI'
        rmod.font.size = Pt(16)
        rmod.font.bold = True
        rmod.font.color.rgb = RGBColor(15, 23, 42)
        mod_h.paragraph_format.space_before = Pt(16)
        mod_h.paragraph_format.space_after = Pt(6)

        # Module overview
        p_mod_info = doc.add_paragraph()
        r_mod_desc = p_mod_info.add_run(MODULE_INFO[cat_name]['desc'])
        r_mod_desc.font.name = 'Segoe UI'
        r_mod_desc.font.size = Pt(9.5)
        r_mod_desc.font.italic = True
        r_mod_desc.font.color.rgb = RGBColor(71, 85, 105)
        p_mod_info.paragraph_format.space_after = Pt(14)

        for file_in_cat_idx, rel_f in enumerate(files_in_cat, start=1):
            clean_path = rel_f.replace('\\', '/')
            meta = file_metadata.get(rel_f, {})
            content = meta.get('content', '')
            lns = meta.get('lines', 0)
            sz_kb = meta.get('size_kb', 0.0)
            lang = get_lang(rel_f)
            desc = FILE_DESCRIPTIONS.get(clean_path, f"Módulo de soporte y lógica para {clean_path}.")

            # File Heading
            fh = doc.add_heading(level=2)
            rfh = fh.add_run(f"{cat_idx}.{file_in_cat_idx}  {clean_path}")
            rfh.font.name = 'Segoe UI'
            rfh.font.size = Pt(11)
            rfh.font.bold = True
            rfh.font.color.rgb = RGBColor(30, 58, 138) # Blue 900
            fh.paragraph_format.space_before = Pt(14)
            fh.paragraph_format.space_after = Pt(2)

            # Metadata badge card
            meta_tbl = doc.add_table(rows=1, cols=1)
            meta_tbl.autofit = False
            meta_tbl.columns[0].width = Inches(7.1)
            meta_cell = meta_tbl.cell(0, 0)
            set_cell_background(meta_cell, "F1F5F9")
            set_cell_margins(meta_cell, top=60, bottom=60, left=100, right=100)
            set_cell_borders(meta_cell, top='E2E8F0', bottom='CBD5E1', left='2563EB', right='E2E8F0', sz='8')

            p_m = meta_cell.paragraphs[0]
            p_m.paragraph_format.space_before = Pt(0)
            p_m.paragraph_format.space_after = Pt(0)
            
            r_m1 = p_m.add_run(f"Archivo #{global_file_counter}  •  Lenguaje: ")
            r_m1.font.name = 'Segoe UI'
            r_m1.font.size = Pt(8.0)
            r_m1.font.bold = True
            r_m1.font.color.rgb = RGBColor(71, 85, 105)

            r_m2 = p_m.add_run(f"{lang}  •  ")
            r_m2.font.name = 'Segoe UI'
            r_m2.font.size = Pt(8.0)
            r_m2.font.bold = True
            r_m2.font.color.rgb = RGBColor(37, 99, 235)

            r_m3 = p_m.add_run(f"Líneas: {lns:,}  •  Tamaño: {sz_kb:.1f} KB  •  Propósito: {desc}")
            r_m3.font.name = 'Segoe UI'
            r_m3.font.size = Pt(8.0)
            r_m3.font.color.rgb = RGBColor(71, 85, 105)

            # Spacing before code
            p_gap = doc.add_paragraph()
            p_gap.paragraph_format.space_before = Pt(2)
            p_gap.paragraph_format.space_after = Pt(2)

            # Format Code Block
            # Convert tabs to 4 spaces, add line numbers
            raw_lines = content.splitlines()
            if not raw_lines:
                raw_lines = ["# Archivo vacío / inicializador de módulo"]

            # Chunk into paragraphs of max 150 lines for optimal pagination and speed
            CHUNK_SIZE = 150
            for start_idx in range(0, len(raw_lines), CHUNK_SIZE):
                chunk = raw_lines[start_idx:start_idx + CHUNK_SIZE]
                formatted_chunk = []
                for line_no, raw_line in enumerate(chunk, start=start_idx + 1):
                    clean_line = raw_line.replace('\t', '    ').rstrip()
                    formatted_chunk.append(f"{line_no:4d} | {clean_line}")

                p_code = doc.add_paragraph(style='SourceCodeBlock')
                run_code = p_code.add_run("\n".join(formatted_chunk))
                run_code.font.name = 'Consolas'
                run_code.font.size = Pt(7.2)
                run_code.font.color.rgb = RGBColor(30, 41, 59)

            # Spacing after code block
            p_after = doc.add_paragraph()
            p_after.paragraph_format.space_before = Pt(0)
            p_after.paragraph_format.space_after = Pt(12)

            global_file_counter += 1

        doc.add_page_break()

    output_filename = "Codigo_Fuente_Gemelo_Digital_Minero.docx"
    print(f"Guardando documento final: {output_filename}...")
    t0 = time.time()
    doc.save(output_filename)
    t1 = time.time()
    file_size_mb = os.path.getsize(output_filename) / (1024 * 1024)
    print(f"Documento guardado exitosamente en {t1 - t0:.2f} segundos!")
    print(f"Tamaño del archivo generado: {file_size_mb:.2f} MB")

if __name__ == '__main__':
    main()
