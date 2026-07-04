"""
Hybrid Persistent Memory System for the Ultimate AI Agent.
- Vector store (Chroma) for semantic recall
- Structured store (SQLite) for core facts, goals, history, versions
- Episodic logs (JSONL) for full reasoning traces with timestamps
- Ingestion module for bulk loading conversation histories, PDFs, principles
- Automatic update detection for long-term calibration
"""

import sqlite3
import json
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import chromadb
from chromadb.utils import embedding_functions

from config.settings import settings
from src.observability.logging import get_structured_logger


logger = get_structured_logger(__name__)


class HybridMemoryManager:
    def __init__(self):
        self.vector_path = settings.vector_db_path
        self.structured_path = settings.structured_db_path
        self.episodic_path = settings.episodic_log_path
        self.episodic_path.mkdir(parents=True, exist_ok=True)

        # Chroma client (persistent)
        self.chroma_client = chromadb.PersistentClient(path=str(self.vector_path))
        self.embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
            api_key=settings.openai_api_key,
            model_name=settings.embedding_model
        ) if settings.embedding_provider == "openai" else embedding_functions.DefaultEmbeddingFunction()

        self.collection = self.chroma_client.get_or_create_collection(
            name=f"agent_memory_{settings.user_id}",
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"}
        )

        # SQLite structured store
        self._init_structured_db()

    def _init_structured_db(self):
        conn = sqlite3.connect(self.structured_path)
        cursor = conn.cursor()

        # Core tables for deep calibration
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profile (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS venture_goals (
                id TEXT PRIMARY KEY,
                venture TEXT,
                goal TEXT,
                kpi TEXT,
                timeline TEXT,
                status TEXT,
                updated_at TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_history (
                id TEXT PRIMARY KEY,
                project TEXT,
                domain TEXT,
                outcome TEXT,
                lessons TEXT,
                artifacts TEXT,
                timestamp TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS constitution (
                principle_id TEXT PRIMARY KEY,
                principle TEXT,
                category TEXT,
                weight REAL,
                last_referenced TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS self_improvement_versions (
                version TEXT PRIMARY KEY,
                changelog TEXT,
                applied_at TEXT,
                rollback_point TEXT,
                approved_by TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS self_improvement_proposals (
                proposal_id TEXT PRIMARY KEY,
                version TEXT,
                type TEXT,
                target TEXT,
                proposed_change TEXT,
                rationale TEXT,
                confidence REAL,
                status TEXT DEFAULT 'pending',
                created_at TEXT,
                reviewed_at TEXT,
                reviewed_by TEXT
            )
        """)

        conn.commit()
        conn.close()
        logger.info("structured_memory_initialized", db_path=str(self.structured_path))

    def seed_from_json(self, seed_path: Path) -> Dict[str, Any]:
        """Bootstrap deep calibration from the rich seed file."""
        with open(seed_path, "r", encoding="utf-8") as f:
            seed = json.load(f)

        conn = sqlite3.connect(self.structured_path)
        cursor = conn.cursor()

        # Seed user_profile
        profile_items = [
            ("name", seed.get("name")),
            ("born", seed.get("born")),
            ("primary_role", seed.get("primary_role")),
            ("experience", seed.get("experience")),
            ("ai_ventures_summary", json.dumps(seed.get("ai_ventures", {}))),
            ("construction_business", json.dumps(seed.get("construction_business", {}))),
            ("goals_aspirations", json.dumps(seed.get("goals_aspirations", []))),
            ("preferences_output_style", seed.get("preferences_output_style")),
        ]
        for key, value in profile_items:
            if value:
                cursor.execute(
                    "INSERT OR REPLACE INTO user_profile (key, value, updated_at) VALUES (?, ?, ?)",
                    (key, json.dumps(value) if isinstance(value, (dict, list)) else str(value), datetime.utcnow().isoformat())
                )

        # Seed constitution
        for i, principle in enumerate(seed.get("core_principles", [])):
            cursor.execute(
                "INSERT OR IGNORE INTO constitution (principle_id, principle, category, weight, last_referenced) VALUES (?, ?, ?, ?, ?)",
                (f"principle_{i}", principle, "core", 1.0, datetime.utcnow().isoformat())
            )

        # Seed some venture goals
        for venture_name, details in seed.get("ai_ventures", {}).get("smarthinkerz_llc", {}).get("entities", []):
            cursor.execute(
                "INSERT OR IGNORE INTO venture_goals (id, venture, goal, kpi, timeline, status, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (str(uuid.uuid4()), venture_name, details.get("description", "")[:200], "See description", "2026-2027", "active", datetime.utcnow().isoformat())
            )

        conn.commit()
        conn.close()

        # Also embed key facts into vector for semantic recall
        self._embed_seed_facts(seed)

        logger.info("memory_seeded_from_json", user_id=seed.get("user_id"))
        return seed

    def _embed_seed_facts(self, seed: Dict[str, Any]):
        """Embed important calibration facts into vector store for semantic retrieval."""
        documents = []
        metadatas = []
        ids = []

        # Embed name + role
        documents.append(f"Tahir ŞENYURT is Managing Director of Cahit Trading & Contracting L.L.C. with 25+ years in construction across Turkey and GCC. He is also founder of Smarthinkerz LLC in Oman developing AI ventures.")
        metadatas.append({"type": "profile", "category": "identity"})
        ids.append("profile_identity")

        # Embed ventures
        for entity in seed.get("ai_ventures", {}).get("smarthinkerz_llc", {}).get("entities", []):
            doc = f"Venture: {entity.get('name')}. {entity.get('description', '')}"
            documents.append(doc[:2000])
            metadatas.append({"type": "venture", "name": entity.get("name")})
            ids.append(f"venture_{entity.get('name', '').replace(' ', '_')[:40]}")

        # Embed core principles
        for i, p in enumerate(seed.get("core_principles", [])):
            documents.append(f"Core Principle: {p}")
            metadatas.append({"type": "principle", "category": "constitution"})
            ids.append(f"principle_{i}")

        if documents:
            self.collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
            logger.info("seed_facts_embedded", count=len(documents))

    def retrieve_relevant(self, query: str, k: int = 6) -> Dict[str, Any]:
        """Semantic + structured retrieval for current task."""
        results = self.collection.query(query_texts=[query], n_results=k)
        semantic_hits = []
        if results and results.get("documents"):
            for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
                semantic_hits.append({"content": doc, "metadata": meta, "relevance": 1 - dist})

        # Also pull recent structured facts
        structured = self._get_recent_structured_facts(limit=5)

        return {
            "semantic_hits": semantic_hits,
            "structured_facts": structured,
            "retrieval_timestamp": datetime.utcnow().isoformat()
        }

    def _get_recent_structured_facts(self, limit: int = 5) -> List[Dict]:
        conn = sqlite3.connect(self.structured_path)
        cursor = conn.cursor()
        cursor.execute("SELECT key, value, updated_at FROM user_profile ORDER BY updated_at DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [{"key": r[0], "value": r[1], "updated_at": r[2]} for r in rows]

    def get_user_context(self, task: str, existing: Dict[str, Any]) -> Dict[str, Any]:
        """Return rich calibrated context, merging seed + recent updates."""
        if existing and len(existing) > 10:
            return existing  # Already loaded

        conn = sqlite3.connect(self.structured_path)
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM user_profile")
        profile = {row[0]: json.loads(row[1]) if row[1].startswith("{") or row[1].startswith("[") else row[1] for row in cursor.fetchall()}

        cursor.execute("SELECT * FROM constitution ORDER BY weight DESC")
        principles = [{"id": r[0], "principle": r[1], "category": r[2]} for r in cursor.fetchall()]

        conn.close()

        context = {
            **profile,
            "core_principles": principles,
            "memory_last_updated": datetime.utcnow().isoformat(),
            "calibration_depth": "deep_persistent"
        }
        return context

    def log_episodic_trace(self, full_export: Dict[str, Any]):
        """Append full reasoning trace + metadata to daily JSONL episodic log."""
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        log_file = self.episodic_path / f"episodic_{date_str}.jsonl"

        entry = {
            "log_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": settings.user_id,
            "task": full_export.get("task"),
            "protocol_version": full_export.get("protocol_version"),
            "refinement_passes": full_export.get("refinement_passes"),
            "power_audit_score": full_export.get("power_audit", {}).get("score") if full_export.get("power_audit") else None,
            "full_trace": full_export.get("reasoning_trace"),
            "futures": full_export.get("futures_horizons"),
            "symbiosis": full_export.get("symbiosis_optimization"),
            "tool_audit": full_export.get("tool_audit_log"),
            "guardrail_violations": full_export.get("guardrail_violations"),
            "final_response_summary": full_export.get("final_response", "")[:500] + "..."
        }

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        logger.info("episodic_trace_logged", log_file=str(log_file), task=entry["task"][:60])

    def ingest_bulk(self, source_type: str, source_path: Path, metadata: Optional[Dict] = None):
        """
        Bulk ingestion for past conversation histories, PDFs (contracts, memos, curricula), principles.
        Production version would use unstructured or pypdf + chunking + embedding.
        """
        logger.info("bulk_ingestion_started", source_type=source_type, path=str(source_path))
        # Placeholder implementation - real version parses PDF/text, chunks, embeds, and updates structured tables
        # For now, we just log and embed a summary marker
        summary = f"Bulk ingested {source_type} from {source_path.name} on {datetime.utcnow().isoformat()}"
        self.collection.upsert(
            documents=[summary],
            metadatas=[{"type": "ingestion", "source": str(source_path), "source_type": source_type, **(metadata or {})}],
            ids=[f"ingest_{uuid.uuid4()}"]
        )
        logger.info("bulk_ingestion_complete", summary=summary[:100])

    def update_from_interaction(self, task: str, output: str, trace: List[Dict]):
        """Auto-detect and persist durable new facts from successful interactions."""
        # Simple heuristic in bootstrap: if task mentions specific venture or goal, update
        if "brainpower" in task.lower() or "arr" in task.lower():
            conn = sqlite3.connect(self.structured_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO venture_goals (id, venture, goal, kpi, timeline, status, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (str(uuid.uuid4()), "Brainpower AI", f"Updated from interaction: {task[:100]}", "See latest pitch", "2026", "in_progress", datetime.utcnow().isoformat())
            )
            conn.commit()
            conn.close()
            logger.info("auto_updated_venture_goal", venture="Brainpower AI")