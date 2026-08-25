from __future__ import annotations
import time
from collections import Counter, defaultdict
from contextlib import contextmanager


class Metrics:
    def __init__(self):
        self.counters = Counter()
        self.timings = defaultdict(list)
        self.gauges = {}

    def inc(self, name, amount=1):
        self.counters[name] += amount

    def set_gauge(self, name, value):
        self.gauges[name] = value

    def observe(self, name, seconds):
        self.timings[name].append(float(seconds))

    @contextmanager
    def timer(self, name):
        start = time.perf_counter()
        try:
            yield
        finally:
            self.observe(name, time.perf_counter() - start)

    def snapshot(self):
        timing_summary = {}
        for name, values in self.timings.items():
            timing_summary[name] = {
                "count": len(values),
                "total": sum(values),
                "avg": (sum(values) / len(values)) if values else 0.0,
                "max": max(values) if values else 0.0,
            }
        return {
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "timings": timing_summary,
        }
