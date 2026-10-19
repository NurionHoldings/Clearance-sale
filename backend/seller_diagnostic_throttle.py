"""Bounded in-memory diagnostic suppression for a single server process.

No tokens, identities, payloads or exception strings are retained. This
optional wrapper limits duplicate allowlisted events; it is not distributed
rate limiting and resets on process restart.
"""
from collections import deque
from threading import Lock
from time import monotonic

from .seller_diagnostics import make_seller_diagnostic_event


class BoundedSellerDiagnosticReporter:
    def __init__(self, sink, *, window_seconds=60, max_events=3, clock=monotonic):
        if not callable(sink) or not callable(clock):
            raise TypeError("Diagnostic sink and clock must be callable")
        if type(window_seconds) not in (int, float) or window_seconds <= 0:
            raise ValueError("Positive diagnostic window required")
        if type(max_events) is not int or max_events < 1:
            raise ValueError("Positive event limit required")
        self._sink = sink
        self._clock = clock
        self._window = window_seconds
        self._limit = max_events
        self._events = deque()
        self._lock = Lock()

    def __call__(self, code, stage):
        event = make_seller_diagnostic_event(code, stage)
        now = self._clock()
        with self._lock:
            while self._events and now - self._events[0] >= self._window:
                self._events.popleft()
            if len(self._events) >= self._limit:
                return False
            self._events.append(now)
        self._sink(event)
        return True
