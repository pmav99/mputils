import time

from typing import Any
from typing import Callable

import pytest

import mputils

from .utils import get_inverse_number
from .utils import get_processname
from .utils import get_threadname
from .utils import raise_zero_division_error
from .utils import sleep


def test_multithread_raises_value_error_if_n_workers_higher_than_available_threads() -> None:
    with pytest.raises(ValueError) as exc:
        mputils.multi.multithread(func=lambda x: x, func_kwargs=[dict(x=1)] * 2, n_workers=1024)
    assert f"The maximum available threads are {mputils.MAX_NUM_CORES}, not: 1024" == str(exc.value)


@pytest.mark.parametrize("concurrency_func", [mputils.multithread, mputils.multiprocess])
def test_multi_functions_return_FutureResults(  # noqa  # pylint: disable=invalid-name
    concurrency_func: Callable[..., Any],
) -> None:
    func_kwargs = [dict(number=n) for n in (1, 2, 3)]
    results = concurrency_func(func=get_inverse_number, func_kwargs=func_kwargs)
    for result in results:
        assert isinstance(result, mputils.multi.FutureResult)
        assert result.exception is None


@pytest.mark.parametrize("concurrency_func", [mputils.multithread, mputils.multiprocess])
def test_multi_functions_return_FutureResults_even_when_exceptions_are_raised(  # noqa  # pylint: disable=invalid-name
    concurrency_func: Callable[..., Any],
) -> None:
    func_kwargs = [dict(number=n) for n in (1, 2, 3)]
    results = concurrency_func(func=raise_zero_division_error, func_kwargs=func_kwargs)
    for result in results:
        assert isinstance(result, mputils.multi.FutureResult)
        assert isinstance(result.exception, ZeroDivisionError)


@pytest.mark.parametrize(
    "number",
    [pytest.param(0, id="An exception is raised"), pytest.param(1, id="Function returns normally")],
)
@pytest.mark.parametrize("concurrency_func", [mputils.multithread, mputils.multiprocess])
def test_omit_kwargs_in_results(concurrency_func: Callable[..., Any], number: float) -> None:
    func_kwargs = [dict(number=number)]
    results = concurrency_func(func=get_inverse_number, func_kwargs=func_kwargs, include_kwargs=False)
    for result in results:
        assert result.kwargs is None


@pytest.mark.parametrize("n_workers", [1, 2])
def test_multithread_pool_size(n_workers: int) -> None:
    # Test that the number of the used threads is equal to the specified number of workers
    func_kwargs = [{"arg": i} for i in range(4 * n_workers)]
    results = mputils.multi.multithread(func=get_threadname, func_kwargs=func_kwargs, n_workers=n_workers)
    thread_names = {result.result for result in results}
    assert len(thread_names) == n_workers


@pytest.mark.parametrize("n_workers", [1, 2])
def test_multiprocess_pool_size(n_workers: int) -> None:
    # Test that the number of the used threads is equal to the specified number of workers
    func_kwargs = [{"arg": i} for i in range(4 * n_workers)]
    results = mputils.multi.multiprocess(func=get_processname, func_kwargs=func_kwargs, n_workers=n_workers)
    thread_names = {result.result for result in results}
    assert len(thread_names) == n_workers


@pytest.mark.parametrize(
    "concurrency_func",
    [mputils.multithread, mputils.multiprocess],
)
def test_parallel_calls_are_faster_than_serial_calls(concurrency_func: Callable[..., Any]) -> None:
    wait_time = 0.1
    func_kwargs = [dict(seconds=wait_time)] * 2
    start = time.time()
    concurrency_func(func=sleep, func_kwargs=func_kwargs, n_workers=2)
    duration = time.time() - start
    assert duration > wait_time
    assert duration < 2 * wait_time
