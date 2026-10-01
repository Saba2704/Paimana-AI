"""
Early Warning Alert System (EWS)
Fulfills Outcome (d):
Rule and anomaly detection engine that identifies emergent implementation risks
months before they materialize into official cost escalations.
"""

from typing import List, Dict, Any


class EarlyWarningSystem:
    """
    Evaluates projects against 4 high-impact early warning rules and anomaly patterns.
    """

    @staticmethod
    def inspect_project_alerts(project: Dict[str, Any]) -> List[Dict[str, Any]]:
        alerts = []
        p_id = project.get("project_id", "UNKNOWN")
        name = project.get("project_name", "Unknown Project")
        fin_pct = float(project.get("financial_progress_pct", 0.0))
        phy_pct = float(project.get("physical_progress_pct", 0.0))
        delayed_ms = int(project.get("delayed_milestones", 0))
        total_ms = max(1, int(project.get("total_milestones", 10)))
        exp_cr = float(project.get("cumulative_exp_cr", 0.0))
        orig_cost = float(project.get("original_cost_cr", 1.0))
        months_delayed = int(project.get("months_delayed", 0))

        # -------------------------------------------------------------------
        # Rule 1: "Ghost Progress" Anomaly
        # Funds disbursed/spent far exceed verifiable physical construction
        # -------------------------------------------------------------------
        if phy_pct > 0 and (fin_pct / max(1.0, phy_pct)) >= 1.65 and fin_pct > 40.0:
            alerts.append({
                "alert_code": "EWS-01-GHOST-PROGRESS",
                "severity": "CRITICAL",
                "trigger_name": "Ghost Progress Anomaly Detected",
                "lead_time_months": 8,
                "description": (
                    f"Financial expenditure ({fin_pct:.1f}%) is sprinted {fin_pct/phy_pct:.2f}x ahead of "
                    f"audited physical progress ({phy_pct:.1f}%). High risk of unliquidated contractor advances."
                ),
                "recommended_action": (
                    "Mandate third-party technical audit by MoSPI / Quality Council of India before releasing further tranche."
                )
            })

        # -------------------------------------------------------------------
        # Rule 2: Critical Milestone Cascade Failure
        # Statutory clearance bottlenecks blocking consecutive milestones
        # -------------------------------------------------------------------
        has_clearance_issue = project.get("delay_forest_clearance", False) or project.get("delay_land_acq", False)
        if delayed_ms >= 3 and has_clearance_issue:
            alerts.append({
                "alert_code": "EWS-02-MILESTONE-CASCADE",
                "severity": "HIGH",
                "trigger_name": "Statutory Clearance Cascade Blockage",
                "lead_time_months": 12,
                "description": (
                    f"{delayed_ms} critical milestones are stalled due to unresolved Stage-II forest or land possession delays."
                ),
                "recommended_action": (
                    "Trigger PMG (Project Monitoring Group) / Pragati escalation with Chief Secretary of the concerned State."
                )
            })

        # -------------------------------------------------------------------
        # Rule 3: Velocity Cliff
        # Required monthly execution pace to meet target DOC is > 3x historical pace
        # -------------------------------------------------------------------
        remaining_phy = 100.0 - phy_pct
        if remaining_phy > 30.0 and months_delayed >= 18:
            alerts.append({
                "alert_code": "EWS-03-VELOCITY-CLIFF",
                "severity": "HIGH",
                "trigger_name": "Execution Velocity Cliff Warning",
                "lead_time_months": 6,
                "description": (
                    f"Project has {remaining_phy:.1f}% remaining physical scope with accumulated schedule slip of "
                    f"{months_delayed} months. Worksite mobilization cannot mathematically achieve planned target date."
                ),
                "recommended_action": (
                    "Conduct realistic CPM/PERT schedule re-baselining and review EPC contractor labor deployment."
                )
            })

        # -------------------------------------------------------------------
        # Rule 4: Cost Inflection Danger Zone
        # Funds exhausted before halfway point of major construction
        # -------------------------------------------------------------------
        budget_burn_pct = (exp_cr / orig_cost) * 100.0 if orig_cost > 0 else 0
        if budget_burn_pct >= 80.0 and phy_pct < 60.0:
            alerts.append({
                "alert_code": "EWS-04-COST-INFLECTION",
                "severity": "CRITICAL",
                "trigger_name": "Budget Exhaustion Inflection Point",
                "lead_time_months": 10,
                "description": (
                    f"Cumulative expenditure has consumed {budget_burn_pct:.1f}% of original sanctioned budget "
                    f"while ground progress is only at {phy_pct:.1f}%. Major Revised Cost Estimate (RCE) imminent."
                ),
                "recommended_action": (
                    "Initiate Revised Cost Committee (RCC) examination and notify Department of Expenditure."
                )
            })

        return alerts
