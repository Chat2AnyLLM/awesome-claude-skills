"""Parallel processing utilities for repository fetching."""

import concurrent.futures
import logging
import threading
from typing import Callable, List, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar('T')
R = TypeVar('R')


class ParallelFetcher:
    """Generic parallel fetcher using ThreadPoolExecutor."""

    def __init__(
        self,
        fetcher_func: Callable[[T], R],
        max_workers: int = 8
    ):
        """Initialize parallel fetcher.

        Args:
            fetcher_func: Function to fetch from single source
            max_workers: Maximum concurrent workers
        """
        self.fetcher_func = fetcher_func
        self.max_workers = max_workers
        self.results: List[R] = []
        self.lock = threading.Lock()

    def fetch_all(self, sources: List[T]) -> List[R]:
        """Fetch from all sources in parallel.

        Args:
            sources: List of sources to fetch from

        Returns:
            List of results from all sources
        """
        if not sources:
            return []

        actual_workers = min(self.max_workers, len(sources))
        logger.debug(f"Using {actual_workers} concurrent workers")

        with concurrent.futures.ThreadPoolExecutor(max_workers=actual_workers) as executor:
            # Submit all tasks
            future_to_source = {
                executor.submit(self._fetch_safe, source): source
                for source in sources
            }

            # Wait for completion
            for future in concurrent.futures.as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    result = future.result()
                    if result:
                        with self.lock:
                            self.results.append(result)
                except Exception as e:
                    logger.error(f"Exception fetching from {source}: {e}")

        return self.results

    def _fetch_safe(self, source: T) -> R:
        """Safely fetch from source with error handling."""
        try:
            return self.fetcher_func(source)
        except Exception as e:
            logger.warning(f"Failed to fetch from {source}: {e}")
            return None