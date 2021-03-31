from __future__ import annotations

import pathlib

import typer

from .actions import copy_path
from .actions import move_path
from .actions import remove_dir
from .actions import remove_file
from .multi import MAX_NUM_CORES
from .multi import multiprocess
from .utils import partition_paths


app = typer.Typer(add_completion=False, invoke_without_command=False, no_args_is_help=True)


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
            func=move_path, func_kwargs=func_kwargs, n_workers=workers, print_exceptions=False
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
            func=copy_path, func_kwargs=func_kwargs, n_workers=workers, print_exceptions=False
        )
        exceptions = {r.exception for r in results if r.exception}
        if len(exceptions) > 1:
            typer.echo("There were exceptions while copying")
            for exc in exceptions:
                typer.echo(exc)
            raise typer.Exit(code=1)


@app.command(no_args_is_help=True)
def remove(
    # fmt: off
    source: pathlib.Path = typer.Argument(..., help="the source directory"),
    glob: str = typer.Option("**/*", help="The glob pattern to use for matching contents"),
    dry_run: bool = typer.Option(False, help="Perform all actions without doing the actual copying"),
    workers: int = typer.Option(MAX_NUM_CORES, help="The number of processes to use while copying"),
    # fmt: on
) -> None:
    """
    Remove contents of `source` directory using multiple processes (one per file).

    If you need to filter out some of the contents use the `--glob` option. E.g. `--glob **/*.nc`
    will remove all the NetCDF files under `source` and nothing else.
    """
    typer.echo(locals())
    source = source.expanduser().resolve()
    # In order to remove a directory it must be empty.
    # Therefore we need to make sure that we remove files before directories
    files, directories = partition_paths(source.glob(glob))
    if dry_run:
        for path in files + directories:
            typer.echo(f"Delete: {path}")
    else:
        # remove files
        func_kwargs = [dict(path=path) for path in files]
        results_files = multiprocess(
            func=remove_file, func_kwargs=func_kwargs, n_workers=workers, print_exceptions=False
        )
        # remove directories
        func_kwargs = [dict(path=path) for path in directories]
        results_dirs = multiprocess(
            func=remove_dir, func_kwargs=func_kwargs, n_workers=workers, print_exceptions=False
        )
        # combine results to check exceptions
        exceptions = {r.exception for r in (results_files + results_dirs) if r.exception}
        if len(exceptions) > 1:
            typer.echo("There were exceptions while deleting files")
            for exc in exceptions:
                typer.echo(exc)
            raise typer.Exit(code=1)
