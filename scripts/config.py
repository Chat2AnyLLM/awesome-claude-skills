#!/usr/bin/env python3
"""
Configuration handling for Claude skills scraper
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional

class Config:
    """Configuration handler for the skills scraper."""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize configuration from YAML file."""
        self.config_path = Path(config_path)
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    @property
    def sources_config(self) -> List[Dict[str, Any]]:
        """Get sources configuration."""
        return self._config.get("sources", [])

    @property
    def generation_config(self) -> Dict[str, Any]:
        """Get generation settings."""
        return self._config.get("generation", {})

    @property
    def logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return self._config.get("logging", {})

    def get_enabled_sources(self) -> List[Dict[str, Any]]:
        """Get list of enabled sources sorted by priority."""
        sources = [source for source in self.sources_config if source.get("enabled", True)]
        return sorted(sources, key=lambda x: x.get("priority", 999))

    def get_output_file(self) -> str:
        """Get output file path."""
        return self.generation_config.get("output_file", "README.md")

    def get_logging_level(self) -> str:
        """Get logging level."""
        return self.logging_config.get("level", "INFO")