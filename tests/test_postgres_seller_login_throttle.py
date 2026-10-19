"""Offline tests for the shared PostgreSQL login throttle."""
import unittest
from backend.postgres_seller_login_throttle import PostgresSellerLoginThrottle


class Cursor:
    def __init__(self, connection):
        self.connection = connection
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def execute(self, query, params):
        self.connection.query = query
        self.connection.params = params
        if self.connection.fail:
            raise RuntimeError("database unavailable")
    def fetchone(self):
        return (self.connection.attempts,)


class Connection:
    autocommit = False
    def __init__(self, attempts=1, fail=False):
        self.attempts = attempts
        self.fail = fail
        self.commits = 0
        self.rollbacks = 0
    def cursor(self):
        return Cursor(self)
    def commit(self):
        self.commits += 1
    def rollback(self):
        self.rollbacks += 1


class SellerLoginThrottleTests(unittest.TestCase):
    def test_attempts_are_counted_and_committed(self):
        db = Connection(attempts=5)
        self.assertTrue(PostgresSellerLoginThrottle(db).consume("a" * 64))
        self.assertEqual(db.commits, 1)
        self.assertEqual(db.params, ("a" * 64, 900, 900))
        self.assertIn("ON CONFLICT", db.query)

    def test_limit_is_denied_after_committing_attempt(self):
        db = Connection(attempts=6)
        self.assertFalse(PostgresSellerLoginThrottle(db).consume("b" * 64))
        self.assertEqual(db.commits, 1)

    def test_database_failure_fails_closed(self):
        db = Connection(fail=True)
        self.assertFalse(PostgresSellerLoginThrottle(db).consume("c" * 64))
        self.assertEqual(db.rollbacks, 1)

    def test_invalid_key_never_queries_database(self):
        db = Connection()
        self.assertFalse(PostgresSellerLoginThrottle(db).consume("raw-ip-address"))
        self.assertEqual(db.commits, 0)

    def test_autocommit_is_rejected(self):
        db = Connection()
        db.autocommit = True
        with self.assertRaises(ValueError):
            PostgresSellerLoginThrottle(db)


if __name__ == "__main__":
    unittest.main()
