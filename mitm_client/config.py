import json
import logging
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

logger = logging.getLogger("mitmproxy-client")


class RecorderConfig(BaseModel):
    match: list[str] = Field(default_factory=list)
    writing_mode: Literal["wb", "ab"] = "wb"


class AppConfig(BaseModel):
    recorder: RecorderConfig = Field(default_factory=RecorderConfig)


def load_config(config_path: Path) -> AppConfig:
    if not config_path.exists():
        logger.warning(f"Config file not found at {config_path}, using default config.")
        return AppConfig()

    with open(config_path, "r") as f:
        config_data = json.load(f)
        return AppConfig.model_validate(config_data)
