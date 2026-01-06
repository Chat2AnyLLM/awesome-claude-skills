"""Git repository operations with caching."""

import shutil
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class GitRepository:
    """Git repository downloader with branch fallback."""

    BRANCH_FALLBACKS = ["main", "master", "develop", "development", "dev", "trunk"]

    def __init__(self, owner: str, name: str, branch: Optional[str] = None):
        """Initialize git repository.

        Args:
            owner: Repository owner
            name: Repository name
            branch: Branch to clone (None means auto-detect default branch)
        """
        self.owner = owner
        self.name = name
        self.branch = branch  # None means auto-detect
        self.url = f"https://github.com/{owner}/{name}.git"

    def _get_default_branch(self) -> str:
        """Get the default branch of a repository using git ls-remote."""
        try:
            logger.debug(f"Detecting default branch for {self.url}")
            result = subprocess.run(
                ["git", "ls-remote", "--symref", self.url, "HEAD"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.startswith("ref: refs/heads/"):
                        # Output format: "ref: refs/heads/main  HEAD"
                        parts = line.split('\t')
                        if len(parts) > 0:
                            detected_branch = parts[0].replace("ref: refs/heads/", "").strip()
                            logger.info(f"Detected default branch '{detected_branch}' for {self.owner}/{self.name}")
                            return detected_branch
        except Exception as e:
            logger.warning(f"Failed to detect default branch for {self.url}: {e}")

        return "main"

    @contextmanager
    def clone(self) -> Generator[Tuple[Path, str], None, None]:
        """Clone repository to temporary directory.

        Yields:
            Tuple of (temp_dir, actual_branch)
        """
        temp_dir = Path(tempfile.mkdtemp(prefix=f"cam_{self.name}_"))
        actual_branch = self.branch

        try:
            # Determine which branch to use
            if self.branch is None:
                # Auto-detect default branch
                actual_branch = self._get_default_branch()
            else:
                actual_branch = self.branch
                # If branch is default "main", try to detect actual default branch
                if self.branch == "main":
                    detected_branch = self._get_default_branch()
                    if detected_branch != "main":
                        actual_branch = detected_branch

            # Try the detected/requested branch first
            branches_to_try = [actual_branch]

            # Add fallbacks if branch is common
            if actual_branch in self.BRANCH_FALLBACKS:
                branches_to_try.extend([b for b in self.BRANCH_FALLBACKS if b != actual_branch])

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