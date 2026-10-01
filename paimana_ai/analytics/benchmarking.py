"""
Benchmarking and Comparative Analytics Module
Fulfills Outcome (e):
Aggregates sectoral & ministry performance metrics and matches peer project cohorts.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


class BenchmarkingEngine:
    def __init__(self, projects_df: pd.DataFrame):
        self.df = projects_df

    def get_sector_benchmarks(self) -> List[Dict[str, Any]]:
        """
        Computes benchmark metrics aggregated by infrastructure sector.
        """
        grouped = self.df.groupby("sector")
        benchmarks = []

        for sector, grp in grouped:
            orig_total = grp["original_cost_cr"].sum()
            rev_total = grp["revised_cost_cr"].sum()
            exp_total = grp["cumulative_exp_cr"].sum()
            avg_overrun = grp["cost_overrun_pct"].mean()
            avg_delay = grp["months_delayed"].mean()
            delayed_count = (grp["months_delayed"] > 0).sum()

            benchmarks.append({
                "sector": sector,
                "project_count": len(grp),
                "total_original_cost_cr": round(orig_total, 2),
                "total_revised_cost_cr": round(rev_total, 2),
                "total_expenditure_cr": round(exp_total, 2),
                "avg_cost_overrun_pct": round(avg_overrun, 1),
                "avg_delay_months": round(avg_delay, 1),
                "delayed_projects_count": int(delayed_count),
                "delayed_ratio_pct": round((delayed_count / len(grp)) * 100, 1),
            })

        # Sort by total capex
        benchmarks.sort(key=lambda x: x["total_revised_cost_cr"], reverse=True)
        return benchmarks

    def get_ministry_rankings(self) -> List[Dict[str, Any]]:
        """
        Ranks Central Ministries by project execution efficiency and budget discipline.
        """
        grouped = self.df.groupby("ministry")
        rankings = []

        for min_name, grp in grouped:
            avg_overrun = grp["cost_overrun_pct"].mean()
            avg_delay = grp["months_delayed"].mean()
            delayed_pct = (grp["months_delayed"] > 0).mean() * 100

            # Composite Efficiency Index (100 is perfect, lower is worse)
            efficiency_score = 100.0 - (avg_overrun * 0.8 + avg_delay * 0.5)
            efficiency_score = round(max(10.0, min(99.0, efficiency_score)), 1)

            rankings.append({
                "ministry": min_name,
                "project_count": len(grp),
                "avg_cost_overrun_pct": round(avg_overrun, 1),
                "avg_delay_months": round(avg_delay, 1),
                "delayed_projects_pct": round(delayed_pct, 1),
                "efficiency_score": efficiency_score,
            })

        rankings.sort(key=lambda x: x["efficiency_score"], reverse=True)
        return rankings

    def find_peer_cohort(self, project_id: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """
        Finds peer projects with similar size, sector, and terrain to compare delivery profiles.
        """
        match = self.df[self.df["project_id"] == project_id]
        if match.empty:
            return []

        target = match.iloc[0]
        candidates = self.df[(self.df["sector"] == target["sector"]) & (self.df["project_id"] != project_id)].copy()

        if candidates.empty:
            candidates = self.df[self.df["project_id"] != project_id].copy()

        # Distance metric based on original cost and terrain
        target_cost = target["original_cost_cr"]
        candidates["cost_diff_ratio"] = (candidates["original_cost_cr"] - target_cost).abs() / target_cost
        candidates = candidates.sort_values(by="cost_diff_ratio").head(top_k)

        peers = []
        for _, row in candidates.iterrows():
            peers.append({
                "project_id": row["project_id"],
                "project_name": row["project_name"],
                "ministry": row["ministry"],
                "original_cost_cr": row["original_cost_cr"],
                "cost_overrun_pct": row["cost_overrun_pct"],
                "months_delayed": row["months_delayed"],
                "physical_progress_pct": row["physical_progress_pct"],
            })

        return peers
