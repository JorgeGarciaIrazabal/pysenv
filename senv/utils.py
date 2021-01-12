import contextlib
import os
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from senv.config import Config


@contextlib.contextmanager
def cd(path: Path):
    cwd = os.getcwd()
    os.chdir(str(path))
    try:
        yield
    finally:
        os.chdir(cwd)


@contextlib.contextmanager
def tmp_env()->None:
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
def tmp_repo() -> Path:
    with TemporaryDirectory(prefix="senv_tmp_repo") as tmp_dir, cd(Path(tmp_dir)):
        shutil.copytree(Config.get().config_path.parent, tmp_dir, dirs_exist_ok=True)
        yield Path(tmp_dir)
