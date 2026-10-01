"""
CUF Attribution & Gap Analysis Module
Directly addresses Technical Dimension (c):
Empirically quantifies the predictive performance attributable to existing CUF
fields vs. augmented non-CUF variables (contractor rating, terrain difficulty,
macro inflation exposure, inter-agency coordination nodes).
"""

from typing import Dict, Any, List
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, HistGradientBoostingClassifier
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error, roc_auc_score


class CUFAttributionStudy:
    """
    Evaluates model performance under two data regimes:
      1. Regime A: CUF-Only (Standard MoSPI Common Upload Form fields)
      2. Regime B: Enhanced CUF (CUF + Augmented Macro/Contractor variables)
    """

    def __init__(self):
        self.cuf_model_reg = HistGradientBoostingRegressor(max_iter=150, learning_rate=0.08, max_depth=6, random_state=42)
        self.cuf_model_clf = HistGradientBoostingClassifier(max_iter=150, learning_rate=0.08, max_depth=6, random_state=42)
        self.enhanced_model_reg = HistGradientBoostingRegressor(max_iter=150, learning_rate=0.08, max_depth=6, random_state=42)
        self.enhanced_model_clf = HistGradientBoostingClassifier(max_iter=150, learning_rate=0.08, max_depth=6, random_state=42)
        self.study_results = {}

    def run_study(
        self,
        X_train_cuf: pd.DataFrame,
        X_test_cuf: pd.DataFrame,
        X_train_enh: pd.DataFrame,
        X_test_enh: pd.DataFrame,
        y_train_cost: pd.Series,
        y_test_cost: pd.Series,
        y_train_risk: pd.Series,
        y_test_risk: pd.Series
    ) -> Dict[str, Any]:
        """
        Trains and compares CUF-only vs Enhanced-CUF regimes.
        """
        # Regime A: Standard CUF
        self.cuf_model_reg.fit(X_train_cuf, y_train_cost)
        self.cuf_model_clf.fit(X_train_cuf, y_train_risk)

        preds_cuf_reg = self.cuf_model_reg.predict(X_test_cuf)
        probs_cuf_clf = self.cuf_model_clf.predict_proba(X_test_cuf)[:, 1]

        r2_cuf = float(r2_score(y_test_cost, preds_cuf_reg))
        rmse_cuf = float(np.sqrt(mean_squared_error(y_test_cost, preds_cuf_reg)))
        auc_cuf = float(roc_auc_score(y_test_risk, probs_cuf_clf))

        # Regime B: Enhanced CUF
        self.enhanced_model_reg.fit(X_train_enh, y_train_cost)
        self.enhanced_model_clf.fit(X_train_enh, y_train_risk)

        preds_enh_reg = self.enhanced_model_reg.predict(X_test_enh)
        probs_enh_clf = self.enhanced_model_clf.predict_proba(X_test_enh)[:, 1]

        r2_enh = float(r2_score(y_test_cost, preds_enh_reg))
        rmse_enh = float(np.sqrt(mean_squared_error(y_test_cost, preds_enh_reg)))
        auc_enh = float(roc_auc_score(y_test_risk, probs_enh_clf))

        # Deltas
        delta_r2 = round(r2_enh - r2_cuf, 4)
        delta_rmse = round(rmse_cuf - rmse_enh, 2)  # reduction in error
        delta_auc = round(auc_enh - auc_cuf, 4)
        pct_variance_explained_gain = round((delta_r2 / max(0.01, r2_cuf)) * 100, 1)

        # Attribution breakdown (% contribution to total explainable variance)
        cuf_contribution_pct = round((r2_cuf / max(0.01, r2_enh)) * 100, 1)
        augmented_contribution_pct = round(100.0 - cuf_contribution_pct, 1)

        # Strategic recommendations for MoSPI CUF schema expansion
        recommendations = [
            {
                "field_name": "contractor_track_record_score",
                "recommended_schema_type": "Float (0.0 to 100.0)",
                "impact_rank": 1,
                "justification": "Contractor past delivery rate accounts for significant schedule slippages and claim litigations."
            },
            {
                "field_name": "terrain_difficulty_index",
                "recommended_schema_type": "Enum (Plain, Rolling, Hilly, Mountainous)",
                "impact_rank": 2,
                "justification": "Tunnels, steep gradients, and coastal marshland drive unforeseen geological variations."
            },
            {
                "field_name": "commodity_price_escalation_index",
                "recommended_schema_type": "Float (WPI Price Adjustment Factor)",
                "impact_rank": 3,
                "justification": "Steel, cement and bitumen escalation clauses directly inflate revised cost sanction requests."
            },
            {
                "field_name": "inter_agency_coordination_nodes",
                "recommended_schema_type": "Integer Count",
                "impact_rank": 4,
                "justification": "Captures multi-departmental friction across State Revenue, NHAI, Railways, and Forest depts."
            }
        ]

        self.study_results = {
            "regime_comparison": {
                "cuf_only": {
                    "r2_score": round(r2_cuf, 4),
                    "rmse_pct": round(rmse_cuf, 2),
                    "roc_auc": round(auc_cuf, 4),
                    "features_count": X_train_cuf.shape[1]
                },
                "enhanced_cuf": {
                    "r2_score": round(r2_enh, 4),
                    "rmse_pct": round(rmse_enh, 2),
                    "roc_auc": round(auc_enh, 4),
                    "features_count": X_train_enh.shape[1]
                },
                "uplift": {
                    "delta_r2": delta_r2,
                    "delta_rmse_reduction": delta_rmse,
                    "delta_roc_auc": delta_auc,
                    "r2_gain_percentage": pct_variance_explained_gain
                }
            },
            "attribution_share": {
                "cuf_fields_share_pct": cuf_contribution_pct,
                "augmented_external_share_pct": augmented_contribution_pct
            },
            "mospi_policy_recommendations": recommendations
        }
        return self.study_results
