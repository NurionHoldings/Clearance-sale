"""Offline checks for the seller identity SQL draft."""
from pathlib import Path
import unittest

SQL_PATH = Path(__file__).resolve().parents[1] / "db/migrations/002_seller_identity_contract_draft.sql"


class SellerIdentitySQLDraftTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sql = SQL_PATH.read_text(encoding="utf-8").lower()

    def test_schema_has_identity_and_membership_boundaries(self):
        for table in ("seller_accounts", "seller_organizations",
                      "seller_memberships", "seller_sessions"):
            self.assertIn("create table if not exists " + table, self.sql)
        self.assertIn("primary key (user_id, seller_id)", self.sql)
        self.assertIn("references seller_accounts(user_id)", self.sql)
        self.assertIn("references seller_organizations(seller_id)", self.sql)

    def test_sessions_store_digest_and_expiry_not_raw_token(self):
        self.assertIn("token_digest char(64) not null unique", self.sql)
        self.assertIn("expires_at timestamptz not null", self.sql)
        self.assertIn("revoked_at timestamptz", self.sql)
        self.assertNotIn("session_token text", self.sql)

    def test_membership_status_and_role_are_restricted(self):
        self.assertIn("'viewer', 'manager', 'owner'", self.sql)
        self.assertIn("'pending', 'active', 'revoked'", self.sql)

    def test_migration_is_explicitly_draft(self):
        self.assertIn("draft only", self.sql)
        self.assertIn("begin;", self.sql)
        self.assertIn("commit;", self.sql)


if __name__ == "__main__":
    unittest.main()
