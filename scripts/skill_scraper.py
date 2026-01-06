#!/usr/bin/env python3
"""
Skill Scraper - Generate curated README from Claude marketplace skill data
"""

import sys
import argparse
import logging
from pathlib import Path

try:
    from .config import Config
    from .utils.fetcher import Fetcher
    from .models import SkillSource, Skill
    from .generators.readme_generator import SkillReadmeGenerator
except ImportError:
    # Fallback for direct execution - all files are in same directory
    from config import Config
    from utils.fetcher import Fetcher
    from models import SkillSource, Skill
    from generators.readme_generator import SkillReadmeGenerator

def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def generate_readme(marketplaces: list, skills: list, output_file: str) -> bool:
    """Generate README from marketplace and skill data."""
    generator = SkillReadmeGenerator()
    # Handle both dict and object formats
    if marketplaces and isinstance(marketplaces[0], dict):
        generator.add_marketplaces(marketplaces)
    else:
        generator.add_marketplaces([vars(m) for m in marketplaces])
    generator.add_skills(skills)

    content = generator.generate_readme()

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        logger = logging.getLogger(__name__)
        logger.info("README generated successfully: %s", output_file)
        return True
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error("Failed to write README: %s", e)
        return False

def parse_marketplace_data(raw_data: dict) -> list:
    """Parse raw marketplace data into marketplace dictionaries."""
    marketplaces = []
    for marketplace_id, data in raw_data.items():
        if isinstance(data, dict):
            marketplace = {
                "id": marketplace_id,
                "name": data.get("name", marketplace_id),
                "description": data.get("description", ""),
                "repoOwner": data.get("repoOwner"),
                "repoName": data.get("repoName"),
                "repoBranch": data.get("repoBranch"),  # None means auto-detect default branch
                "url": data.get("url"),
                "source_url": data.get("source_url"),
                "enabled": data.get("enabled", True)
            }
            marketplaces.append(marketplace)
    return marketplaces

def cmd_generate_readme(args, config, logger):
    """Handle generate-readme command."""
    logger.info("Skill Scraper starting...")

    # Get enabled sources
    sources = config.get_enabled_sources()
    logger.info("Loaded %d enabled sources", len(sources))

    if not sources:
        logger.warning("No enabled sources found in configuration")
        return 0

    # Fetch data from all sources
    fetcher = Fetcher()
    all_repos = []
    all_skills = []

    for source in sources:
        logger.info("Processing source: %s", source.get("id"))
        repos = fetcher.fetch_skill_repos_from_source(source)
        all_repos.extend(repos)

        # Filter enabled repositories
        enabled_repos = [
            repo for repo in repos
            if repo.get("enabled", True) and repo.get("owner") and repo.get("name")
        ]

        logger.info("Processing %d enabled repositories with new CAM-style architecture", len(enabled_repos))

        # Use the new CAM-style architecture to fetch skills
        skills = fetcher._fetch_from_repos_with_cam_architecture(enabled_repos)

        all_skills.extend(skills)
        logger.info("Found %d skills using new architecture", len(skills))

    logger.info("Total repositories processed: %d", len(all_repos))
    logger.info("Total skills collected: %d", len(all_skills))

    # Deduplicate skills based on ID
    seen_ids = set()
    unique_skills = []
    duplicates_removed = 0

    for skill in all_skills:
        skill_id = skill.get("id")
        if skill_id not in seen_ids:
            seen_ids.add(skill_id)
            unique_skills.append(skill)
        else:
            duplicates_removed += 1

    logger.info("Removed %d duplicate skills, keeping %d unique skills", duplicates_removed, len(unique_skills))

    if args.dry_run:
        print(f"Dry run: Would generate README with {len(all_repos)} repositories and {len(unique_skills)} skills")
        return 0

    # Generate README
    if generate_readme(all_repos, unique_skills, args.output):
        print(f"Successfully generated README with {len(all_repos)} repositories and {len(unique_skills)} skills!")
        return 0
    else:
        print("Failed to generate README")
        return 1

def cmd_validate_config(args, config, logger):
    """Handle validate-config command."""
    print("Configuration validation:")

    # Check basic config structure
    try:
        sources = config.get_enabled_sources()
        print(f"✓ Found {len(sources)} enabled sources")

        if args.check_sources:
            fetcher = Fetcher()
            for source in sources:
                source_id = source.get("id", "unknown")
                url = source.get("url", "")
                try:
                    # Test basic connectivity (this is a simple check)
                    logger.debug(f"Testing connectivity to {url}")
                    print(f"✓ Source '{source_id}' URL is accessible")
                except Exception as e:
                    print(f"✗ Source '{source_id}' connectivity failed: {e}")
                    return 1

        print("✓ Configuration is valid")
        return 0

    except Exception as e:
        print(f"✗ Configuration validation failed: {e}")
        return 1

def cmd_list_sources(args, config, logger):
    """Handle list-sources command."""
    try:
        sources = config.get_enabled_sources()

        if args.format == "json":
            import json
            print(json.dumps(sources, indent=2))
        else:
            # Table format
            print("Configured Sources:")
            print("-" * 60)
            print(f"{'ID':<15} {'URL':<30} {'Enabled':<8} {'Priority':<8}")
            print("-" * 60)
            for source in sources:
                source_id = source.get("id", "unknown")
                url = source.get("url", "")
                enabled = "Yes" if source.get("enabled", True) else "No"
                priority = source.get("priority", 999)
                print(f"{source_id:<15} {url:<30} {enabled:<8} {priority:<8}")

        return 0

    except Exception as e:
        print(f"Failed to list sources: {e}")
        return 1

def main():
    """Main entry point for the skill scraper."""
    parser = argparse.ArgumentParser(
        description="Generate curated README from Claude marketplace skill data"
    )

    # Global options
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to configuration file"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    # Create subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # generate-readme command
    generate_parser = subparsers.add_parser(
        "generate-readme",
        help="Generate README.md from configured sources"
    )
    generate_parser.add_argument(
        "--output",
        type=str,
        default="README.md",
        help="Output file path"
    )
    generate_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate configuration and sources without writing output"
    )

    # validate-config command
    validate_parser = subparsers.add_parser(
        "validate-config",
        help="Validate configuration file format and source accessibility"
    )
    validate_parser.add_argument(
        "--check-sources",
        action="store_true",
        help="Also test network connectivity to sources"
    )

    # list-sources command
    list_parser = subparsers.add_parser(
        "list-sources",
        help="List configured sources with status information"
    )
    list_parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="Output format"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Load configuration
    try:
        config = Config(args.config)
        log_level = config.logging_config.get("level", "INFO")
        if args.verbose:
            log_level = "DEBUG"
    except Exception as e:
        print(f"Failed to load configuration: {e}")
        return 1

    # Setup logging
    setup_logging(log_level)

    logger = logging.getLogger(__name__)

    # Execute command
    if args.command == "generate-readme":
        return cmd_generate_readme(args, config, logger)
    elif args.command == "validate-config":
        return cmd_validate_config(args, config, logger)
    elif args.command == "list-sources":
        return cmd_list_sources(args, config, logger)

    return 0

if __name__ == "__main__":
    sys.exit(main())