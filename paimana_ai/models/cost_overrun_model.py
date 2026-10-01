"""
Cost Overrun Prediction Engine
Provides dual capabilities:
  1. Regression: Forecasts exact cost escalation percentage and anticipated revised cost.
  2. Classification: Predicts probability of severe cost overrun (>20%).
"""

from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, HistGradientBoostingClassifier, RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, roc_auc_score, accuracy_score
import joblib


class CostOverrunPredictor:
    def __init__(self):
        self.regressor = HistGradientBoostingRegressor(
            max_iter=150, learning_rate=0.08, max_depth=6, random_state=42
        )
        self.classifier = HistGradientBoostingClassifier(
            max_iter=150, learning_rate=0.08, max_depth=6, random_state=42
        )
        self.feature_names = []
        self.metrics = {}

    def fit(self, X_train: pd.DataFrame, y_train_reg: pd.Series, y_train_clf: pd.Series, feature_names: list):
        self.feature_names = feature_names
        self.regressor.fit(X_train, y_train_reg)
        self.classifier.fit(X_train, y_train_clf)

    def evaluate(self, X_test: pd.DataFrame, y_test_reg: pd.Series, y_test_clf: pd.Series) -> Dict[str, float]:
        reg_preds = self.regressor.predict(X_test)
        clf_probs = self.classifier.predict_proba(X_test)[:, 1]
        clf_preds = (clf_probs >= 0.5).astype(int)

        rmse = float(np.sqrt(mean_squared_error(y_test_reg, reg_preds)))
        mae = float(mean_absolute_error(y_test_reg, reg_preds))
        r2 = float(r2_score(y_test_reg, reg_preds))
        roc_auc = float(roc_auc_score(y_test_clf, clf_probs))
        acc = float(accuracy_score(y_test_clf, clf_preds))

        self.metrics = {
            "reg_rmse": round(rmse, 3),
            "reg_mae": round(mae, 3),
            "reg_r2": round(r2, 4),
            "clf_roc_auc": round(roc_auc, 4),
            "clf_accuracy": round(acc, 4),
        }
        return self.metrics

    def predict_single(self, input_features: Dict[str, Any], original_cost_cr: float) -> Dict[str, Any]:
        """
        Runs inference on a single project feature dictionary.
        """
        row = [input_features.get(f, 0.0) for f in self.feature_names]
        X = np.array([row])

        pred_overrun_pct = max(0.0, float(self.regressor.predict(X)[0]))
        prob_severe = float(self.classifier.predict_proba(X)[0, 1])

        escalation_amount_cr = round(original_cost_cr * (pred_overrun_pct / 100.0), 2)
        projected_final_cost_cr = round(original_cost_cr + escalation_amount_cr, 2)

        return {
            "predicted_cost_overrun_pct": round(pred_overrun_pct, 2),
            "predicted_escalation_amount_cr": escalation_amount_cr,
            "projected_final_cost_cr": projected_final_cost_cr,
            "severe_overrun_risk_prob": round(prob_severe, 3),
            "severe_overrun_flag": prob_severe >= 0.5
        }
