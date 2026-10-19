"""Minimal, bounded seller-dashboard diagnostic event contract.

Only fixed event codes and stages are accepted. No token, user ID, seller ID,
exception string, stack trace, query, or inventory values are recorded.
The sink is injected by the trusted server; this module does not persist logs.
"""
from dataclasses import dataclass

EVENT_CODE = "seller_dashboard_dependency_failed"
STAGES = frozenset({"session", "membership", "inventory_scope", "dashboard"})


@dataclass(frozen=True)
class SellerDiagnosticEvent:
    code: str
    stage: str


def make_seller_diagnostic_event(code, stage):
    if code != EVENT_CODE or stage not in STAGES:
        raise ValueError("Unsupported diagnostic event")
    return SellerDiagnosticEvent(code=EVENT_CODE, stage=stage)


def safe_report_seller_diagnostic(report_event, code, stage):
    """Best-effort report; diagnostic failures must never affect access control."""
    if report_event is None:
        return
    try:
        report_event(make_seller_diagnostic_event(code, stage))
    except Exception:
        pass
