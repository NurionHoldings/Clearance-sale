"""Deterministic tests for bounded seller diagnostic reporting."""
import unittest

from backend.seller_diagnostic_throttle import BoundedSellerDiagnosticReporter
from backend.seller_diagnostics import EVENT_CODE


class SellerDiagnosticThrottleTests(unittest.TestCase):
    def setUp(self):
        self.time = 100.0
        self.events = []
        self.report = BoundedSellerDiagnosticReporter(
            self.events.append, window_seconds=60, max_events=3,
            clock=lambda: self.time,
        )

    def test_repeated_events_are_bounded(self):
        self.assertEqual(
            [self.report(EVENT_CODE, "dashboard") for _ in range(5)],
            [True, True, True, False, False],
        )
        self.assertEqual(len(self.events), 3)
        self.assertEqual({event.stage for event in self.events}, {"dashboard"})

    def test_limit_resets_after_window(self):
        for _ in range(3):
            self.report(EVENT_CODE, "session")
        self.time += 60
        self.assertTrue(self.report(EVENT_CODE, "membership"))
        self.assertEqual(len(self.events), 4)

    def test_unapproved_event_never_reaches_sink(self):
        with self.assertRaises(ValueError):
            self.report("secret-connection-string", "dashboard")
        self.assertEqual(self.events, [])

    def test_invalid_configuration_rejected(self):
        with self.assertRaises(ValueError):
            BoundedSellerDiagnosticReporter(self.events.append, max_events=0)
        with self.assertRaises(ValueError):
            BoundedSellerDiagnosticReporter(self.events.append, window_seconds=0)


if __name__ == "__main__":
    unittest.main()
