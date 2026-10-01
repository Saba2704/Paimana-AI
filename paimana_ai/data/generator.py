"""
PAIMANA Calibrated Dataset Generator
Synthesizes a realistic repository of 1,981 central sector projects calibrated to
the April 2026 MoSPI report totals:
  - Original Cost: ~₹37.13 lakh Crore
  - Revised Cost:  ~₹42.78 lakh Crore
  - Cumulative Expenditure: ~₹20.36 lakh Crore
  - 17 Central Ministries and 22 Infrastructure Sectors
"""

import random
from typing import List, Dict, Any
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from paimana_ai.data.paimana_cuf_schema import InfrastructureProjectRecord


# Ministry and Sector distributions calibrated to MoSPI Central Sector Portfolio
MINISTRY_PORTFOLIO = [
    {"ministry": "Ministry of Road Transport and Highways", "agency": "NHAI", "sector": "Road Transport and Highways", "weight": 0.28, "cost_mult": 1.14},
    {"ministry": "Ministry of Railways", "agency": "RVNL", "sector": "Railways", "weight": 0.22, "cost_mult": 1.28},
    {"ministry": "Ministry of Petroleum and Natural Gas", "agency": "IOCL", "sector": "Petroleum", "weight": 0.12, "cost_mult": 1.11},
    {"ministry": "Ministry of Power", "agency": "NTPC", "sector": "Power", "weight": 0.10, "cost_mult": 1.15},
    {"ministry": "Ministry of Coal", "agency": "Coal India Ltd", "sector": "Coal", "weight": 0.06, "cost_mult": 1.10},
    {"ministry": "Ministry of Housing and Urban Affairs", "agency": "DMRC", "sector": "Urban Development", "weight": 0.05, "cost_mult": 1.20},
    {"ministry": "Ministry of Steel", "agency": "SAIL", "sector": "Steel", "weight": 0.03, "cost_mult": 1.16},
    {"ministry": "Ministry of Ports, Shipping and Waterways", "agency": "Sagarmala / Port Trusts", "sector": "Shipping and Ports", "weight": 0.03, "cost_mult": 1.08},
    {"ministry": "Ministry of Jal Shakti", "agency": "National Water Dev Agency", "sector": "Water Resources", "weight": 0.03, "cost_mult": 1.25},
    {"ministry": "Ministry of Civil Aviation", "agency": "AAI", "sector": "Civil Aviation", "weight": 0.02, "cost_mult": 1.09},
    {"ministry": "Department of Telecommunications", "agency": "BSNL / BBNL", "sector": "Telecommunications", "weight": 0.02, "cost_mult": 1.07},
    {"ministry": "Department of Atomic Energy", "agency": "NPCIL", "sector": "Atomic Energy", "weight": 0.015, "cost_mult": 1.22},
    {"ministry": "Ministry of Mines", "agency": "NALCO / MECL", "sector": "Mining", "weight": 0.015, "cost_mult": 1.12},
    {"ministry": "Ministry of Chemicals and Fertilizers", "agency": "HURL", "sector": "Fertilizers", "weight": 0.01, "cost_mult": 1.18},
    {"ministry": "Ministry of New and Renewable Energy", "agency": "SECI", "sector": "Renewable Energy", "weight": 0.01, "cost_mult": 1.05},
    {"ministry": "Ministry of Heavy Industries", "agency": "BHEL", "sector": "Heavy Industry", "weight": 0.005, "cost_mult": 1.12},
    {"ministry": "Department of Space", "agency": "ISRO", "sector": "Space Infrastructure", "weight": 0.005, "cost_mult": 1.06},
]

STATES = [
    "Maharashtra", "Uttar Pradesh", "Gujarat", "Tamil Nadu", "Karnataka",
    "Madhya Pradesh", "West Bengal", "Rajasthan", "Bihar", "Odisha",
    "Andhra Pradesh", "Telangana", "Assam", "Kerala", "Jharkhand",
    "Punjab", "Chhattisgarh", "Haryana", "Jammu and Kashmir", "Multi-State"
]

