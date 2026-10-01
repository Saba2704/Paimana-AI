"""
PAIMANA-AI Backend Server
FastAPI application exposing REST endpoints for predictive analytics,
early warnings, benchmarking, scenario simulations, and AI copilot.
"""

from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import pandas as pd

from paimana_ai.data.generator import generate_calibrated_projects
from paimana_ai.data.preprocessor import engineer_derived_features, prepare_datasets, CUF_NUMERIC_FEATURES, CUF_BOOLEAN_FEATURES
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


# Global state containers
PORTFOLIO_DF: pd.DataFrame = None
COST_MODEL: CostOverrunPredictor = None
TIME_MODEL: TimeOverrunPredictor = None
BENCHMARK_RESULTS: Dict[str, Any] = {}
CUF_STUDY_RESULTS: Dict[str, Any] = {}
EXPLAINER: DriverAnalysisExplainer = None
BENCHMARK_ENGINE: BenchmarkingEngine = None
COPILOT: ProjectIntelligenceCopilot = None
FEATURE_NAMES: List[str] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Generate dataset and train models
    global PORTFOLIO_DF, COST_MODEL, TIME_MODEL, BENCHMARK_RESULTS, CUF_STUDY_RESULTS, EXPLAINER, BENCHMARK_ENGINE, COPILOT, FEATURE_NAMES

    print("[PAIMANA-AI] Initializing calibrated portfolio (1,981 projects)...")
    df_raw = generate_calibrated_projects(n_projects=1981, random_seed=42)

    # Compute risk scores and RAG status for all projects
    print("[PAIMANA-AI] Computing Composite Risk Index (CRI) for all projects...")
    cris = []
    rags = []
    for _, row in df_raw.iterrows():
        p_dict = row.to_dict()
        res = ProjectRiskScorer.calculate_cri(p_dict)
        cris.append(res["composite_risk_index"])
        rags.append(res["rag_status"])
    df_raw["composite_risk_index"] = cris
    df_raw["rag_status"] = rags

    PORTFOLIO_DF = df_raw

    # Prepare datasets
    print("[PAIMANA-AI] Training predictive models and running scientific benchmarks...")
    X_train_cuf, X_test_cuf, y_train_cost, y_test_cost, cuf_cols = prepare_datasets(
        df_raw, target_type="cost_regression", include_augmented=False
    )
    X_train_enh, X_test_enh, _, _, enh_cols = prepare_datasets(
        df_raw, target_type="cost_regression", include_augmented=True
    )
    _, _, y_train_time, y_test_time, _ = prepare_datasets(
        df_raw, target_type="time_regression", include_augmented=True
    )
    _, _, y_train_risk, y_test_risk, _ = prepare_datasets(
        df_raw, target_type="cost_classification", include_augmented=True
    )

    FEATURE_NAMES = enh_cols

    # Train Cost Predictor
    COST_MODEL = CostOverrunPredictor()
    COST_MODEL.fit(X_train_enh, y_train_cost, y_train_risk, FEATURE_NAMES)
    COST_MODEL.evaluate(X_test_enh, y_test_cost, y_test_risk)

    # Train Time Predictor
    _, _, y_train_time_clf, y_test_time_clf, _ = prepare_datasets(
        df_raw, target_type="time_classification", include_augmented=True
    )
    TIME_MODEL = TimeOverrunPredictor()
    TIME_MODEL.fit(X_train_enh, y_train_time, y_train_time_clf, FEATURE_NAMES)
    TIME_MODEL.evaluate(X_test_enh, y_test_time, y_test_time_clf)

    # Run Statistical vs AI/ML Benchmarks (Dimension b)
    benchmarker = StatisticalVsAIBenchmarker()
    BENCHMARK_RESULTS = benchmarker.run_benchmark(
        X_train_enh, X_test_enh,
        y_train_cost, y_test_cost,
        y_train_time, y_test_time,
        y_train_risk, y_test_risk
    )

    # Run CUF Attribution Study (Dimension c)
    cuf_study = CUFAttributionStudy()
    CUF_STUDY_RESULTS = cuf_study.run_study(
        X_train_cuf, X_test_cuf,
        X_train_enh, X_test_enh,
        y_train_cost, y_test_cost,
        y_train_risk, y_test_risk
    )

    # Initialize Explainer, Benchmarks, and Copilot
    EXPLAINER = DriverAnalysisExplainer(FEATURE_NAMES)
    BENCHMARK_ENGINE = BenchmarkingEngine(PORTFOLIO_DF)
    COPILOT = ProjectIntelligenceCopilot(PORTFOLIO_DF)

    print("[PAIMANA-AI] Initialization complete! Platform ready.")
    yield


