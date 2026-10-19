"""Offline diagnostic event contract tests."""
import unittest

from backend.seller_diagnostics import (
    EVENT_CODE, STAGES, SellerDiagnosticEvent,
    make_seller_diagnostic_event, safe_report_seller_diagnostic,
)


class SellerDiagnosticsTests(unittest.TestCase):
    def test_only_allowlisted_event_and_stages_are_accepted(self):
        for stage in STAGES:
            self.assertEqual(
                make_seller_diagnostic_event(EVENT_CODE, stage),
                SellerDiagnosticEvent(EVENT_CODE, stage),
            )
        for code, stage in (
            ("database-password", "session"),
            (EVENT_CODE, "private-token"),
            (EVENT_CODE, None),
            (EVENT_CODE, []),
            (EVENT_CODE, {}),
            ([], "session"),
        ):
            with self.assertRaises(ValueError):
                make_seller_diagnostic_event(code, stage)

    def test_safe_report_emits_only_bounded_event(self):
        events = []
        safe_report_seller_diagnostic(events.append, EVENT_CODE, "membership")
        self.assertEqual(events, [SellerDiagnosticEvent(EVENT_CODE, "membership")])
        self.assertEqual(set(vars(events[0])), {"code", "stage"})

    def test_reporter_failure_does_not_escape(self):
        def broken(event):
            raise RuntimeError("logging backend unavailable")
        safe_report_seller_diagnostic(broken, EVENT_CODE, "dashboard")
        safe_report_seller_diagnostic(None, EVENT_CODE, "dashboard")


if __name__ == "__main__":
    unittest.main()
