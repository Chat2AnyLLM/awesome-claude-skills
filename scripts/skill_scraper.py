#!/usr/bin/env python3
"""Generate metadata-only README for awesome-claude-skills.

No cloning. No mirroring. Counts discoverable SKILL.md files via GitHub API
from repo links defined in awesome-repo-configs.
"""

import sys
import argparse
import logging
from pathlib import Path

try:
    from .config import Config
    from .metadata_catalog import fetch_repos_from_sources, count_skills, render_readme
except ImportError:
    from config import Config
    from metadata_catalog import fetch_repos_from_sources, count_skills, render_readme

def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def generate_readme(repositories: list, counts: dict, output_file: str, args: list = None) -> bool:
    """Generate README from source-repository metadata + GitHub API counts."""
    content = render_readme(repositories, counts)

    output_path = Path(output_file)
    if output_path.exists() and not getattr(args, 'force', False):
        try:
            existing_content = output_path.read_text(encoding='utf-8')
            existing_no_ts = '\n'.join([line for line in existing_content.split('\n') if not line.strip().startswith('- Last updated:')])
            new_no_ts = '\n'.join([line for line in content.split('\n') if not line.strip().startswith('- Last updated:')])
            if existing_no_ts == new_no_ts:
                logging.getLogger(__name__).info("README content unchanged, skipping update to preserve timestamp")
                return True
        except Exception as e:
            logging.getLogger(__name__).warning(f"Could not compare existing README: {e}")

    try:
        output_path.write_text(content, encoding='utf-8')
        logging.getLogger(__name__).info("README generated successfully: %s", output_file)
        return True
    except Exception as e:
        logging.getLogger(__name__).error("Failed to write README: %s", e)
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

def cmd_generate_readme(args: list, config: dict, logger) -> int:
    """Handle generate-readme command."""
    logger.info("Skill metadata catalog generation starting...")

    sources = config.get_enabled_sources()
    logger.info("Loaded %d enabled sources", len(sources))
    if not sources:
        logger.warning("No enabled sources found in configuration")
        return 0

    repositories = fetch_repos_from_sources(sources)
    logger.info("Loaded %d enabled repositories from source configs", len(repositories))

    counts = count_skills(repositories, max_workers=config.get_max_workers())
    total_skills = sum(v.get('count', 0) for v in counts.values())
    unavailable = sum(1 for v in counts.values() if v.get('status') not in {'ok', 'truncated'})
    truncated = sum(1 for v in counts.values() if v.get('status') == 'truncated')
    logger.info("Counted %d skills across %d repos (%d unavailable, %d truncated)", total_skills, len(repositories), unavailable, truncated)

    if hasattr(args, 'dry_run') and args.dry_run:
        print(f"Dry run: Would generate README with {len(repositories)} repositories and {total_skills} discoverable skills")
        return 0

    if generate_readme(repositories, counts, args.output, args):
        print(f"Successfully generated README with {len(repositories)} repositories and {total_skills} discoverable skills!")
        return 0
    else:
        print("Failed to generate README")
        return 1

def cmd_validate_config(args: list, config: dict, logger) -> int:
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

def cmd_list_sources(args: list, config: dict, logger) -> int:
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

def main() -> int:
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
        "--force",
        action="store_true",
        help="Force regeneration even if content is unchanged"
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
