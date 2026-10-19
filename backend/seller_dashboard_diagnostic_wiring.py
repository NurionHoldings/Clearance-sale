"""Opt-in wiring of bounded diagnostics into the seller dashboard boundary.

Create one reporter per server process and reuse it across requests. No logging
backend is configured here and no production services are connected.
"""
from .seller_diagnostic_throttle import BoundedSellerDiagnosticReporter


def make_bounded_dashboard_reporter(sink, *, window_seconds=60, max_events=3,
                                    clock=None):
    """Return a callback compatible with get_session_seller_dashboard(report_error=).

    The trusted sink receives only a validated SellerDiagnosticEvent object.
    """
    options = {"window_seconds": window_seconds, "max_events": max_events}
    if clock is not None:
        options["clock"] = clock
    return BoundedSellerDiagnosticReporter(sink, **options)
