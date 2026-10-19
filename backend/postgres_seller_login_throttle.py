"""Atomic shared login-attempt throttle for a trusted PostgreSQL connection.

The caller supplies an HMAC-derived bucket digest, not a raw IP, username,
or password. The connection must be transactional. This module does not
connect to production or apply migrations.
"""
import re

_BUCKET = re.compile(r"[0-9a-f]{64}\Z")


class PostgresSellerLoginThrottle:
    def __init__(self, connection):
        if getattr(connection, "autocommit", None) is not False:
            raise ValueError("Transactional connection required")
        self.connection = connection

    def consume(self, bucket_digest, *, limit=5, window_seconds=900):
        """Commit an atomic attempt; return False on limit or database failure.

        Use a dedicated transaction/connection, not the login transaction.
        An unsuccessful authentication must still consume its attempt.
        """
        if (not isinstance(bucket_digest, str) or not _BUCKET.fullmatch(bucket_digest)
                or type(limit) is not int or not 1 <= limit <= 100
                or type(window_seconds) is not int or not 60 <= window_seconds <= 86400):
            return False
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO seller_login_attempt_buckets "
                    "(bucket_digest,window_start,attempts) "
                    "VALUES (%s,now(),1) "
                    "ON CONFLICT (bucket_digest) DO UPDATE SET "
                    "attempts=CASE WHEN seller_login_attempt_buckets.window_start "
                    "<= now() - (%s * interval '1 second') THEN 1 "
                    "ELSE seller_login_attempt_buckets.attempts + 1 END, "
                    "window_start=CASE WHEN seller_login_attempt_buckets.window_start "
                    "<= now() - (%s * interval '1 second') THEN now() "
                    "ELSE seller_login_attempt_buckets.window_start END, "
                    "updated_at=now() RETURNING attempts",
                    (bucket_digest, window_seconds, window_seconds),
                )
                row = cursor.fetchone()
            self.connection.commit()
            return bool(row and type(row[0]) is int and row[0] <= limit)
        except Exception:
            try:
                self.connection.rollback()
            except Exception:
                pass
            return False
