"""
PAIMANA CUF (Common Upload Form) Schema Definition
Covers standard MoSPI Common Upload Form fields and augmented (Non-CUF) indicators.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class CUFStandardFields(BaseModel):
    """Standard fields collected in PAIMANA / OCMS Common Upload Form."""
    project_id: str = Field(..., description="Unique Project Code (e.g. MO-RAIL-0142)")
    project_name: str = Field(..., description="Sanctioned Project Title")
    ministry: str = Field(..., description="Central Line Ministry (e.g. Ministry of Railways)")
    sector: str = Field(..., description="Infrastructure Sector (e.g. Railways, Highways, Power)")
    implementing_agency: str = Field(..., description="Executing PSU / Agency (e.g. NHAI, RVNL, NTPC)")
    state: str = Field(..., description="Primary State / Multi-State")
    original_cost_cr: float = Field(..., description="Original Sanctioned Cost in ₹ Crore")
    revised_cost_cr: float = Field(..., description="Revised Approved Cost in ₹ Crore")
    cumulative_exp_cr: float = Field(..., description="Cumulative Expenditure in ₹ Crore")
    original_doc: str = Field(..., description="Original Date of Commissioning (YYYY-MM)")
    revised_doc: str = Field(..., description="Revised/Anticipated Date of Commissioning (YYYY-MM)")
    physical_progress_pct: float = Field(..., ge=0, le=100, description="Reported Physical Progress (%)")
    financial_progress_pct: float = Field(..., ge=0, description="Financial Expenditure vs Revised Cost (%)")
    total_milestones: int = Field(..., ge=0, description="Total Scheduled Milestones")
    achieved_milestones: int = Field(..., ge=0, description="Completed Milestones")
    delayed_milestones: int = Field(..., ge=0, description="Milestones with slippage")
    
    # Common Delay Drivers reported in CUF monthly updates
    delay_land_acq: bool = Field(False, description="Land Acquisition bottleneck flag")
    delay_forest_clearance: bool = Field(False, description="Forest/Environment clearance delay flag")
    delay_utility_shift: bool = Field(False, description="Utility shifting (power lines/pipes) flag")
    delay_contractor: bool = Field(False, description="Contractor slow mobilization/disputes flag")
    delay_law_order: bool = Field(False, description="Local law & order or ROW agitation flag")
    delay_geo_technical: bool = Field(False, description="Unforeseen geological/technical hurdles flag")
    status: str = Field("Ongoing", description="Status: Ongoing, Completed, Frozen")


class AugmentedNonCUFFields(BaseModel):
    """Augmented external/macro indicators not currently captured in standard CUF."""
    contractor_track_record_score: float = Field(
        70.0, ge=0, le=100,
        description="Historical rating of primary contractor's past project delivery efficiency"
    )
    terrain_difficulty_index: int = Field(
        2, ge=1, le=4,
        description="Geospatial terrain difficulty: 1=Plain, 2=Rolling/Coastal, 3=Hilly, 4=Mountainous/Tunneling"
    )
    commodity_inflation_exposure: float = Field(
        1.0, ge=0.5, le=2.5,
        description="Sensitivity multiplier to steel, cement and fuel wholesale price index swings"
    )
    monsoon_vulnerability_score: float = Field(
        0.5, ge=0.0, le=1.0,
        description="Vulnerability to prolonged monsoon suspension based on project coordinates"
    )
    inter_agency_coordination_nodes: int = Field(
        3, ge=1, le=12,
        description="Number of external stakeholder agencies required for ROW/clearance approvals"
    )


class InfrastructureProjectRecord(CUFStandardFields, AugmentedNonCUFFields):
    """Comprehensive project entity combining standard CUF and augmented indicators."""
    months_delayed: int = Field(0, description="Current schedule slippage in months")
    cost_overrun_pct: float = Field(0.0, description="Percentage cost escalation vs original sanctioned cost")
    composite_risk_index: Optional[float] = Field(None, description="Calculated Composite Risk Index (0-100)")
    rag_status: Optional[str] = Field(None, description="RAG Status: Red, Amber, Green")
