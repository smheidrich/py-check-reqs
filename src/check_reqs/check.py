# Copyright see https://github.com/HansBug/hbutils at commit cited below
# SPDX-License-Identifier: Apache-2.0

# This file was originally based on the `check_reqs` function from the
# `hbutils` package at commit 927b0757449a781ce8e30132f26b06089a24cd71.
# By now, it is barely recognizable as such and is expected to become even less
# so in the future, but AFAIK that is irrelevant as far as copyright is
# concerned and so it retains the original `hbutils` license & copyright.

from collections.abc import Iterable
from importlib.metadata import PackageNotFoundError, distribution, metadata

from packaging.metadata import Metadata, RawMetadata
from packaging.requirements import Requirement


def check_reqs(req_strs: Iterable[str]) -> bool:
  return all(
    _check_req_recursive(req)
    for req_str in req_strs
    if not (req := Requirement(req_str)).marker or req.marker.evaluate()
  )


def _check_req_recursive(req: Requirement) -> bool:
  try:
    version = distribution(req.name).version
  except PackageNotFoundError:
    return False  # req not installed

  if not req.specifier.contains(version):
    return False  # req version does not match

  jsonish_req_metadata = metadata(req.name).json
  # We can ignore the type because if it somehow doesn't match the expected
  # format, Metadata.from_raw will raise an exception - oh well.
  raw_req_metadata: RawMetadata = jsonish_req_metadata  # type: ignore[assignment]
  req_metadata = Metadata.from_raw(raw_req_metadata, validate=False)
  for child_req in req_metadata.requires_dist or []:
    # A dependency is only required to be present if ...
    if (
      not child_req.marker  # ... it doesn't have a marker
      or child_req.marker.evaluate()  # ... its marker matches our env
      or any(  # ... its marker matches our env given one of our extras
        child_req.marker.evaluate({"extra": extra}) for extra in req.extras
      )
    ):
      if not _check_req_recursive(child_req):
        return False

  return True
