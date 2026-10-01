"""
Time Overrun Prediction Engine
Provides dual capabilities:
  1. Regression: Forecasts anticipated schedule slippage in months.
  2. Classification: Predicts probability of severe project delay (>12 months).
"""

from typing import Dict, Any, Tuple
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, HistGradientBoostingClassifier
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, roc_auc_score, accuracy_score


class TimeOverrunPredictor:
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
            "time_rmse_months": round(rmse, 2),
            "time_mae_months": round(mae, 2),
            "time_r2": round(r2, 4),
            "clf_roc_auc": round(roc_auc, 4),
            "clf_accuracy": round(acc, 4),
        }
        return self.metrics

    def predict_single(self, input_features: Dict[str, Any], original_doc_str: str) -> Dict[str, Any]:
        """
        Runs inference on a single project feature dictionary.
        """
        row = [input_features.get(f, 0.0) for f in self.feature_names]
        X = np.array([row])

        pred_months_delay = max(0, int(round(self.regressor.predict(X)[0])))
        prob_severe = float(self.classifier.predict_proba(X)[0, 1])

        # Compute projected completion date
        try:
            orig_dt = datetime.strptime(original_doc_str, "%Y-%m")
            proj_dt = orig_dt + timedelta(days=pred_months_delay * 30)
            projected_doc = proj_dt.strftime("%Y-%m")
        except Exception:
            projected_doc = "N/A"

        return {
            "predicted_months_delayed": pred_months_delay,
            "projected_commissioning_date": projected_doc,
            "severe_delay_risk_prob": round(prob_severe, 3),
            "severe_delay_flag": prob_severe >= 0.5
        }
