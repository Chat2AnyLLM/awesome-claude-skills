# Marketplace scraper data models for skills

from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class SkillSource:
    """Represents a data source configuration for skills."""
    id: str
    url: str
    format: str = "json"
    enabled: bool = True
    priority: int = 999
    timeout: int = 30

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SkillSource':
        """Create SkillSource from dictionary data."""
        return cls(
            id=data.get("id", ""),
            url=data.get("url", ""),
            format=data.get("format", "json"),
            enabled=data.get("enabled", True),
            priority=data.get("priority", 999),
            timeout=data.get("timeout", 30)
        )

@dataclass
class Skill:
    """Represents an individual skill."""
    id: str
    name: str
    description: str
    category: Optional[str] = None
    marketplace_id: Optional[str] = None
    repo_owner: Optional[str] = None
    repo_name: Optional[str] = None
    repo_branch: Optional[str] = None
    directory: Optional[str] = None
    readme_url: Optional[str] = None
    tags: Optional[List[str]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Skill':
        """Create Skill from dictionary data."""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            category=data.get("category"),
            marketplace_id=data.get("marketplace_id"),
            repo_owner=data.get("repo_owner"),
            repo_name=data.get("repo_name"),
            repo_branch=data.get("repo_branch", "main"),
            directory=data.get("directory"),
            readme_url=data.get("readme_url"),
            tags=data.get("tags", [])
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Skill to dictionary."""
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
        }
        if self.category:
            data["category"] = self.category
        if self.marketplace_id:
            data["marketplace_id"] = self.marketplace_id
        if self.repo_owner:
            data["repo_owner"] = self.repo_owner
        if self.repo_name:
            data["repo_name"] = self.repo_name
        if self.repo_branch:
            data["repo_branch"] = self.repo_branch
        if self.directory:
            data["directory"] = self.directory
        if self.readme_url:
            data["readme_url"] = self.readme_url
        if self.tags:
            data["tags"] = self.tags
        return data