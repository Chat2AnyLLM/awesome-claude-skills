"""Git repository operations with caching."""

import shutil
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Tuple
import logging

logger = logging.getLogger(__name__)


class GitRepository:
    """Git repository downloader with branch fallback."""

    BRANCH_FALLBACKS = ["main", "master", "develop", "development", "dev", "trunk"]

    def __init__(self, owner: str, name: str, branch: str = "main"):
        """Initialize git repository.

        Args:
            owner: Repository owner
            name: Repository name
            branch: Branch to clone (with automatic fallback)
        """
        self.owner = owner
        self.name = name
        self.branch = branch
        self.url = f"https://github.com/{owner}/{name}.git"

    @contextmanager
    def clone(self) -> Generator[Tuple[Path, str], None, None]:
        """Clone repository to temporary directory.

        Yields:
            Tuple of (temp_dir, actual_branch)
        """
        temp_dir = Path(tempfile.mkdtemp(prefix=f"cam_{self.name}_"))
        actual_branch = self.branch

        try:
            # Try requested branch first
            branches_to_try = [self.branch]

            # Add fallbacks if branch is common
            if self.branch in self.BRANCH_FALLBACKS:
                branches_to_try.extend([b for b in self.BRANCH_FALLBACKS if b != self.branch])

            success = False
            for branch in branches_to_try:
                try:
                    logger.info(f"Cloning {self.url} (branch: {branch})...")
                    subprocess.run(
                        ["git", "clone", "--depth", "1", "--branch", branch, self.url, str(temp_dir)],
                        check=True,
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    actual_branch = branch
                    success = True
                    logger.info(f"Successfully cloned {self.owner}/{self.name} on branch {branch}")
                    break
                except subprocess.CalledProcessError:
                    if branch == branches_to_try[-1]:
                        # All branches failed, raise RuntimeError instead of CalledProcessError
                        raise RuntimeError(f"Failed to clone repository from any branch")
                    logger.debug(f"Branch {branch} not found, trying next...")

            if not success:
                raise RuntimeError(f"Failed to clone repository from any branch")

            yield temp_dir, actual_branch

        finally:
            # Cleanup
            shutil.rmtree(temp_dir, ignore_errors=True)