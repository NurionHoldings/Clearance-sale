"""Offline lifecycle and authorization tests for security admin sessions."""
from datetime import datetime, timedelta, timezone
import unittest
from backend.seller_session_lifecycle import issue_session, revoke_session
from backend.security_admin_session_resolver import resolve_security_admin
from backend.admin_security_alert_session_bridge import handle_session_admin_security_alerts


class Store:
    def __init__(self, record):
        self.record = record
    def load_session_record(self, token):
        return self.record


class AdminSessionLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 19, tzinfo=timezone.utc)
        self.token, self.record = issue_session(user_id="admin-user", now=self.now)
        self.store = Store(self.record)
        self.calls = []
    def role(self, user_id):
        self.calls.append(user_id)
        return {"role": "security_admin", "active": True}
    def resolve(self):
        return resolve_security_admin(
            token=self.token, auth_store=self.store,
            load_admin_role=self.role, now=self.now)

    def test_valid_session_and_active_admin_grant(self):
        self.assertEqual(self.resolve()["role"], "security_admin")
        self.assertEqual(self.calls, ["admin-user"])

    def test_expired_session_denied_before_role_lookup(self):
        self.store.record = self.record
        self.assertIsNone(resolve_security_admin(
            token=self.token, auth_store=self.store,
            load_admin_role=self.role, now=self.now + timedelta(hours=12)))
        self.assertEqual(self.calls, [])

    def test_revoked_session_denied_before_role_lookup(self):
        self.store.record = revoke_session(self.record, now=self.now)
        self.assertIsNone(self.resolve())
        self.assertEqual(self.calls, [])

    def test_missing_admin_grant_denied(self):
        self.assertIsNone(resolve_security_admin(
            token=self.token, auth_store=self.store,
            load_admin_role=lambda user: {"role": "seller_owner", "active": True},
            now=self.now))

    def test_invalid_session_denies_dashboard_before_loading_alerts(self):
        self.store.record = revoke_session(self.record, now=self.now)
        def fail_loader(*args):
            self.fail("Unauthorized access reached alert data")
        status, _, headers = handle_session_admin_security_alerts(
            method="GET", session_token=self.token,
            resolve_admin_session=lambda token: resolve_security_admin(
                token=token, auth_store=self.store,
                load_admin_role=self.role, now=self.now),
            load_aggregates=fail_loader, load_review=fail_loader)
        self.assertEqual(status, 403)
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertEqual(self.calls, [])


if __name__ == "__main__":
    unittest.main()
