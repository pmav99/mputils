import multiprocessing
import threading
import time

from typing import Any


def get_threadname(**kwargs: Any) -> str:  # noqa  # pylint: disable=unused-argument
    # We add a tiny amount of sleep to make sure that all the threads are getting used.
    time.sleep(0.0001)
    return threading.current_thread().name


def get_processname(**kwargs: Any) -> str:  # noqa  # pylint: disable=unused-argument
    # We add a tiny amount of sleep to make sure that all the processes are getting used.
    time.sleep(0.01)
    return multiprocessing.current_process().name


def raise_zero_division_error(**kwargs: Any) -> None:  # noqa  # pylint: disable=unused-argument
    raise ZeroDivisionError


def get_inverse_number(number: float) -> float:
    return 1 / number
