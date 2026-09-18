import json
from fastapi.testclient import TestClient
from synergy_quantlab.api import app
from synergy_quantlab.enterprise.auth import sign_token
from synergy_quantlab.enterprise.models import Role

SECRET="dev-only-change-me-not-for-production"

def token(role):
    return sign_token(SECRET,subject="fund-user",roles=[Role(role)],tenant_id="fund-a",ttl_seconds=3600)

def test_product_enterprise_endpoint_and_audit_linkage():
    c=TestClient(app)
    request_id="acceptance-123"
    res=c.post('/enterprise/v1/validation/evaluate',json={'returns': [0.002, -0.001, 0.0015, 0.001, 0.0005, 0.002, -0.001, 0.0015, 0.001, 0.0005, 0.002, -0.001, 0.0015, 0.001, 0.0005, 0.002, -0.001, 0.0015, 0.001, 0.0005, 0.002, -0.001, 0.0015, 0.001, 0.0005, 0.002, -0.001, 0.0015, 0.001, 0.0005, 0.002, -0.001, 0.0015, 0.001, 0.0005, 0.002, -0.001, 0.0015, 0.001, 0.0005, 0.002, -0.001, 0.0015, 0.001, 0.0005, 0.002, -0.001, 0.0015, 0.001, 0.0005], 'costs_bps': 1.0},headers={"Authorization":"Bearer "+token('researcher'),"X-Request-ID":request_id})
    assert res.status_code==200, res.text
    body=res.json()
    for key in ['gate', 'metrics', 'request_id']: assert key in body
    assert body["request_id"]==request_id
    admin=token("admin")
    audit=c.get('/enterprise/audit',headers={"Authorization":"Bearer "+admin})
    assert audit.status_code==200
    assert any(e["request_id"]==request_id for e in audit.json())

def test_product_endpoint_requires_authorized_role():
    c=TestClient(app)
    res=c.post('/enterprise/v1/validation/evaluate',json={'returns': [0.002, -0.001, 0.0015, 0.001, 0.0005, 0.002, -0.001, 0.0015, 0.001, 0.0005, 0.002, -0.001, 0.0015, 0.001, 0.0005, 0.002, -0.001, 0.0015, 0.001, 0.0005, 0.002, -0.001, 0.0015, 0.001, 0.0005, 0.002, -0.001, 0.0015, 0.001, 0.0005, 0.002, -0.001, 0.0015, 0.001, 0.0005, 0.002, -0.001, 0.0015, 0.001, 0.0005, 0.002, -0.001, 0.0015, 0.001, 0.0005, 0.002, -0.001, 0.0015, 0.001, 0.0005], 'costs_bps': 1.0},headers={"Authorization":"Bearer "+token("viewer")})
    assert res.status_code==403

def test_api_exposes_enterprise_control_routes():
    paths={r.path for r in app.routes}
    assert '/enterprise/health' in paths
    assert '/enterprise/v1/validation/evaluate' in paths
