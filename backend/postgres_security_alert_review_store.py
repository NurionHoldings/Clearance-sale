"""Transactional PostgreSQL adapter for administrator alert review updates.

No connections, schema changes or HTTP endpoints are created here.
The caller must supply a dedicated transactional connection.
"""
from .admin_security_alert_review import (
    SecurityAlertReview, transition_security_alert_review,
)


class SecurityReviewConflict(RuntimeError):
    pass


class PostgresSecurityAlertReviewStore:
    def __init__(self, connection):
        if getattr(connection, "autocommit", None) is not False:
            raise ValueError("Transactional connection required")
        self.connection = connection

    def load(self, bucket_digest):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT bucket_digest,state,updated_at,version "
                "FROM seller_security_alert_reviews WHERE bucket_digest=%s",
                (bucket_digest,),
            )
            row = cursor.fetchone()
        return SecurityAlertReview(*row) if row else None

    def save_transition(self, *, principal, bucket_digest, next_state,
                        expected_version, now=None):
        """Compare-and-swap; commit only a matching version."""
        if type(expected_version) is not int or expected_version < 0:
            raise ValueError("Invalid expected version")
        try:
            current = self.load(bucket_digest)
            actual_version = current.version if current else 0
            if actual_version != expected_version:
                raise SecurityReviewConflict("Security review changed")
            updated = transition_security_alert_review(
                principal=principal, current=current, bucket_digest=bucket_digest,
                next_state=next_state, now=now,
            )
            with self.connection.cursor() as cursor:
                if current is None:
                    cursor.execute(
                        "INSERT INTO seller_security_alert_reviews "
                        "(bucket_digest,state,updated_at,version) "
                        "VALUES (%s,%s,%s,%s) ON CONFLICT DO NOTHING",
                        (updated.bucket_digest, updated.state,
                         updated.updated_at, updated.version),
                    )
                else:
                    cursor.execute(
                        "UPDATE seller_security_alert_reviews "
                        "SET state=%s,updated_at=%s,version=%s "
                        "WHERE bucket_digest=%s AND version=%s",
                        (updated.state, updated.updated_at, updated.version,
                         updated.bucket_digest, expected_version),
                    )
                if cursor.rowcount != 1:
                    raise SecurityReviewConflict("Security review changed")
            self.connection.commit()
            return updated
        except Exception:
            try:
                self.connection.rollback()
            except Exception:
                pass
            raise
