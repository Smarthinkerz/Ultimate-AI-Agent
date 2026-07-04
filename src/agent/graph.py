"""
Main LangGraph definition for the Ultimate AI Agent System.
Implements the full Ultimate Reasoning Engine as native nodes + cycles.
Uses SqliteSaver for production checkpointing and resumability.
"""

from typing import Dict, Any, Literal, Optional, List
from datetime import datetime
import uuid
import json

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from src.agent.state import AgentState, Phase, RefinementPass, PowerAuditResult, ToolAuditEntry, AgentStateModel
from src.agent.reasoning_engine import (
    deconstruct_to_first_principles,
    multi_framework_synthesis,
    adversarial_critique,
    power_audit,
    futures_and_compounding_lens,
    human_ai_symbiosis_optimization,
)
from src.agent.memory import HybridMemoryManager
from src.agent.tools.registry import ToolRegistry
from src.agent.guardrails import GuardrailEngine
from src.config.settings import settings
from src.observability.logging import get_structured_logger

logger = get_structured_logger(__name__)


def create_ultimate_agent_graph(checkpointer: Optional[SqliteSaver] = None) -> StateGraph:
    """
    Factory that builds and compiles the complete agent graph with all mandated components.
    The refinement loop is a native cycle with conditional routing.
    """
    workflow = StateGraph(AgentState)

    # === NODE DEFINITIONS ===
    # (all your node functions remain unchanged: load_user_calibration, deconstruction_node,
    # synthesis_node, refinement passes, futures_node, symbiosis_node, tool_orchestration_node,
    # guardrails_node, output_synthesis_node, self_improvement_node)

    # === BUILD THE GRAPH ===
    workflow.add_node("load_calibration", load_user_calibration)
    workflow.add_node("deconstruction", deconstruction_node)
    workflow.add_node("synthesis", synthesis_node)

    workflow.add_node("refinement_pass_1", refinement_pass_1_initial)
    workflow.add_node("refinement_pass_2", refinement_pass_2_critique)
    workflow.add_node("refinement_pass_3", refinement_pass_3_refinement)
    workflow.add_node("refinement_pass_4", refinement_pass_4_power_audit)

    workflow.add_node("futures", futures_node)
    workflow.add_node("symbiosis", symbiosis_node)
    workflow.add_node("tools", tool_orchestration_node)
    workflow.add_node("guardrails", guardrails_node)
    workflow.add_node("output", output_synthesis_node)
    workflow.add_node("self_improvement", self_improvement_node)

    workflow.set_entry_point("load_calibration")
    workflow.add_edge("load_calibration", "deconstruction")
    workflow.add_edge("deconstruction", "synthesis")
    workflow.add_edge("synthesis", "refinement_pass_1")

    workflow.add_edge("refinement_pass_1", "refinement_pass_2")
    workflow.add_edge("refinement_pass_2", "refinement_pass_3")
    workflow.add_edge("refinement_pass_3", "refinement_pass_4")

    workflow.add_conditional_edges(
        "refinement_pass_4",
        should_continue_refinement,
        {
            "continue_refinement": "refinement_pass_2",
            "exit_refinement": "futures"
        }
    )

    workflow.add_edge("futures", "symbiosis")
    workflow.add_edge("symbiosis", "tools")
    workflow.add_edge("tools", "guardrails")

    workflow.add_conditional_edges(
        "guardrails",
        lambda s: "output" if not s.get("human_approval_required") else "human_gate",
        {
            "output": "output",
            "human_gate": END
        }
    )

    workflow.add_edge("output", "self_improvement")
    workflow.add_edge("self_improvement", END)

    workflow.add_node("human_gate", lambda s: {"human_approval_required": True, "last_updated": datetime.utcnow()})
    workflow.add_edge("human_gate", END)

    if checkpointer is None:
        from langgraph.checkpoint.memory import MemorySaver
        checkpointer = MemorySaver()

    compiled_graph = workflow.compile(checkpointer=checkpointer)
    logger.info("ultimate_agent_graph_compiled", nodes=len(workflow.nodes), has_cycle=True)
    return compiled_graph


def run_ultimate_agent(
    task: str,
    mode: Literal["chat", "batch", "mentor"] = "chat",
    thread_id: Optional[str] = None,
    checkpointer: Optional[SqliteSaver] = None
) -> Dict[str, Any]:
    """
    High-level entry point. Handles thread/checkpointing and returns final state + output.
    """
    graph = create_ultimate_agent_graph(checkpointer=checkpointer)

    initial_state: AgentState = {
        "messages": [{"role": "human", "content": task}],
        "task": task,
        "task_metadata": {"mode": mode, "thread_id": thread_id or str(uuid.uuid4())},
        "user_context": {},
        "current_phase": Phase.DECONSTRUCTION,
        "reasoning_trace": [],
        "refinement_pass": 1,
        "power_audit_result": None,
        "memory_context": {},
        "episodic_log_refs": [],
        "tool_audit_log": [],
        "pending_tool_calls": [],
        "tool_budget_remaining_usd": settings.max_tool_cost_usd,
        "futures_horizons": None,
        "symbiosis_optimization": None,
        "guardrail_violations": [],
        "human_approval_required": False,
        "human_approval_reason": None,
        "approved_by_human": False,
        "proposed_updates": [],
        "self_improvement_triggered": False,
        "final_output": None,
        "full_trace_export": None,
        "error_state": None,
        "cost_accumulated_usd": 0.0,
        "start_time": datetime.utcnow(),
        "last_updated": datetime.utcnow(),
    }

    config = {"configurable": {"thread_id": thread_id or str(uuid.uuid4())}}

    final_state = graph.invoke(initial_state, config=config)

    return {
        "final_output": final_state.get("final_output"),
        "full_trace_export": final_state.get("full_trace_export"),
        "power_audit": final_state.get("power_audit_result"),
        "refinement_passes": final_state.get("refinement_pass"),
        "proposed_self_improvements": final_state.get("proposed_updates", []),
        "thread_id": config["configurable"]["thread_id"],
        "cost_usd": final_state.get("cost_accumulated_usd", 0.0)
    }

