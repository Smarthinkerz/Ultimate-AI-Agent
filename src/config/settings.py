# config/settings.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: list[str] = ["*"]
    user_id: str = "tahir_senyurt"
    max_tool_cost_usd: float = 10.0
    max_refinement_passes: int = 4
    calibration_seed_path: str = "config/user_calibration_seed.json"
    enable_self_improvement: bool = True
    human_approval_required: bool = False

# This is the instance your code imports everywhere
settings = Settings()
