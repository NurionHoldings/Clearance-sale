"""Offline end-to-end checks for bounded dashboard diagnostics."""
import unittest

from backend.seller_access_policy import SellerMembership, SellerPrincipal
from backend.seller_dashboard_diagnostic_wiring import make_bounded_dashboard_reporter
from backend.seller_dashboard_service import SellerAccessDenied
from backend.seller_dashboard_session_service import get_session_seller_dashboard


class BoundedDashboardDiagnosticsTests(unittest.TestCase):
    def test_repeated_loader_failures_are_bounded_and_public_error_is_safe(self):
        now = [100.0]
        events = []
        reporter = make_bounded_dashboard_reporter(
            events.append, window_seconds=60, max_events=2, clock=lambda: now[0],
        )

        def broken_session(token):
            raise RuntimeError("private-db-host and session-secret")

        for _ in range(5):
            with self.assertRaises(SellerAccessDenied) as caught:
                get_session_seller_dashboard(
                    session_token="private-token", seller_id="seller-A",
                    load_session=broken_session,
                    load_membership=lambda user, seller: None,
                    query_inventory_by_seller=lambda seller: [],
                    report_error=reporter,
                )
            self.assertEqual(str(caught.exception), "Seller dashboard unavailable")
            self.assertIsNone(caught.exception.__cause__)

        self.assertEqual(len(events), 2)
        self.assertEqual({(event.code, event.stage) for event in events}, {
            ("seller_dashboard_dependency_failed", "session"),
        })
        self.assertNotIn("private", repr(events))
        now[0] += 60
        with self.assertRaises(SellerAccessDenied):
            get_session_seller_dashboard(
                session_token="private-token", seller_id="seller-A",
                load_session=broken_session,
                load_membership=lambda user, seller: None,
                query_inventory_by_seller=lambda seller: [],
                report_error=reporter,
            )
        self.assertEqual(len(events), 3)

    def test_sink_failure_does_not_change_public_error(self):
        def broken(*args):
            raise RuntimeError("sensitive internal error")

        reporter = make_bounded_dashboard_reporter(broken)
        with self.assertRaises(SellerAccessDenied) as caught:
            get_session_seller_dashboard(
                session_token="trusted-session", seller_id="seller-A",
                load_session=lambda token: SellerPrincipal("user-1", True),
                load_membership=lambda user, seller: SellerMembership(
                    "user-1", "seller-A", "owner", "active"
                ),
                query_inventory_by_seller=broken,
                report_error=reporter,
            )
        self.assertEqual(str(caught.exception), "Seller dashboard unavailable")


if __name__ == "__main__":
    unittest.main()
