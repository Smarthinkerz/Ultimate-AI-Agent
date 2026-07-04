# src/config/settings.py

from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API server
    api_host: str = Field(default="0.0.0.0", validation_alias="API_HOST")
    api_port: int = Field(default=8000, validation_alias="API_PORT")
    cors_origins: list[str] = Field(default=["*"], validation_alias="CORS_ORIGINS")

    # LLM
    llm_provider: str = Field(default="openai", validation_alias="LLM_PROVIDER")
    llm_model: str = Field(default="gpt-4o", validation_alias="LLM_MODEL")
    llm_temperature: float = Field(default=0.2, validation_alias="LLM_TEMPERATURE")
    llm_max_tokens: int = Field(default=8192, validation_alias="LLM_MAX_TOKENS")
    openai_api_key: Optional[str] = Field(default=None, validation_alias="OPENAI_API_KEY")
    openai_base_url: Optional[str] = Field(default=None, validation_alias="OPENAI_BASE_URL")
    grok_api_key: Optional[str] = Field(default=None, validation_alias="GROK_API_KEY")

    # Embeddings
    embedding_provider: str = Field(default="openai", validation_alias="EMBEDDING_PROVIDER")
    embedding_model: str = Field(default="text-embedding-3-large", validation_alias="EMBEDDING_MODEL")
    chroma_openai_api_key: Optional[str] = Field(default=None, validation_alias="CHROMA_OPENAI_API_KEY")

    # Memory backends
    vector_db_path: Path = Field(default=Path("./data/chroma"), validation_alias="VECTOR_DB_PATH")
    structured_db_path: Path = Field(default=Path("./data/agent_memory.sqlite"), validation_alias="STRUCTURED_DB_PATH")
    episodic_log_path: Path = Field(default=Path("./data/episodic_logs"), validation_alias="EPISODIC_LOG_PATH")
    checkpoint_db_path: Path = Field(default=Path("./data/checkpoints.sqlite"), validation_alias="CHECKPOINT_DB_PATH")

    # User calibration
    user_id: str = Field(default="tahir_senyurt", validation_alias="USER_ID")
    user_name: str = Field(default="Tahir ŞENYURT", validation_alias="USER_NAME")
    calibration_seed_path: str = Field(default="config/user_calibration_seed.json", validation_alias="CALIBRATION_SEED_PATH")

    # Governance & safety
    human_approval_required: bool = Field(default=False, validation_alias="HUMAN_APPROVAL_REQUIRED")
    max_refinement_passes: int = Field(default=4, validation_alias="MAX_REFINEMENT_PASSES")
    max_tool_cost_usd: float = Field(default=10.0, validation_alias="MAX_TOOL_COST_USD")
    enable_self_improvement: bool = Field(default=True, validation_alias="ENABLE_SELF_IMPROVEMENT")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")

    # Observability
    langsmith_tracing: bool = Field(default=False, validation_alias="LANGSMITH_TRACING")
    langsmith_api_key: Optional[str] = Field(default=None, validation_alias="LANGSMITH_API_KEY")
    langsmith_project: str = Field(default="ultimate-ai-agent", validation_alias="LANGSMITH_PROJECT")

    # Deployment
    environment: str = Field(default="development", validation_alias="ENVIRONMENT")

    model_config = {
        "extra": "ignore",
        "populate_by_name": True,
    }


# This is the instance your code imports everywhere
settings = Settings()
