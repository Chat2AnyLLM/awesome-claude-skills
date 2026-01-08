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

**[📋 View Complete Skills List](FULL-SKILLS.md#complete-skills-listing)** - Convenient for searching through all skills without size limits."""

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
        """Generate intelligent hierarchical table of contents with links to domain files."""
        toc_lines = ["\n## Contents\n"]

        # Main sections with their subsections
        toc_lines.extend([
        ])

        # Add intelligent skill categories with counts
        toc_lines.append("- **Skills by Domain:**")

        # Count skills by intelligent categories
        skill_categories = self._get_intelligent_categories()

        # Sort categories by count (descending)
        sorted_categories = sorted(skill_categories.items(), key=lambda x: len(x[1]), reverse=True)

        for category, skills in sorted_categories:
            count = len(skills)
            # Create file path for domain file
            domain_filename = self._category_to_filename(category)
            toc_lines.append(f"  - [{category}](./domains/{domain_filename}) - {count} skills")

        # Add remaining sections
        toc_lines.extend([
            "- [Creating Skills](#creating-skills)",
            "  - [Skill Development](#skill-development)",
            "  - [Best Practices](#best-practices)",
            "  - [Resources](#resources)",
            "- [Contributing](#contributing)",
            "- [Resources](#resources)",
            "  - [Official Documentation](#official-documentation)",
            "  - [Community Resources](#community-resources)",
            "  - [Development Tools](#development-tools)",
            "- [Join the Community](#join-the-community)",
            "  - [Social Media](#social-media)",
            "  - [Contribution](#contribution)",
            "  - [Support](#support)",
            "- [License](#license)",
        ])

        toc_lines.append("")
        return "\n".join(toc_lines)

    def generate_full_document_table_of_contents(self) -> str:
        """Generate table of contents for the full document with local anchors."""
        toc_lines = ["\n## Contents\n"]

        # Main sections with their subsections
        toc_lines.extend([
        ])

        # Add intelligent skill categories with local anchors for full document
        toc_lines.append("- **Skills by Domain:**")

        # Count skills by intelligent categories
        skill_categories = self._get_intelligent_categories()

        # Sort categories by count (descending)
        sorted_categories = sorted(skill_categories.items(), key=lambda x: len(x[1]), reverse=True)

        for category, skills in sorted_categories:
            count = len(skills)
            # Use local anchor instead of external link
            anchor = self._category_to_anchor(category)
            toc_lines.append(f"  - [{category}](#{anchor}) - {count} skills")

        # Add remaining sections
        toc_lines.extend([
            "- [Creating Skills](#creating-skills)",
            "  - [Skill Development](#skill-development)",
            "  - [Best Practices](#best-practices)",
            "  - [Resources](#resources)",
            "- [Contributing](#contributing)",
            "- [Resources](#resources)",
            "  - [Official Documentation](#official-documentation)",
            "  - [Community Resources](#community-resources)",
            "  - [Development Tools](#development-tools)",
            "- [Join the Community](#join-the-community)",
            "  - [Social Media](#social-media)",
            "  - [Contribution](#contribution)",
            "  - [Support](#support)",
            "- [License](#license)",
        ])

        toc_lines.append("")
        return "\n".join(toc_lines)
    
    def _category_to_filename(self, category: str) -> str:
        """Convert category name to filename."""
        filename = category.lower()
        filename = filename.replace(" ", "-")
        filename = filename.replace("&", "and")
        filename = ''.join(c if c.isalnum() or c == '-' else '' for c in filename)
        while '--' in filename:
            filename = filename.replace('--', '-')
        return f"{filename}.md"
    
    def _escape_liquid_syntax(self, text: str) -> str:
        """Escape Liquid template syntax in text to prevent Jekyll errors."""
        # Use {% raw %} tags to prevent Liquid processing
        if '{{' in text or '}}' in text or '{%' in text or '%}' in text:
            # For table cells, we can't use raw tags, so escape differently
            text = text.replace('{{', '&#123;&#123;')
            text = text.replace('}}', '&#125;&#125;')
            text = text.replace('{%', '&#123;%')
            text = text.replace('%}', '%&#125;')
        return text

    def _get_intelligent_categories(self) -> Dict[str, List[Dict]]:
        """Categorize skills intelligently based on names and descriptions."""
        categories = defaultdict(list)
        
        # Define category keywords for intelligent classification
        category_keywords = {
            'Frontend Development': ['react', 'vue', 'angular', 'nextjs', 'tailwind', 'component', 'frontend', 'css', 'styled', 'html', 'svelte', 'widget', 'layout', 'responsive', 'browser'],
            'Backend Development': ['backend', 'fastapi', 'django', 'nodejs', 'spring', 'nestjs', 'express', 'server', 'middleware', 'handler', 'request', 'response', 'database', 'orm', 'api', 'rest'],
            'DevOps & Infrastructure': ['devops', 'docker', 'kubernetes', 'terraform', 'jenkins', 'ci/cd', 'deployment', 'cloud', 'aws', 'gcp', 'azure', 'infrastructure', 'ssh', 'yaml', 'ansible', 'makefile', 'infrastructure-as-code'],
            'Data & Analytics': ['data', 'analytics', 'pandas', 'polars', 'sql', 'dataframe', 'query', 'pipeline', 'etl', 'warehousing', 'spark', 'dbt', 'statistics', 'metrics', 'bigquery'],
            'Machine Learning': ['ml', 'machine learning', 'pytorch', 'tensorflow', 'sklearn', 'model', 'training', 'inference', 'neural', 'dataset', 'optimization', 'clustering', 'regression', 'classification'],
            'Testing & Quality': ['test', 'testing', 'pytest', 'jest', 'vitest', 'mock', 'assertion', 'benchmark', 'coverage', 'qa', 'validation', 'contract', 'snapshot', 'unit test'],
            'Security': ['security', 'auth', 'encryption', 'jwt', 'password', 'vulnerability', 'xss', 'csrf', 'ssl', 'tls', 'firewall', 'compliance', 'soc2', 'policy', 'secret', 'oauth'],
            'AI & LLM': ['ai', 'llm', 'gpt', 'claude', 'langchain', 'rag', 'agent', 'embedding', 'huggingface', 'transformer', 'alignment', 'safety', 'multimodal'],
            'Documentation': ['documentation', 'readme', 'changelog', 'doc', 'guide', 'tutorial', 'comment', 'javadoc', 'swagger', 'openapi'],
            'Version Control & Collaboration': ['git', 'github', 'pull request', 'pr', 'commit', 'branch', 'merge', 'code review', 'collaboration'],
            'Tools & Utilities': ['tool', 'utility', 'mcp', 'helper', 'builder', 'generator', 'creator', 'optimizer', 'analyzer', 'converter'],
            'Business & Productivity': ['business', 'crm', 'sales', 'marketing', 'slack', 'teams', 'notion', 'email', 'webhook', 'workflow', 'automation', 'zapier', 'linear'],
        }
        
        for skill in self.skills:
            name_lower = skill.get('name', '').lower()
            desc_lower = skill.get('description', '').lower()
            combined = f"{name_lower} {desc_lower}"
            
            categorized = False
            for category, keywords in category_keywords.items():
                if any(keyword in combined for keyword in keywords):
                    categories[category].append(skill)
                    categorized = True
                    break
            
            if not categorized:
                categories['Uncategorized'].append(skill)
        
        return categories

    def _get_subcategories(self, category_name: str, skills: List[Dict]) -> Dict[str, List[Dict]]:
        """Break down large categories into more specific subcategories."""
        subcategories_map = {
            'Backend Development': {
                'Web Frameworks': ['nextjs', 'express', 'fastapi', 'django', 'nestjs', 'spring', 'flask', 'laravel', 'rails', 'hono', 'actix', 'startup'],
                'APIs & REST': ['api', 'rest', 'graphql', 'endpoint', 'openapi', 'swagger', 'grpc', 'api-designer', 'api-gateway'],
                'Database Design': ['database', 'sql', 'postgres', 'mysql', 'mongodb', 'schema', 'migration', 'orm', 'entity'],
                'Authentication': ['auth', 'jwt', 'oauth', 'password', 'session', 'login', 'token', 'keycloak', 'identity'],
                'Microservices': ['microservice', 'saga', 'distributed', 'event-driven', 'saga-orchestration', 'orchestration'],
                'Message Queues': ['queue', 'rabbitmq', 'kafka', 'pubsub', 'messaging', 'event', 'broker', 'consumer'],
                'Caching': ['cache', 'redis', 'memcached', 'caching', 'cache-manager'],
                'Request Handling': ['request', 'response', 'middleware', 'handler', 'interceptor', 'decorator', 'filter'],
            },
            'DevOps & Infrastructure': {
                'Cloud Platforms': ['aws', 'azure', 'gcp', 'cloud', 'linode', 'digitalocean', 'heroku', 'vertex'],
                'Containers': ['kubernetes', 'docker', 'container', 'helm', 'argocd', 'k8s'],
                'CI/CD': ['ci', 'cd', 'jenkins', 'github-action', 'gitlab-ci', 'circleci', 'pipeline', 'workflow'],
                'Infrastructure as Code': ['terraform', 'cloudformation', 'ansible', 'pulumi', 'bicep', 'iac'],
                'Monitoring': ['monitoring', 'prometheus', 'grafana', 'elk', 'datadog', 'logging', 'alert', 'metric'],
                'Service Mesh': ['service-mesh', 'istio', 'linkerd', 'consul', 'mesh'],
                'Security': ['security', 'vault', 'secret', 'encryption', 'firewall', 'compliance'],
                'Networking': ['load-balance', 'nginx', 'traefik', 'loadbalancer', 'proxy', 'dns', 'network'],
            },
            'Data & Analytics': {
                'Data Pipelines': ['pipeline', 'airflow', 'dbt', 'etl', 'kafka', 'spark', 'beam', 'orchestration'],
                'Data Warehousing': ['warehouse', 'bigquery', 'snowflake', 'redshift', 'postgres', 'schema'],
                'Analytics & Queries': ['analytics', 'query', 'reporting', 'dashboard', 'analysis', 'visualization'],
                'Data Science': ['dataframe', 'pandas', 'polars', 'numpy', 'scipy', 'analysis', 'processing'],
                'Time Series': ['time-series', 'timescale', 'prometheus', 'influx', 'temporal'],
                'Business Intelligence': ['business', 'tableau', 'powerbi', 'metabase', 'looker', 'intelligence'],
            },
            'Machine Learning': {
                'Model Training': ['training', 'pytorch', 'tensorflow', 'sklearn', 'xgboost', 'train', 'trainer'],
                'Feature Engineering': ['feature', 'preprocessing', 'normalization', 'scaling', 'transformer'],
                'Model Evaluation': ['evaluation', 'metric', 'validation', 'testing', 'cross-validation', 'assessment'],
                'Model Deployment': ['deployment', 'inference', 'serving', 'endpoint', 'prediction', 'model-deploy'],
                'Hyperparameter Tuning': ['hyperparameter', 'tuning', 'optimization', 'grid-search', 'search'],
            },
        }
        
        if category_name not in subcategories_map:
            return {}
        
        subcategories = defaultdict(list)
        subcat_keywords = subcategories_map[category_name]
        
        for skill in skills:
            name_lower = skill.get('name', '').lower()
            desc_lower = skill.get('description', '').lower()
            combined = f"{name_lower} {desc_lower}"
            
            categorized = False
            for subcat, keywords in subcat_keywords.items():
                if any(keyword in combined for keyword in keywords):
                    subcategories[subcat].append(skill)
                    categorized = True
                    break
            
            if not categorized:
                # Add to first subcategory as fallback
                first_subcat = list(subcat_keywords.keys())[0]
                subcategories[first_subcat].append(skill)
        
        return dict(subcategories)

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

    def generate_domain_file(self, category_name: str, skills_in_category: List[Dict]) -> str:
        """Generate a domain-specific markdown file content."""
        lines = []
        
        # Add header with back navigation
        lines.append(f"# {category_name}")
        lines.append("")
        lines.append(f"[← Back to Main README](../README.md)")
        lines.append("")
        lines.append(f"*{len(skills_in_category)} skills in this domain*")
        lines.append("")
        
        # Check if category has subcategories (only for large categories with 50+ skills)
        subcategories = self._get_subcategories(category_name, skills_in_category) if len(skills_in_category) >= 50 else {}
        
        if subcategories:
            # Add table of contents for subcategories
            lines.append("## Table of Contents")
            lines.append("")
            sorted_subcats = sorted(
                [(k, v) for k, v in subcategories.items() if v],
                key=lambda x: len(x[1]),
                reverse=True
            )
            for subcat_name, subcat_skills in sorted_subcats:
                anchor = subcat_name.lower().replace(" ", "-")
                anchor = ''.join(c if c.isalnum() or c == '-' else '' for c in anchor)
                while '--' in anchor:
                    anchor = anchor.replace('--', '-')
                lines.append(f"- [{subcat_name}](#{anchor}) - {len(subcat_skills)} skills")
            lines.append("")
            
            # Display by subcategories
            for subcat_name, subcat_skills in sorted_subcats:
                # Create anchor for subcategory
                anchor = subcat_name.lower().replace(" ", "-")
                anchor = ''.join(c if c.isalnum() or c == '-' else '' for c in anchor)
                while '--' in anchor:
                    anchor = anchor.replace('--', '-')
                
                # Subheader for subcategory
                lines.append(f'<a name="{anchor}"></a>')
                lines.append(f"## {subcat_name}")
                lines.append(f"*{len(subcat_skills)} skills*")
                lines.append("")
                
                # Create skills table for this subcategory
                lines.append("| Skill | Description | Author |")
                lines.append("| --- | --- | --- |")
                
                # Sort skills by name within subcategory
                sorted_skills = sorted(subcat_skills, key=lambda x: x.get('name', '').lower())
                
                for skill in sorted_skills:
                    name = skill.get('name', 'Unknown')
                    url = skill.get('url', '') or skill.get('readme_url', '')
                    description = skill.get('description', '').replace('\n', ' ').strip()
                    # Truncate description to ~100 chars
                    if len(description) > 100:
                        description = description[:97] + '...'
                    author = skill.get('author', '') or skill.get('repo_owner', 'Unknown')
                    
                    if url:
                        skill_link = f"[{name}]({url})"
                    else:
                        skill_link = name
                    
                    # Escape pipe characters and Liquid syntax in description
                    description = description.replace("|", "\\|")
                    description = self._escape_liquid_syntax(description)
                    
                    lines.append(f"| {skill_link} | {description} | {author} |")
                
                lines.append("")
        else:
            # Display all skills without subcategories
            lines.append("| Skill | Description | Author |")
            lines.append("| --- | --- | --- |")
            
            # Sort skills by name within category
            sorted_skills = sorted(skills_in_category, key=lambda x: x.get('name', '').lower())
            
            for skill in sorted_skills:
                name = skill.get('name', 'Unknown')
                url = skill.get('url', '') or skill.get('readme_url', '')
                description = skill.get('description', '').replace('\n', ' ').strip()
                # Truncate description to ~100 chars
                if len(description) > 100:
                    description = description[:97] + '...'
                author = skill.get('author', '') or skill.get('repo_owner', 'Unknown')
                
                if url:
                    skill_link = f"[{name}]({url})"
                else:
                    skill_link = name
                
                # Escape pipe characters and Liquid syntax in description
                description = description.replace("|", "\\|")
                description = self._escape_liquid_syntax(description)
                
                lines.append(f"| {skill_link} | {description} | {author} |")
            
            lines.append("")
        
        # Add back navigation at bottom
        lines.append("")
        lines.append(f"[← Back to Main README](../README.md)")
        
        return "\n".join(lines)
    
    def generate_domain_files_mapping(self) -> Dict[str, str]:
        """Generate mapping of domain filenames to their content."""
        if not self.skills:
            return {}
        
        domain_files = {}
        
        # Get intelligent categories
        intelligent_categories = self._get_intelligent_categories()
        
        # Sort categories by count (descending) then alphabetically
        sorted_categories = sorted(
            intelligent_categories.items(), 
            key=lambda x: (-len(x[1]), x[0])
        )
        
        # Generate content for each category
        for category_name, skills_in_category in sorted_categories:
            if not skills_in_category:
                continue
            
            filename = self._category_to_filename(category_name)
            content = self.generate_domain_file(category_name, skills_in_category)
            domain_files[filename] = content
        
        return domain_files

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
        """Generate README content with Contents section that links to FULL-SKILLS.md."""
        lines = []

        # Start with title and badges
        lines.append(self.generate_title().strip())

        # Add Contents section
        lines.append(self.generate_table_of_contents_for_full_readme())

        # Add main sections to README.md
        lines.append(self.generate_creating_skills().strip())
        lines.append("")
        lines.append(self.generate_contributing().strip())
        lines.append("")
        lines.append(self.generate_resources().strip())
        lines.append("")
        lines.append(self.generate_community().strip())
        lines.append("")
        lines.append(self.generate_license().strip())

        content = "\n".join(lines)

        # Validate markdown format
        if not self.validate_markdown(content):
            logger.warning("Generated markdown failed validation")
        else:
            logger.info("Generated markdown validation successful")

        return content

    def generate_table_of_contents_for_full_readme(self) -> str:
        """Generate Contents section for README that links to FULL-SKILLS.md sections."""
        lines = ["\n## Contents\n"]

        # Add main sections (these stay in README.md)
        lines.extend([
            "- [Creating Skills](#creating-skills)",
            "- [Contributing](#contributing)",
            "- [Resources](#resources)",
            "- [Join the Community](#join-the-community)",
            "- [License](#license)",
        ])

        # Add skills by domain section (links to FULL-SKILLS.md)
        lines.append("- **Skills by Domain:**")

        # Get intelligent categories
        intelligent_categories = self._get_intelligent_categories()
        sorted_categories = sorted(
            intelligent_categories.items(),
            key=lambda x: (-len(x[1]), x[0])
        )

        # Add category links to TOC - point to FULL-SKILLS.md
        for category_name, skills_in_category in sorted_categories:
            if not skills_in_category:
                continue

            anchor = self._category_to_anchor(category_name)
            lines.append(f"  - [{category_name}](FULL-SKILLS.md#{anchor})")

            # Add subcategories to TOC if they exist (for large categories)
            subcategories = self._get_subcategories(category_name, skills_in_category) if len(skills_in_category) >= 50 else {}
            if subcategories:
                sorted_subcats = sorted(
                    [(k, v) for k, v in subcategories.items() if v],
                    key=lambda x: len(x[1]),
                    reverse=True
                )
                for subcat_name, _ in sorted_subcats:
                    sub_anchor = self._category_to_anchor(f"{category_name}-{subcat_name}")
                    lines.append(f"    - [{subcat_name}](FULL-SKILLS.md#{sub_anchor})")

        lines.append("")

        return "\n".join(lines)

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

    def generate_full_document(self) -> str:
        """Generate a comprehensive full document with all table of contents and all skill tables."""
        lines = []

        # Start with main README content but replace table of contents with full document version
        main_readme = self.generate_readme()
        # Replace the table of contents section with the full document version
        toc_pattern = r"## Table of Contents\n\n.*?(?=\n## |\n## Creating Skills|\Z)"
        full_toc = self.generate_full_document_table_of_contents()
        main_readme_with_full_toc = re.sub(toc_pattern, full_toc.strip(), main_readme, flags=re.DOTALL)
        lines.append(main_readme_with_full_toc.rstrip())
        lines.append("")

        # Add separator for full skill listing
        lines.append("---")
        lines.append("")

        # Add anchor for direct linking to skills listing
        lines.append('<a name="complete-skills-listing"></a>')
        lines.append("")

        # Add full skills section header
        lines.append("# Complete Skills Listing")
        lines.append("")
        lines.append("*This section contains all skills organized by domain with complete tables.*")
        lines.append("")

        # Generate complete table of contents for all skills
        lines.append("## Complete Contents")
        lines.append("")

        # Get intelligent categories
        intelligent_categories = self._get_intelligent_categories()
        sorted_categories = sorted(
            intelligent_categories.items(),
            key=lambda x: (-len(x[1]), x[0])
        )

        # Build TOC with anchors to each domain section
        toc_entries = []
        for category_name, skills_in_category in sorted_categories:
            if not skills_in_category:
                continue

            count = len(skills_in_category)
            anchor = self._category_to_anchor(category_name)
            toc_entries.append(f"- [{category_name}](#{anchor}) - {count} skills")

            # Add subcategories to TOC if they exist
            subcategories = self._get_subcategories(category_name, skills_in_category) if len(skills_in_category) >= 50 else {}
            if subcategories:
                sorted_subcats = sorted(
                    [(k, v) for k, v in subcategories.items() if v],
                    key=lambda x: len(x[1]),
                    reverse=True
                )
                for subcat_name, subcat_skills in sorted_subcats:
                    sub_anchor = self._category_to_anchor(f"{category_name}-{subcat_name}")
                    toc_entries.append(f"  - [{subcat_name}](#{sub_anchor}) - {len(subcat_skills)} skills")

        lines.extend(toc_entries)
        lines.append("")

        # Now add all the actual skill content
        for category_name, skills_in_category in sorted_categories:
            if not skills_in_category:
                continue

            # Add domain header
            anchor = self._category_to_anchor(category_name)
            lines.append(f'<a name="{anchor}"></a>')
            lines.append(f"# {category_name}")
            lines.append("")
            lines.append(f"*{len(skills_in_category)} skills in this domain*")
            lines.append("")

            # Check if category has subcategories
            subcategories = self._get_subcategories(category_name, skills_in_category) if len(skills_in_category) >= 50 else {}

            if subcategories:
                # Add subcategory TOC
                lines.append("## Table of Contents")
                lines.append("")
                sorted_subcats = sorted(
                    [(k, v) for k, v in subcategories.items() if v],
                    key=lambda x: len(x[1]),
                    reverse=True
                )
                for subcat_name, subcat_skills in sorted_subcats:
                    sub_anchor = self._category_to_anchor(f"{category_name}-{subcat_name}")
                    lines.append(f"- [{subcat_name}](#{sub_anchor}) - {len(subcat_skills)} skills")
                lines.append("")

                # Display by subcategories
                for subcat_name, subcat_skills in sorted_subcats:
                    sub_anchor = self._category_to_anchor(f"{category_name}-{subcat_name}")
                    lines.append(f'<a name="{sub_anchor}"></a>')
                    lines.append(f"## {subcat_name}")
                    lines.append(f"*{len(subcat_skills)} skills*")
                    lines.append("")

                    # Create skills list for this subcategory using awesome format
                    lines.append("### Skills")
                    lines.append("")

                    # Sort skills by name within subcategory
                    sorted_skills = sorted(subcat_skills, key=lambda x: x.get('name', '').lower())

                    for skill in sorted_skills:
                        name = skill.get('name', 'Unknown')
                        url = skill.get('url', '') or skill.get('readme_url', '')
                        description = skill.get('description', '').replace('\n', ' ').strip()

                        # Keep descriptions concise like awesome lists
                        if len(description) > 120:
                            description = description[:117] + '...'

                        if url:
                            skill_link = f"[{name}]({url})"
                        else:
                            skill_link = name

                        lines.append(f"- {skill_link} - {description}")

                    lines.append("")
            else:
                # Display all skills without subcategories using awesome format
                lines.append("### Skills")
                lines.append("")

                # Sort skills by name within category
                sorted_skills = sorted(skills_in_category, key=lambda x: x.get('name', '').lower())

                for skill in sorted_skills:
                    name = skill.get('name', 'Unknown')
                    url = skill.get('url', '') or skill.get('readme_url', '')
                    description = skill.get('description', '').replace('\n', ' ').strip()

                    # Keep descriptions concise like awesome lists
                    if len(description) > 120:
                        description = description[:117] + '...'

                    if url:
                        skill_link = f"[{name}]({url})"
                    else:
                        skill_link = name

                    lines.append(f"- {skill_link} - {description}")

                lines.append("")

        return "\n".join(lines)

    def _category_to_anchor(self, category_name: str) -> str:
        """Convert category name to HTML anchor."""
        anchor = category_name.lower()
        anchor = anchor.replace(" ", "-")
        anchor = anchor.replace("&", "and")
        anchor = ''.join(c if c.isalnum() or c == '-' else '' for c in anchor)
        while '--' in anchor:
            anchor = anchor.replace('--', '-')
        return anchor

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

            logger.info("Markdown validation passed")
            return True

        except Exception as e:
            logger.error(f"Markdown validation failed: {e}")
            return False
