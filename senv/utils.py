import contextlib
import os
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterator

from senv.pyproject import PyProject


@contextlib.contextmanager
def cd(path: Path):
    cwd = os.getcwd()
    os.chdir(str(path))
    try:
        yield
    finally:
        os.chdir(cwd)


@contextlib.contextmanager
def cd_tmp_dir(prefix="senv_") -> Iterator[Path]:
    with TemporaryDirectory(prefix=prefix) as tmp_dir, cd(Path(tmp_dir)):
        yield Path(tmp_dir)


@contextlib.contextmanager
def tmp_env() -> None:
    """
    Temporarily set the process environment variables.

    >>> with tmp_env():
    ...   "PLUGINS_DIR" in os.environ
    False
    >>> with tmp_env():
    ...   os.environ["PLUGINS_DIR"] = "tmp"
    ...   "PLUGINS_DIR" in os.environ
    True
    >>> "PLUGINS_DIR" in os.environ
    False

    """
    old_environ = dict(os.environ)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old_environ)


@contextlib.contextmanager
def tmp_repo() -> Iterator[PyProject]:
    """
    duplicate repository in temporary directory and point PyProject to this new path
    This is useful if we want to make temporary modifications
    for long running tasks or that can fail.
    That way no temporary change will never affect the real repository
    :return:
    """
    # this might not be very realistic for very big projects
    original_config_path = PyProject.get().config_path
    with cd_tmp_dir(prefix="senv_tmp_repo-") as tmp_dir:
        project_dir = Path(tmp_dir, "project")
        shutil.copytree(PyProject.get().config_path.parent, project_dir)
        PyProject.read_toml(Path(project_dir, "pyproject.toml"))
        yield PyProject.get()
    PyProject.read_toml(original_config_path)
