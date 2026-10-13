"""
Module: pipeline_builder.py
Phase 12 & 13: Strict Pipeline + ColumnTransformer construction.
Zero data leakage: all learned transformations are strictly enclosed within pipelines.
"""

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

def build_preprocessing_pipeline(numeric_features, categorical_features, scale_numeric=False):
    """
    Constructs a ColumnTransformer with strict encapsulation of imputation and encoding.
    """
    num_steps = [('imputer', SimpleImputer(strategy='median'))]
    if scale_numeric:
        num_steps.append(('scaler', StandardScaler()))
    numeric_transformer = Pipeline(steps=num_steps)
    
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ],
        remainder='drop'
    )
    return preprocessor

def create_model_pipeline(model, numeric_features, categorical_features, scale_numeric=False):
    """
    Creates end-to-end Pipeline combining preprocessor and estimator.
    """
    preprocessor = build_preprocessing_pipeline(
        numeric_features, categorical_features, scale_numeric=scale_numeric
    )
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('model', model)
    ])
    return pipeline
