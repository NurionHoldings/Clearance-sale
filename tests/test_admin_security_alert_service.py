"""Offline authorization and privacy tests for admin security alerts."""
import unittest
from backend.admin_security_alert_service import (
    SecurityAlertsUnavailable, get_admin_security_alerts,
)


class AdminSecurityAlertsTests(unittest.TestCase):
    def setUp(self):
        self.admin = {"authenticated": True, "active": True,
                      "role": "security_admin"}
        self.rows = [("a" * 64, "login_denied", 5),
                     ("b" * 64, "login_throttled", 15)]

    def test_active_security_admin_reads_bounded_alerts(self):
        result = get_admin_security_alerts(
            principal=self.admin, load_aggregates=lambda: self.rows,
            max_alerts=1)
        self.assertTrue(result["read_only"])
        self.assertEqual(result["total_returned"], 1)
        self.assertEqual(result["alerts"][0]["severity"], "critical")
        self.assertEqual(set(result["alerts"][0]),
                         {"severity", "reason", "attempts", "bucket_digest"})

    def test_non_admin_denied_before_loading(self):
        for principal in (None, {}, {"role": "security_admin"},
                          {"authenticated": True, "active": True,
                           "role": "seller_owner"},
                          {"authenticated": True, "active": False,
                           "role": "security_admin"}):
            calls = []
            def loader():
                calls.append(True)
                return self.rows
            with self.assertRaises(SecurityAlertsUnavailable):
                get_admin_security_alerts(
                    principal=principal, load_aggregates=loader)
            self.assertEqual(calls, [])

    def test_loader_error_is_masked(self):
        def broken():
            raise RuntimeError("private database details")
        with self.assertRaisesRegex(SecurityAlertsUnavailable,
                                    "^Security alerts unavailable$"):
            get_admin_security_alerts(
                principal=self.admin, load_aggregates=broken)


if __name__ == "__main__":
    unittest.main()
