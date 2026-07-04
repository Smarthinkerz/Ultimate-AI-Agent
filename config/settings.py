"""
Production-grade settings management using Pydantic Settings.
Loads from .env, supports multiple LLM providers, memory paths, governance flags.
"""

import json
import os
from pathlib import Path
from typing import List, Optional, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLM Configuration
    llm_provider: Literal["openai", "anthropic", "groq", "xai", "local"] = Field(
        default="openai", validation_alias="LLM_PROVIDER"
    )
    llm_model: str = Field(default="gpt-4o", validation_alias="LLM_MODEL")
    llm_temperature: float = Field(default=0.2, validation_alias="LLM_TEMPERATURE", ge=0.0, le=1.0)
    llm_max_tokens: int = Field(default=8192, validation_alias="LLM_MAX_TOKENS")
    openai_api_key: Optional[str] = Field(default=None, validation_alias="OPENAI_API_KEY")
    openai_base_url: Optional[str] = Field(default=None, validation_alias="OPENAI_BASE_URL")
    grok_api_key: Optional[str] = Field(default=None, validation_alias="GROK_API_KEY")

    # Embeddings
    embedding_provider: Literal["openai", "huggingface", "local"] = Field(
        default="openai", validation_alias="EMBEDDING_PROVIDER"
    )
    embedding_model: str = Field(default="text-embedding-3-large", validation_alias="EMBEDDING_MODEL")
    chroma_openai_api_key: Optional[str] = Field(default=None, validation_alias="CHROMA_OPENAI_API_KEY")

    # Memory Paths
    vector_db_path: Path = Field(default=Path("./data/chroma"), validation_alias="VECTOR_DB_PATH")
    structured_db_path: Path = Field(default=Path("./data/agent_memory.sqlite"), validation_alias="STRUCTURED_DB_PATH")
    episodic_log_path: Path = Field(default=Path("./data/episodic_logs"), validation_alias="EPISODIC_LOG_PATH")
    checkpoint_db_path: Path = Field(default=Path("./data/checkpoints.sqlite"), validation_alias="CHECKPOINT_DB_PATH")

    # User & Calibration
    user_id: str = Field(default="tahir_senyurt", validation_alias="USER_ID")
    user_name: str = Field(default="Tahir ŞENYURT", validation_alias="USER_NAME")
    calibration_seed_path: Path = Field(
        default=Path("./config/user_calibration_seed.json"), validation_alias="CALIBRATION_SEED_PATH"
    )

    # Governance & Protocol
    human_approval_required: bool = Field(default=True, validation_alias="HUMAN_APPROVAL_REQUIRED")
    max_refinement_passes: int = Field(default=4, validation_alias="MAX_REFINEMENT_PASSES", ge=1, le=10)
    max_tool_cost_usd: float = Field(default=5.0, validation_alias="MAX_TOOL_COST_USD")
    enable_self_improvement: bool = Field(default=True, validation_alias="ENABLE_SELF_IMPROVEMENT")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")

    # Observability
    langsmith_tracing: bool = Field(default=False, validation_alias="LANGSMITH_TRACING")
    langsmith_api_key: Optional[str] = Field(default=None, validation_alias="LANGSMITH_API_KEY")
    langsmith_project: str = Field(default="ultimate-ai-agent", validation_alias="LANGSMITH_PROJECT")

    # Deployment
    environment: Literal["development", "staging", "production"] = Field(
        default="development", validation_alias="ENVIRONMENT"
    )
    api_host: str = Field(default="0.0.0.0", validation_alias="API_HOST")
    api_port: int = Field(default=8000, validation_alias="API_PORT")
    cors_origins: List[str] = Field(default=["http://localhost:3000"], validation_alias="CORS_ORIGINS")

    # Cultural / Domain
    default_cultural_context: str = Field(default="oman_gcc", validation_alias="DEFAULT_CULTURAL_CONTEXT")
    sharia_review_enabled: bool = Field(default=True, validation_alias="SHARIA_REVIEW_ENABLED")

    # Tool Governance (parsed from JSON string or env)
    allowed_tools: List[str] = Field(
        default=[
            "pdf_analyzer", "financial_modeler", "curriculum_designer",
            "visual_prompt_generator", "japan_market_simulator",
            "decision_graph_modeler", "sharia_ethics_reviewer",
            "code_generator", "web_search_governed"
        ],
        validation_alias="ALLOWED_TOOLS"
    )
    denied_tools: List[str] = Field(
        default=["unrestricted_shell", "arbitrary_code_exec"],
        validation_alias="DENIED_TOOLS"
    )

    model_config = {
        "extra": "ignore",
        "populate_by_name": True,
    }

    @field_validator("allowed_tools", "denied_tools", mode="before")
    @classmethod
    def parse_list_from_env(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [item.strip() for item in v.split(",") if item.strip()]
        return v

    def get_llm(self):
        """Factory for LangChain chat model based on provider."""
        from langchain_openai import ChatOpenAI
        # Extend with if-elif for anthropic, groq, etc. as needed.
        # For xAI/Grok: base_url + api_key works if OpenAI compatible.
        if self.llm_provider in ["openai", "xai", "groq"]:
            return ChatOpenAI(
                model=self.llm_model,
                temperature=self.llm_temperature,
                max_tokens=self.llm_max_tokens,
                api_key=self.openai_api_key,
                base_url=self.openai_base_url,
            )
        # Placeholder for other providers - production would add langchain-anthropic etc.
        raise NotImplementedError(f"Provider {self.llm_provider} not fully wired in bootstrap. Add adapter.")

    def get_embeddings(self):
        """Factory for embeddings."""
        from langchain_openai import OpenAIEmbeddings
        if self.embedding_provider == "openai":
            return OpenAIEmbeddings(
                model=self.embedding_model,
                api_key=self.openai_api_key,
            )
        # Add huggingface / local fallback in full impl
        raise NotImplementedError("Only OpenAI embeddings wired in this production bootstrap.")


# Global settings instance
settings = Settings()

print(f"DEBUG: OPENAI_API_KEY from os.environ: {os.environ.get('OPENAI_API_KEY')}")
print(f"DEBUG: settings.openai_api_key: {settings.openai_api_key}")

# Ensure data directories exist
for p in [settings.vector_db_path, settings.episodic_log_path, settings.structured_db_path.parent]:
    p.mkdir(parents=True, exist_ok=True)