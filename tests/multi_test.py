from typing import Any
from typing import Callable

import pytest

import mputils

from .utils import get_inverse_number
from .utils import get_processname
from .utils import get_threadname
from .utils import raise_zero_division_error


CONCURRENCY_FUNCS = pytest.mark.parametrize("concurrency_func", [mputils.multithread, mputils.multiprocess],)

# Some help functions to test multithreading


# The actual tests


def test_multithread_raises_value_error_if_n_workers_higher_than_available_threads() -> None:
    with pytest.raises(ValueError) as exc:
        mputils.multi.multithread(func=lambda x: x, func_kwargs=[dict(x=1)] * 2, n_workers=1024)
    assert f"The maximum available threads are {mputils.MAX_NUM_CORES}, not: 1024" == str(exc.value)


@CONCURRENCY_FUNCS
def test_multi_functions_return_FutureResults(  # noqa  # pylint: disable=invalid-name
    concurrency_func: Callable[..., Any],
) -> None:
    func_kwargs = [dict(number=n) for n in (1, 2, 3)]
    results = concurrency_func(func=get_inverse_number, func_kwargs=func_kwargs)
    for result in results:
        assert isinstance(result, mputils.multi.FutureResult)
        assert result.exception is None


@CONCURRENCY_FUNCS
def test_multi_functions_return_FutureResults_even_when_exceptions_are_raised(  # noqa  # pylint: disable=invalid-name
    concurrency_func: Callable[..., Any],
) -> None:
    func_kwargs = [dict(number=n) for n in (1, 2, 3)]
    results = concurrency_func(func=raise_zero_division_error, func_kwargs=func_kwargs)
    for result in results:
        assert isinstance(result, mputils.multi.FutureResult)
        assert isinstance(result.exception, Exception)


@pytest.mark.parametrize("n_workers", [1, 2, 4])
def test_multithread_pool_size(n_workers: int) -> None:
    # Test that the number of the used threads is equal to the specified number of workers
    func_kwargs = [{"arg": i} for i in range(4 * n_workers)]
    results = mputils.multi.multithread(func=get_threadname, func_kwargs=func_kwargs, n_workers=n_workers)
    thread_names = {result.result for result in results}
    assert len(thread_names) == n_workers


@pytest.mark.parametrize("n_workers", [1, 2, 4])
def test_multiprocess_pool_size(n_workers: int) -> None:
    # Test that the number of the used threads is equal to the specified number of workers
    func_kwargs = [{"arg": i} for i in range(4 * n_workers)]
    results = mputils.multi.multiprocess(func=get_processname, func_kwargs=func_kwargs, n_workers=n_workers)
    thread_names = {result.result for result in results}
    assert len(thread_names) == n_workers
