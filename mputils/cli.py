from __future__ import annotations

import pathlib
import shutil

import typer

from .multi import MAX_NUM_CORES
from .multi import multiprocess


app = typer.Typer(add_completion=False, invoke_without_command=False, no_args_is_help=True)


def copy_(source: pathlib.Path, destination: pathlib.Path, follow_symlinks: bool = True) -> None:
    destination.parent.mkdir(exist_ok=True, parents=True)
    if source.is_dir():
        destination.mkdir(exist_ok=True)
    else:
        shutil.copy2(src=source, dst=destination, follow_symlinks=follow_symlinks)


def move_(source: pathlib.Path, destination: pathlib.Path) -> None:
    destination.parent.mkdir(exist_ok=True, parents=True)
    # shutil.move does not accept pathlib.Path objects until python 3.9!
    shutil.move(src=source.as_posix(), dst=destination.as_posix())


@app.command(no_args_is_help=True)
def move(
    # fmt: off
    source: pathlib.Path = typer.Argument(..., help="the source directory"),
    destination: pathlib.Path = typer.Argument(..., help="the destination directory"),
    glob: str = typer.Option("**/*", help="The glob pattern to use for matching contents"),
    dry_run: bool = typer.Option(False, help="Perform all actions without doing the actual moving"),
    workers: int = typer.Option(MAX_NUM_CORES, help="The number of processes to use while moving"),
    # fmt: on
) -> None:
    """
    Move contents of `source` directory to `destination` using multiple processes (one per file).

    If you need to filter out some of the contents use the `--glob` option. E.g. `--glob **/*.nc`
    will copy all the NetCDF files under `source` and nothing else.
    """
    typer.echo(locals())
    source = source.expanduser().resolve()
    destination = destination.expanduser().resolve()
    pairs = {src_path: destination / src_path.relative_to(source) for src_path in source.glob(glob)}
    if dry_run:
        for source_path, destination_path in pairs.items():
            typer.echo(f"{source_path} -> {destination_path}")
    else:
        func_kwargs = [dict(source=src, destination=dst) for src, dst in pairs.items()]
        results = multiprocess(
            func=move_, func_kwargs=func_kwargs, n_workers=workers, print_exceptions=False
        )
        exceptions = {r.exception for r in results if r.exception}
        if len(exceptions) > 1:
            typer.echo("There were exceptions while moving files")
            for exc in exceptions:
                typer.echo(exc)
            raise typer.Exit(code=1)


@app.command(no_args_is_help=True)
def copy(
    # fmt: off
    source: pathlib.Path = typer.Argument(..., help="the source directory"),
    destination: pathlib.Path = typer.Argument(..., help="the destination directory"),
    glob: str = typer.Option("**/*", help="The glob pattern to use for matching contents"),
    dry_run: bool = typer.Option(False, help="Perform all actions without doing the actual copying"),
    workers: int = typer.Option(MAX_NUM_CORES, help="The number of processes to use while copying"),
    # fmt: on
) -> None:
    """
    Copy contents of `source` directory to `destination` using multiple processes (one per file).

    If you need to filter out some of the contents use the `--glob` option. E.g. `--glob **/*.nc`
    will copy all the NetCDF files under `source` and nothing else.
    """
    typer.echo(locals())
    source = source.expanduser().resolve()
    destination = destination.expanduser().resolve()
    pairs = {src_path: destination / src_path.relative_to(source) for src_path in source.glob(glob)}
    if dry_run:
        for source_path, destination_path in pairs.items():
            typer.echo(f"{source_path} -> {destination_path}")
    else:
        func_kwargs = [dict(source=src, destination=dst) for src, dst in pairs.items()]
        results = multiprocess(
            func=copy_, func_kwargs=func_kwargs, n_workers=workers, print_exceptions=False
        )
        exceptions = {r.exception for r in results if r.exception}
        if len(exceptions) > 1:
            typer.echo("There were exceptions while copying")
            for exc in exceptions:
                typer.echo(exc)
            raise typer.Exit(code=1)
