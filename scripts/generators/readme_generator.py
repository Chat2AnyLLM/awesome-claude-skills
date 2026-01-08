#!/usr/bin/env python3
"""
README generator for skills scraper
"""

import logging
from typing import List, Dict, Any
from collections import defaultdict
import re
import unicodedata
from datetime import datetime, timezone

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
        """Generate the README title with badges."""
        now = datetime.now(timezone.utc)
        timestamp = now.strftime("%Y-%m-%d %H:%M UTC")
        skill_count = len(self.skills)
        return f"""# Awesome Claude Skills

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Chat2AnyLLM/awesome-claude-skills/pulls)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A curated list of awesome Claude Code skills to enhance your Claude Code experience.

Total Skills: {skill_count}

Last updated: {timestamp}

"""

    def generate_what_are_skills(self) -> str:
        """Generate the 'What Are Claude Skills?' section."""
        return """
## What Are Claude Skills?

Claude Skills are customizable workflows and tools that extend Claude's capabilities. They allow you to:

- **Automate repetitive tasks** - Create reusable workflows for common development patterns
- **Integrate with external tools** - Connect Claude with APIs, databases, and services
- **Enhance productivity** - Leverage specialized expertise across different domains
- **Customize behavior** - Adapt Claude's responses for specific use cases and requirements

Skills can be used across Claude.ai, Claude Code, and the Claude API to provide domain-specific assistance and automation."""

    def generate_getting_started(self) -> str:
        """Generate the getting started section."""
        return """
## Getting Started

### Installation

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue.svg)](https://github.com/Chat2AnyLLM/code-assistant-manager.git)

To get started with Claude Code skills, install the Code Assistant Manager (CAM):

```bash
# Install CAM
curl -fsSL https://raw.githubusercontent.com/Chat2AnyLLM/code-assistant-manager/main/install.sh | bash

# List available skills
cam skill list

# Install a specific skill (example)
cam skill install zechenzhangAGI/AI-research-SKILLs:19-emerging-techniques/model-merging -a codebuddy,claude
```

### Using Skills in Claude Code

Once installed, skills are automatically available in your Claude Code environment. You can:

- Use skills through natural language commands
- Access specialized tools and workflows
- Integrate with your development workflow

### Using Skills with Claude API

Skills can also be used programmatically via the Claude API for automation and integration purposes."""

    def generate_creating_skills(self) -> str:
        """Generate the creating skills section."""
        return """
## Creating Skills

Want to contribute your own skills? Here's how to get started:

### Skill Development

1. **Choose a domain** - Identify a specific area where you have expertise
2. **Define the workflow** - Map out the steps and logic for your skill
3. **Implement the skill** - Use Claude Code's skill development framework
4. **Test thoroughly** - Ensure your skill works reliably across different scenarios
5. **Document clearly** - Provide comprehensive documentation and examples

### Best Practices

- **Keep it focused** - Each skill should solve one specific problem well
- **Handle errors gracefully** - Include proper error handling and validation
- **Provide examples** - Include usage examples and edge cases
- **Follow conventions** - Use standard patterns and naming conventions

### Resources

- [Claude Code Documentation](https://docs.anthropic.com/claude/docs/claude-code)
- [Skill Development Guide](https://github.com/anthropics/claude-code/tree/main/docs/skills)
- [Community Examples](https://github.com/anthropics/claude-code/tree/main/examples)"""

    def generate_resources(self) -> str:
        """Generate the resources section."""
        return """
## Resources

### Official Documentation
- [Claude Code](https://docs.anthropic.com/claude/docs/claude-code) - Official Claude Code documentation
- [Claude API](https://docs.anthropic.com/claude/reference/getting-started-with-the-api) - API reference and guides
- [Anthropic Console](https://console.anthropic.com/) - Manage your Claude API usage

### Community Resources
- [Claude Code GitHub](https://github.com/anthropics/claude-code) - Source code and issues
- [Awesome Claude](https://github.com/sindresorhus/awesome-claude) - Curated list of Claude resources
- [Claude Community](https://community.anthropic.com/) - Community discussions and support

### Development Tools
- [Code Assistant Manager](https://github.com/Chat2AnyLLM/code-assistant-manager) - Tool for managing Claude skills
- [Claude CLI](https://github.com/anthropics/claude-code/tree/main/packages/cli) - Command-line interface for Claude"""

    def generate_community(self) -> str:
        """Generate the join the community section."""
        return """
## Join the Community

Connect with other Claude developers and skill creators:

### Social Media
- **Twitter/X**: [@anthropic](https://twitter.com/anthropic)
- **LinkedIn**: [Anthropic](https://www.linkedin.com/company/anthropic)
- **Discord**: [Claude Community](https://discord.gg/anthropic)

### Contribution
- **GitHub Issues**: [Report bugs and request features](https://github.com/Chat2AnyLLM/awesome-claude-skills/issues)
- **Pull Requests**: [Contribute skills and improvements](https://github.com/Chat2AnyLLM/awesome-claude-skills/pulls)
- **Discussions**: [Share ideas and get help](https://github.com/Chat2AnyLLM/awesome-claude-skills/discussions)

### Support
- **Documentation**: [Claude Code Docs](https://docs.anthropic.com/claude/docs/claude-code)
- **Community Forum**: [Anthropic Community](https://community.anthropic.com/)
- **Stack Overflow**: [claude-code tag](https://stackoverflow.com/questions/tagged/claude-code)"""

    def generate_license(self) -> str:
        """Generate the license section."""
        return """
## License

This repository is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

---

*Built with ❤️ by the Claude Code community. Empowering developers with AI-enhanced workflows.*"""

    def generate_installation(self) -> str:
        """Generate installation section with CAM instructions."""
        return """## Installation

To get started with Claude Code skills, install the Code Assistant Manager (CAM):

```bash
# Install CAM
curl -fsSL https://raw.githubusercontent.com/Chat2AnyLLM/code-assistant-manager/main/install.sh | bash

# List available skills
cam skill list

# Install a specific skill (example)
cam skill install zechenzhangAGI/AI-research-SKILLs:19-emerging-techniques/model-merging -a codebuddy,claude
```

"""

    def get_category_mapping(self) -> Dict[str, str]:
        """Get mapping of specific categories to main sections."""
        return {
            # Core Development
            "architecture": "Core Development",
            "architectural-pattern": "Core Development",
            "architecture-decision": "Core Development",
            "async": "Core Development",
            "build": "Core Development",
            "code-review": "Core Development",
            "documentation": "Core Development",
            "infrastructure": "Core Development",
            "meta-infrastructure": "Core Development",
            "orchestration": "Core Development",
            "packaging": "Core Development",
            "performance": "Core Development",
            "planning": "Core Development",
            "project-initialization": "Core Development",
            "project-management": "Core Development",
            "review": "Core Development",
            "review-patterns": "Core Development",
            "specialized": "Core Development",
            "specification": "Core Development",
            "testing": "Core Development",
            "testing-automation": "Core Development",

            # AI & Machine Learning
            "agent-workflow": "AI & Machine Learning",
            "analysis-methods": "AI & Machine Learning",
            "artifact-generation": "AI & Machine Learning",
            "delegation-framework": "AI & Machine Learning",
            "delegation-implementation": "AI & Machine Learning",
            "hook-development": "AI & Machine Learning",
            "hook-management": "AI & Machine Learning",
            "media-generation": "AI & Machine Learning",
            "navigation": "AI & Machine Learning",
            "output-patterns": "AI & Machine Learning",

            # Automation & Workflow
            "session-management": "Automation & Workflow",
            "workflow": "Automation & Workflow",
            "workflow-automation": "Automation & Workflow",
            "workflow-methodology": "Automation & Workflow",
            "workflow-ops": "Automation & Workflow",
            "workflow-optimization": "Automation & Workflow",
            "workflow-orchestration": "Automation & Workflow",
            "workspace-ops": "Automation & Workflow",

            # Infrastructure & Operations
            "governance": "Infrastructure & Operations",
            "conservation": "Infrastructure & Operations",
            "cultivation": "Infrastructure & Operations",

            # Language & Framework Specific
            "javascript": "Language & Framework Specific",
            "typescript": "Language & Framework Specific",
            "python": "Language & Framework Specific",
            "java": "Language & Framework Specific",
            "csharp": "Language & Framework Specific",
            "cpp": "Language & Framework Specific",
            "rust": "Language & Framework Specific",
            "go": "Language & Framework Specific",
            "php": "Language & Framework Specific",
            "ruby": "Language & Framework Specific",
            "kotlin": "Language & Framework Specific",
            "swift": "Language & Framework Specific",
            "react": "Language & Framework Specific",
            "vue": "Language & Framework Specific",
            "angular": "Language & Framework Specific",
            "nextjs": "Language & Framework Specific",
            "nestjs": "Language & Framework Specific",
            "django": "Language & Framework Specific",
            "flask": "Language & Framework Specific",
            "spring": "Language & Framework Specific",
            "dotnet": "Language & Framework Specific",
            "laravel": "Language & Framework Specific",
            "rails": "Language & Framework Specific",

            # DevOps & Deployment
            "docker": "DevOps & Deployment",
            "kubernetes": "DevOps & Deployment",
            "terraform": "DevOps & Deployment",
            "aws": "DevOps & Deployment",
            "azure": "DevOps & Deployment",
            "gcp": "DevOps & Deployment",
            "ci-cd": "DevOps & Deployment",
            "deployment": "DevOps & Deployment",
            "monitoring": "DevOps & Deployment",
            "security": "DevOps & Deployment",

            # Database & Data
            "database": "Database & Data",
            "sql": "Database & Data",
            "nosql": "Database & Data",
            "mongodb": "Database & Data",
            "postgresql": "Database & Data",
            "mysql": "Database & Data",
            "redis": "Database & Data",

            # Tools & Utilities
            "git": "Tools & Utilities",
            "vscode": "Tools & Utilities",
            "cli": "Tools & Utilities",
            "api": "Tools & Utilities",
            "web": "Tools & Utilities",
            "mobile": "Tools & Utilities",
            "game": "Tools & Utilities",
            "desktop": "Tools & Utilities"
        }

    def get_dynamic_categories(self) -> Dict[str, List[str]]:
        """Generate dynamic category structure based on actual skills."""
        # Get all categories from skills
        all_categories = set()
        for skill in self.skills:
            category = skill.get("category", "")
            if category and self._is_valid_category(category):
                all_categories.add(category)

        logger.info(f"Found {len(all_categories)} valid categories: {sorted(all_categories)}")

        # Initialize sections
        sections = {
            "Core Development": [],
            "AI & Machine Learning": [],
            "Automation & Workflow": [],
            "Infrastructure & Operations": [],
            "Language & Framework Specific": [],
            "DevOps & Deployment": [],
            "Database & Data": [],
            "Tools & Utilities": [],
            "General Purpose": []
        }

        # Get category mapping
        category_mapping = self.get_category_mapping()

        # Categorize skills
        for category in all_categories:
            # Check if category is in our mapping
            if category in category_mapping:
                main_section = category_mapping[category]
                if main_section in sections and category not in sections[main_section]:
                    sections[main_section].append(category)
            else:
                # Try to intelligently categorize unknown categories
                main_section = self._categorize_unknown_category(category)
                if main_section in sections and category not in sections[main_section]:
                    sections[main_section].append(category)

        # Log the results
        for section, categories in sections.items():
            if categories:
                logger.info(f"Section '{section}' has {len(categories)} categories: {categories}")

        # Remove empty sections
        return {k: sorted(v) for k, v in sections.items() if v}

    def _categorize_unknown_category(self, category: str) -> str:
        """Categorize unknown categories based on keywords."""
        category_lower = category.lower()

        # Language/framework keywords
        if any(lang in category_lower for lang in ['javascript', 'typescript', 'python', 'java', 'csharp', 'cpp', 'rust', 'go', 'php', 'ruby', 'kotlin', 'swift']):
            return "Language & Framework Specific"

        # Framework keywords
        if any(fw in category_lower for fw in ['react', 'vue', 'angular', 'nextjs', 'nestjs', 'django', 'flask', 'spring', 'dotnet', 'laravel', 'rails']):
            return "Language & Framework Specific"

        # DevOps keywords
        if any(devops in category_lower for devops in ['docker', 'kubernetes', 'terraform', 'aws', 'azure', 'gcp', 'ci', 'cd', 'deployment', 'monitoring', 'security']):
            return "DevOps & Deployment"

        # Database keywords
        if any(db in category_lower for db in ['database', 'sql', 'nosql', 'mongo', 'postgres', 'mysql', 'redis']):
            return "Database & Data"

        # Tool/utility keywords
        if any(tool in category_lower for tool in ['git', 'vscode', 'cli', 'api', 'web', 'mobile', 'game', 'desktop']):
            return "Tools & Utilities"

        # AI/ML keywords
        if any(ai in category_lower for ai in ['ai', 'ml', 'machine', 'learning', 'neural', 'model', 'nlp', 'computer-vision']):
            return "AI & Machine Learning"

        # Workflow/automation keywords
        if any(workflow in category_lower for workflow in ['workflow', 'automation', 'orchestration', 'pipeline']):
            return "Automation & Workflow"

        # Infrastructure keywords
        if any(infra in category_lower for infra in ['infrastructure', 'cloud', 'server', 'deployment']):
            return "Infrastructure & Operations"

        # Default fallback
        return "General Purpose"

    def _is_valid_category(self, category: str) -> bool:
        """
        Validate if a category name is well-formed and usable.

        Returns True if category is valid, False otherwise.
        """
        if not category or category.strip() == "" or len(category.strip()) > 50:
            return False

        clean_category = category.strip()

        # Skip obviously malformed categories (numbers only, very short, etc.)
        if clean_category.isdigit() or len(clean_category) < 4:
            return False

        # Skip categories that contain "category" as a separate word or have malformed patterns
        if " category" in clean_category.lower() or clean_category.lower().startswith("category "):
            return False

        if any(word in clean_category.lower() for word in ["stridecategory", "str ", "category:"]):
            return False

        # Skip other malformed patterns
        if any(char in clean_category for char in [")", "(", ";", ":", "//", "category:"]):
            return False

        return True

    def generate_table_of_contents(self) -> str:
        """Generate hierarchical table of contents matching the README section structure."""
        toc_lines = ["## Contents\n"]

        # Main sections with their subsections
        toc_lines.extend([
            "- [What Are Claude Skills?](#what-are-claude-skills)",
            "- [Getting Started](#getting-started)",
            "  - [Installation](#installation)",
            "  - [Using Skills in Claude Code](#using-skills-in-claude-code)",
            "  - [Using Skills with Claude API](#using-skills-with-claude-api)",
            "- [Automation & Workflow](#automation-and-workflow)",
            "  - [workflow](#workflow)",
            "    - [claude-scientific-skills](#claude-scientific-skills)",
            "    - [claude-skills](#claude-skills)",
            "    - [planning-with-files](#planning-with-files)",
            "    - [claude-night-market](#claude-night-market)",
            "    - [n8n-skills](#n8n-skills)",
            "    - [claude-code-templates](#claude-code-templates)",
            "    - [claude-code-plugins-plus](#claude-code-plugins-plus)",
            "    - [claude-code-plugins-plus-skills](#claude-code-plugins-plus-skills)",
            "    - [agents](#agents)",
            "- [Language & Framework Specific](#language-and-framework-specific)",
            "  - [Uncategorized](#uncategorized)",
            "    - [iothackbot](#iothackbot)",
            "    - [awesome-claude-skills](#awesome-claude-skills)",
            "- [Creating Skills](#creating-skills)",
            "- [Contributing](#contributing)",
            "- [Resources](#resources)",
            "- [Join the Community](#join-the-community)",
        ])

        toc_lines.append("")
        return "\n".join(toc_lines)

    def generate_marketplaces_table(self) -> str:
        """Generate repositories table."""
        if not self.marketplaces:
            return ""

        lines = ["\n## Repositories\n"]
        lines.append("| Repository | Description |")
        lines.append("| --- | --- |")

        for repo in sorted(self.marketplaces, key=lambda x: x.get("name", "")):
            name = repo.get("name", repo.get("id", "Unknown"))
            owner = repo.get("owner", "")
            description = f"Skills repository by {owner}"  # Default description since repos don't have descriptions

            # Construct URL from owner and name if available
            if owner and name:
                url = f"https://github.com/{owner}/{name}"
                repo_name_cell = f"[{name}]({url})"
            else:
                repo_name_cell = name

            lines.append(f"| {repo_name_cell} | {description} |")

        lines.append("")
        return "\n".join(lines)

    def generate_skills_by_category(self) -> str:
        """Generate skills organized by logical categories following Uber Go guide structure."""
        if not self.skills:
            return ""

        # Group skills by category
        categories = defaultdict(list)
        for skill in self.skills:
            category = skill.get("category", "Uncategorized")
            categories[category].append(skill)

        lines = [""]

        # Get dynamic categories structure
        skill_categories = self.get_dynamic_categories()

        # Create a mapping of skills to their dynamic categories
        skill_to_dynamic_category = {}
        category_mapping = self.get_category_mapping()

        for skill in self.skills:
            skill_id = skill.get("id", str(id(skill)))  # Use skill ID or memory address as key
            original_category = skill.get("category", "Uncategorized")
            # Check if category is in our mapping
            if original_category in category_mapping:
                dynamic_category = category_mapping[original_category]
            else:
                # Try to intelligently categorize unknown categories based on skill name/description
                dynamic_category = self._categorize_skill(skill)
            skill_to_dynamic_category[skill_id] = dynamic_category

        # Re-group skills by dynamic categories
        dynamic_categories = defaultdict(list)
        for skill in self.skills:
            skill_id = skill.get("id", str(id(skill)))
            dynamic_cat = skill_to_dynamic_category[skill_id]
            dynamic_categories[dynamic_cat].append(skill)

        # Generate content for each main category
        for main_section, subcategories in skill_categories.items():
            section_has_content = False

            for category in subcategories:
                # Check if this subcategory has skills in our dynamic categorization
                skills_in_category = [
                    skill for skill in dynamic_categories.get(main_section, [])
                    if skill_to_dynamic_category[skill.get("id", str(id(skill)))] == main_section
                ]

                if skills_in_category:
                    if not section_has_content:
                        # Add main section header
                        lines.append(f"## {main_section}")
                        lines.append("")
                        section_has_content = True

                    # Add category subsection
                    clean_category = category.strip()
                    lines.append(f"### {clean_category}")
                    lines.append("")

                    # Group skills by marketplace within category
                    marketplace_skills = defaultdict(list)
                    for skill in skills_in_category:
                        marketplace_id = skill.get("marketplace_id", "unknown")
                        marketplace_skills[marketplace_id].append(skill)

                    # Generate content for each marketplace
                    for marketplace_id in sorted(marketplace_skills.keys()):
                        skills = marketplace_skills[marketplace_id]
                        marketplace_name = self._get_marketplace_name(marketplace_id)
                        if marketplace_name:
                            lines.append(f"#### {marketplace_name}")
                            lines.append("")

                        # Table header
                        lines.append("| Skill | Description | Version | Author | Directory |")
                        lines.append("| --- | --- | --- | --- | --- |")

                        # Sort skills alphabetically by directory name
                        sorted_skills = sorted(skills, key=lambda s: s.get("directory", ""))

                        for skill in sorted_skills:
                            name = skill.get("name", "Unknown Skill")
                            description = (
                                skill.get("description", "").replace("\n", " ").strip()
                            )
                            version = skill.get("version", "")

                            # Truncate description for table readability
                            if len(description) > 120:
                                description = description[:117] + "..."

                            # For skills, we don't have author field in the same way as plugins
                            # Use repo_owner as author
                            author = skill.get("repo_owner", "Unknown")

                            directory = skill.get("directory", "Unknown")
                            readme_url = skill.get("readme_url", "")

                            # Use skill name from metadata, fallback to directory if name is empty
                            skill_name = name if name else directory

                            # Make skill name a hyperlink if URL exists
                            if readme_url:
                                skill_name_cell = f"[{skill_name}]({readme_url})"
                            else:
                                skill_name_cell = skill_name

                            # Escape pipe characters in description
                            description = description.replace("|", "\\|")

                            lines.append(
                                f"| {skill_name_cell} | {description} | {version} | {author} | {directory} |"
                            )

                        lines.append("")

            if section_has_content:
                lines.append("")

        return "\n".join(lines)

    def _categorize_skill(self, skill) -> str:
        """Categorize a skill based on its name, description, and directory."""
        name = skill.get("name", "").lower()
        description = skill.get("description", "").lower()
        directory = skill.get("directory", "").lower()

        # Combine all text for keyword matching
        text = f"{name} {description} {directory}"

        # Language/framework keywords
        if any(lang in text for lang in ['javascript', 'typescript', 'python', 'java', 'csharp', 'cpp', 'rust', 'go', 'php', 'ruby', 'kotlin', 'swift']):
            return "Language & Framework Specific"

        # Framework keywords
        if any(fw in text for fw in ['react', 'vue', 'angular', 'nextjs', 'nestjs', 'django', 'flask', 'spring', 'dotnet', 'laravel', 'rails']):
            return "Language & Framework Specific"

        # DevOps keywords
        if any(devops in text for devops in ['docker', 'kubernetes', 'terraform', 'aws', 'azure', 'gcp', 'ci', 'cd', 'deployment', 'monitoring', 'security']):
            return "DevOps & Deployment"

        # Database keywords
        if any(db in text for db in ['database', 'sql', 'nosql', 'mongo', 'postgres', 'mysql', 'redis']):
            return "Database & Data"

        # Tool/utility keywords
        if any(tool in text for tool in ['git', 'vscode', 'cli', 'api', 'web', 'mobile', 'game', 'desktop']):
            return "Tools & Utilities"

        # AI/ML keywords
        if any(ai in text for ai in ['ai', 'ml', 'machine', 'learning', 'neural', 'model', 'nlp', 'computer-vision']):
            return "AI & Machine Learning"

        # Workflow/automation keywords
        if any(workflow in text for workflow in ['workflow', 'automation', 'orchestration', 'pipeline']):
            return "Automation & Workflow"

        # Infrastructure keywords
        if any(infra in text for infra in ['infrastructure', 'cloud', 'server', 'deployment']):
            return "Infrastructure & Operations"

        # Default fallback
        return "General Purpose"

    def generate_contributing(self) -> str:
        """Generate contributing section."""
        return """
## Contributing

We welcome contributions! Please see our [contributing guidelines](CONTRIBUTING.md) for details on how to add new marketplaces or skills.

To add a new skill or marketplace:
1. Fork this repository
2. Add the entry to the appropriate section
3. Ensure the skill is verified and documented
4. Submit a pull request with a clear description
"""

    def generate_readme(self) -> str:
        """Generate complete README content with enhanced sections."""
        sections = [
            self.generate_title(),
            self.generate_what_are_skills(),
            self.generate_getting_started(),
            self.generate_table_of_contents(),
            self.generate_skills_by_category(),
            self.generate_creating_skills(),
            self.generate_contributing(),
            self.generate_resources(),
            self.generate_community(),
            self.generate_license(),
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
            link_pattern = r"\[([^\]]*)\]\(([^)]*)\)"
            links = re.findall(link_pattern, content)

            for text, url in links:
                if not text.strip():
                    logger.warning("Found empty link text in markdown")
                    return False
                if not url.strip():
                    logger.warning("Found empty URL in markdown link")
                    return False

            # Basic check for table structure - just ensure tables have separators
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if "|" in line and not line.strip().startswith("#"):
                    # Check if this is a table header row
                    if i + 1 < len(lines):
                        next_line = lines[i + 1]
                        # Check if next line is a separator with dashes and pipes
                        if (
                            "|" in next_line
                            and ("---" in next_line or "---" in next_line.replace(" ", ""))
                        ):
                            continue

            logger.info("Markdown validation passed")
            return True

        except Exception as e:
            logger.error(f"Markdown validation failed: {e}")
            return False
