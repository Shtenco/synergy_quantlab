from __future__ import annotations
from typing import Any
from uuid import UUID

from .core import deployment_gate


CONTRACT_ID = "synergy.trading.validation-decision/v1"
AUTHORITY = "trading_validation"


def validation_decision_payload(
    *,
    candidate_event_id: UUID | str,
    metrics: dict[str, float],
    protocol_id: str,
    dataset_manifest_sha256: str | None = None,
    warnings: list[str] | None = None,
    min_trades: int = 30,
    max_dd: float = 0.20,
    min_sharpe: float = 0.5,
) -> dict[str, Any]:
    gate = deployment_gate(
        metrics, min_trades=min_trades, max_dd=max_dd, min_sharpe=min_sharpe
    )
    return {
        "candidate_event_id": str(candidate_event_id),
        "gate": gate,
        "metrics": {
            "n": int(metrics.get("n", 0)),
            "total_return": float(metrics.get("total_return", 0.0)),
            "sharpe": float(metrics.get("sharpe", 0.0)),
            "max_drawdown": float(metrics.get("max_drawdown", 0.0)),
            "hit_rate": float(metrics.get("hit_rate", 0.0)),
        },
        "protocol_id": protocol_id,
        "dataset_manifest_sha256": dataset_manifest_sha256,
        "warnings": list(warnings or []),
    }
