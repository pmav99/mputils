# mputils

Move and copy files efficiently using multiprocessing

## Installation

```
pipx install 'git+https://github.com/pmav99/mputils'
```

## Usage

```
mputils copy --help
mputils move --help
```

Examples

```
mputils copy --workers 10 --glob '**/*.nc' /scratch/calculations/2005 /data/2005
```

## Rationale

When you have a lot of data (as in TBs) you are probably using mechanical disks for storage. This
means that operations like copying files around can be quite slow. To make matters even worse, `mv`
and `cp` are single-threaded and they are working serially, i.e. they process files one after the
other.  So even if you have a beefy 64C/128T server, you can only use a single Thread to copy your
files.

This is where `mputils` comes in.

`mputils` creates a [Pool of
processes](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ProcessPoolExecutor)
and lets it consume the list of the files that are to be moved.

### What about `mv`?

When working on a local filesystem (e.g. `ext4`) the `mv` operation does not copy any data; it just
changes the metadata of the file and, consequently, it is way faster than `mputils move`.
Nevertheless, when copying data *across* filesystems (or when working with network-based filesystems
that don't support full-POSIX compliance) the data do get copied and in those cases `mputils move`
should be significantly faster than `mv`.
