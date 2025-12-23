#!/usr/bin/env python3
"""
Validation utilities for skills scraper
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class Validator:
    """Validation utilities for skills data."""

    @staticmethod
    def validate_json_data(data: Any) -> bool:
        """Basic validation for JSON data structure."""
        if not isinstance(data, dict):
            logger.warning("Data is not a dictionary")
            return False
        return True

    @staticmethod
    def validate_marketplace_data(marketplace_data: Dict[str, Any]) -> bool:
        """Validate marketplace data structure."""
        required_fields = ["id", "name", "repoOwner", "repoName"]
        for field in required_fields:
            if field not in marketplace_data:
                logger.warning(f"Missing required field '{field}' in marketplace data")
                return False
        return True