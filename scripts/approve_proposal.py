#!/usr/bin/env python3
"""
CLI for human review and approval of self-improvement proposals.
Usage: python scripts/approve_proposal.py --list
       python scripts/approve_proposal.py --id=<proposal_id> --approve
"""

import argparse
import sqlite3
from datetime import datetime
from src.agent.memory import HybridMemoryManager
from src.observability.logging import get_structured_logger

logger = get_structured_logger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true", help="List pending proposals")
    parser.add_argument("--id", help="Proposal ID to review")
    parser.add_argument("--approve", action="store_true", help="Approve the proposal")
    parser.add_argument("--reject", action="store_true", help="Reject the proposal")
    parser.add_argument("--notes", default="", help="Reviewer notes")
    args = parser.parse_args()

    memory = HybridMemoryManager()
    conn = sqlite3.connect(memory.structured_path)
    cursor = conn.cursor()

    if args.list:
        cursor.execute("SELECT proposal_id, type, target, proposed_change, confidence, status, created_at FROM self_improvement_proposals WHERE status = 'pending' ORDER BY created_at DESC")
        rows = cursor.fetchall()
        print(f"\nPending Self-Improvement Proposals ({len(rows)}):\n")
        for r in rows:
            print(f"ID: {r[0]}")
            print(f"  Type: {r[1]} | Target: {r[2]} | Confidence: {r[4]}")
            print(f"  Change: {r[3][:150]}...")
            print(f"  Status: {r[5]} | Created: {r[6]}")
            print("-" * 60)
        conn.close()
        return

    if args.id:
        if not (args.approve or args.reject):
            print("Must specify --approve or --reject")
            return

        status = "approved" if args.approve else "rejected"
        cursor.execute(
            "UPDATE self_improvement_proposals SET status = ?, reviewed_at = ?, reviewed_by = ? WHERE proposal_id = ?",
            (status, datetime.utcnow().isoformat(), "cli_reviewer", args.id)
        )
        conn.commit()
        print(f"Proposal {args.id} marked as {status}.")

        if args.approve:
            print("NOTE: In production this would trigger the actual apply logic (prompt edit, schema migration, changelog append, rollback point creation).")
            logger.info("proposal_approved_via_cli", proposal_id=args.id, notes=args.notes)

    conn.close()


if __name__ == "__main__":
    main()