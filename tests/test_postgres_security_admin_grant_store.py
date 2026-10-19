"""Offline tests for separate administrator grant lookup."""
import unittest
import uuid
from backend.postgres_security_admin_grant_store import PostgresSecurityAdminGrantStore


class Cursor:
    def __init__(self, row, calls):
        self.row, self.calls = row, calls
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def execute(self, query, params):
        self.calls.append((query, params))
    def fetchone(self):
        return self.row


class Connection:
    autocommit = False
    def __init__(self, row):
        self.row, self.calls = row, []
    def cursor(self):
        return Cursor(self.row, self.calls)


class GrantStoreTests(unittest.TestCase):
    def setUp(self):
        self.user_id = str(uuid.uuid4())

    def test_active_grant(self):
        connection = Connection(("security_admin", True))
        store = PostgresSecurityAdminGrantStore(connection)
        self.assertEqual(store.load_admin_role(self.user_id),
                         {"role": "security_admin", "active": True})
        self.assertEqual(connection.calls[0][1], (self.user_id,))
        self.assertIn("revoked_at IS NULL", connection.calls[0][0])

    def test_inactive_or_wrong_role_denied(self):
        for row in [None, ("security_admin", False), ("seller_owner", True)]:
            self.assertIsNone(PostgresSecurityAdminGrantStore(
                Connection(row)).load_admin_role(self.user_id))

    def test_invalid_user_id_no_query(self):
        connection = Connection(("security_admin", True))
        self.assertIsNone(PostgresSecurityAdminGrantStore(
            connection).load_admin_role("not-a-uuid"))
        self.assertEqual(connection.calls, [])

    def test_autocommit_rejected(self):
        connection = Connection(None)
        connection.autocommit = True
        with self.assertRaises(ValueError):
            PostgresSecurityAdminGrantStore(connection)


if __name__ == "__main__":
    unittest.main()
