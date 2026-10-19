"""Strict allowlisted diagnostics for seller dashboards."""
from dataclasses import dataclass

EVENT_CODE = "seller_dashboard_dependency_failed"
STAGES = frozenset(("session", "membership", "inventory_scope", "dashboard"))


@dataclass(frozen=True)
class SellerDiagnosticEvent:
    code: str
    stage: str


def make_seller_diagnostic_event(code, stage):
    if (
        not isinstance(code, str)
        or not isinstance(stage, str)
        or code != EVENT_CODE
        or stage not in STAGES
    ):
        raise ValueError("Unsupported diagnostic event")
    return SellerDiagnosticEvent(code=EVENT_CODE, stage=stage)


def safe_report_seller_diagnostic(report_event, code, stage):
    """Best-effort reporting never overrides authorization failures."""
    if report_event is None:
        return
    try:
        report_event(make_seller_diagnostic_event(code, stage))
    except Exception:
        pass
