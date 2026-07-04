# config/settings.py

from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API server
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: list[str] = ["*"]

    # LLM
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o"
    llm_temperature: float = 0.2
    llm_max_tokens: int = 8192
    openai_api_key: Optional[str] = None
    openai_base_url: Optional[str] = None

    # Embeddings
    embedding_provider: str = "openai"
    embedding_model: str = "text-embedding-3-large"

    # Memory backends
    vector_db_path: Path = Path("./data/chroma")
    structured_db_path: Path = Path("./data/agent_memory.sqlite")
    episodic_log_path: Path = Path("./data/episodic_logs")
    checkpoint_db_path: Path = Path("./data/checkpoints.sqlite")

    # User calibration
    user_id: str = "tahir_senyurt"
    user_name: str = "Tahir ŞENYURT"
    calibration_seed_path: str = "config/user_calibration_seed.json"

    # Governance & safety
    human_approval_required: bool = False
    max_refinement_passes: int = 4
    max_tool_cost_usd: float = 10.0
    enable_self_improvement: bool = True
    log_level: str = "INFO"

    # Observability
    langsmith_tracing: bool = False
    langsmith_api_key: Optional[str] = None
    langsmith_project: str = "ultimate-ai-agent"

    # Deployment
    environment: str = "development"

    class Config:
        extra = "ignore"


# This is the instance your code imports everywhere
settings = Settings()
