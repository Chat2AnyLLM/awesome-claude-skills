"""Base fetching framework for skills, agents, and plugins."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Generic, List, Optional, TypeVar
import logging

logger = logging.getLogger(__name__)

# Generic type for entity (Skill, Agent, Plugin, etc.)
T = TypeVar('T')

@dataclass
class RepoConfig:
    """Generic repository configuration."""
    owner: str
    name: str
    branch: Optional[str] = None  # None means auto-detect default branch
    path: Optional[str] = None  # Subdirectory path (skills_path, agents_path, etc.)
    exclude: Optional[List[str]] = None  # Paths/patterns to exclude from scanning
    enabled: bool = True


class EntityParser(ABC, Generic[T]):
    """Abstract parser for converting raw data to entities."""

    @abstractmethod
    def parse_from_file(
        self,
        file_path: Path,
        repo_config: RepoConfig
    ) -> Optional[T]:
        """Parse entity from a file.

        Args:
            file_path: Path to the file to parse
            repo_config: Repository configuration

        Returns:
            Parsed entity or None if invalid
        """
        pass

    @abstractmethod
    def get_file_pattern(self) -> str:
        """Get glob pattern for entity files (e.g., 'SKILL.md', '*.md')."""
        pass

    @abstractmethod
    def create_entity_key(self, repo_config: RepoConfig, entity_name: str) -> str:
        """Create unique key for entity."""
        pass


class BaseEntityFetcher(ABC, Generic[T]):
    """Base class for fetching entities from repositories.

    This provides a unified interface for fetching skills, agents, plugins, etc.
    """

    def __init__(self, parser: EntityParser[T], cache_ttl: int = 3600):
        """Initialize fetcher.

        Args:
            parser: Parser for converting files to entities
            cache_ttl: Cache time-to-live in seconds
        """
        self.parser = parser
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, Any] = {}

    def fetch_from_repos(
        self,
        repos: List[RepoConfig],
        max_workers: int = 8,
        use_cache: bool = True
    ) -> List[T]:
        """Fetch entities from multiple repositories in parallel.

        Args:
            repos: List of repository configurations
            max_workers: Maximum number of concurrent fetchers
            use_cache: Whether to use caching

        Returns:
            List of discovered entities
        """
        from .parallel import ParallelFetcher

        # Filter enabled repos
        enabled_repos = [r for r in repos if r.enabled]

        if not enabled_repos:
            logger.warning("No enabled repositories found")
            return []

        logger.info(f"Fetching from {len(enabled_repos)} repositories in parallel")

        # Use parallel fetcher
        parallel_fetcher = ParallelFetcher(
            fetcher_func=self._fetch_from_single_repo,
            max_workers=max_workers
        )

        results = parallel_fetcher.fetch_all(enabled_repos)

        # Flatten results
        all_entities = []
        for entities in results:
            all_entities.extend(entities)

        logger.info(f"Total entities fetched: {len(all_entities)}")
        return all_entities

    def _fetch_from_single_repo(self, repo: RepoConfig) -> List[T]:
        """Fetch entities from a single repository.

        Args:
            repo: Repository configuration

        Returns:
            List of entities found in the repository
        """
        from .repository import GitRepository

        git_repo = GitRepository(
            owner=repo.owner,
            name=repo.name,
            branch=repo.branch
        )

        entities = []

        try:
            # Clone/download repository
            with git_repo.clone() as (temp_dir, actual_branch):
                # Get scan directories (support multiple paths separated by '|')
                scan_dirs = self._get_scan_dirs(temp_dir, repo)

                for scan_dir in scan_dirs:
                    if not scan_dir.exists():
                        logger.warning(f"Path not found: {scan_dir}")
                        continue

                    # Find entity files
                    file_pattern = self.parser.get_file_pattern()
                    for entity_file in scan_dir.rglob(file_pattern):
                        # Check if file should be excluded
                        if self._should_exclude_file(entity_file, temp_dir, repo):
                            logger.debug(f"Excluded file: {entity_file}")
                            continue

                        try:
                            entity = self.parser.parse_from_file(entity_file, repo)
                            if entity:
                                entities.append(entity)
                                logger.debug(f"Found entity: {entity}")
                        except Exception as e:
                            logger.warning(f"Failed to parse {entity_file}: {e}")

        except Exception as e:
            logger.error(f"Failed to fetch from {repo.owner}/{repo.name}: {e}")

        return entities

    def _get_scan_dirs(self, temp_dir: Path, repo: RepoConfig) -> List[Path]:
        """Get scan directories from repo path (supports multiple paths separated by '|').

        For agents, if no path is specified, automatically find all 'agents' directories
        in the repository. For other entity types, use the specified path or repo root.

        Args:
            temp_dir: Repository root directory
            repo: Repository configuration

        Returns:
            List of directories to scan
        """
        if not repo.path:
            # No path specified - different behavior for different entity types
            if hasattr(self.parser, '__class__') and 'Agent' in self.parser.__class__.__name__:
                # For agents: automatically find all 'agents' directories in the repo
                return self._find_agent_directories(temp_dir)
            else:
                # For other entities: scan from repo root
                return [temp_dir]

        # Split by '|' to support multiple paths
        paths = [p.strip().strip('/') for p in repo.path.split('|') if p.strip()]

        scan_dirs = []
        for path in paths:
            if path:  # Skip empty paths
                scan_dirs.append(temp_dir / path)
            else:
                scan_dirs.append(temp_dir)  # Empty path means repo root

        return scan_dirs

    def _find_agent_directories(self, repo_root: Path) -> List[Path]:
        """Find all directories that might contain agents.

        Looks for common agent directory names throughout the repository.

        Args:
            repo_root: Repository root directory

        Returns:
            List of directories that likely contain agents
        """
        agent_dirs = []

        # Common agent directory names to look for
        agent_dir_names = {'agents', 'agent', 'claude-agents', 'subagents', 'ai-agents'}

        try:
            # Walk through all directories in the repository
            for dir_path in repo_root.rglob('*'):
                if dir_path.is_dir() and dir_path.name.lower() in agent_dir_names:
                    agent_dirs.append(dir_path)
        except Exception as e:
            logger.warning(f"Error scanning for agent directories: {e}")
            # Fallback to repo root if scanning fails
            return [repo_root]

        # If no agent directories found, fall back to repo root
        if not agent_dirs:
            logger.debug(f"No agent directories found, using repo root: {repo_root}")
            return [repo_root]

        logger.debug(f"Found agent directories: {[str(d.relative_to(repo_root)) for d in agent_dirs]}")
        return agent_dirs

    def _should_exclude_file(self, file_path: Path, repo_root: Path, repo_config: RepoConfig) -> bool:
        """Check if a file should be excluded based on exclude patterns.

        Args:
            file_path: Absolute path to the file
            repo_root: Root directory of the repository
            repo_config: Repository configuration

        Returns:
            True if the file should be excluded, False otherwise
        """
        # Get relative path from repo root
        try:
            rel_path = file_path.relative_to(repo_root)
            rel_path_str = str(rel_path)
        except ValueError:
            # File is not under repo root (shouldn't happen, but be safe)
            return False

        # Always exclude paths containing "backup" (hardcoded rule)
        if "backup" in rel_path_str.lower():
            return True

        # Check configured exclude patterns
        if not repo_config.exclude:
            return False

        # Check each exclude pattern
        for pattern in repo_config.exclude:
            # Handle different pattern types
            if pattern == "**/README.md":
                # Special case: exclude all README.md files in any directory
                if file_path.name == "README.md":
                    return True
            elif pattern.startswith("**/"):
                # Pattern like **/filename - match filename anywhere in repo
                filename = pattern[3:]  # Remove **/
                if file_path.name == filename:
                    return True
            elif pattern.startswith("*"):
                # Pattern like *.md - check filename
                if file_path.name == pattern[1:]:
                    return True
            elif pattern.endswith("*"):
                # Pattern like "backups/*" - check if path starts with pattern
                if rel_path_str.startswith(pattern[:-1]):
                    return True
            elif pattern in rel_path_str:
                # Direct substring match
                return True

        return False