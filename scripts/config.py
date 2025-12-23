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
        # If the config_path is absolute or exists, use it directly
        if self.config_path.is_absolute() or self.config_path.exists():
            config_file = self.config_path
        else:
            # Search for config.yaml in current directory and parent directories
            current_dir = Path.cwd()
            config_file = None

            # Search up to 3 levels up the directory tree
            for _ in range(4):
                candidate = current_dir / "config.yaml"
                if candidate.exists():
                    config_file = candidate
                    break
                if current_dir.parent == current_dir:
                    break  # Reached root directory
                current_dir = current_dir.parent

            if config_file is None:
                raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(config_file, 'r', encoding='utf-8') as f:
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

    @property
    def parallel_config(self) -> Dict[str, Any]:
        """Get parallel processing configuration."""
        return self._config.get("parallel", {})

    def get_max_workers(self) -> int:
        """Get maximum number of parallel workers."""
        return self.parallel_config.get("max_workers", 8)