""" Multithreading/multiprocessing utilities """
from __future__ import annotations

import os

from concurrent.futures import as_completed
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Type
from typing import Union

import pydantic


MAX_NUM_CORES = len(os.sched_getaffinity(os.getpid()))


class FutureResult(pydantic.BaseModel):
    exception: Optional[Exception] = None
    kwargs: Optional[Dict[str, Any]] = None
    result: Any = None

    class Config:
        arbitrary_types_allowed: bool = True


def multi(
    func: Callable[..., Any],
    executor: Type[Union[ProcessPoolExecutor, ThreadPoolExecutor]],
    func_kwargs: List[Dict[str, Any]],
    n_workers: int = MAX_NUM_CORES,
    print_exceptions: bool = True,
    include_kwargs: bool = True,
) -> List[FutureResult]:
    if n_workers > MAX_NUM_CORES:
        raise ValueError(f"The maximum available threads are {MAX_NUM_CORES}, not: {n_workers}")
    with executor(max_workers=n_workers) as xctr:
        futures_to_kwargs = {xctr.submit(func, **kwargs): kwargs for kwargs in func_kwargs}
        results = []
        for future in as_completed(futures_to_kwargs):
            result_kwargs: Optional[Dict[str, Any]] = futures_to_kwargs[future]
            try:
                func_result = future.result()
            except Exception as exc:  # pylint: disable=broad-except
                if print_exceptions:
                    print(f"<{result_kwargs}> generated an exception: {exc}")
                if not include_kwargs:
                    result_kwargs = None
                results.append(FutureResult(exception=exc, kwargs=result_kwargs))
            else:
                if not include_kwargs:
                    result_kwargs = None
                results.append(FutureResult(result=func_result, kwargs=result_kwargs))
        return results


def multithread(
    func: Callable[..., Any],
    func_kwargs: List[Dict[str, Any]],
    n_workers: int = MAX_NUM_CORES,
    print_exceptions: bool = True,
    include_kwargs: bool = True,
) -> List[FutureResult]:
    results = multi(
        func=func,
        func_kwargs=func_kwargs,
        n_workers=n_workers,
        print_exceptions=print_exceptions,
        include_kwargs=include_kwargs,
        executor=ThreadPoolExecutor,
    )
    return results


def multiprocess(
    func: Callable[..., Any],
    func_kwargs: List[Dict[str, Any]],
    n_workers: int = MAX_NUM_CORES,
    print_exceptions: bool = True,
    include_kwargs: bool = True,
) -> List[FutureResult]:
    results = multi(
        func=func,
        func_kwargs=func_kwargs,
        n_workers=n_workers,
        print_exceptions=print_exceptions,
        include_kwargs=include_kwargs,
        executor=ProcessPoolExecutor,
    )
    return results
