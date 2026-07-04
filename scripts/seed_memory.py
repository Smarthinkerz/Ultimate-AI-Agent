"""
Hybrid memory manager for the Ultimate AI Agent.
Handles both episodic (logs) and semantic (vector DB) memory storage.
"""

import os
import json
from config.settings import settings              # ✅ fixed import
from src.observability.logging import get_structured_logger

logger = get_structured_logger(__name__)


class HybridMemoryManager:
    def __init__(self, settings=settings):
        """
        Initialize the hybrid memory manager.
        - Episodic memory stored in JSON log files
        - Semantic memory stored in vector DB (e.g., Chroma)
        """
        self.settings = settings
        self.episodic_dir = os.path.join("data", "episodic_logs")
        self.semantic_dir = os.path.join("data", "chroma")

        os.makedirs(self.episodic_dir, exist_ok=True)
        os.makedirs(self.semantic_dir, exist_ok=True)

        logger.info("HybridMemoryManager initialized",
                    episodic_dir=self.episodic_dir,
                    semantic_dir=self.semantic_dir)

    def add_memory(self, item: dict, user_id: str = None):
        """
        Add a memory item.
        - If episodic: append to JSON log file
        - If semantic: store in vector DB (placeholder for now)
        """
        # Episodic storage
        episodic_file = os.path.join(self.episodic_dir, f"{user_id or 'default'}_log.json")
        try:
            if os.path.exists(episodic_file):
                with open(episodic_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = []

            data.append(item)

            with open(episodic_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            logger.info("Episodic memory updated", user_id=user_id, item=item)

        except Exception as e:
            logger.error("Failed to update episodic memory", error=str(e))

        # Semantic storage (placeholder)
        # TODO: integrate with Chroma or other vector DB
        semantic_file = os.path.join(self.semantic_dir, f"{user_id or 'default'}_semantic.json")
        try:
            if os.path.exists(semantic_file):
                with open(semantic_file, "r", encoding="utf-8") as f:
                    vectors = json.load(f)
            else:
                vectors = []

            vectors.append(item)

            with open(semantic_file, "w", encoding="utf-8") as f:
                json.dump(vectors, f, indent=2)

            logger.info("Semantic memory updated", user_id=user_id, item=item)

        except Exception as e:
            logger.error("Failed to update semantic memory", error=str(e))
