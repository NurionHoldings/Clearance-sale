"""Offline tests for seller session lifecycle primitives."""
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import unittest

from backend.seller_session_lifecycle import (
    digest_session_token, issue_session, revoke_session, verify_session,
)


class SellerSessionLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 19, tzinfo=timezone.utc)
        self.token, self.record = issue_session(user_id="user-1", now=self.now)

    def test_issue_and_verify(self):
        self.assertNotEqual(self.token, self.record.token_digest)
        self.assertEqual(digest_session_token(self.token), self.record.token_digest)
        self.assertEqual(verify_session(token=self.token, record=self.record,
                                        now=self.now).user_id, "user-1")

    def test_invalid_token_denied(self):
        self.assertIsNone(verify_session(token="wrong", record=self.record,
                                         now=self.now))
        self.assertIsNone(verify_session(token=None, record=self.record,
                                         now=self.now))

    def test_expired_session_denied(self):
        self.assertIsNone(verify_session(
            token=self.token, record=self.record,
            now=self.now + timedelta(hours=12)))

    def test_revoked_session_denied(self):
        revoked = revoke_session(self.record, now=self.now + timedelta(minutes=1))
        self.assertIsNone(verify_session(
            token=self.token, record=revoked, now=self.now + timedelta(minutes=2)))

    def test_future_and_overlong_session_denied(self):
        self.assertIsNone(verify_session(
            token=self.token, record=self.record,
            now=self.now - timedelta(seconds=1)))
        overlong = replace(self.record, expires_at=self.now + timedelta(days=7))
        self.assertIsNone(verify_session(
            token=self.token, record=overlong, now=self.now))

    def test_naive_timestamp_rejected(self):
        with self.assertRaises(ValueError):
            issue_session(user_id="user-1", now=datetime(2026, 10, 19))


if __name__ == "__main__":
    unittest.main()
