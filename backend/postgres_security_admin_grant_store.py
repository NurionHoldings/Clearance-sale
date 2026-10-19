"""Read-only PostgreSQL security administrator grant lookup.

Requires a trusted transactional connection and a verified user ID.
Does not grant privileges, create connections or commit transactions.
"""
import uuid


class PostgresSecurityAdminGrantStore:
    def __init__(self, connection):
        if getattr(connection, "autocommit", None) is not False:
            raise ValueError("Transactional connection required")
        self.connection = connection

    def load_admin_role(self, user_id):
        try:
            verified = str(uuid.UUID(user_id))
        except (TypeError, ValueError, AttributeError):
            return None
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "SELECT role, active FROM security_admin_grants "
                    "WHERE user_id=%s AND active=TRUE AND revoked_at IS NULL",
                    (verified,),
                )
                row = cursor.fetchone()
            if row == ("security_admin", True):
                return {"role": "security_admin", "active": True}
        except Exception:
            return None
        return None
