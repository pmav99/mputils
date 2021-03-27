from __future__ import annotations

from typing import List

from .multi import FutureResult
from .multi import MAX_NUM_CORES
from .multi import multiprocess
from .multi import multithread


__all__: List[str] = [
    "MAX_NUM_CORES",
    "FutureResult",
    "multiprocess",
    "multithread",
]
