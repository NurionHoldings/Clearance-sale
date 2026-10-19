"""Offline tests for admin security alerts API response boundary."""
import unittest
from backend.admin_security_alert_api_adapter import handle_admin_security_alerts_request


class AdminSecurityAlertsApiTests(unittest.TestCase):
    def setUp(self):
        self.principal = {"authenticated": True, "active": True,
                          "role": "security_admin"}
        self.rows = [("a" * 64, "login_denied", 6)]
        self.calls = []
        def load_aggregates():
            self.calls.append("aggregates")
            return self.rows
        def load_review(digest):
            self.calls.append("review")
            return None
        self.args = dict(principal=self.principal,
                         load_aggregates=load_aggregates,
                         load_review=load_review)

    def test_get_returns_read_only_alerts(self):
        status, body = handle_admin_security_alerts_request(
            method="GET", **self.args)
        self.assertEqual(status, 200)
        self.assertTrue(body["read_only"])
        self.assertEqual(body["alerts"][0]["review_state"], "open")
        self.assertEqual(body["alerts"][0]["review_version"], 0)

    def test_non_get_is_rejected_without_loading(self):
        status, _ = handle_admin_security_alerts_request(
            method="POST", **self.args)
        self.assertEqual(status, 405)
        self.assertEqual(self.calls, [])

    def test_non_admin_is_denied_before_loading(self):
        self.args["principal"] = {"authenticated": True, "active": True,
                                  "role": "seller_owner"}
        status, body = handle_admin_security_alerts_request(
            method="GET", **self.args)
        self.assertEqual(status, 403)
        self.assertEqual(self.calls, [])
        self.assertEqual(body, {"error": "security_alerts_unavailable"})

    def test_bad_limit_rejected(self):
        status, _ = handle_admin_security_alerts_request(
            method="GET", max_alerts=0, **self.args)
        self.assertEqual(status, 400)
        self.assertEqual(self.calls, [])


if __name__ == "__main__":
    unittest.main()
