"""Shared SQL repository transaction boundary."""

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from sqlalchemy.orm import Session

from app.infrastructure.sql.factory import AuditAwareSession


class Transaction:
    """Handle yielded by :meth:`SQLRepository.transaction`.

    Exists so a service can declare, at the point where it decides there is
    nothing to audit, that the upcoming commit legitimately carries no audit
    event — without that declaration the AuditAwareSession guard rejects it.
    """

    def __init__(self) -> None:
        self.audit_skipped = False

    def skip_audit(self) -> None:
        """Mark this transaction as intentionally recording no audit event."""
        self.audit_skipped = True


class SQLRepository:
    """Own SQLAlchemy access so services never depend on Session."""

    def __init__(self, session: Session):
        self.session = session

    @contextmanager
    def transaction(self, *, skip_audit: bool = False) -> Generator[Transaction]:
        """Commit the enclosed unit of work, rolling back on any exception.

        Replaces the try/except/rollback/raise block that every write path
        would otherwise repeat verbatim.
        """
        tx = Transaction()
        if skip_audit:
            tx.skip_audit()
        try:
            yield tx
        except Exception:
            self.rollback()
            raise
        self.commit(skip_audit=tx.audit_skipped)

    def flush(self) -> None:
        self.session.flush()

    def commit(self, *, skip_audit: bool = False) -> None:
        if isinstance(self.session, AuditAwareSession):
            self.session.commit(skip_audit=skip_audit)
            return
        # Unit and integration tests may deliberately provide a vanilla Session.
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()

    def refresh(self, entity: Any) -> None:
        self.session.refresh(entity)
