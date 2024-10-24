from collections.abc import Iterable

from .check import check_reqs
from .exceptions import RequirementNotFulfilledError


def require(requirement_strs: Iterable[str]) -> None:
  if not check_reqs(requirement_strs):
    raise RequirementNotFulfilledError()  # TODO include data on which ones


__all__ = ["require", "RequirementNotFulfilledError"]
