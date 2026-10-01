"""
PAIMANA-AI Comprehensive Automated Test Suite
Verifies data generation, ML models, benchmarking, risk scoring, early warnings,
copilot, and FastAPI API routes.
"""

import pytest
import pandas as pd
import numpy as np
from fastapi.testclient import TestClient

from paimana_ai.data.generator import generate_calibrated_projects
from paimana_ai.data.preprocessor import engineer_derived_features, prepare_datasets
from paimana_ai.models.cost_overrun_model import CostOverrunPredictor
from paimana_ai.models.time_overrun_model import TimeOverrunPredictor
from paimana_ai.models.benchmark_engine import StatisticalVsAIBenchmarker
from paimana_ai.models.cuf_attribution_study import CUFAttributionStudy
from paimana_ai.models.explainability import DriverAnalysisExplainer
from paimana_ai.analytics.risk_scoring import ProjectRiskScorer
from paimana_ai.analytics.early_warning import EarlyWarningSystem
from paimana_ai.analytics.benchmarking import BenchmarkingEngine
from paimana_ai.analytics.simulator import ScenarioSimulator
from paimana_ai.copilot.copilot import ProjectIntelligenceCopilot
from paimana_ai.server.main import app


# -------------------------------------------------------------------------
# Test 1: Calibrated Data Generation
# -------------------------------------------------------------------------
def test_data_generation_calibration():
    df = generate_calibrated_projects(n_projects=200, random_seed=42)
    assert len(df) == 200
    assert "project_id" in df.columns
    assert "original_cost_cr" in df.columns
    assert "revised_cost_cr" in df.columns
    assert "cumulative_exp_cr" in df.columns
    assert "cost_overrun_pct" in df.columns
    assert "months_delayed" in df.columns
    # Check cost logic
    assert (df["revised_cost_cr"] >= df["original_cost_cr"] * 0.9).all()
    # Check sector diversity
    assert len(df["sector"].unique()) >= 5


# -------------------------------------------------------------------------
# Test 2: Feature Engineering
# -------------------------------------------------------------------------
def test_feature_engineering():
    df = generate_calibrated_projects(n_projects=50, random_seed=42)
    df_feat = engineer_derived_features(df)
    assert "burn_divergence_ratio" in df_feat.columns
    assert "milestone_slippage_ratio" in df_feat.columns
    assert "total_bottlenecks" in df_feat.columns
    assert "unspent_budget_cr" in df_feat.columns
    assert (df_feat["burn_divergence_ratio"] >= 0).all()


# -------------------------------------------------------------------------
# Test 3: Cost and Time Predictive Models
# -------------------------------------------------------------------------
def test_cost_and_time_models():
    df = generate_calibrated_projects(n_projects=100, random_seed=42)
    X_train, X_test, y_train_cost, y_test_cost, feature_cols = prepare_datasets(
        df, target_type="cost_regression", include_augmented=True
    )
    _, _, y_train_risk, y_test_risk, _ = prepare_datasets(
        df, target_type="cost_classification", include_augmented=True
    )

    cost_model = CostOverrunPredictor()
    cost_model.fit(X_train, y_train_cost, y_train_risk, feature_cols)
    metrics = cost_model.evaluate(X_test, y_test_cost, y_test_risk)

    assert "reg_rmse" in metrics
    assert "reg_r2" in metrics
    assert "clf_roc_auc" in metrics

    # Single prediction
    sample_feat = {f: 1.0 for f in feature_cols}
    pred = cost_model.predict_single(sample_feat, original_cost_cr=1000.0)
    assert "predicted_cost_overrun_pct" in pred
    assert "projected_final_cost_cr" in pred
    assert pred["projected_final_cost_cr"] >= 1000.0


# -------------------------------------------------------------------------
# Test 4: Technical Dimension (b) - AI/ML vs Statistical Benchmarks
# -------------------------------------------------------------------------
def test_dimension_b_benchmarker():
    df = generate_calibrated_projects(n_projects=100, random_seed=42)
    X_tr, X_te, y_tr_cost, y_te_cost, _ = prepare_datasets(df, target_type="cost_regression", include_augmented=True)
    _, _, y_tr_time, y_te_time, _ = prepare_datasets(df, target_type="time_regression", include_augmented=True)
    _, _, y_tr_risk, y_te_risk, _ = prepare_datasets(df, target_type="cost_classification", include_augmented=True)

    benchmarker = StatisticalVsAIBenchmarker()
    results = benchmarker.run_benchmark(
        X_tr, X_te, y_tr_cost, y_te_cost, y_tr_time, y_te_time, y_tr_risk, y_te_risk
    )

    assert "cost_benchmarks" in results
    assert "risk_benchmarks" in results
    assert "summary_findings" in results
    assert len(results["cost_benchmarks"]) >= 3


