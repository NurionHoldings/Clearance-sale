"""Offline tests for seller password hashing and verification."""
import unittest
from backend.seller_password_security import hash_seller_password, verify_seller_password


class SellerPasswordSecurityTests(unittest.TestCase):
    def test_password_round_trip(self):
        password = "A-strong-example-passphrase-2026"
        encoded = hash_seller_password(password)
        self.assertTrue(verify_seller_password(password, encoded))
        self.assertFalse(verify_seller_password("incorrect-password", encoded))
        self.assertNotIn(password, encoded)

    def test_salts_are_unique(self):
        password = "A-strong-example-passphrase-2026"
        self.assertNotEqual(hash_seller_password(password),
                            hash_seller_password(password))

    def test_malformed_hash_fails_closed(self):
        for value in (None, "", "plaintext", "scrypt$999999999$8$1$aa$bb"):
            with self.subTest(value=value):
                self.assertFalse(verify_seller_password(
                    "A-strong-example-passphrase-2026", value))

    def test_short_password_rejected(self):
        with self.assertRaises(ValueError):
            hash_seller_password("short")
        self.assertFalse(verify_seller_password("short", "anything"))


if __name__ == "__main__":
    unittest.main()
