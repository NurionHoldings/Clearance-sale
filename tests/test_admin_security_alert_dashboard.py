"""Offline tests for administrator alert and review dashboard composition."""
from datetime import datetime, timezone
import unittest
from backend.admin_security_alert_dashboard import get_admin_security_alert_dashboard
from backend.admin_security_alert_service import SecurityAlertsUnavailable
from backend.admin_security_alert_review import SecurityAlertReview


class AdminSecurityAlertDashboardTests(unittest.TestCase):
    def setUp(self):
        self.admin = {"authenticated": True, "active": True,
                      "role": "security_admin"}
        self.rows = [("a" * 64, "login_denied", 6),
                     ("b" * 64, "login_throttled", 16)]

    def test_join_reviews_and_default_open(self):
        def load_review(digest):
            if digest == "b" * 64:
                return SecurityAlertReview(
                    digest, "reviewing",
                    datetime(2026, 10, 19, tzinfo=timezone.utc), 2)
            return None
        result = get_admin_security_alert_dashboard(
            principal=self.admin, load_aggregates=lambda: self.rows,
            load_review=load_review)
        self.assertTrue(result["read_only"])
        self.assertEqual(
            [(a["review_state"], a["review_version"]) for a in result["alerts"]],
            [("reviewing", 2), ("open", 0)])

    def test_unauthorized_user_cannot_query_any_loader(self):
        calls = []
        def aggregate():
            calls.append("aggregate")
            return self.rows
        def review(digest):
            calls.append("review")
            return None
        with self.assertRaises(SecurityAlertsUnavailable):
            get_admin_security_alert_dashboard(
                principal={"authenticated": True, "active": True,
                           "role": "seller_owner"},
                load_aggregates=aggregate, load_review=review)
        self.assertEqual(calls, [])

    def test_review_loader_failure_is_masked(self):
        def broken(digest):
            raise RuntimeError("database detail")
        with self.assertRaisesRegex(
                SecurityAlertsUnavailable, "^Security alerts unavailable$"):
            get_admin_security_alert_dashboard(
                principal=self.admin, load_aggregates=lambda: self.rows,
                load_review=broken)


if __name__ == "__main__":
    unittest.main()
