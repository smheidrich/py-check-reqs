from pathlib import Path
from tempfile import gettempdir

import pytest


@pytest.fixture(scope="session")
def cache_path() -> Path:
  """
  Path of cache directory that persists across pytest sessions/invocations.
  """
  temp_root_path = Path(gettempdir())
  cache_dir_path = temp_root_path / "pytest-cache-check-reqs"
  cache_dir_path.mkdir(exist_ok=True)
  return cache_dir_path
