"""Offline tests for trusted administrator session security boundary."""
import unittest
from backend.admin_security_alert_session_bridge import handle_session_admin_security_alerts


class AdminAlertSessionBridgeTests(unittest.TestCase):
    def setUp(self):
        self.calls = []
        def resolve(token):
            self.calls.append("session")
            return {"authenticated": True, "active": True, "role": "security_admin"}
        def aggregates():
            self.calls.append("aggregates")
            return [("a" * 64, "login_denied", 5)]
        def review(digest):
            self.calls.append("review")
            return None
        self.args = dict(session_token="t" * 40, resolve_admin_session=resolve,
                         load_aggregates=aggregates, load_review=review)

    def test_valid_session_returns_no_store_read_model(self):
        status, body, headers = handle_session_admin_security_alerts(
            method="GET", **self.args)
        self.assertEqual(status, 200)
        self.assertEqual(body["total_returned"], 1)
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertEqual(self.calls, ["session", "aggregates", "review"])

    def test_missing_session_denied_without_loading(self):
        self.args["session_token"] = ""
        status, _, headers = handle_session_admin_security_alerts(
            method="GET", **self.args)
        self.assertEqual(status, 403)
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertEqual(self.calls, [])

    def test_non_get_never_resolves_session(self):
        status, _, _ = handle_session_admin_security_alerts(
            method="POST", **self.args)
        self.assertEqual(status, 405)
        self.assertEqual(self.calls, [])

    def test_session_resolution_error_is_denied(self):
        def broken(token):
            raise RuntimeError("internal session error")
        self.args["resolve_admin_session"] = broken
        status, body, _ = handle_session_admin_security_alerts(
            method="GET", **self.args)
        self.assertEqual(status, 403)
        self.assertEqual(body, {"error": "security_alerts_unavailable"})


if __name__ == "__main__":
    unittest.main()
