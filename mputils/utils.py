from __future__ import annotations

import itertools
import pathlib

from typing import Any
from typing import Iterable
from typing import List
from typing import Tuple


def partition(pred: Any, iterable: Iterable[Any]) -> Any:
    "Use a predicate to partition entries into false entries and true entries"
    # partition(is_odd, range(10)) --> 0 2 4 6 8   and  1 3 5 7 9
    iter1, iter2 = itertools.tee(iterable)
    return itertools.filterfalse(pred, iter1), filter(pred, iter2)


def partition_paths(paths: Iterable[pathlib.Path]) -> Tuple[List[pathlib.Path], List[pathlib.Path]]:
    files, directories = list(map(sorted, partition(pathlib.Path.is_dir, paths)))
    # When we have nested directories we want children to get removed before their parents
    # That's why we reverse the order of directories
    return files, directories[::-1]  # type: ignore
