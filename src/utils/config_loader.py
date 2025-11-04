"""
Configuration loader for YAML configs and environment variables.
"""

import os
from pathlib import Path
from typing import Dict, Any

import yaml
from dotenv import load_dotenv
from loguru import logger


class ConfigLoader:
    """Loads and merges configuration from YAML files and environment variables."""

    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}

    def load(self) -> Dict[str, Any]:
        """Load configuration from file and environment."""
        # Load environment variables
        load_dotenv()

        # Load YAML configuration
        if self.config_path.exists():
            with self.config_path.open("r") as f:
                self.config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {self.config_path}")
        else:
            logger.warning(f"Configuration file not found: {self.config_path}")
            self.config = {}

        # Override with environment variables
        self._apply_env_overrides()

        return self.config

    def _apply_env_overrides(self):
        """Apply environment variable overrides."""
        # Dashboard settings
        if os.getenv("DASHBOARD_HOST"):
            self.config.setdefault("dashboard", {})["host"] = os.getenv("DASHBOARD_HOST")

        if os.getenv("DASHBOARD_PORT"):
            self.config.setdefault("dashboard", {})["port"] = int(os.getenv("DASHBOARD_PORT"))

        # Logging
        if os.getenv("LOG_LEVEL"):
            self.config.setdefault("logging", {})["level"] = os.getenv("LOG_LEVEL")

        # Debug mode
        if os.getenv("DEBUG"):
            debug_value = os.getenv("DEBUG").lower() in ["true", "1", "yes"]
            self.config.setdefault("dashboard", {})["debug"] = debug_value

        logger.debug("Environment variable overrides applied")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key."""
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def save(self, output_path: str = None):
        """Save current configuration to file."""
        path = Path(output_path) if output_path else self.config_path

        with path.open("w") as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)

        logger.info(f"Configuration saved to {path}")


def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """Convenience function to load configuration."""
    loader = ConfigLoader(config_path)
    return loader.load()
