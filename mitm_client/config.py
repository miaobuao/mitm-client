import logging
from pathlib import Path
from typing import Literal

import json5
from pydantic import BaseModel, Field

logger = logging.getLogger("mitmproxy-client")


class RecorderConfig(BaseModel):
    match: list[str] = Field(default_factory=list)
    writing_mode: Literal["wb", "ab"] = "wb"


class ReplayConfig(BaseModel):
    passthrough_rules: list[str] = Field(default_factory=list)


class AppConfig(BaseModel):
    recorder: RecorderConfig = Field(default_factory=RecorderConfig)
    replay: ReplayConfig = Field(default_factory=ReplayConfig)


def load_config(config_path: Path) -> AppConfig:
    if not config_path.exists():
        logger.warning(f"Config file not found at {config_path}, using default config.")
        return AppConfig()

    with open(config_path, "r") as f:
        config_data = json5.load(f)
        return AppConfig.model_validate(config_data)


if __name__ == "__main__":
    config = load_config(Path("./config.json5"))
    print(config)
