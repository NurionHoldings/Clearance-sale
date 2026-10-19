"""Offline tests for independent security alert review state."""
from datetime import datetime, timezone
import unittest
from backend.admin_security_alert_review import transition_security_alert_review


class SecurityAlertReviewTests(unittest.TestCase):
    def setUp(self):
        self.admin = {"authenticated": True, "active": True,
                      "role": "security_admin"}
        self.key = "a" * 64
        self.now = datetime(2026, 10, 19, tzinfo=timezone.utc)

    def transition(self, current, state, principal=None):
        return transition_security_alert_review(
            principal=self.admin if principal is None else principal,
            current=current, bucket_digest=self.key,
            next_state=state, now=self.now)

    def test_review_lifecycle_increments_version(self):
        opened = self.transition(None, "open")
        reviewing = self.transition(opened, "reviewing")
        resolved = self.transition(reviewing, "resolved")
        self.assertEqual([opened.version, reviewing.version, resolved.version],
                         [1, 2, 3])
        self.assertEqual(resolved.state, "resolved")
        self.assertEqual(opened.state, "open")

    def test_invalid_transition_is_rejected(self):
        opened = self.transition(None, "open")
        with self.assertRaises(ValueError):
            self.transition(opened, "resolved")
        with self.assertRaises(ValueError):
            self.transition(opened, "open")

    def test_non_admin_cannot_update(self):
        with self.assertRaises(PermissionError):
            self.transition(None, "open", principal={
                "authenticated": True, "active": True, "role": "seller_owner"})

    def test_new_review_cannot_start_resolved(self):
        with self.assertRaises(ValueError):
            self.transition(None, "resolved")


if __name__ == "__main__":
    unittest.main()
