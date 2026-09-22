"""Machine Learning database models: datasets, experimentos_ml, modelos_ml, hiperparametros_ml, resultados_cv."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from database.connection import Base

class DatasetModel(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    version = Column(String(20), default="1.0.0")
    origen = Column(String(50), default="SINTETICO_DIGITAL_TWIN") # SINTETICO_DIGITAL_TWIN, MSHA_MINING, UCI_SUPPLY_CHAIN
    descripcion = Column(Text, nullable=True)
    total_filas = Column(Integer, default=10000)
    total_columnas = Column(Integer, default=20)
    columnas_json = Column(Text, nullable=True)
    path_archivo = Column(String(255), nullable=True)
    random_seed = Column(Integer, default=42)
    created_at = Column(DateTime, default=datetime.utcnow)

    experimentos = relationship("ExperimentoML", back_populates="dataset")

class ExperimentoML(Base):
    __tablename__ = "experimentos_ml"

    id = Column(Integer, primary_key=True, index=True)
    codigo_experimento = Column(String(100), unique=True, nullable=False, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    target_column = Column(String(100), default="riesgo_stockout")
    target_type = Column(String(50), default="CLASIFICACION") # CLASIFICACION, REGRESION
    random_seed = Column(Integer, default=42)
    cv_splits = Column(Integer, default=5)
    test_size_pct = Column(Float, default=0.20)
    metricas_seleccion = Column(String(50), default="f1_macro")
    mejor_modelo_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    dataset = relationship("DatasetModel", back_populates="experimentos")
    modelos = relationship("ModeloML", back_populates="experimento", cascade="all, delete-orphan")

class ModeloML(Base):
    __tablename__ = "modelos_ml"

    id = Column(Integer, primary_key=True, index=True)
    experimento_id = Column(Integer, ForeignKey("experimentos_ml.id"), nullable=False, index=True)
    nombre_algoritmo = Column(String(100), nullable=False) # Random Forest, XGBoost, Logistic Regression, Hybrid RF+XGB, Hybrid LR+RF
    tipo_arquitectura = Column(String(50), default="BASICO") # BASICO, HIBRIDO_ENSEMBLE, HIBRIDO_STACKING
    
    # Métricas en Test Set
    accuracy = Column(Float, default=0.0)
    precision = Column(Float, default=0.0)
    recall_clase_critica = Column(Float, default=0.0) # Recall clase 1 (Alto Riesgo)
    f1_score = Column(Float, default=0.0)
    f1_macro = Column(Float, default=0.0)
    roc_auc = Column(Float, default=0.0)
    pr_auc = Column(Float, default=0.0)
    
    # Métricas agregadas de CV
    cv_f1_macro_mean = Column(Float, default=0.0)
    cv_f1_macro_std = Column(Float, default=0.0)
    cv_f1_macro_ic95_inf = Column(Float, default=0.0)
    cv_f1_macro_ic95_sup = Column(Float, default=0.0)
    
    tiempo_entrenamiento_segundos = Column(Float, default=0.0)
    es_mejor_modelo = Column(Integer, default=0) # 1 si fue seleccionado como mejor
    path_modelo_serializado = Column(String(255), nullable=True)
    metricas_completas_json = Column(Text, nullable=True)
    feature_importance_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    experimento = relationship("ExperimentoML", back_populates="modelos")
    hiperparametros = relationship("HiperparametroML", back_populates="modelo", cascade="all, delete-orphan")
    resultados_cv = relationship("ResultadoCV", back_populates="modelo", cascade="all, delete-orphan")

class HiperparametroML(Base):
    __tablename__ = "hiperparametros_ml"

    id = Column(Integer, primary_key=True, index=True)
    modelo_id = Column(Integer, ForeignKey("modelos_ml.id"), nullable=False, index=True)
    parametro = Column(String(100), nullable=False)
    valor = Column(String(255), nullable=False)

    modelo = relationship("ModeloML", back_populates="hiperparametros")

class ResultadoCV(Base):
    __tablename__ = "resultados_cv"

    id = Column(Integer, primary_key=True, index=True)
    modelo_id = Column(Integer, ForeignKey("modelos_ml.id"), nullable=False, index=True)
    fold_numero = Column(Integer, nullable=False) # 1, 2, 3, 4, 5
    accuracy = Column(Float, nullable=False)
    precision = Column(Float, nullable=False)
    recall = Column(Float, nullable=False)
    f1_score = Column(Float, nullable=False)
    f1_macro = Column(Float, nullable=False)
    roc_auc = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    modelo = relationship("ModeloML", back_populates="resultados_cv")
