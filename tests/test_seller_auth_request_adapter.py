"""Offline integration tests for guarded seller auth request composition."""
import unittest
from backend.seller_auth_request_adapter import handle_auth_request
from backend.seller_password_security import hash_seller_password
from backend.seller_session_lifecycle import digest_session_token


class Connection:
    def __init__(self):
        self.commits = 0
    def commit(self):
        self.commits += 1
    def rollback(self):
        pass


class Store:
    def __init__(self):
        self.connection = Connection()
        self.password_hash = hash_seller_password("example-secure-password-2026")
        self.record = None
    def get_active_account_hash(self, user_id):
        return self.password_hash if user_id == "user-1" else None
    def save_session(self, record):
        self.record = record
    def revoke_token(self, token):
        if self.record and self.record.token_digest == digest_session_token(token):
            self.record = None
            return 1
        return 0


class SellerAuthRequestTests(unittest.TestCase):
    def setUp(self):
        self.store = Store()
        self.params = dict(action="login", method="POST", scheme="https",
                           origin="https://seller.example.com",
                           allowed_origins=("https://seller.example.com",),
                           content_type="application/json", content_length=100,
                           attempt_allowed=True, store=self.store,
                           credentials={"user_id": "user-1",
                                        "password": "example-secure-password-2026"})

    def test_login_commits_and_sets_host_cookie(self):
        status, body, cookie = handle_auth_request(**self.params)
        self.assertEqual(status, 200)
        self.assertTrue(body["authenticated"])
        self.assertIn("__Host-seller_session=", cookie)
        self.assertEqual(self.store.connection.commits, 1)

    def test_untrusted_request_never_reads_account(self):
        status, body, cookie = handle_auth_request(
            **(self.params | {"attempt_allowed": False}))
        self.assertEqual(status, 403)
        self.assertIsNone(cookie)
        self.assertEqual(self.store.connection.commits, 0)

    def test_invalid_credentials_no_cookie(self):
        status, body, cookie = handle_auth_request(
            **(self.params | {"credentials": {"user_id": "user-1",
                                               "password": "wrong-password-2026"}}))
        self.assertEqual(status, 403)
        self.assertIsNone(cookie)

    def test_logout_clears_cookie_after_commit(self):
        login_status, _, login_cookie = handle_auth_request(**self.params)
        self.assertEqual(login_status, 200)
        token = login_cookie.split(";", 1)[0].split("=", 1)[1]
        status, body, cookie = handle_auth_request(
            **(self.params | {"action": "logout", "credentials": None,
                               "session_token": token}))
        self.assertEqual(status, 200)
        self.assertIn("Max-Age=0", cookie)
        self.assertEqual(self.store.connection.commits, 2)


if __name__ == "__main__":
    unittest.main()
