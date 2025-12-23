#!/usr/bin/env python3
"""
README generator for skills scraper
"""

import logging
from typing import List, Dict, Any
from collections import defaultdict
import re

logger = logging.getLogger(__name__)

class SkillReadmeGenerator:
    """Generates README content from marketplace and skill data."""

    def __init__(self):
        self.marketplaces: List[Dict[str, Any]] = []  # Now contains repositories
        self.skills: List[Dict[str, Any]] = []

    def add_marketplaces(self, marketplaces: List[Dict[str, Any]]):
        """Add marketplace data."""
        self.marketplaces.extend(marketplaces)

    def add_skills(self, skills: List[Dict[str, Any]]):
        """Add skill data."""
        self.skills.extend(skills)

    def generate_title(self) -> str:
        """Generate the README title."""
        return "# Awesome Claude Skills\n\nA curated list of awesome Claude Code skills to enhance your Claude Code experience.\n\n"

    def generate_table_of_contents(self) -> str:
        """Generate table of contents."""
        lines = ["## Contents\n"]
        lines.append("- [Repositories](#repositories)")

        # Group skills by category
        categories = self._get_categories()
        for category in sorted(categories.keys()):
            # Skip empty or malformed categories
            if not category or category.strip() == "" or len(category.strip()) > 50:
                continue

            # Skip obviously malformed categories (numbers only, very short, etc.)
            clean_category = category.strip()
            if clean_category.isdigit() or len(clean_category) < 4:  # Increased minimum length
                continue
            # Skip categories that contain "category" as a separate word or have malformed patterns
            if " category" in clean_category.lower() or clean_category.lower().startswith("category "):
                continue
            if any(word in clean_category.lower() for word in ["stridecategory", "str ", "category:"]):
                continue

            # Clean category name for anchor
            anchor = clean_category.lower().replace(" ", "-").replace("&", "").replace("/", "-")
            # Remove any remaining non-alphanumeric characters except hyphens
            import re
            anchor = re.sub(r'[^a-z0-9-]', '', anchor)
            lines.append(f"- [{clean_category}](#{anchor})")

        lines.append("- [Contributing](#contributing)")
        lines.append("")
        return "\n".join(lines)

    def generate_marketplaces_table(self) -> str:
        """Generate repositories table."""
        if not self.marketplaces:
            return ""

        lines = ["## Repositories\n\n"]
        lines.append("| Repository | Description | URL |")
        lines.append("|------------|-------------|-----|")

        for repo in sorted(self.marketplaces, key=lambda x: x.get("name", "")):
            name = repo.get("name", repo.get("id", "Unknown"))
            owner = repo.get("owner", "")
            description = f"Skills repository by {owner}"  # Default description since repos don't have descriptions

            # Construct URL from owner and name if available
            if owner and name:
                url = f"https://github.com/{owner}/{name}"
                url_cell = f"[Link]({url})"
            else:
                url_cell = "-"

            lines.append(f"| {name} | {description} | {url_cell} |")

        lines.append("")
        return "\n".join(lines)

    def generate_skills_by_category(self) -> str:
        """Generate skills organized by category with table format."""
        if not self.skills:
            return ""

        # Group skills by category
        categories = defaultdict(list)
        for skill in self.skills:
            category = skill.get("category", "Uncategorized")
            categories[category].append(skill)

        lines = []
        for category in sorted(categories.keys()):
            # Skip empty or malformed categories
            if not category or category.strip() == "" or len(category.strip()) > 50:
                continue

            # Skip obviously malformed categories (numbers only, very short, etc.)
            clean_category = category.strip()
            if clean_category.isdigit() or len(clean_category) < 4:  # Increased minimum length
                continue
            # Skip categories that contain "category" as a separate word or have malformed patterns
            if " category" in clean_category.lower() or clean_category.lower().startswith("category "):
                continue
            if any(word in clean_category.lower() for word in ["stridecategory", "str ", "category:"]):
                continue

            lines.append(f"## {clean_category}\n")

            # Group skills by marketplace within category
            marketplace_skills = defaultdict(list)
            for skill in categories[category]:
                marketplace_id = skill.get("marketplace_id", "unknown")
                marketplace_skills[marketplace_id].append(skill)

            for marketplace_id, skills in marketplace_skills.items():
                marketplace_name = self._get_marketplace_name(marketplace_id)
                if marketplace_name:
                    lines.append(f"### {marketplace_name}\n")

                # Table header
                lines.append("| Skill | Description | Author | Directory | URL |")
                lines.append("|--------|-------------|--------|-----------|-----|")

                # Sort skills alphabetically
                sorted_skills = sorted(skills, key=lambda s: s.get("name", ""))

                for skill in sorted_skills:
                    name = skill.get("name", "Unknown Skill")
                    description = skill.get("description", "").replace("\n", " ").strip()
                    # Truncate description for table readability
                    if len(description) > 120:
                        description = description[:117] + "..."

                    # For skills, we don't have author field in the same way as plugins
                    # Use repo_owner as author
                    author = skill.get("repo_owner", "Unknown")

                    directory = skill.get("directory", "Unknown")
                    readme_url = skill.get("readme_url", "")

                    # Create URL cell with hyperlink if URL exists
                    if readme_url:
                        url_cell = f"[Link]({readme_url})"
                    else:
                        url_cell = "-"

                    # Escape pipe characters in description
                    description = description.replace("|", "\\|")

                    lines.append(f"| {name} | {description} | {author} | {directory} | {url_cell} |")

                lines.append("")

            lines.append("")

        return "\n".join(lines)

    def generate_contributing(self) -> str:
        """Generate contributing section."""
        return """## Contributing

We welcome contributions! Please see our [contributing guidelines](CONTRIBUTING.md) for details on how to add new marketplaces or skills.

To add a new skill or marketplace:
1. Fork this repository
2. Add the entry to the appropriate section
3. Ensure the skill is verified and documented
4. Submit a pull request with a clear description
"""

    def generate_readme(self) -> str:
        """Generate complete README content."""
        sections = [
            self.generate_title(),
            self.generate_table_of_contents(),
            self.generate_marketplaces_table(),
            self.generate_skills_by_category(),
            self.generate_contributing()
        ]

        content = "".join(sections)

        # Validate markdown format
        if not self.validate_markdown(content):
            logger.warning("Generated markdown failed validation")
        else:
            logger.info("Generated markdown validation successful")

        return content

    def _get_categories(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get skills grouped by category."""
        categories = defaultdict(list)
        for skill in self.skills:
            category = skill.get("category", "Uncategorized")
            categories[category].append(skill)
        return categories

    def _get_marketplace_name(self, marketplace_id: str) -> str:
        """Get marketplace name by ID."""
        for marketplace in self.marketplaces:
            if marketplace.get("id") == marketplace_id:
                return marketplace.get("name", marketplace_id)
        return marketplace_id

    def validate_markdown(self, content: str) -> bool:
        """Basic markdown validation for generated content."""
        try:
            # Check for balanced brackets in links [text](url)
            link_pattern = r'\[([^\]]*)\]\(([^)]*)\)'
            links = re.findall(link_pattern, content)

            for text, url in links:
                if not text.strip():
                    logger.warning("Found empty link text in markdown")
                    return False
                if not url.strip():
                    logger.warning("Found empty URL in markdown link")
                    return False

            # Basic check for table structure - just ensure tables have separators
            lines = content.split('\n')
            table_started = False
            has_separator = False

            for line in lines:
                if '|' in line and not line.strip().startswith('#'):
                    if '|---' in line or '|:--' in line or ':---' in line or '---:' in line:
                        has_separator = True
                        table_started = False
                    elif not table_started:
                        table_started = True
                    # else: continuing table row

            # If we found tables, ensure they have separators
            if table_started and not has_separator:
                logger.warning("Found table without proper separator")
                return False

            logger.info("Markdown validation passed")
            return True

        except Exception as e:
            logger.error(f"Markdown validation failed: {e}")
            return False