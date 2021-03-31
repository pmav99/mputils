from __future__ import annotations

import pathlib
import shutil


def copy_path(source: pathlib.Path, destination: pathlib.Path, follow_symlinks: bool = True) -> None:
    destination.parent.mkdir(exist_ok=True, parents=True)
    if source.is_dir():
        destination.mkdir(exist_ok=True)
    else:
        shutil.copy2(src=source, dst=destination, follow_symlinks=follow_symlinks)


def move_path(source: pathlib.Path, destination: pathlib.Path) -> None:
    destination.parent.mkdir(exist_ok=True, parents=True)
    # shutil.move does not accept pathlib.Path objects until python 3.9!
    shutil.move(src=source.as_posix(), dst=destination.as_posix())


def remove_dir(path: pathlib.Path) -> None:
    path.rmdir()


def remove_file(path: pathlib.Path) -> None:
    path.unlink()