PROJECT_TEMPLATES = {
    "Road Transport and Highways": [
        "Four-Laning of {loc1} to {loc2} Highway Section (NH-{num})",
        "Access-Controlled Greenfield Expressway ({loc1}-{loc2} Corridor)",
        "Bypass & Ring Road Construction around {loc1} City",
        "Economic Corridor Enhancement Package-{pnum} ({loc1} Spur)"
    ],
    "Railways": [
        "Doubling & Electrification of {loc1}-{loc2} Rail Link ({km} km)",
        "Dedicated Freight Corridor (Western/Eastern Feeder #{num})",
        "New Broad Gauge Line Connection to {loc1} Hinterland",
        "Redevelopment & Multi-Modal Modernization of {loc1} Junction"
    ],
    "Petroleum": [
        "Cross-Country Natural Gas Pipeline Extension ({loc1}-{loc2})",
        "Capacity Augmentation of {loc1} Petroleum Refinery to {km} MMTPA",
        "Underground Strategic Crude Oil Storage Facility at {loc1}",
        "Petrochemical Complex & Polypropylene Unit Expansion at {loc1}"
    ],
    "Power": [
        "Supercritical Thermal Power Project Stage-III ({loc1})",
        "High Voltage Inter-Regional Direct Current (HVDC) Line ({loc1}-{loc2})",
        "Pumped Storage Hydroelectric Power Plant at {loc1}",
        "Ultra-Mega Substation and Smart Grid Integration ({loc1})"
    ],
    "Urban Development": [
        "Metro Rail Corridor Phase-II ({loc1} Metro Line-{num})",
        "Intelligent Urban Mobility & Regional Rapid Transit Link ({loc1}-{loc2})",
        "Comprehensive Wastewater Treatment & Storm Drainage System ({loc1})"
    ]
}


