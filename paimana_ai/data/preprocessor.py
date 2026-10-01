"""
PAIMANA Data Preprocessor & Feature Engineering Pipeline
Handles feature derivations, CUF vs Non-CUF partitioning, and train/test preparation.
"""

from typing import Tuple, List, Dict, Any
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer


# Feature groups for CUF vs Non-CUF attribution analysis
CUF_NUMERIC_FEATURES = [
    "original_cost_cr",
    "physical_progress_pct",
    "financial_progress_pct",
    "total_milestones",
    "achieved_milestones",
    "delayed_milestones",
]

CUF_BOOLEAN_FEATURES = [
    "delay_land_acq",
    "delay_forest_clearance",
    "delay_utility_shift",
    "delay_contractor",
    "delay_law_order",
    "delay_geo_technical",
]

CUF_CATEGORICAL_FEATURES = [
    "sector",
    "ministry",
    "state",
]

# Augmented variables (Dimension c evaluation)
AUGMENTED_FEATURES = [
    "contractor_track_record_score",
    "terrain_difficulty_index",
    "commodity_inflation_exposure",
    "monsoon_vulnerability_score",
    "inter_agency_coordination_nodes",
]


def engineer_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes high-signal ratios and operational velocity metrics.
    """
    df = df.copy()

    # Financial to Physical Progress Divergence (Burn rate distortion)
    # A ratio > 1.2 indicates financial spending is sprinting ahead of ground reality
    df["burn_divergence_ratio"] = (
        df["financial_progress_pct"] / df["physical_progress_pct"].clip(lower=1.0)
    ).round(3)

    # Milestone slippage velocity
    df["milestone_slippage_ratio"] = (
        df["delayed_milestones"] / df["total_milestones"].clip(lower=1)
    ).round(3)

    # Total statutory/contractual bottleneck friction count
    bottleneck_cols = [
        "delay_land_acq", "delay_forest_clearance", "delay_utility_shift",
        "delay_contractor", "delay_law_order", "delay_geo_technical"
    ]
    df["total_bottlenecks"] = df[bottleneck_cols].sum(axis=1)

    # Unspent sanctioned allocation
    df["unspent_budget_cr"] = (df["revised_cost_cr"] - df["cumulative_exp_cr"]).clip(lower=0.0).round(2)

    # Classification targets
    df["is_cost_overrun_20pct"] = (df["cost_overrun_pct"] >= 20.0).astype(int)
    df["is_delay_12months"] = (df["months_delayed"] >= 12).astype(int)

    return df


def prepare_datasets(
    df: pd.DataFrame,
    target_type: str = "cost_regression",
    include_augmented: bool = True,
    test_size: float = 0.2,
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, List[str]]:
    """
    Prepares training and testing feature matrices.
    target_type:
      - 'cost_regression': target is cost_overrun_pct
      - 'time_regression': target is months_delayed
      - 'cost_classification': target is is_cost_overrun_20pct
      - 'time_classification': target is is_delay_12months
    """
    df_feat = engineer_derived_features(df)

    feature_cols = CUF_NUMERIC_FEATURES + CUF_BOOLEAN_FEATURES + ["burn_divergence_ratio", "milestone_slippage_ratio", "total_bottlenecks"]
    
    if include_augmented:
        feature_cols = feature_cols + AUGMENTED_FEATURES

    X = df_feat[feature_cols].copy()

    # Convert booleans to int
    for col in CUF_BOOLEAN_FEATURES:
        X[col] = X[col].astype(int)

    if target_type == "cost_regression":
        y = df_feat["cost_overrun_pct"]
    elif target_type == "time_regression":
        y = df_feat["months_delayed"]
    elif target_type == "cost_classification":
        y = df_feat["is_cost_overrun_20pct"]
    elif target_type == "time_classification":
        y = df_feat["is_delay_12months"]
    else:
        raise ValueError(f"Unknown target_type: {target_type}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    return X_train, X_test, y_train, y_test, feature_cols
