import os
import subprocess as sp
import venv
from pathlib import Path
from sys import stderr
from textwrap import dedent
from typing import Protocol

import pytest


class MakeVenvWithPkgInstalled(Protocol):
  def __call__(self, dir_name: str, extra_cmd: str) -> Path:
    ...


@pytest.fixture(scope="session")
def make_venv_with_pkg_installed(cache_path: Path) -> MakeVenvWithPkgInstalled:
  def _make_venv_with_pkg_installed(dir_name: str, extra_cmd: str) -> Path:
    venv_path = cache_path / dir_name
    install_succeeded_marker_path = venv_path / "install-succeeded"

    if install_succeeded_marker_path.exists():
      print(
        dedent(
          f"""\
          Reusing {dir_name} venv from a previous test session:
          {venv_path}
          If something goes wrong, try deleting it?
          """.rstrip()
        ),
        file=stderr,
      )
    else:
      venv.create(venv_path, with_pip=True)
      cwd = os.getcwd()
      sp.run(
        f". {venv_path}/bin/activate && pip install -e {cwd} && {extra_cmd}",
        shell=True,
        check=True,
      )
      install_succeeded_marker_path.touch()
    return venv_path

  return _make_venv_with_pkg_installed


@pytest.fixture(scope="session")
def venv_with_typer_slim_path(
  make_venv_with_pkg_installed: MakeVenvWithPkgInstalled,
) -> Path:
  """
  Path of a venv with typer-slim==0.12.5 installed.
  """
  return make_venv_with_pkg_installed(
    "typer-slim", "pip install typer-slim==0.12.5"
  )


@pytest.fixture(scope="session")
def venv_with_typer_slim_standard_path(
  make_venv_with_pkg_installed: MakeVenvWithPkgInstalled,
) -> Path:
  """
  Path of a venv with typer-slim[standard]==0.12.5 installed.
  """
  return make_venv_with_pkg_installed(
    "typer-slim-standard", "pip install 'typer-slim[standard]==0.12.5'"
  )


@pytest.fixture(scope="session")
def venv_with_typer_slim_standard_no_pygments_path(
  make_venv_with_pkg_installed: MakeVenvWithPkgInstalled,
) -> Path:
  """
  Path of venv after typer-slim[standard]==0.12.5 install & Pygments uninstall.

  Because the `standard` extra depends on `rich` and `rich` depends on
  `Pygments`, uninstalling Pygments makes the extra no longer fulfilled.
  """
  return make_venv_with_pkg_installed(
    "typer-slim-standard-no-pygments",
    "pip install 'typer-slim[standard]==0.12.5' && pip uninstall -y Pygments",
  )


def test_non_extra_requirement_fulfilled(
  venv_with_typer_slim_path: Path,
) -> None:
  sp.run(
    [
      venv_with_typer_slim_path / "bin/python",
      "-c",
      "from check_reqs import require; require(['typer-slim'])",
    ],
    check=True,
  )


def test_extra_requirement_not_fulfilled(
  venv_with_typer_slim_path: Path,
) -> None:
  with pytest.raises(sp.CalledProcessError) as exc_info:
    sp.run(
      [
        venv_with_typer_slim_path / "bin/python",
        "-c",
        "from check_reqs import require; require(['typer-slim[standard]'])",
      ],
      check=True,
      capture_output=True,
      encoding="utf-8",
    )
  assert "RequirementNotFulfilledError" in exc_info.value.stderr


def test_extra_requirement_fulfilled(
  venv_with_typer_slim_standard_path: Path,
) -> None:
  sp.run(
    [
      venv_with_typer_slim_standard_path / "bin/python",
      "-c",
      "from check_reqs import require; require(['typer-slim[standard]'])",
    ],
    check=True,
  )


@pytest.mark.xfail(
  strict=True,
  reason="same issue as https://github.com/HansBug/hbutils/issues/109",
)
def test_extra_requirement_not_fulfilled_due_to_missing_transitive(
  venv_with_typer_slim_standard_no_pygments_path: Path,
) -> None:
  """
  Regression test for https://github.com/HansBug/hbutils/issues/109.

  TODO Of course, it isn't actually fixed yet, so it's more like a
  "pre-regression test".
  """
  with pytest.raises(sp.CalledProcessError) as exc_info:
    sp.run(
      [
        venv_with_typer_slim_standard_no_pygments_path / "bin/python",
        "-c",
        "from check_reqs import require; require(['typer-slim[standard]'])",
      ],
      check=True,
      capture_output=True,
      encoding="utf-8",
    )
  assert "RequirementNotFulfilledError" in exc_info.value.stderr
