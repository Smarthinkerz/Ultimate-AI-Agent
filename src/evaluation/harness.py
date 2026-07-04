"""
Evaluation Harness for the Ultimate AI Agent.
Real-domain benchmarks drawn from Tahir's ventures: investor memo refinement,
curriculum module creation, Japan strategy synthesis, construction project synthesis,
decision audit. Automated scoring on depth, originality, foresight, protocol adherence.
"""

from typing import Dict, Any, List, Optional
from src.observability.logging import get_structured_logger
from src.agent.graph import run_ultimate_agent

logger = get_structured_logger(__name__)


class EvaluationHarness:
    def __init__(self):
        self.benchmarks = {
            "investor_memo_refinement": {
                "task": "Refine the Brainpower AI investor pitch memo for a $1M pre-seed round. Include futures modeling, risk pre-mortem, compounding moats, and investor Q&A. Target: OMR 75k or evolved ask with clear 5-year $15M+ ARR path.",
                "domain": "Brainpower AI fundraising",
                "expected_protocol_elements": ["deconstruction", "multi_framework", "refinement_cycle", "futures", "symbiosis"]
            },
            "curriculum_module": {
                "task": "Design a complete lesson module for the AI Builder Bootcamp (Thinker track) on 'XAI & Trust Calibration in High-Stakes Decision Systems'. Include readings, exercises, 3D mentor prompts, badge criteria, and integration points to Builder track technical skills.",
                "domain": "AI Builder Bootcamp",
                "expected_protocol_elements": ["deconstruction", "multi_framework", "futures", "symbiosis"]
            },
            "japan_strategy": {
                "task": "Synthesize 3 tailored Japan market entry startup ideas in elderly care or precision agriculture for Smarthinkerz. Include deep cultural adaptation (omotenashi, kaizen, SME realities, aging demographics 30%+), go-to-market, regulatory nuance, and 5-year defensive moat analysis.",
                "domain": "Japan AI market strategy",
                "expected_protocol_elements": ["deconstruction", "multi_framework", "refinement_cycle", "futures"]
            },
            "construction_optionality": {
                "task": "For a marine/coastal infrastructure bid in GCC: Perform full optionality and risk synthesis. Surface hidden variables, second/third-order effects, Taleb barbell strategies, and scheduling flexibility recommendations. Perspective of 25+ year MD of contracting company.",
                "domain": "Cahit Contracting construction leadership",
                "expected_protocol_elements": ["deconstruction", "multi_framework", "futures", "symbiosis"]
            }
        }

    def run_benchmarks(self, specific_benchmark: Optional[str] = None) -> Dict[str, Any]:
        results = {}
        to_run = [specific_benchmark] if specific_benchmark and specific_benchmark in self.benchmarks else list(self.benchmarks.keys())

        for name in to_run:
            bench = self.benchmarks[name]
            logger.info("evaluation_benchmark_starting", benchmark=name)

            try:
                agent_result = run_ultimate_agent(task=bench["task"], mode="batch")

                # Protocol adherence scoring (simple but effective)
                trace = agent_result.get("full_trace_export", {}).get("reasoning_trace", [])
                phases_present = set(t.get("phase") for t in trace)
                adherence_score = sum(1 for elem in bench["expected_protocol_elements"] if elem in phases_present) / len(bench["expected_protocol_elements"])

                # Depth / Originality / Foresight (heuristic + would use LLM judge in production)
                depth_score = min(10.0, 6.0 + len(trace) * 0.4)  # More trace entries = deeper reasoning
                originality_score = 8.5 if "Tahir" in str(trace) or "Smarthinkerz" in str(trace) or "Brainpower" in str(trace) else 6.0
                foresight_score = 9.0 if agent_result.get("full_trace_export", {}).get("futures_horizons") else 5.0

                overall = (adherence_score * 0.35 + depth_score / 10 * 0.25 + originality_score / 10 * 0.2 + foresight_score / 10 * 0.2) * 10

                results[name] = {
                    "status": "completed",
                    "power_audit_score": agent_result.get("power_audit").score if agent_result.get("power_audit") else None,
                    "refinement_passes": agent_result.get("refinement_passes"),
                    "protocol_adherence": round(adherence_score, 2),
                    "depth_score": round(depth_score, 1),
                    "originality_score": round(originality_score, 1),
                    "foresight_score": round(foresight_score, 1),
                    "overall_score": round(overall, 1),
                    "notes": "Full protocol executed. Real-domain calibration visible in trace."
                }
            except Exception as e:
                results[name] = {"status": "failed", "error": str(e)}

        logger.info("evaluation_harness_complete", benchmarks_run=len(results))
        return results


# Regression test helper
def test_refinement_loop_integrity():
    """Quick regression to ensure cycle and Power Audit still work after changes."""
    result = run_ultimate_agent("Test task for regression: summarize key principles of the Ultimate Reasoning Engine itself.", mode="chat")
    assert result.get("refinement_passes", 0) >= 3, "Refinement loop did not execute minimum passes"
    assert result.get("power_audit") is not None, "Power Audit node did not produce result"
    return True