from dataclasses import dataclass


@dataclass
class RequirementNotFulfilledError(Exception):
  pass  # TODO: Include data about exact unfulfilled reqs.
