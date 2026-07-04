import json
from pathlib import Path

def load_user_calibration(seed_file: str = "config/user_calibration_seed.json") -> dict:
    """
    Load user calibration settings from a JSON seed file.
    Returns a dict with calibration data.
    """
    path = Path(seed_file)
    if not path.exists():
        raise FileNotFoundError(f"Calibration seed file not found: {seed_file}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