app = FastAPI(
    title="PAIMANA-AI: Predictive Project Monitoring Platform",
    description="AI-Powered Predictive Analytics, Early Warning & Decision Support for MoSPI Central Sector Infrastructure Projects",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def get_root():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "PAIMANA-AI API is running. Visit /docs for OpenAPI swagger."}


# -------------------------------------------------------------------------
# API Endpoints
# -------------------------------------------------------------------------

@app.get("/api/kpis")
def get_portfolio_kpis():
    """Returns high-level macroeconomic indicators for the 1,981 project portfolio."""
    total_projects = len(PORTFOLIO_DF)
    orig_total = float(PORTFOLIO_DF["original_cost_cr"].sum())
    rev_total = float(PORTFOLIO_DF["revised_cost_cr"].sum())
    exp_total = float(PORTFOLIO_DF["cumulative_exp_cr"].sum())
    total_overrun_cr = rev_total - orig_total
    avg_overrun_pct = float(PORTFOLIO_DF["cost_overrun_pct"].mean())

    delayed_projects = int((PORTFOLIO_DF["months_delayed"] > 0).sum())
    avg_delay_months = float(PORTFOLIO_DF["months_delayed"].mean())

    rag_counts = PORTFOLIO_DF["rag_status"].value_counts().to_dict()

    return {
        "total_monitored_projects": total_projects,
        "aggregate_original_cost_lakh_cr": round(orig_total / 100000.0, 2),
        "aggregate_revised_cost_lakh_cr": round(rev_total / 100000.0, 2),
        "cumulative_expenditure_lakh_cr": round(exp_total / 100000.0, 2),
        "aggregate_cost_escalation_cr": round(total_overrun_cr, 2),
        "portfolio_avg_cost_overrun_pct": round(avg_overrun_pct, 2),
        "delayed_projects_count": delayed_projects,
        "delayed_projects_ratio_pct": round((delayed_projects / total_projects) * 100, 1),
        "portfolio_avg_delay_months": round(avg_delay_months, 1),
        "rag_breakdown": {
            "RED": rag_counts.get("RED", 0),
            "AMBER": rag_counts.get("AMBER", 0),
            "GREEN": rag_counts.get("GREEN", 0)
        }
    }


@app.get("/api/projects")
def list_projects(
    search: Optional[str] = None,
    ministry: Optional[str] = None,
    sector: Optional[str] = None,
    rag_status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100)
):
    """Filterable, searchable, and paginated project registry."""
    df_filtered = PORTFOLIO_DF.copy()

    if search:
        s = search.lower()
        df_filtered = df_filtered[
            df_filtered["project_name"].str.lower().str.contains(s) |
            df_filtered["project_id"].str.lower().str.contains(s) |
            df_filtered["implementing_agency"].str.lower().str.contains(s)
        ]

    if ministry and ministry != "All":
        df_filtered = df_filtered[df_filtered["ministry"] == ministry]

    if sector and sector != "All":
        df_filtered = df_filtered[df_filtered["sector"] == sector]

    if rag_status and rag_status != "All":
        df_filtered = df_filtered[df_filtered["rag_status"] == rag_status]

    total_records = len(df_filtered)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    sliced = df_filtered.iloc[start_idx:end_idx].to_dict(orient="records")

    return {
        "total_records": total_records,
        "page": page,
        "page_size": page_size,
        "total_pages": (total_records + page_size - 1) // page_size,
        "projects": sliced
    }


@app.get("/api/projects/{project_id}")
def get_project_detail(project_id: str):
    """Deep-dive profile of a project with SHAP drivers, CRI, and alerts."""
    match = PORTFOLIO_DF[PORTFOLIO_DF["project_id"] == project_id]
    if match.empty:
        raise HTTPException(status_code=404, detail="Project not found")

    p = match.iloc[0].to_dict()

    # Risk Scoring
    cri_detail = ProjectRiskScorer.calculate_cri(p)
    # Early Warning Alerts
    alerts = EarlyWarningSystem.inspect_project_alerts(p)
    # Explainable Drivers
    drivers = EXPLAINER.explain_project_drivers(p)
    # Peer Cohort
    peers = BENCHMARK_ENGINE.find_peer_cohort(project_id, top_k=4)

    return {
        "project": p,
        "risk_profile": cri_detail,
        "early_warning_alerts": alerts,
        "driver_analysis": drivers,
        "peer_cohort": peers
    }


class CustomPredictionRequest(BaseModel):
    original_cost_cr: float
    physical_progress_pct: float
    financial_progress_pct: float
    total_milestones: int
    achieved_milestones: int
    delayed_milestones: int
    delay_land_acq: bool = False
    delay_forest_clearance: bool = False
    delay_utility_shift: bool = False
    delay_contractor: bool = False
    delay_law_order: bool = False
    delay_geo_technical: bool = False
    contractor_track_record_score: float = 70.0
    terrain_difficulty_index: int = 2
    commodity_inflation_exposure: float = 1.0
    monsoon_vulnerability_score: float = 0.5
    inter_agency_coordination_nodes: int = 3
    original_doc: str = "2027-06"


