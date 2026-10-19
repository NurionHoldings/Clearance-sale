"""Offline tests for privacy-safe suspicious login alerts."""
import unittest
from backend.seller_login_alert_projection import project_login_alerts


class LoginAlertProjectionTests(unittest.TestCase):
    def test_warning_and_critical_thresholds(self):
        rows = [
            ("a" * 64, "login_denied", 4),
            ("a" * 64, "login_throttled", 1),
            ("b" * 64, "login_denied", 15),
            ("c" * 64, "login_denied", 3),
        ]
        alerts = project_login_alerts(rows)
        self.assertEqual([(a.severity, a.attempts) for a in alerts],
                         [("critical", 15), ("warning", 5)])
        self.assertEqual(set(vars(alerts[0])),
                         {"bucket_digest", "severity", "reason", "attempts"})

    def test_invalid_and_unbounded_input_is_rejected(self):
        for rows in (
            [("invalid-ip", "login_denied", 6)],
            [("a" * 64, "login_success", 6)],
            [("a" * 64, "login_denied", True)],
            [("a" * 64, "login_denied", -1)],
            [("a" * 64, "login_denied", 1)] * 10001,
        ):
            with self.assertRaises(ValueError):
                project_login_alerts(rows)

    def test_alert_count_is_bounded(self):
        rows = [(format(i, "064x"), "login_denied", 6) for i in range(10)]
        self.assertEqual(len(project_login_alerts(rows, max_alerts=3)), 3)


if __name__ == "__main__":
    unittest.main()
