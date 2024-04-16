from __future__ import annotations

import json

from pydantic import BaseModel
from pydantic_settings import BaseSettings
from backend.src.consts.directory import ROOT_DIRECTORY
from backend.src.utils.log import get_logger
from backend.src.utils.json_encoder import CustomJsonEncoder

_logger = get_logger(__name__)


class OpenAIConfiguration(BaseModel):
    api_key: str


class PineconeConfiguration(BaseModel):
    api_key: str


class StreamlitConfiguration(BaseModel):
    api_key: str


class Configurations(BaseSettings):
    openai__api_key: str
    pinecone__api_key: str
    streamlit__api_key: str

    class Config:
        env_file = ROOT_DIRECTORY / ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"

    def __init__(self) -> None:
        super().__init__()
        self.is_env_exists()
        self.is_all_variables_loaded()

    def is_env_exists(self) -> None:
        env_file_path = self.Config.env_file
        if not env_file_path.exists():
            _logger.warning(f"Environment file does not exist: {env_file_path}")

    def is_all_variables_loaded(self) -> None:
        for section_name, section in vars(self).items():
            if isinstance(section, BaseModel):
                for key, value in section.dict().items():
                    if value is None:
                        _logger.warning(f"{section_name}.{key} was not found!!")

    def __str__(self) -> str:
        settings_dict = self.dict()

        for _, section in settings_dict.items():
            for k, v in section.items():
                if isinstance(v, str):
                    section[k] = f"{v[0]}***{v[-1]}" if len(v) > 1 else "*****"

        return json.dumps(settings_dict, indent=4, cls=CustomJsonEncoder)














