"""
Simple tests not requiring separate envs like the e2e tests.

Specifically, these are simpler in the sense that they all run the library
functions under test in the same Python interpreter that was used to launch
pytest.
This makes them more limited in that we can only test against packages
installed in this Python environment, not create new venvs or anything like
that like we do in e2e, but the upshot is that we get coverage and run faster.
"""
import pytest

from check_reqs import RequirementNotFulfilledError, require


def test_packaging_installed() -> None:
  require(["packaging"])


def test_sane_packaging_version_installed() -> None:
  require(["packaging<100000000"])


def test_insane_packaging_version_not_installed() -> None:
  with pytest.raises(RequirementNotFulfilledError):
    require(["packaging>100000000"])


def test_numpy_not_installed() -> None:
  with pytest.raises(RequirementNotFulfilledError):
    require(["numpy"])


def test_pytest_installed() -> None:
  require(["pytest"])


def test_pytest_dev_extra_not_installed() -> None:
  with pytest.raises(RequirementNotFulfilledError):
    require(["pytest[dev]"])


def test_mypy_installed() -> None:
  require(["mypy"])


def test_mypy_dmypy_extra_installed() -> None:
  require(["mypy[dmypy]"])


# TODO: I don't like this behavior, IMHO it should raise for nonexistent extra
@pytest.mark.xfail(
  strict=True, reason="documented limitation of original hbutils function"
)
def test_nonexistent_extra_not_installed() -> None:
  with pytest.raises(RequirementNotFulfilledError):
    require(["packaging[nonexistent-extra]"])
