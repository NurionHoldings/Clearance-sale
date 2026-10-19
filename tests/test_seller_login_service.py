"""Offline seller login transaction tests."""
from datetime import datetime, timedelta, timezone
import unittest

from backend.seller_login_service import (
    SellerLoginDenied, authenticate_seller, logout_seller, resolve_seller_session,
)
from backend.seller_password_security import hash_seller_password
from backend.seller_session_lifecycle import digest_session_token


class Connection:
    def __init__(self):
        self.commits = 0
        self.rollbacks = 0
    def commit(self):
        self.commits += 1
    def rollback(self):
        self.rollbacks += 1


class Store:
    def __init__(self):
        self.connection = Connection()
        self.hash = hash_seller_password("long-example-password-2026")
        self.record = None
        self.fail_save = False
    def get_active_account_hash(self, user_id):
        return self.hash if user_id == "user-1" else None
    def save_session(self, record):
        if self.fail_save:
            raise RuntimeError("database failed")
        self.record = record
    def load_session_record(self, token):
        return self.record if self.record and self.record.token_digest == digest_session_token(token) else None
    def revoke_token(self, token):
        if self.record and self.record.token_digest == digest_session_token(token):
            from dataclasses import replace
            self.record = replace(self.record, revoked_at=datetime.now(timezone.utc))
            return 1
        return 0


class SellerLoginServiceTests(unittest.TestCase):
    def setUp(self):
        self.store = Store()
        self.now = datetime.now(timezone.utc)

    def test_login_commit_and_resolve(self):
        token, expires = authenticate_seller(
            user_id="user-1", password="long-example-password-2026",
            store=self.store, now=self.now)
        self.assertEqual(self.store.connection.commits, 1)
        self.assertEqual(expires, self.now + timedelta(hours=12))
        self.assertEqual(resolve_seller_session(
            token=token, store=self.store, now=self.now).user_id, "user-1")

    def test_wrong_password_denied_without_session(self):
        with self.assertRaises(SellerLoginDenied):
            authenticate_seller(user_id="user-1", password="wrong-password-2026",
                                store=self.store, now=self.now)
        self.assertIsNone(self.store.record)
        self.assertEqual(self.store.connection.commits, 0)

    def test_database_failure_rolls_back(self):
        self.store.fail_save = True
        with self.assertRaises(SellerLoginDenied):
            authenticate_seller(user_id="user-1",
                                password="long-example-password-2026",
                                store=self.store, now=self.now)
        self.assertEqual(self.store.connection.rollbacks, 1)
        self.assertEqual(self.store.connection.commits, 0)

    def test_logout_revokes_and_commits(self):
        token, _ = authenticate_seller(
            user_id="user-1", password="long-example-password-2026",
            store=self.store, now=self.now)
        logout_seller(token=token, store=self.store)
        self.assertEqual(self.store.connection.commits, 2)
        self.assertIsNone(resolve_seller_session(
            token=token, store=self.store, now=self.now))


if __name__ == "__main__":
    unittest.main()