# -------------------------------------------------------------------------
# Test 5: Technical Dimension (c) - CUF Attribution Study
# -------------------------------------------------------------------------
def test_dimension_c_cuf_study():
    df = generate_calibrated_projects(n_projects=100, random_seed=42)
    X_tr_cuf, X_te_cuf, y_tr_cost, y_te_cost, _ = prepare_datasets(df, target_type="cost_regression", include_augmented=False)
    X_tr_enh, X_te_enh, _, _, _ = prepare_datasets(df, target_type="cost_regression", include_augmented=True)
    _, _, y_tr_risk, y_te_risk, _ = prepare_datasets(df, target_type="cost_classification", include_augmented=False)

    study = CUFAttributionStudy()
    res = study.run_study(
        X_tr_cuf, X_te_cuf, X_tr_enh, X_te_enh, y_tr_cost, y_te_cost, y_tr_risk, y_te_risk
    )

    assert "regime_comparison" in res
    assert "uplift" in res["regime_comparison"]
    assert "mospi_policy_recommendations" in res
    assert len(res["mospi_policy_recommendations"]) == 4


# -------------------------------------------------------------------------
# Test 6: Risk Scoring & Early Warning Alerts
# -------------------------------------------------------------------------
def test_risk_scoring_and_early_warning():
    sample_proj = {
        "project_id": "PM-TST-001",
        "project_name": "Test Greenfield Highway",
        "financial_progress_pct": 75.0,
        "physical_progress_pct": 35.0,
        "total_milestones": 12,
        "delayed_milestones": 5,
        "months_delayed": 24,
        "original_cost_cr": 1200.0,
        "cumulative_exp_cr": 950.0,
        "cost_overrun_pct": 30.0,
        "delay_land_acq": True,
        "delay_forest_clearance": True,
        "contractor_track_record_score": 45.0,
        "terrain_difficulty_index": 3,
        "inter_agency_coordination_nodes": 6
    }

    cri = ProjectRiskScorer.calculate_cri(sample_proj)
    assert 0 <= cri["composite_risk_index"] <= 100
    assert cri["rag_status"] in ["RED", "AMBER", "GREEN"]

    alerts = EarlyWarningSystem.inspect_project_alerts(sample_proj)
    assert len(alerts) >= 1
    assert any(a["alert_code"] == "EWS-01-GHOST-PROGRESS" for a in alerts)


# -------------------------------------------------------------------------
# Test 7: Scenario Simulator
# -------------------------------------------------------------------------
def test_scenario_simulator():
    sample_proj = {
        "project_id": "PM-TST-002",
        "original_cost_cr": 2000.0,
        "revised_cost_cr": 2400.0,
        "cost_overrun_pct": 20.0,
        "months_delayed": 12,
        "original_doc": "2026-12",
        "physical_progress_pct": 50.0
    }
    sim = ScenarioSimulator.simulate_intervention(
        baseline_project=sample_proj,
        clearance_delay_months=6,
        commodity_inflation_shock_pct=15.0
    )
    assert sim["simulated"]["simulated_cost_overrun_pct"] > 20.0
    assert sim["simulated"]["simulated_delay_months"] > 12


# -------------------------------------------------------------------------
# Test 8: Project Intelligence Copilot
# -------------------------------------------------------------------------
def test_copilot():
    df = generate_calibrated_projects(n_projects=30, random_seed=42)
    copilot = ProjectIntelligenceCopilot(df)
    p_id = df.iloc[0]["project_id"]

    brief = copilot.generate_executive_brief(p_id)
    assert "executive_brief_markdown" in brief
    assert p_id in brief["executive_brief_markdown"]

    ans = copilot.answer_query("Analyze Railway bottlenecks")
    assert "response" in ans


# -------------------------------------------------------------------------
# Test 9: FastAPI Server Endpoints
# -------------------------------------------------------------------------
def test_fastapi_server_routes():
    with TestClient(app) as client:
        # KPI Endpoint
        res_kpi = client.get("/api/kpis")
        assert res_kpi.status_code == 200
        kpi_data = res_kpi.json()
        assert kpi_data["total_monitored_projects"] == 1981

        # Projects Endpoint
        res_proj = client.get("/api/projects?page=1&page_size=5")
        assert res_proj.status_code == 200
        assert len(res_proj.json()["projects"]) == 5

        # Sector Benchmarks Endpoint
        res_sec = client.get("/api/benchmarks/sectors")
        assert res_sec.status_code == 200
        assert len(res_sec.json()) > 0

        # AI vs Stats Endpoint (Dimension b)
        res_b = client.get("/api/benchmarks/ai-vs-stats")
        assert res_b.status_code == 200
        assert "cost_benchmarks" in res_b.json()

        # CUF Evaluation Endpoint (Dimension c)
        res_c = client.get("/api/cuf-evaluation")
        assert res_c.status_code == 200
        assert "mospi_policy_recommendations" in res_c.json()

        # Alerts Endpoint
        res_alerts = client.get("/api/alerts")
        assert res_alerts.status_code == 200
        assert "alerts" in res_alerts.json()
