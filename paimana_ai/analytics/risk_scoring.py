"""
Project Risk Scoring Framework: Composite Risk Index (CRI)
Fulfills Outcome (c):
Calculates a multi-dimensional risk score (0-100) combining financial velocity,
milestone integrity, statutory clearance friction, and agency execution metrics.
"""

from typing import Dict, Any
import numpy as np


class ProjectRiskScorer:
    """
    Computes normalized sub-indices and overall Composite Risk Index (CRI).
    """

    @staticmethod
    def calculate_cri(project: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates CRI (0-100) and RAG status.
        Formula:
          CRI = (0.30 * Financial_Risk) +
                (0.25 * Milestone_Velocity_Risk) +
                (0.25 * Bottleneck_Severity_Risk) +
                (0.20 * Execution_Capacity_Risk)
        """
        # 1. Financial Risk (0 - 100)
        # Ratio of financial progress to physical progress
        fin_pct = float(project.get("financial_progress_pct", 0.0))
        phy_pct = max(1.0, float(project.get("physical_progress_pct", 1.0)))
        burn_ratio = fin_pct / phy_pct
        
        cost_overrun_pct = float(project.get("cost_overrun_pct", 0.0))
        # High overrun or high burn disparity escalates financial risk
        fin_risk = min(100.0, (burn_ratio - 1.0) * 45.0 + (cost_overrun_pct * 1.5))
        fin_risk = max(0.0, fin_risk)

        # 2. Milestone & Velocity Risk (0 - 100)
        total_ms = max(1, int(project.get("total_milestones", 10)))
        delayed_ms = int(project.get("delayed_milestones", 0))
        slippage_ratio = delayed_ms / total_ms
        months_delayed = float(project.get("months_delayed", 0))
        
        ms_risk = min(100.0, (slippage_ratio * 60.0) + (months_delayed * 1.8))
        ms_risk = max(0.0, ms_risk)

        # 3. Bottleneck Severity Risk (0 - 100)
        bottleneck_score = 0.0
        if project.get("delay_land_acq", False):
            bottleneck_score += 30.0
        if project.get("delay_forest_clearance", False):
            bottleneck_score += 30.0
        if project.get("delay_utility_shift", False):
            bottleneck_score += 15.0
        if project.get("delay_contractor", False):
            bottleneck_score += 15.0
        if project.get("delay_law_order", False):
            bottleneck_score += 10.0
        bottleneck_risk = min(100.0, bottleneck_score)

        # 4. Execution Capacity & Non-CUF Factors (0 - 100)
        contractor_score = float(project.get("contractor_track_record_score", 70.0))
        terrain = int(project.get("terrain_difficulty_index", 2))
        nodes = int(project.get("inter_agency_coordination_nodes", 3))

        exec_risk = ((100.0 - contractor_score) * 0.5) + (terrain * 8.0) + (nodes * 3.5)
        exec_risk = min(100.0, max(0.0, exec_risk))

        # Weighted Composite Score
        composite_score = (
            (0.30 * fin_risk) +
            (0.25 * ms_risk) +
            (0.25 * bottleneck_risk) +
            (0.20 * exec_risk)
        )
        composite_score = round(min(100.0, max(0.0, composite_score)), 1)

        # RAG Status Assignment
        if composite_score >= 70.0:
            rag = "RED"
            status_desc = "Critical Risk - Immediate Cabinet/Secretarial Intervention Mandated"
        elif composite_score >= 40.0:
            rag = "AMBER"
            status_desc = "Moderate Risk - Heightened Inter-Departmental Monitoring"
        else:
            rag = "GREEN"
            status_desc = "Low Risk - Project Proceeding Within Standard Tolerance"

        return {
            "composite_risk_index": composite_score,
            "rag_status": rag,
            "status_description": status_desc,
            "sub_indices": {
                "financial_risk": round(fin_risk, 1),
                "milestone_velocity_risk": round(ms_risk, 1),
                "bottleneck_severity_risk": round(bottleneck_risk, 1),
                "execution_capacity_risk": round(exec_risk, 1),
            }
        }
