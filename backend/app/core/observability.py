from __future__ import annotations

import time
import uuid
from collections import defaultdict
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Iterator

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)


def current_request_id() -> str:
    return request_id_var.get() or "no-request"


def new_request_id() -> str:
    return str(uuid.uuid4())


@dataclass
class LatencySummary:
    count: int = 0
    total_ms: float = 0.0
    max_ms: float = 0.0

    @property
    def avg_ms(self) -> float:
        if self.count == 0:
            return 0.0
        return self.total_ms / self.count


@dataclass
class MetricsRegistry:
    counters: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    latencies: dict[str, LatencySummary] = field(default_factory=dict)

    def increment(self, name: str, value: int = 1) -> None:
        self.counters[name] += value

    def observe_latency(self, name: str, elapsed_ms: float) -> None:
        summary = self.latencies.setdefault(name, LatencySummary())
        summary.count += 1
        summary.total_ms += elapsed_ms
        summary.max_ms = max(summary.max_ms, elapsed_ms)

    def snapshot(self) -> dict[str, object]:
        return {
            "counters": dict(self.counters),
            "latencies": {
                name: {
                    "count": summary.count,
                    "avg_ms": round(summary.avg_ms, 3),
                    "max_ms": round(summary.max_ms, 3),
                }
                for name, summary in self.latencies.items()
            },
        }


metrics_registry = MetricsRegistry()


@contextmanager
def observe_latency(name: str) -> Iterator[None]:
    started = time.perf_counter()
    try:
        yield
    finally:
        elapsed_ms = (time.perf_counter() - started) * 1000
        metrics_registry.observe_latency(name, elapsed_ms)
