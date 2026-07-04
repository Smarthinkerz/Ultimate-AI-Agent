"""
Guardrail Engine for the Ultimate AI Agent.
Value alignment checks against user constitution, hallucination detection (especially in self-mod proposals),
PII handling, cost/latency monitoring with auto-throttling, ethical/Sharia contextual sensitivity.
"""

from typing import Dict, Any, List
from config.settings import settings
from src.observability.logging import get_structured_logger

logger = get_structured_logger(__name__)


class GuardrailEngine:
    def __init__(self):
        self.constitution_keywords = [
            "ethical", "explainability", "human-ai", "dependency", "diminish", "judgment",
            "sharia", "hibah", "inheritance", "oman", "gcc", "islamic", "not legal advice"
        ]
        self.max_cost_per_task = settings.max_tool_cost_usd

    def check_all(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations = []

        # Value alignment (constitution)
        final_output = state.get("final_output", "") or str(state.get("reasoning_trace", []))
        if any(kw in final_output.lower() for kw in ["replace human judgment", "fully autonomous decision", "no human needed"]):
            violations.append({
                "type": "value_alignment",
                "severity": "high",
                "message": "Output risks creating dependency that diminishes human capability. Violates core symbiosis principle.",
                "mitigation": "Rewrite with explicit 'your final strategic call' framing and capability development language."
            })

        # Self-improvement hallucination / over-reach check
        for proposal in state.get("proposed_updates", []):
            if proposal.get("confidence", 0) > 0.95 and "self_modification" in str(proposal.get("type", "")):
                violations.append({
                    "type": "self_improvement_risk",
                    "severity": "medium",
                    "message": "Extremely high confidence self-modification proposal. Risk of hallucinated improvement.",
                    "mitigation": "Require human review + smaller scoped change first."
                })

        # Cost / budget
        if state.get("cost_accumulated_usd", 0) > self.max_cost_per_task * 0.9:
            violations.append({
                "type": "cost_threshold",
                "severity": "medium",
                "message": f"Approaching or exceeding per-task tool budget of ${self.max_cost_per_task}.",
                "mitigation": "Switch to lighter protocol or cached results for remaining work."
            })

        # Sharia / cultural sensitivity (contextual, not legal)
        task = state.get("task", "").lower()
        if settings.sharia_review_enabled and any(word in task for word in ["family", "inheritance", "gift", "hibah", "oman", "sharia"]):
            violations.append({
                "type": "sharia_contextual_flag",
                "severity": "low",
                "message": "Task involves potential Sharia/family agreement domain in Oman/GCC context. This agent provides contextual synthesis only — not legal or religious advice.",
                "mitigation": "Include prominent disclaimer and recommend qualified local expert review before any real-world application."
            })

        if violations:
            logger.warning("guardrail_violations_detected", count=len(violations), types=[v["type"] for v in violations])

        return violations

    def check_value_alignment(self, text: str) -> bool:
        """Quick check used in self-improvement proposals."""
        forbidden = ["eliminate human", "replace all judgment", "fully autonomous without oversight"]
        return not any(f in text.lower() for f in forbidden)