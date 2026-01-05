"""Entity-specific parsers for skills."""

import json
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
        if file_path.name != "SKILL.md":
            return None

        skill_dir = file_path.parent

        # Skip generated/cache skills that start with 'cam_'
        if skill_dir.name.startswith('cam_'):
            logger.debug(f"Skipping generated skill directory: {skill_dir.name}")
            return None

        # Parse metadata from SKILL.md
        meta = self._parse_metadata(file_path)

        # Calculate paths
        directory = skill_dir.name

        # Find the repo root by looking for .git directory
        repo_root = skill_dir
        # Check current dir first
        if (skill_dir / '.git').exists():
            repo_root = skill_dir
        else:
            for parent in skill_dir.parents:
                if (parent / '.git').exists():
                    repo_root = parent
                    break
            else:
                # Fallback to the original logic if .git not found
                try:
                    repo_root = skill_dir.parents[-2]
                except IndexError:
                    repo_root = skill_dir.parent

        # Get relative path from repo root to skill directory
        try:
            repo_relative_path = str(skill_dir.relative_to(repo_root))
        except ValueError:
            repo_relative_path = directory

        source_directory = repo_relative_path

        # If skills_path is set, source_directory should be relative to skills_path
        if repo_config.path:
            skills_path = Path(repo_config.path)
            try:
                # Try to make source_directory relative to skills_path
                full_skills_path = repo_root / skills_path
                source_directory = str(skill_dir.relative_to(full_skills_path))
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
            name=meta.get("name", directory),
            description=meta.get("description", ""),
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
        """Skills use SKILL.md files."""
        return "SKILL.md"

    def create_entity_key(self, repo_config: RepoConfig, entity_name: str) -> str:
        """Create skill key: owner/repo:directory."""
        return f"{repo_config.owner}/{repo_config.name}:{entity_name}"

    def _parse_metadata(self, skill_md: Path) -> dict:
        """Parse skill metadata from SKILL.md."""
        meta = {"name": "", "description": "", "category": "Uncategorized", "tags": []}

        try:
            with open(skill_md, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse YAML frontmatter
            if content.startswith("---"):
                try:
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        frontmatter_str = parts[1]
                        try:
                            frontmatter = yaml.safe_load(frontmatter_str)
                        except yaml.YAMLError as e:
                            logger.info(f"Retrying YAML parse for {skill_md} with robust cleaning")
                            # Fallback for unquoted colons in values and nested brackets in flow sequences
                            fixed_lines = []
                            for line in frontmatter_str.split('\n'):
                                if ':' in line and not line.strip().startswith('#'):
                                    key, val = line.split(':', 1)
                                    val = val.strip()

                                    # Handle flow sequences with nested brackets (e.g., [ray[train], torch])
                                    if val.startswith('[') and val.endswith(']'):
                                        # Check if there are unquoted nested brackets
                                        import re
                                        # Find items with nested brackets like ray[train]
                                        if re.search(r'\w+\[[^\]]+\]', val):
                                            # Quote items that contain brackets
                                            items = []
                                            # Simple parser for comma-separated values
                                            current_item = ''
                                            bracket_depth = 0
                                            for char in val[1:-1]:  # Remove outer brackets
                                                if char == '[':
                                                    bracket_depth += 1
                                                elif char == ']':
                                                    bracket_depth -= 1
                                                elif char == ',' and bracket_depth == 0:
                                                    items.append(current_item.strip())
                                                    current_item = ''
                                                    continue
                                                current_item += char
                                            if current_item.strip():
                                                items.append(current_item.strip())

                                            # Quote items that need it
                                            quoted_items = []
                                            for item in items:
                                                if '[' in item and not (item.startswith('"') or item.startswith("'")):
                                                    quoted_items.append(f'"{item}"')
                                                else:
                                                    quoted_items.append(item)
                                            val = '[' + ', '.join(quoted_items) + ']'
                                    # If value contains colon and is not quoted, wrap it
                                    elif ':' in val and not (val.startswith('"') or val.startswith("'")):
                                        val = f'"{val}"'

                                    fixed_lines.append(f"{key}: {val}")
                                else:
                                    fixed_lines.append(line)

                            frontmatter = yaml.safe_load('\n'.join(fixed_lines))

                        if frontmatter and isinstance(frontmatter, dict):
                            meta.update(frontmatter)
                            # Remove frontmatter from content for further processing
                            content = parts[2]
                except Exception as e:
                    logger.warning(f"Failed to parse YAML frontmatter in {skill_md}: {e}")

            # Extract name from first header if not in frontmatter
            if not meta.get("name"):
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('# '):
                        meta["name"] = line[2:].strip()
                        break

            # Look for description (text after name until next header or special markers) if not in frontmatter
            if not meta.get("description"):
                lines = content.split('\n')
                in_description = False
                description_lines = []

                for line in lines:
                    line = line.strip()
                    if line.startswith('# ') and meta.get("name") and line[2:].strip() == meta["name"]:
                        in_description = True
                        continue
                    elif line.startswith('#') and in_description:
                        break
                    elif in_description and line:
                        description_lines.append(line)

                if description_lines:
                    meta["description"] = ' '.join(description_lines).strip()

        except Exception as e:
            logger.warning(f"Failed to parse SKILL.md at {skill_md}: {e}")

        return meta