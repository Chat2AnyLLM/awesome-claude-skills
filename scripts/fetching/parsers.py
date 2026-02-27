"""Entity-specific parsers for skills."""

from pathlib import Path
from typing import Optional, Dict, Any
import logging
import yaml

from .base import EntityParser, RepoConfig
from ..models import Skill

logger = logging.getLogger(__name__)


class SkillParser(EntityParser[Skill]):
    """Parser for skill entities."""

    def parse_from_file(
        self,
        file_path: Path,
        repo_config: RepoConfig
    ) -> Optional[Skill]:
        """Parse skill from SKILL.md file."""
        # Only check for SKILL.md files - agent files should not be considered skills
        # unless they have a SKILL.md file in their folder
        if file_path.name.lower() != "skill.md":
            return None

        skill_dir = file_path.parent

        # Skip generated/cache skills that start with 'cam_'
        if skill_dir.name.startswith('cam_'):
            logger.debug(f"Skipping generated skill directory: {skill_dir.name}")
            return None

        # Parse metadata from the file
        meta = self._parse_metadata(file_path)
        if meta is None:
            return None

        # Calculate paths
        directory = skill_dir.name

        # Find the repo root by looking for .git directory
        repo_root_search_dir = skill_dir

        repo_root = repo_root_search_dir
        # Check current dir first
        if (repo_root_search_dir / '.git').exists():
            repo_root = repo_root_search_dir
        else:
            for parent in repo_root_search_dir.parents:
                if (parent / '.git').exists():
                    repo_root = parent
                    break
            else:
                # Fallback to the original logic if .git not found
                try:
                    repo_root = repo_root_search_dir.parents[-2]
                except IndexError:
                    repo_root = repo_root_search_dir.parent

        # Get relative path from repo root to skill directory
        try:
            repo_relative_path = str(skill_dir.relative_to(repo_root))
        except ValueError:
            repo_relative_path = directory

        # If skills_path is set, adjust repo_relative_path accordingly
        if repo_config.path:
            skills_path = Path(repo_config.path)
            try:
                # Try to make repo_relative_path relative to skills_path
                full_skills_path = repo_root / skills_path
                repo_relative_path = str(skill_dir.relative_to(full_skills_path))
            except ValueError:
                # If we can't make it relative, keep the full path but warn
                logger.warning(f"Skill directory {skill_dir} is not under skills_path {repo_config.path}")

        # Determine directory name for key
        if skill_dir == repo_root:
            # Use repo name for root skills if directory would be "."
            directory = repo_config.name if repo_config.name else "."
        else:
            directory = skill_dir.name

        # Create skill entity
        skill = Skill(
            id=self.create_entity_key(repo_config, directory),
            name=str(meta.get("name", directory) or directory),
            description=str(meta.get("description", "") or ""),
            category=meta.get("category", "Uncategorized"),
            tags=meta.get("tags", []),
            marketplace_id=f"{repo_config.owner}/{repo_config.name}",
            repo_owner=repo_config.owner,
            repo_name=repo_config.name,
            repo_branch=repo_config.branch,
            directory=directory,
            readme_url=f"https://github.com/{repo_config.owner}/{repo_config.name}/tree/{repo_config.branch}/{repo_relative_path}",
        )

        return skill

    def get_file_pattern(self) -> str:
        """Skills use SKILL.md or skill.md files (case-insensitive)."""
        return "SKILL.md"

    def create_entity_key(self, repo_config: RepoConfig, entity_name: str) -> str:
        """Create skill key: owner/repo:directory."""
        return f"{repo_config.owner}/{repo_config.name}:{entity_name}"

    def _parse_metadata(self, skill_md: Path) -> Optional[Dict[str, Any]]:
        """Parse skill metadata from SKILL.md."""
        meta = {"name": "", "description": "", "category": "Uncategorized", "tags": []}

        try:
            with open(skill_md, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.warning(f"Failed to read skill file {skill_md}: {e}")
            return None

        # Parse YAML frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter_str = parts[1]
                try:
                    frontmatter = yaml.safe_load(frontmatter_str)
                    if frontmatter and isinstance(frontmatter, dict):
                        meta.update(frontmatter)
                except yaml.YAMLError:
                    pass
            content = parts[2]

        return meta