def generate_calibrated_projects(n_projects: int = 1981, random_seed: int = 42) -> pd.DataFrame:
    """
    Generates n_projects matching the exact macroeconomic distribution of PAIMANA April 2026.
    Target totals:
      - Original Cost: ~₹37,13,000 Cr (~₹1,874 Cr avg)
      - Revised Cost:  ~₹42,78,000 Cr (~₹2,159 Cr avg)
      - Expenditure:   ~₹20,36,000 Cr (~₹1,027 Cr avg)
    """
    random.seed(random_seed)
    np.random.seed(random_seed)

    records = []
    weights = [m["weight"] for m in MINISTRY_PORTFOLIO]
    norm_weights = [w / sum(weights) for w in weights]

    # Target scale multipliers
    target_orig_total = 3713000.0  # ₹37.13 lakh Cr
    raw_orig_costs = []

    # First pass: generate baseline costs with log-normal distribution (mega project tail)
    for _ in range(n_projects):
        # Log-normal with mean ~1800 Cr and realistic tail (projects range from 150 Cr to 60,000+ Cr)
        raw_cost = max(150.0, float(np.random.lognormal(mean=6.8, sigma=1.05)))
        raw_orig_costs.append(raw_cost)

    scale_factor = target_orig_total / sum(raw_orig_costs)
    calibrated_orig_costs = [c * scale_factor for c in raw_orig_costs]

    for idx in range(n_projects):
        m_info = np.random.choice(MINISTRY_PORTFOLIO, p=norm_weights)
        ministry = m_info["ministry"]
        agency = m_info["agency"]
        sector = m_info["sector"]
        cost_mult = m_info["cost_mult"]

        state = random.choice(STATES)
        loc1 = random.choice(["Kanpur", "Varanasi", "Surat", "Pune", "Bhubaneswar", "Nagpur", "Raipur", "Indore", "Guwahati", "Kochi", "Salem", "Jaipur", "Ranchi", "Vadodara", "Vishakhapatnam", "Hubballi", "Amritsar", "Siliguri"])
        loc2 = random.choice(["Patna", "Ahmedabad", "Nashik", "Cuttack", "Bhopal", "Jabalpur", "Dibrugarh", "Madurai", "Jodhpur", "Dhanbad", "Rajkot", "Vijayawada", "Belagavi", "Ludhiana", "Asansol"])
        
        template_list = PROJECT_TEMPLATES.get(sector, [
            "{loc1} Infrastructure Development & Upgradation Package-{pnum}",
            "Integrated {sector} Facility at {loc1}",
            "Capacity Modernization of {loc1} Infrastructure Hub"
        ])
        tmpl = random.choice(template_list)
        p_name = tmpl.format(
            loc1=loc1, loc2=loc2, sector=sector,
            num=random.randint(12, 98), pnum=random.randint(1, 6),
            km=random.randint(45, 380)
        )

        p_id = f"PM-{sector[:3].upper()}-{idx+1:04d}"
        orig_cost = round(calibrated_orig_costs[idx], 2)

        # Baseline delay factors with sectoral probabilities
        if sector in ["Railways", "Road Transport and Highways"]:
            p_land = 0.52
            p_forest = 0.44
            p_util = 0.38
        elif sector in ["Coal", "Mining"]:
            p_land = 0.48
            p_forest = 0.58
            p_util = 0.20
        elif sector in ["Power", "Petroleum"]:
            p_land = 0.25
            p_forest = 0.22
            p_util = 0.30
        else:
            p_land = 0.28
            p_forest = 0.20
            p_util = 0.25

        delay_land = random.random() < p_land
        delay_forest = random.random() < p_forest
        delay_utility = random.random() < p_util
        delay_contractor = random.random() < 0.32
        delay_law_order = random.random() < 0.12
        delay_geotech = random.random() < 0.18

        # Delay months simulation
        bottleneck_count = sum([delay_land, delay_forest, delay_utility, delay_contractor, delay_law_order, delay_geotech])
        is_delayed = bottleneck_count > 0 or (random.random() < 0.35)

        if is_delayed:
            months_delayed = int(np.random.gamma(shape=2.5, scale=8.0) + bottleneck_count * 5)
            months_delayed = min(months_delayed, 144)  # cap at 12 years
            # Cost escalation driven by delay and bottlenecks
            escalation_rate = 0.04 + (months_delayed / 120.0) * 0.45 + (bottleneck_count * 0.05) + np.random.normal(0, 0.03)
            escalation_rate = max(0.0, escalation_rate * cost_mult)
        else:
            months_delayed = 0
            escalation_rate = 0.0

        revised_cost = round(orig_cost * (1.0 + escalation_rate), 2)
        cost_overrun_pct = round(escalation_rate * 100, 2)

        # Physical and financial progress
        # Current progress correlates with how far the project has advanced
        raw_progress = np.random.beta(a=2.2, b=1.8) * 100.0
        physical_progress = round(min(98.5, max(5.0, raw_progress)), 1)

        # Financial burn rate often leads physical progress in problematic projects
        burn_lead = 1.0 + (0.35 if bottleneck_count >= 2 else 0.05) + np.random.normal(0, 0.08)
        burn_lead = max(0.85, burn_lead)
        financial_progress = round(min(100.0, physical_progress * burn_lead), 1)
        cumulative_exp = round((financial_progress / 100.0) * revised_cost, 2)

        # Milestones
        total_milestones = random.randint(8, 45)
        achieved_milestones = int((physical_progress / 100.0) * total_milestones)
        achieved_milestones = min(total_milestones, max(0, achieved_milestones))
        delayed_milestones = int(bottleneck_count * random.uniform(1.2, 2.5))
        delayed_milestones = min(total_milestones - achieved_milestones, max(0, delayed_milestones))
        pending_milestones = total_milestones - achieved_milestones

        # Timeline dates
        base_date = datetime(2021, 1, 1) + timedelta(days=random.randint(0, 1500))
        duration_months = random.randint(24, 72)
        orig_doc_dt = base_date + timedelta(days=duration_months * 30)
        revised_doc_dt = orig_doc_dt + timedelta(days=months_delayed * 30)

        # Augmented Non-CUF Indicators (Dimension c)
        contractor_score = round(max(20.0, min(99.0, 75.0 - (10.0 if delay_contractor else 0.0) + np.random.normal(0, 12))), 1)
        terrain_difficulty = 3 if sector in ["Railways", "Power"] and state in ["Jammu and Kashmir", "Assam", "Uttarakhand", "Himachal Pradesh"] else (
            2 if state in ["Maharashtra", "Odisha", "Gujarat"] else 1
        )
        if random.random() < 0.15:
            terrain_difficulty = min(4, terrain_difficulty + 1)

        commodity_exposure = round(float(np.random.choice([1.0, 1.2, 1.4, 1.8], p=[0.4, 0.35, 0.18, 0.07])), 2)
        monsoon_vulnerability = round(float(np.random.beta(2, 3)), 2)
        inter_agency_nodes = random.randint(2, 8) + (2 if delay_land or delay_forest else 0)

        records.append({
            "project_id": p_id,
            "project_name": p_name,
            "ministry": ministry,
            "sector": sector,
            "implementing_agency": agency,
            "state": state,
            "original_cost_cr": orig_cost,
            "revised_cost_cr": revised_cost,
            "cumulative_exp_cr": cumulative_exp,
            "original_doc": orig_doc_dt.strftime("%Y-%m"),
            "revised_doc": revised_doc_dt.strftime("%Y-%m"),
            "months_delayed": months_delayed,
            "cost_overrun_pct": cost_overrun_pct,
            "physical_progress_pct": physical_progress,
            "financial_progress_pct": financial_progress,
            "total_milestones": total_milestones,
            "achieved_milestones": achieved_milestones,
            "delayed_milestones": delayed_milestones,
            "pending_milestones": pending_milestones,
            "delay_land_acq": delay_land,
            "delay_forest_clearance": delay_forest,
            "delay_utility_shift": delay_utility,
            "delay_contractor": delay_contractor,
            "delay_law_order": delay_law_order,
            "delay_geo_technical": delay_geotech,
            "contractor_track_record_score": contractor_score,
            "terrain_difficulty_index": terrain_difficulty,
            "commodity_inflation_exposure": commodity_exposure,
            "monsoon_vulnerability_score": monsoon_vulnerability,
            "inter_agency_coordination_nodes": inter_agency_nodes,
            "status": "Ongoing"
        })

    df = pd.DataFrame(records)
    
    # Adjust final aggregate expenditure and revised cost to closely match PAIMANA macro figures
    total_rev = df["revised_cost_cr"].sum()
    total_exp = df["cumulative_exp_cr"].sum()
    
    # Fine scale adjustment towards ₹42.78 lakh Cr and ₹20.36 lakh Cr
    df["revised_cost_cr"] = (df["revised_cost_cr"] * (4278000.0 / total_rev)).round(2)
    df["cumulative_exp_cr"] = (df["cumulative_exp_cr"] * (2036000.0 / total_exp)).round(2)
    df["cost_overrun_pct"] = (((df["revised_cost_cr"] - df["original_cost_cr"]) / df["original_cost_cr"]) * 100).round(2)
    
    return df


if __name__ == "__main__":
    df = generate_calibrated_projects(1981)
    print("Generated PAIMANA projects:", len(df))
    print(f"Total Original Cost: ₹{df['original_cost_cr'].sum() / 100000:.2f} Lakh Crore")
    print(f"Total Revised Cost:  ₹{df['revised_cost_cr'].sum() / 100000:.2f} Lakh Crore")
    print(f"Total Expenditure:   ₹{df['cumulative_exp_cr'].sum() / 100000:.2f} Lakh Crore")
    print("Delayed projects count:", (df["months_delayed"] > 0).sum())
