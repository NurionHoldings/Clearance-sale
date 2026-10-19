"""Offline contract tests for PostgreSQL seller authentication adapter."""
from datetime import datetime, timedelta, timezone
import unittest
from backend.postgres_seller_auth_store import PostgresSellerAuthStore
from backend.seller_session_lifecycle import issue_session


class Cursor:
    def __init__(self, db):
        self.db = db
        self.rowcount = 1
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def execute(self, sql, params):
        self.db.queries.append((sql, params))
    def fetchone(self):
        return self.db.row


class Connection:
    autocommit = False
    def __init__(self):
        self.queries = []
        self.row = None
    def cursor(self):
        return Cursor(self)


class PostgresSellerAuthStoreTests(unittest.TestCase):
    def setUp(self):
        self.db = Connection()
        self.store = PostgresSellerAuthStore(self.db)
        self.now = datetime(2026, 10, 19, tzinfo=timezone.utc)
        self.token, self.record = issue_session(user_id="user-1", now=self.now)

    def test_autocommit_connection_rejected(self):
        self.db.autocommit = True
        with self.assertRaises(ValueError):
            PostgresSellerAuthStore(self.db)

    def test_session_write_stages_without_committing(self):
        self.store.save_session(self.record)
        sql, params = self.db.queries[-1]
        self.assertIn("INSERT INTO seller_sessions", sql)
        self.assertEqual(params[2], self.record.token_digest)
        self.assertNotIn(self.token, params)

    def test_session_lookup_uses_digest_not_token(self):
        self.db.row = (self.record.session_id, self.record.user_id,
                       self.record.token_digest, self.record.created_at,
                       self.record.expires_at, None)
        found = self.store.load_session_record(self.token)
        self.assertEqual(found.user_id, "user-1")
        sql, params = self.db.queries[-1]
        self.assertEqual(params, (self.record.token_digest,))
        self.assertIn("a.status='active'", sql)
        self.assertIn("s.expires_at > now()", sql)

    def test_revoke_uses_digest(self):
        self.assertEqual(self.store.revoke_token(self.token), 1)
        sql, params = self.db.queries[-1]
        self.assertIn("revoked_at=now()", sql)
        self.assertEqual(params, (self.record.token_digest,))

    def test_membership_requires_active_account_and_organization(self):
        self.db.row = ("user-1", "seller-A", "viewer", "active")
        member = self.store.load_membership("user-1", "seller-A")
        self.assertEqual(member.role, "viewer")
        sql, params = self.db.queries[-1]
        self.assertIn("o.status='active'", sql)
        self.assertIn("a.status='active'", sql)
        self.assertEqual(params, ("user-1", "seller-A"))

    def test_invalid_token_does_not_query_database(self):
        self.assertIsNone(self.store.load_session_record(None))
        self.assertEqual(self.store.revoke_token(None), 0)
        self.assertEqual(self.db.queries, [])


if __name__ == "__main__":
    unittest.main()
