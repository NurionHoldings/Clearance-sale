"""Offline PostgreSQL alert review optimistic concurrency tests."""
from datetime import datetime, timezone
import unittest
from backend.postgres_security_alert_review_store import (
    PostgresSecurityAlertReviewStore, SecurityReviewConflict,
)


class Cursor:
    def __init__(self, db):
        self.db = db
        self.rowcount = 0
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def execute(self, sql, params):
        if sql.startswith("SELECT"):
            self.result = self.db.row
        elif sql.startswith("INSERT"):
            self.rowcount = 0 if self.db.row else 1
            if self.rowcount:
                self.db.row = (params[0], params[1], params[2], params[3])
        elif sql.startswith("UPDATE"):
            self.rowcount = int(bool(self.db.row and self.db.row[3] == params[4]))
            if self.rowcount:
                self.db.row = (params[3], params[0], params[1], params[2])
    def fetchone(self):
        return self.result


class Connection:
    autocommit = False
    def __init__(self):
        self.row = None
        self.commits = 0
        self.rollbacks = 0
    def cursor(self):
        return Cursor(self)
    def commit(self):
        self.commits += 1
    def rollback(self):
        self.rollbacks += 1


class SecurityReviewStoreTests(unittest.TestCase):
    def setUp(self):
        self.db = Connection()
        self.store = PostgresSecurityAlertReviewStore(self.db)
        self.admin = {"authenticated": True, "active": True,
                      "role": "security_admin"}
        self.args = dict(principal=self.admin, bucket_digest="a" * 64,
                         now=datetime(2026, 10, 19, tzinfo=timezone.utc))

    def test_create_and_transition(self):
        opened = self.store.save_transition(
            **self.args, next_state="open", expected_version=0)
        reviewing = self.store.save_transition(
            **self.args, next_state="reviewing", expected_version=1)
        self.assertEqual((opened.version, reviewing.version), (1, 2))
        self.assertEqual(self.db.commits, 2)

    def test_stale_version_rolls_back(self):
        self.store.save_transition(
            **self.args, next_state="open", expected_version=0)
        with self.assertRaises(SecurityReviewConflict):
            self.store.save_transition(
                **self.args, next_state="reviewing", expected_version=0)
        self.assertEqual(self.db.commits, 1)
        self.assertEqual(self.db.rollbacks, 1)

    def test_non_admin_does_not_commit(self):
        with self.assertRaises(PermissionError):
            self.store.save_transition(
                **(self.args | {"principal": {"role": "seller_owner"}}),
                next_state="open", expected_version=0)
        self.assertEqual(self.db.commits, 0)


if __name__ == "__main__":
    unittest.main()
