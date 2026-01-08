# Awesome Claude Skills

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Chat2AnyLLM/awesome-claude-skills/pulls)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A curated list of awesome Claude Code skills to enhance your Claude Code experience.

Total Skills: 3769

Last updated: 2026-01-08 12:49 UTC

**[📋 View Complete Skills List](FULL-SKILLS.md)** - Convenient for searching through all skills without size limits.
## What Are Claude Skills?

Claude Skills are customizable workflows and tools that extend Claude's capabilities. They allow you to:

- **Automate repetitive tasks** - Create reusable workflows for common development patterns
- **Integrate with external tools** - Connect Claude with APIs, databases, and services
- **Enhance productivity** - Leverage specialized expertise across different domains
- **Customize behavior** - Adapt Claude's responses for specific use cases and requirements

Skills can be used across Claude.ai, Claude Code, and the Claude API to provide domain-specific assistance and automation.
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

Skills can also be used programmatically via the Claude API for automation and integration purposes.
## Table of Contents

- [What Are Claude Skills?](#what-are-claude-skills)
- [Getting Started](#getting-started)
  - [Installation](#installation)
  - [Using Skills in Claude Code](#using-skills-in-claude-code)
  - [Using Skills with Claude API](#using-skills-with-claude-api)
- **Skills by Domain:**
  - [Backend Development](./domains/backend-development.md) - 1475 skills
  - [DevOps & Infrastructure](./domains/devops-and-infrastructure.md) - 439 skills
  - [Data & Analytics](./domains/data-and-analytics.md) - 315 skills
  - [AI & LLM](./domains/ai-and-llm.md) - 262 skills
  - [Version Control & Collaboration](./domains/version-control-and-collaboration.md) - 261 skills
  - [Frontend Development](./domains/frontend-development.md) - 224 skills
  - [Machine Learning](./domains/machine-learning.md) - 184 skills
  - [Testing & Quality](./domains/testing-and-quality.md) - 178 skills
  - [Security](./domains/security.md) - 169 skills
  - [Uncategorized](./domains/uncategorized.md) - 103 skills
  - [Documentation](./domains/documentation.md) - 80 skills
  - [Tools & Utilities](./domains/tools-and-utilities.md) - 65 skills
  - [Business & Productivity](./domains/business-and-productivity.md) - 14 skills
- [Creating Skills](#creating-skills)
  - [Skill Development](#skill-development)
  - [Best Practices](#best-practices)
  - [Resources](#resources)
- [Contributing](#contributing)
- [Resources](#resources)
  - [Official Documentation](#official-documentation)
  - [Community Resources](#community-resources)
  - [Development Tools](#development-tools)
- [Join the Community](#join-the-community)
  - [Social Media](#social-media)
  - [Contribution](#contribution)
  - [Support](#support)
- [License](#license)

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
- [Community Examples](https://github.com/anthropics/claude-code/tree/main/examples)
## Contributing

We welcome contributions! Please see our [contributing guidelines](CONTRIBUTING.md) for details on how to add new marketplaces or skills.

To add a new skill or marketplace:
1. Fork this repository
2. Add the entry to the appropriate section
3. Ensure the skill is verified and documented
4. Submit a pull request with a clear description

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
- [Claude CLI](https://github.com/anthropics/claude-code/tree/main/packages/cli) - Command-line interface for Claude
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
- **Stack Overflow**: [claude-code tag](https://stackoverflow.com/questions/tagged/claude-code)
## License

This repository is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

---

*Built with ❤️ by the Claude Code community. Empowering developers with AI-enhanced workflows.*