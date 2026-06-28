from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.exceptions import RetryableIngestionError

P = ParamSpec("P")
R = TypeVar("R")

DEFAULT_RETRY = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(RetryableIngestionError),
    reraise=True,
)


def with_ingestion_retry(func: Callable[P, R]) -> Callable[P, R]:
    """Retry wrapper for stages that may fail transiently."""

    @wraps(func)
    @DEFAULT_RETRY
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return func(*args, **kwargs)

    return wrapper
