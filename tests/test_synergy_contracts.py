from uuid import UUID
import pytest

from synergy_quantlab.synergy_contracts import (
    CONTRACT_ID,
    validate_portfolio_candidate,
    validation_decision_payload,
)


def test_validation_contract_payload_uses_real_deployment_gate():
    payload = validation_decision_payload(
        candidate_event_id=UUID("11111111-1111-4111-8111-111111111111"),
        metrics={
            "n": 100,
            "total_return": 0.05,
            "sharpe": 0.8,
            "max_drawdown": 0.05,
            "hit_rate": 0.53,
        },
        protocol_id="purged-wf-v1",
        dataset_manifest_sha256="1" * 64,
    )
    assert CONTRACT_ID == "synergy.trading.validation-decision/v1"
    assert payload["gate"] == "CANARY"
    assert payload["candidate_event_id"].startswith("11111111")


def test_quantlab_accepts_well_formed_midas_candidate():
    validate_portfolio_candidate({
        "confidence": 0.61,
        "positions": [{"symbol":"EURUSD","side":"BUY","notional":"1000"}],
    })


def test_quantlab_rejects_malformed_midas_candidate():
    with pytest.raises(ValueError):
        validate_portfolio_candidate({
            "confidence": 1.4,
            "positions": [{"symbol":"EURUSD","side":"BUY","notional":"1000"}],
        })
