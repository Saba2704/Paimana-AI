"""
What-If Scenario Simulation Engine
Allows policymakers and project administrators to test policy interventions
and macroeconomic shocks in real time.
"""

from typing import Dict, Any
from datetime import datetime, timedelta


class ScenarioSimulator:
    @staticmethod
    def simulate_intervention(
        baseline_project: Dict[str, Any],
        clearance_delay_months: int = 0,
        commodity_inflation_shock_pct: float = 0.0,
        contractor_efficiency_change_pct: float = 0.0,
        fast_track_clearances: bool = False
    ) -> Dict[str, Any]:
        """
        Calculates dynamic project impact under simulated variables.
        """
        orig_cost = float(baseline_project.get("original_cost_cr", 1000.0))
        cur_cost_overrun_pct = float(baseline_project.get("cost_overrun_pct", 10.0))
        cur_delay_months = int(baseline_project.get("months_delayed", 6))
        orig_doc = baseline_project.get("original_doc", "2026-12")

        # Simulate schedule changes
        sim_delay_months = cur_delay_months + clearance_delay_months

        # If fast-tracked or contractor boosted
        if fast_track_clearances:
            sim_delay_months = max(0, sim_delay_months - 6)

        contractor_factor = 1.0 - (contractor_efficiency_change_pct / 100.0) * 0.4
        sim_delay_months = max(0, int(round(sim_delay_months * contractor_factor)))

        # Simulate cost escalation
        # Schedule delay contributes ~0.25% cost escalation per month
        delay_cost_escalation = (sim_delay_months - cur_delay_months) * 0.35
        # Commodity shock applies to remaining physical work
        phy_pct = float(baseline_project.get("physical_progress_pct", 50.0))
        remaining_work_ratio = max(0.1, (100.0 - phy_pct) / 100.0)
        macro_inflation_cost_pct = (commodity_inflation_shock_pct * 0.45) * remaining_work_ratio

        sim_overrun_pct = max(0.0, round(cur_cost_overrun_pct + delay_cost_escalation + macro_inflation_cost_pct, 2))
        sim_revised_cost_cr = round(orig_cost * (1.0 + (sim_overrun_pct / 100.0)), 2)
        capex_delta_cr = round(sim_revised_cost_cr - float(baseline_project.get("revised_cost_cr", orig_cost)), 2)

        # Projected Commissioning Date
        try:
            dt = datetime.strptime(orig_doc, "%Y-%m")
            sim_dt = dt + timedelta(days=sim_delay_months * 30)
            sim_doc = sim_dt.strftime("%Y-%m")
        except Exception:
            sim_doc = "N/A"

        # Re-evaluate simulated CRI
        sim_cri = min(100.0, max(10.0, (sim_overrun_pct * 1.2) + (sim_delay_months * 1.1) + 20.0))
        sim_rag = "RED" if sim_cri >= 70 else ("AMBER" if sim_cri >= 40 else "GREEN")

        return {
            "project_id": baseline_project.get("project_id"),
            "baseline": {
                "revised_cost_cr": float(baseline_project.get("revised_cost_cr", orig_cost)),
                "cost_overrun_pct": cur_cost_overrun_pct,
                "months_delayed": cur_delay_months,
                "rag_status": baseline_project.get("rag_status", "AMBER")
            },
            "simulated": {
                "simulated_revised_cost_cr": sim_revised_cost_cr,
                "simulated_cost_overrun_pct": sim_overrun_pct,
                "simulated_delay_months": sim_delay_months,
                "simulated_completion_date": sim_doc,
                "simulated_cri_score": round(sim_cri, 1),
                "simulated_rag_status": sim_rag,
                "net_capex_impact_cr": capex_delta_cr,
                "schedule_shift_months": sim_delay_months - cur_delay_months
            },
            "policy_implication": (
                f"{'Avoided' if capex_delta_cr < 0 else 'Added'} Capex impact of ₹{abs(capex_delta_cr):,.2f} Cr "
                f"with a net schedule shift of {sim_delay_months - cur_delay_months:+d} months."
            )
        }
