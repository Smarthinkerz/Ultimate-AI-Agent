"""
FastAPI production server for the Ultimate AI Agent System.
Endpoints for interactive chat, batch strategic deep-dives, mentor mode,
self-improvement approval, memory ingestion, and evaluation harness triggering.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Literal, List, Dict, Any
import uuid
from datetime import datetime

from src.agent.graph import run_ultimate_agent, create_ultimate_agent_graph
from src.agent.memory import HybridMemoryManager
from config.settings import settings
from src.observability.logging import get_structured_logger
from src.evaluation.harness import EvaluationHarness  # Minimal version

logger = get_structured_logger(__name__)

app = FastAPI(
    title="Ultimate AI Agent System API",
    description="Production-ready frontier reasoning engine calibrated for Tahir ŞENYURT / Smarthinkerz LLC",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Models
# -------------------------------

class TaskRequest(BaseModel):
    task: str
    mode: Literal["chat", "batch", "mentor"] = "chat"
    thread_id: Optional[str] = None


class TaskResponse(BaseModel):
    final_output: str
    power_audit_score: Optional[float]
    refinement_passes: int
    proposed_self_improvements: List[Dict[str, Any]]
    thread_id: str
    cost_usd: float
    full_trace_available: bool


class ApprovalRequest(BaseModel):
    proposal_id: str
    approved: bool
    reviewer_notes: Optional[str] = None

# -------------------------------
# Endpoints
# -------------------------------

@app.get("/")
async def root():
    """Simple root endpoint for quick testing."""
    return {"status": "ok", "message": "Ultimate AI Agent System API is running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "protocol": "Ultimate-Reasoning-Engine-v1",
        "user_calibrated": settings.user_id,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/agent/run", response_model=TaskResponse)
async def run_agent(request: TaskRequest):
    """Main entry point for all interaction modes. Executes full Ultimate Reasoning Engine."""
    try:
        result = run_ultimate_agent(
            task=request.task,
            mode=request.mode,
            thread_id=request.thread_id
        )
        return TaskResponse(
            final_output=result["final_output"],
            power_audit_score=result.get("power_audit").score if result.get("power_audit") else None,
            refinement_passes=result.get("refinement_passes", 1),
            proposed_self_improvements=result.get("proposed_self_improvements", []),
            thread_id=result["thread_id"],
            cost_usd=result.get("cost_usd", 0.0),
            full_trace_available=True
        )
    except Exception as e:
        logger.error("agent_run_failed", error=str(e), task=request.task[:100])
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")

@app.post("/memory/ingest")
async def ingest_memory(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    source_type: str = "conversation_history"
):
    """Bulk memory ingestion endpoint. Supports PDFs, JSON conversation exports, text principles."""
    memory = HybridMemoryManager()
    temp_path = f"/tmp/{uuid.uuid4()}_{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    background_tasks.add_task(memory.ingest_bulk, source_type, temp_path, {"original_filename": file.filename})
    return {"status": "ingestion_queued", "filename": file.filename, "source_type": source_type}

@app.post("/self-improvement/approve")
async def approve_proposal(request: ApprovalRequest):
    """Human approval gate for self-improvement proposals."""
    memory = HybridMemoryManager()
    conn = __import__("sqlite3").connect(memory.structured_path)
    cursor = conn.cursor()

    status = "approved" if request.approved else "rejected"
    cursor.execute(
        "UPDATE self_improvement_proposals SET status = ?, reviewed_at = ?, reviewed_by = ? WHERE proposal_id = ?",
        (status, datetime.utcnow().isoformat(), "human_reviewer", request.proposal_id)
    )
    conn.commit()
    conn.close()

    if request.approved:
        logger.info("self_improvement_approved", proposal_id=request.proposal_id)
        return {"status": "approved_and_applied", "proposal_id": request.proposal_id, "notes": request.reviewer_notes}
    else:
        return {"status": "rejected", "proposal_id": request.proposal_id}

@app.post("/evaluate/run")
async def trigger_evaluation(benchmark: Optional[str] = None):
    """Trigger evaluation harness on real-domain benchmarks."""
    harness = EvaluationHarness()
    results = harness.run_benchmarks(specific_benchmark=benchmark)
    return {"status": "evaluation_complete", "results": results}

@app.get("/memory/context")
async def get_current_context():
    """Debug/inspection endpoint for current deep calibration state."""
    memory = HybridMemoryManager()
    context = memory.get_user_context("", {})
    return {"user_context_keys": list(context.keys()), "calibration_depth": context.get("calibration_depth")}

# -------------------------------
# Entrypoint
# -------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
