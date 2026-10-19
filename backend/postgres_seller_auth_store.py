"""PostgreSQL seller authentication store, using an injected DB-API connection.

No connection creation, credentials, migration execution, or HTTP exposure.
The host owns transaction commit/rollback, pooling, and privilege separation.
"""
from .seller_access_policy import SellerMembership
from .seller_session_lifecycle import SessionRecord, digest_session_token


class PostgresSellerAuthStore:
    def __init__(self, connection):
        if getattr(connection, "autocommit", None) is not False:
            raise ValueError("Authentication store requires autocommit=False")
        self.connection = connection

    def get_active_account_hash(self, user_id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT password_hash FROM seller_accounts "
                "WHERE user_id=%s AND status='active'", (user_id,)
            )
            row = cursor.fetchone()
        return row[0] if row else None

    def save_session(self, record):
        """Stage an authenticated session; caller must commit atomically."""
        if not isinstance(record, SessionRecord) or record.revoked_at is not None:
            raise ValueError("New, unrevoked session record required")
        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO seller_sessions "
                "(session_id,user_id,token_digest,created_at,expires_at,revoked_at) "
                "VALUES (%s,%s,%s,%s,%s,%s)",
                (record.session_id, record.user_id, record.token_digest,
                 record.created_at, record.expires_at, None),
            )

    def load_session_record(self, token):
        """Look up by digest only; never send the raw token to SQL."""
        try:
            digest = digest_session_token(token)
        except (TypeError, ValueError):
            return None
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT s.session_id,s.user_id,s.token_digest,s.created_at,"
                "s.expires_at,s.revoked_at FROM seller_sessions s "
                "JOIN seller_accounts a ON a.user_id=s.user_id "
                "WHERE s.token_digest=%s AND a.status='active' "
                "AND s.revoked_at IS NULL AND s.expires_at > now()",
                (digest,),
            )
            row = cursor.fetchone()
        return SessionRecord(*map(str, row[:2]), str(row[2]), *row[3:]) if row else None

    def revoke_token(self, token):
        """Stage revocation; caller must commit before acknowledging logout."""
        try:
            digest = digest_session_token(token)
        except (TypeError, ValueError):
            return 0
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE seller_sessions SET revoked_at=now() "
                "WHERE token_digest=%s AND revoked_at IS NULL",
                (digest,),
            )
            return cursor.rowcount

    def load_membership(self, user_id, seller_id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT m.user_id,m.seller_id,m.role,m.status "
                "FROM seller_memberships m "
                "JOIN seller_organizations o ON o.seller_id=m.seller_id "
                "JOIN seller_accounts a ON a.user_id=m.user_id "
                "WHERE m.user_id=%s AND m.seller_id=%s "
                "AND m.status='active' AND o.status='active' "
                "AND a.status='active'",
                (user_id, seller_id),
            )
            row = cursor.fetchone()
        return SellerMembership(str(row[0]), str(row[1]), row[2], row[3]) if row else None
