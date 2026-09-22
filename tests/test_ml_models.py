"""
Unit and integration tests for ML pipeline, 5 models, and 5-fold CV.
"""
import pytest
import numpy as np
from data.synthetic.generator import generate_mining_dataset
from ml.models.models_suite import get_model_instances
from ml.feature_engineering.pipeline import MiningFeaturePipeline
from ml.training.trainer import ModelTrainer

def test_feature_engineering_pipeline():
    df = generate_mining_dataset(n_samples=200, random_state=42)
    X_train, X_test, y_train, y_test, scaler, features = MiningFeaturePipeline.prepare_train_test(df)
    
    assert X_train.shape[1] == len(features)
    assert len(y_train) + len(y_test) == 200
    assert not np.isnan(X_train).any()

def test_train_all_5_models():
    df = generate_mining_dataset(n_samples=300, random_state=42)
    res = ModelTrainer.train_and_evaluate_all(df, random_state=42)

    assert len(res["trained_models"]) == 5
    assert len(res["comparison_df"]) == 5
    assert res["best_model_name"] in res["trained_models"]
    assert "F1-Macro" in res["comparison_df"].columns
