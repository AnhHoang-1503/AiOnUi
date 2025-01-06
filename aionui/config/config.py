import os
from typing import Optional
from pydantic import BaseModel, Field
import yaml
from aionui.enums.platform import Platform
from ..utils.common import get_platform, get_user_data_dir, get_chrome_binary_path


class Config(BaseModel):
    platform: Platform = Field(default_factory=get_platform, frozen=True)
    """Current platform"""
    user_data_dir: Optional[str] = Field(default_factory=lambda: get_user_data_dir(get_platform()))
    """User data directory"""
    chrome_binary_path: Optional[str] = Field(default_factory=lambda: get_chrome_binary_path(get_platform()))
    """Chrome binary path"""
    debug_port: Optional[int] = Field(default=9222)
    """Debug port to connect over CDP (Chrome DevTools Protocol)"""

    def __init__(self, config_path: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        if config_path:
            self.load_config(config_path)

    def load_config(self, config_path: str) -> None:
        """
        Loads the config from a YAML file.
        """
        if not os.path.isfile(config_path):
            raise FileNotFoundError(f"Config file not found at {config_path}")
        if not config_path.endswith(".yaml"):
            raise ValueError("Config file must be a YAML file")
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
            validated_data = self.model_validate(config)
            for key, value in validated_data.model_dump().items():
                if hasattr(self, key) and not self.model_fields[key].frozen:
                    setattr(self, key, value)
