#!/usr/bin/env python3
"""
HTTP and Git fetching utilities for skills scraper
"""

import requests
import json
import logging
import time
import hashlib
import tempfile
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin
from .validators import Validator

logger = logging.getLogger(__name__)

class Fetcher:
    """HTTP and Git data fetching utilities."""

    def __init__(self, timeout: int = 30, cache_ttl: int = 3600):
        self.timeout = timeout
        self.cache_ttl = cache_ttl  # Cache TTL in seconds (default 1 hour)
        self.session = requests.Session()
        self.cache: Dict[str, Dict[str, Any]] = {}  # URL -> {data, timestamp}

    def _get_cache_key(self, url: str) -> str:
        """Generate cache key from URL."""
        return hashlib.md5(url.encode()).hexdigest()

    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is still valid."""
        if 'timestamp' not in cache_entry:
            return False
        return (time.time() - cache_entry['timestamp']) < self.cache_ttl

    def _get_cached_data(self, url: str) -> Optional[Dict[str, Any]]:
        """Get data from cache if valid."""
        cache_key = self._get_cache_key(url)
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if self._is_cache_valid(cache_entry):
                logger.debug("Cache hit for: %s", url)
                return cache_entry['data']
            else:
                logger.debug("Cache expired for: %s", url)
                del self.cache[cache_key]
        return None

    def _set_cached_data(self, url: str, data: Dict[str, Any]):
        """Store data in cache."""
        cache_key = self._get_cache_key(url)
        self.cache[cache_key] = {
            'data': data,
            'timestamp': time.time()
        }

    def fetch_json(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch JSON data from URL with caching and performance monitoring."""
        # Check cache first
        cached_data = self._get_cached_data(url)
        if cached_data is not None:
            return cached_data

        start_time = time.time()
        try:
            logger.info("Fetching data from: %s", url)
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            fetch_time = time.time() - start_time
            logger.info("Successfully fetched data from %s in %.2f seconds", url, fetch_time)

            if not Validator.validate_json_data(data):
                return None

            # Cache the successful response
            self._set_cached_data(url, data)

            return data

        except requests.exceptions.RequestException as e:
            fetch_time = time.time() - start_time
            logger.error("Failed to fetch %s in %.2f seconds: %s", url, fetch_time, e)
            return None
        except json.JSONDecodeError as e:
            fetch_time = time.time() - start_time
            logger.error("Failed to parse JSON from %s in %.2f seconds: %s", url, fetch_time, e)
            return None

    def fetch_skill_repos_from_source(self, source_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch skill repository data from a configured source."""
        url = source_config.get("url")
        if not url:
            logger.error("No URL specified in source config")
            return []

        data = self.fetch_json(url)
        if not data:
            return []

        # The expected format is a dict with repo IDs as keys
        repos = []
        for repo_id, repo_data in data.items():
            if isinstance(repo_data, dict):
                repo_data["id"] = repo_id
                repo_data["source_url"] = url
                repos.append(repo_data)

        logger.info("Fetched %d skill repositories from %s", len(repos), url)
        return repos

    def clone_and_scan_repository(self, repo_owner: str, repo_name: str, repo_branch: str = "main", skills_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Clone a repository and scan for SKILL.md files to extract skills."""
        skills = []

        # Create temporary directory for cloning
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            repo_url = f"https://github.com/{repo_owner}/{repo_name}.git"

            try:
                logger.info(f"Cloning repository: {repo_owner}/{repo_name}")

                # Clone the repository
                result = subprocess.run(
                    ["git", "clone", "--depth", "1", "--branch", repo_branch, repo_url, str(temp_path / "repo")],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )

                if result.returncode != 0:
                    logger.error(f"Failed to clone {repo_url}: {result.stderr}")
                    return skills

                repo_path = temp_path / "repo"

                # Determine scan directory
                scan_dir = repo_path
                if skills_path:
                    scan_dir = repo_path / skills_path.strip("/")
                    if not scan_dir.exists():
                        logger.warning(f"Skills path not found: {scan_dir}")
                        return skills

                # Scan for SKILL.md files recursively
                for skill_md_path in scan_dir.rglob("SKILL.md"):
                    skill_dir = skill_md_path.parent
                    if not skill_dir.is_dir():
                        continue

                    # Parse the SKILL.md file
                    skill_data = self._parse_skill_md(skill_md_path)
                    if not skill_data:
                        continue

                    # Build skill entry
                    try:
                        rel_path = skill_dir.relative_to(scan_dir)
                        source_directory = str(rel_path).replace("\\", "/")

                        # Handle root level SKILL.md
                        if source_directory == ".":
                            source_directory = "."
                            directory = skill_dir.name if skill_dir != scan_dir else repo_name
                        else:
                            directory = skill_dir.name

                        path_from_repo_root = skill_dir.relative_to(repo_path)
                        readme_path = str(path_from_repo_root).replace("\\", "/")

                        skill = {
                            "id": f"{repo_owner}/{repo_name}:{source_directory}",
                            "name": skill_data.get("name", directory),
                            "description": skill_data.get("description", ""),
                            "category": skill_data.get("category", "Uncategorized"),
                            "marketplace_id": f"{repo_owner}/{repo_name}",
                            "repo_owner": repo_owner,
                            "repo_name": repo_name,
                            "repo_branch": repo_branch,
                            "directory": directory,
                            "readme_url": f"https://github.com/{repo_owner}/{repo_name}/tree/{repo_branch}/{readme_path}",
                            "tags": skill_data.get("tags", [])
                        }
                        skills.append(skill)
                        logger.debug(f"Found skill: {skill['id']}")

                    except ValueError as e:
                        logger.warning(f"Failed to process skill at {skill_dir}: {e}")
                        continue

            except subprocess.TimeoutExpired:
                logger.error(f"Timeout cloning repository: {repo_url}")
            except Exception as e:
                logger.error(f"Error processing repository {repo_owner}/{repo_name}: {e}")

        logger.info(f"Found {len(skills)} skills in {repo_owner}/{repo_name}")
        return skills

    def _parse_skill_md(self, skill_md_path: Path) -> Optional[Dict[str, Any]]:
        """Parse a SKILL.md file to extract skill metadata."""
        try:
            with open(skill_md_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Simple frontmatter parsing (similar to code-assistant-manager)
            skill_data = {}

            # Extract name from first header
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('# '):
                    skill_data["name"] = line[2:].strip()
                    break

            # Look for description (text after name until next header or special markers)
            in_description = False
            description_lines = []

            for line in lines:
                line = line.strip()
                if line.startswith('# ') and skill_data.get("name") and line[2:].strip() == skill_data["name"]:
                    in_description = True
                    continue
                elif line.startswith('#') and in_description:
                    break
                elif in_description and line:
                    description_lines.append(line)

            if description_lines:
                skill_data["description"] = ' '.join(description_lines).strip()

            # Look for category (common patterns) - improved parsing
            content_lower = content.lower()
            category = None

            # Try different patterns for category extraction
            if "category:" in content_lower or "categories:" in content_lower:
                # Simple extraction - look for lines containing category
                for line in lines:
                    line_lower = line.lower().strip()
                    if "category:" in line_lower or "categories:" in line_lower:
                        # Extract everything after the colon
                        parts = line.split(":", 1)
                        if len(parts) > 1:
                            category = parts[1].strip().strip("*").strip()
                            # Clean up common issues
                            category = category.strip('"').strip("'").strip()
                            # Remove any trailing comments or malformed text
                            category = category.split('#')[0].strip()
                            category = category.split('//')[0].strip()
                            category = category.split(';')[0].strip()
                            break

            # If no category found, try to extract from content
            if not category:
                # Look for patterns like "**Category:** Something"
                for line in lines:
                    if "**category:**" in line.lower() or "**categories:**" in line.lower():
                        parts = line.split(":", 1)
                        if len(parts) > 1:
                            category = parts[1].strip().strip("*").strip()
                            break

            # Clean up category if found
            if category:
                # Remove any remaining special characters and clean it up
                import re
                category = re.sub(r'[^\w\s-]', '', category).strip()
                # Capitalize first letter
                if category:
                    category = category[0].upper() + category[1:]

            skill_data["category"] = category or "Uncategorized"

            # Look for tags
            tags = []
            for line in lines:
                line_lower = line.lower().strip()
                if "tags:" in line_lower or "tag:" in line_lower:
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        tag_part = parts[1].strip()
                        # Simple comma-separated parsing
                        tag_list = [tag.strip().strip("*").strip() for tag in tag_part.split(",")]
                        tags.extend(tag_list)
            if tags:
                skill_data["tags"] = tags

            return skill_data

        except Exception as e:
            logger.warning(f"Failed to parse SKILL.md at {skill_md_path}: {e}")
            return None

    def fetch_skills_from_marketplace(self, marketplace_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch all skills from a marketplace by cloning its repository."""
        repo_owner = marketplace_data.get("repoOwner")
        repo_name = marketplace_data.get("repoName")
        repo_branch = marketplace_data.get("repoBranch", "main")

        if not repo_owner or not repo_name:
            logger.warning("Missing repo information for marketplace: %s", marketplace_data.get("id"))
            return []

        # Clone and scan the repository
        skills = self.clone_and_scan_repository(repo_owner, repo_name, repo_branch)
        return skills