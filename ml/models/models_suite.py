"""
Machine Learning Models Suite for Mining Spare Parts Logistics.
Implements exactly 5 models:
- 3 Basic Models:
  1. Random Forest Classifier
  2. XGBoost Classifier
  3. Logistic Regression (L2 regularized)
- 2 Hybrid Models:
  4. Hybrid 1: Random Forest + XGBoost Ensemble (Soft Voting / Stacking)
  5. Hybrid 2: Logistic Regression + Random Forest (Stacking Meta-Learner)
"""
from typing import Dict, Any
from sklearn.ensemble import RandomForestClassifier, VotingClassifier, StackingClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier

def get_model_instances(random_state: int = 42) -> Dict[str, Any]:
    """Instantiates the 5 specified classification models with reproducible seeds."""
    
    # Model 1: Random Forest
    rf = RandomForestClassifier(
        n_estimators=150,
        max_depth=12,
        min_samples_split=4,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=random_state,
        n_jobs=-1
    )

    # Model 2: XGBoost
    xgb = XGBClassifier(
        n_estimators=160,
        max_depth=6,
        learning_rate=0.08,
        subsample=0.85,
        colsample_bytree=0.85,
        scale_pos_weight=1.2,
        random_state=random_state,
        eval_metric="logloss",
        n_jobs=-1
    )

    # Model 3: Logistic Regression
    lr = LogisticRegression(
        C=1.0,
        max_iter=1000,
        class_weight="balanced",
        solver="lbfgs",
        random_state=random_state
    )

    # Model 4 (Hybrid 1): Random Forest + XGBoost Ensemble (Soft Voting)
    hybrid_rf_xgb = VotingClassifier(
        estimators=[
            ("rf", RandomForestClassifier(n_estimators=120, max_depth=10, random_state=random_state, class_weight="balanced")),
            ("xgb", XGBClassifier(n_estimators=120, max_depth=5, learning_rate=0.08, random_state=random_state, eval_metric="logloss"))
        ],
        voting="soft",
        weights=[0.45, 0.55]
    )

    # Model 5 (Hybrid 2): Logistic Regression + Random Forest Stacking Meta-Learner
    hybrid_lr_rf = StackingClassifier(
        estimators=[
            ("lr_base", LogisticRegression(C=0.8, max_iter=800, random_state=random_state)),
            ("rf_base", RandomForestClassifier(n_estimators=100, max_depth=8, random_state=random_state))
        ],
        final_estimator=LogisticRegression(C=1.2, random_state=random_state),
        cv=5,
        passthrough=False
    )

    return {
        "Random Forest": rf,
        "XGBoost": xgb,
        "Logistic Regression": lr,
        "Hybrid RF + XGBoost (Ensemble)": hybrid_rf_xgb,
        "Hybrid LR + RF (Stacking)": hybrid_lr_rf
    }
