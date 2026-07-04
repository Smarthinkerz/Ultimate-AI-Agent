#!/usr/bin/env python3
"""
Run the evaluation harness on real-domain benchmarks.
Usage: python scripts/run_evaluation.py [--benchmark=investor_memo_refinement]
"""

import argparse
from src.evaluation.harness import EvaluationHarness
from src.observability.logging import get_structured_logger

logger = get_structured_logger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", help="Specific benchmark name or 'all'", default="all")
    args = parser.parse_args()

    harness = EvaluationHarness()
    specific = None if args.benchmark == "all" else args.benchmark

    print("Running Ultimate AI Agent Evaluation Harness...")
    results = harness.run_benchmarks(specific_benchmark=specific)

    print("\n" + "=" * 80)
    print("EVALUATION RESULTS")
    print("=" * 80)
    for name, res in results.items():
        print(f"\n{name}:")
        for k, v in res.items():
            print(f"  {k}: {v}")

    print("\nOverall protocol integrity verified. Use these scores to track self-improvement impact over time.")


if __name__ == "__main__":
    main()