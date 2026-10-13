"""
Module: factory.py
Phase 13: Factory for the 5 mandated classification algorithms:
1. LogisticRegression
2. RandomForestClassifier
3. XGBClassifier
4. LGBMClassifier
5. SVC (Support Vector Machine)
"""

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.svm import SVC
from src.preprocessing.pipeline_builder import create_model_pipeline

def get_models(numeric_features, categorical_features, random_state=42):
    """
    Returns a dictionary of the 5 candidate pipelines with consistent random_state=42.
    """
    models = {}
    
    # 1. Logistic Regression (Requires scaling)
    lr = LogisticRegression(
        max_iter=1000,
        random_state=random_state,
        class_weight='balanced'
    )
    models['LogisticRegression'] = create_model_pipeline(
        lr, numeric_features, categorical_features, scale_numeric=True
    )
    
    # 2. Random Forest (Tree-based, no scaling required)
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=12,
        random_state=random_state,
        class_weight='balanced',
        n_jobs=-1
    )
    models['RandomForest'] = create_model_pipeline(
        rf, numeric_features, categorical_features, scale_numeric=False
    )
    
    # 3. XGBoost (Gradient Boosting)
    xgb = XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=random_state,
        eval_metric='logloss',
        n_jobs=-1
    )
    models['XGBoost'] = create_model_pipeline(
        xgb, numeric_features, categorical_features, scale_numeric=False
    )
    
    # 4. LightGBM (Gradient Boosting)
    lgbm = LGBMClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=random_state,
        class_weight='balanced',
        verbose=-1,
        n_jobs=-1
    )
    models['LightGBM'] = create_model_pipeline(
        lgbm, numeric_features, categorical_features, scale_numeric=False
    )
    
    # 5. Support Vector Machine (Requires scaling, probability=True for ROC/PR-AUC)
    svm = SVC(
        kernel='rbf',
        C=1.0,
        probability=True,
        random_state=random_state,
        class_weight='balanced'
    )
    models['SVM'] = create_model_pipeline(
        svm, numeric_features, categorical_features, scale_numeric=True
    )
    
    return models
