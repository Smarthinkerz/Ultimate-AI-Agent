#!/usr/bin/env python3
"""
Interactive REPL demo for the Ultimate AI Agent.
Shows full protocol execution, trace, and self-improvement proposals.
"""

from src.agent.graph import run_ultimate_agent
from config.settings import settings
import json


def main():
    print("=" * 80)
    print("ULTIMATE AI AGENT SYSTEM — Interactive Demo")
    print(f"Calibrated for: {settings.user_name} | Protocol: Ultimate-Reasoning-Engine-v1")
    print("Type 'exit' to quit. All interactions logged to episodic memory.")
    print("=" * 80)

    while True:
        try:
            task = input("\n> Enter task (or 'exit'): ").strip()
            if task.lower() in ("exit", "quit"):
                break
            if not task:
                continue

            print("\n[Executing full Ultimate Reasoning Engine... this may take 30-90s depending on LLM latency]\n")
            result = run_ultimate_agent(task=task, mode="chat")

            print("\n" + "=" * 80)
            print("FINAL OUTPUT")
            print("=" * 80)
            print(result["final_output"])

            print("\n" + "-" * 80)
            print(f"Power Audit Score: {result.get('power_audit').score if result.get('power_audit') else 'N/A'} / 10")
            print(f"Refinement Passes: {result.get('refinement_passes')}")
            print(f"Cost (USD): {result.get('cost_usd', 0):.2f}")
            print(f"Thread ID: {result['thread_id']}")

            if result.get("proposed_self_improvements"):
                print("\nSelf-Improvement Proposals Generated (review via /self-improvement/approve or approve_proposal.py):")
                for p in result["proposed_self_improvements"]:
                    print(f"  - [{p['type']}] {p['proposed_change'][:120]}... (confidence {p['confidence']})")

            print("\nFull structured trace exported to episodic logs and available via API.")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Check your .env LLM keys and that memory has been seeded.")


if __name__ == "__main__":
    main()