@app.post("/api/predict")
def predict_custom_project(req: CustomPredictionRequest):
    """On-the-fly model inference for custom project parameters."""
    req_dict = req.dict()
    # Compute derived features
    fin = req_dict["financial_progress_pct"]
    phy = max(1.0, req_dict["physical_progress_pct"])
    req_dict["burn_divergence_ratio"] = round(fin / phy, 3)
    req_dict["milestone_slippage_ratio"] = round(req_dict["delayed_milestones"] / max(1, req_dict["total_milestones"]), 3)
    req_dict["total_bottlenecks"] = sum([
        req_dict["delay_land_acq"], req_dict["delay_forest_clearance"], req_dict["delay_utility_shift"],
        req_dict["delay_contractor"], req_dict["delay_law_order"], req_dict["delay_geo_technical"]
    ])

    cost_res = COST_MODEL.predict_single(req_dict, req_dict["original_cost_cr"])
    time_res = TIME_MODEL.predict_single(req_dict, req_dict["original_doc"])
    
    # Calculate CRI
    req_dict["cost_overrun_pct"] = cost_res["predicted_cost_overrun_pct"]
    req_dict["months_delayed"] = time_res["predicted_months_delayed"]
    cri_res = ProjectRiskScorer.calculate_cri(req_dict)

    return {
        "cost_prediction": cost_res,
        "time_prediction": time_res,
        "risk_evaluation": cri_res
    }


class SimulationRequest(BaseModel):
    project_id: str
    clearance_delay_months: int = 0
    commodity_inflation_shock_pct: float = 0.0
    contractor_efficiency_change_pct: float = 0.0
    fast_track_clearances: bool = False


@app.post("/api/simulate")
def simulate_scenario(req: SimulationRequest):
    """Runs What-If scenario simulation on an existing project."""
    match = PORTFOLIO_DF[PORTFOLIO_DF["project_id"] == req.project_id]
    if match.empty:
        raise HTTPException(status_code=404, detail="Project not found")

    p = match.iloc[0].to_dict()
    sim_result = ScenarioSimulator.simulate_intervention(
        baseline_project=p,
        clearance_delay_months=req.clearance_delay_months,
        commodity_inflation_shock_pct=req.commodity_inflation_shock_pct,
        contractor_efficiency_change_pct=req.contractor_efficiency_change_pct,
        fast_track_clearances=req.fast_track_clearances
    )
    return sim_result


@app.get("/api/benchmarks/sectors")
def get_sector_benchmarks():
    return BENCHMARK_ENGINE.get_sector_benchmarks()


@app.get("/api/benchmarks/ministries")
def get_ministry_rankings():
    return BENCHMARK_ENGINE.get_ministry_rankings()


@app.get("/api/benchmarks/ai-vs-stats")
def get_ai_vs_stats_benchmarks():
    """Directly answers Dimension (b): Classical Statistics vs Modern AI/ML."""
    return BENCHMARK_RESULTS


@app.get("/api/cuf-evaluation")
def get_cuf_attribution_study():
    """Directly answers Dimension (c): CUF vs Augmented Feature Uplift."""
    return CUF_STUDY_RESULTS


@app.get("/api/alerts")
def get_all_active_alerts(severity: Optional[str] = None):
    """Fulfills Outcome (d): Real-time portfolio early warning alerts."""
    all_alerts = []
    for _, row in PORTFOLIO_DF.iterrows():
        p = row.to_dict()
        alerts = EarlyWarningSystem.inspect_project_alerts(p)
        for a in alerts:
            a["project_id"] = p["project_id"]
            a["project_name"] = p["project_name"]
            a["sector"] = p["sector"]
            a["ministry"] = p["ministry"]
            if severity is None or a["severity"] == severity.upper():
                all_alerts.append(a)

    return {
        "total_active_alerts": len(all_alerts),
        "critical_count": sum(1 for a in all_alerts if a["severity"] == "CRITICAL"),
        "high_count": sum(1 for a in all_alerts if a["severity"] == "HIGH"),
        "alerts": all_alerts[:50]  # top 50
    }


class CopilotChatRequest(BaseModel):
    query: str
    project_id: Optional[str] = None


@app.post("/api/copilot/chat")
def copilot_chat(req: CopilotChatRequest):
    """Fulfills Outcome (h): LLM Project Intelligence Assistant."""
    if req.project_id:
        return COPILOT.generate_executive_brief(req.project_id)
    return COPILOT.answer_query(req.query)
