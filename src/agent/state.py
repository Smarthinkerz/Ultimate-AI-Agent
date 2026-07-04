"""
AgentState definition for the Ultimate Reasoning Engine LangGraph.
Uses TypedDict for LangGraph compatibility + Pydantic for validation where beneficial.
All fields support the full protocol: reasoning traces, refinement cycles, memory, governance.
"""

from typing import TypedDict, List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class Phase(str, Enum):
    DECONSTRUCTION = "deconstruction"
    SYNTHESIS = "synthesis"
    REFINEMENT = "refinement"
    FUTURES = "futures"
    SYMBIOSIS = "symbiosis"
    TOOLS = "tools"
    GUARDRAILS = "guardrails"
    OUTPUT = "output"
    SELF_IMPROVEMENT = "self_improvement"


class RefinementPass(int, Enum):
    PASS_1_INITIAL = 1
    PASS_2_CRITIQUE = 2
    PASS_3_REFINEMENT = 3
    PASS_4_POWER_AUDIT = 4


class PowerAuditResult(BaseModel):
    passed: bool
    score: float = Field(ge=0.0, le=10.0)
    rationale: str
    protocol_adherence: Dict[str, bool]  # e.g. {"deconstruction": True, "all_frameworks": True, ...}
    would_competitor_match: bool
    improvement_suggestions: List[str]


class ToolAuditEntry(BaseModel):
    tool_name: str
    timestamp: datetime
    pre_validation_reasoning: str
    alternatives_considered: List[str]
    why_rejected: Optional[str]
    post_execution_reflection: Optional[str]
    cost_estimate_usd: Optional[float]
    success: bool
    error: Optional[str]


class AgentState(TypedDict):
    # Core conversation
    messages: List[Dict[str, Any]]  # LangChain message dicts or HumanMessage/AIMessage serialized
    task: str
    task_metadata: Dict[str, Any]  # mode (chat/batch/mentor), priority, token_budget, etc.

    # Deep User Calibration (loaded once, updated incrementally)
    user_context: Dict[str, Any]  # Snapshot from hybrid memory + seed

    # Reasoning Engine State
    current_phase: Phase
    reasoning_trace: List[Dict[str, Any]]  # Structured log: {"phase": , "framework": , "output": , "rationale": , "timestamp": }
    refinement_pass: RefinementPass
    power_audit_result: Optional[PowerAuditResult]

    # Memory
    memory_context: Dict[str, Any]  # Retrieved semantic hits + structured facts + relevant episodes
    episodic_log_refs: List[str]  # Pointers to full JSONL entries for this task

    # Tool Governance
    tool_audit_log: List[ToolAuditEntry]
    pending_tool_calls: List[Dict[str, Any]]
    tool_budget_remaining_usd: float

    # Futures & Symbiosis
    futures_horizons: Optional[Dict[str, Any]]  # immediate, 6-18mo, 3-5yr models
    symbiosis_optimization: Optional[Dict[str, Any]]

    # Guardrails & Safety
    guardrail_violations: List[Dict[str, Any]]
    human_approval_required: bool
    human_approval_reason: Optional[str]
    approved_by_human: bool

    # Self-Improvement
    proposed_updates: List[Dict[str, Any]]  # From self-improvement subgraph
    self_improvement_triggered: bool

    # Output & Trace
    final_output: Optional[str]
    full_trace_export: Optional[Dict[str, Any]]  # Complete structured export for downstream (Brainpower, Studio, etc.)

    # Meta / Control
    error_state: Optional[str]
    cost_accumulated_usd: float
    start_time: datetime
    last_updated: datetime


class AgentStateModel(BaseModel):
    """Pydantic wrapper for validation and serialization convenience."""
    task: str
    user_context: Dict[str, Any] = Field(default_factory=dict)
    current_phase: Phase = Phase.DECONSTRUCTION
    reasoning_trace: List[Dict[str, Any]] = Field(default_factory=list)
    refinement_pass: int = 1
    memory_context: Dict[str, Any] = Field(default_factory=dict)
    tool_audit_log: List[Dict[str, Any]] = Field(default_factory=list)
    guardrail_violations: List[Dict[str, Any]] = Field(default_factory=list)
    human_approval_required: bool = False
    cost_accumulated_usd: float = 0.0

    class Config:
        use_enum_values = True