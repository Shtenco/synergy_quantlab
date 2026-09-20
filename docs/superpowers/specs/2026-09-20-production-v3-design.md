# QuantLab V3 Production Hardening Design

**Version:** 3.0.0  
**Branch:** `production/v3.0.0`  
**Status:** design approved for implementation planning

## Goal

Turn QuantLab from a metric/deployment-gate API into a customer-grade validation evidence service that makes the validation protocol reproducible, immutable, tenant-scoped, auditable, and safe to operate in production environments.

## Current-state findings

The current enterprise endpoint `POST /enterprise/v1/validation/evaluate` accepts a caller-supplied return series, cost model and gate thresholds, computes metrics, writes an audit event, and returns `gate + metrics + request_id`.

The core already contains:
- `purged_walk_forward()`;
- `cost_adjust()`;
- `performance_report()`;
- `deployment_gate()`.

The repository also ships PostgreSQL DDL for `audit_events` and `idempotency_keys`, but idempotency is not used by the runtime. The current production auth boundary is HS256-based and the current health endpoint does not prove PostgreSQL/control-plane readiness.

## V3 invariants

1. Validation evidence must be reproducible from a pinned protocol and dataset identity.
2. A validation artifact is immutable after successful creation.
3. Tenant A must never be able to read or overwrite Tenant B evidence.
4. The same `Idempotency-Key` plus identical canonical request returns the original artifact.
5. The same key plus a different canonical request returns HTTP 409.
6. Invalid numerical inputs fail before any evidence artifact is committed.
7. Production readiness fails closed when the authoritative control store is unavailable.
8. Production auth uses an injected verifier interface; HS256 remains dev/test only.
9. Existing V1 endpoint remains available during V3 migration but is explicitly legacy/pilot behavior.

## Architecture

```text
client
  -> customer gateway / OIDC / mTLS
  -> AuthVerifier
  -> tenant + RBAC
  -> IdempotencyStore
  -> ValidationService
       -> ValidationProtocol
       -> dataset digest
       -> purged walk-forward / supplied OOS evidence
       -> cost adjustment
       -> metrics
       -> deployment gate
  -> ValidationArtifactStore (PostgreSQL)
  -> AuditStore
  -> metrics / structured logs / traces
```

## Authentication contract

Introduce:

```python
class AuthVerifier(Protocol):
    def verify(self, token: str) -> Principal: ...
```

Implement:
- `HS256AuthVerifier` for dev/tests only;
- `JWKSAuthVerifier` for production reference deployment.

Production mode must reject startup when configured to use HS256 as the only verifier.

JWKS verification requirements:
- asymmetric JWT only;
- issuer verification;
- audience verification;
- `exp`, `nbf`, `iat` validation;
- `kid`-based key selection;
- bounded JWKS cache with refresh after unknown `kid`;
- tenant claim required;
- unknown roles rejected.

## Control-plane readiness

Endpoints:
- `GET /enterprise/live`: process is alive; no DB dependency.
- `GET /enterprise/ready`: control store + authoritative audit store reachable.
- Keep `GET /enterprise/health` as compatibility alias, but document that V3 orchestration should use live/ready.

A readiness failure returns HTTP 503.

## Idempotency contract

Header: `Idempotency-Key`.

Canonical request hash:
- stable JSON canonicalization;
- tenant ID included in scope;
- operation name included in scope;
- SHA-256 digest.

Stored fields:
- tenant_id;
- operation;
- idempotency_key;
- request_hash;
- response_json;
- resource_id;
- created_at;
- expires_at.

Behavior:
- absent key: allowed for read-only endpoints; required for V3 artifact creation;
- new key: reserve then process;
- existing key + same hash + committed response: replay stored response;
- existing key + different hash: HTTP 409;
- existing key + in-progress reservation: HTTP 409 or bounded retry-after response, never duplicate processing.

## Validation protocol

```python
@dataclass(frozen=True)
class ValidationProtocol:
    protocol_version: str
    strategy_id: str
    dataset_id: str
    dataset_sha256: str
    annualization: float
    costs_bps: float | tuple[float, ...]
    min_trades: int
    max_drawdown: float
    min_sharpe: float
    min_train: int | None
    test_size: int | None
    purge: int
    embargo: int
```

Rules:
- annualization > 0 and finite;
- all costs finite and >= 0;
- max_drawdown in [0, 1];
- min_trades > 0;
- purge/embargo >= 0;
- walk-forward geometry validated before execution;
- protocol hash is stored with every artifact.

## Validation artifact

```python
@dataclass(frozen=True)
class ValidationArtifact:
    validation_id: UUID
    tenant_id: str
    strategy_id: str
    dataset_id: str
    dataset_sha256: str
    protocol_hash: str
    code_version: str
    created_at: datetime
    request_id: str
    metrics: Mapping[str, float]
    deployment_gate: str
    fold_summary: tuple[FoldSummary, ...]
```

Artifacts are append-only. Corrections create a new validation ID.

## Numerical safety

Reject:
- NaN or infinite returns;
- return <= -1.0;
- NaN/Inf costs;
- negative costs;
- cost vector length mismatch;
- invalid annualization;
- impossible walk-forward geometry;
- empty dataset where the selected operation requires observations.

No invalid request may create an idempotency success response or validation artifact.

## V3 API

`POST /enterprise/v3/validations`
- roles: RESEARCHER, RISK
- requires `Idempotency-Key`
- creates immutable artifact

`GET /enterprise/v3/validations/{validation_id}`
- same-tenant only
- roles: RESEARCHER, RISK, ADMIN

`GET /enterprise/v3/validations?strategy_id=...`
- tenant scoped
- bounded pagination

The V1 endpoint remains for migration and continues returning its existing response shape.

## Persistence

PostgreSQL is authoritative for:
- validation_artifacts;
- validation_fold_summaries;
- idempotency_keys;
- operational audit.

ClickHouse remains optional analytical audit mirror.

All database access must use a pooled connection interface. Migrations are additive and versioned.

## Observability

Every request must carry or receive:
- `X-Request-ID`;
- stable service name;
- tenant-safe structured JSON logs;
- Prometheus counters/histograms;
- optional OpenTelemetry trace context.

Never put JWTs, secrets, raw customer datasets, or full returns arrays into logs.

## Failure semantics

- authentication failure: 401;
- authorization failure: 403;
- idempotency conflict: 409;
- validation input failure: 422;
- authoritative control-store unavailable: 503;
- audit persistence failure for privileged creation: fail closed;
- unexpected internal failure: 500 with request ID, no sensitive detail.

## Deployment and CI

CI must run:
- full unit suite;
- PostgreSQL integration suite in a service container;
- migration apply test;
- tenant-isolation tests;
- idempotency tests;
- numerical-invalid-input tests;
- package build/import test;
- ruff.

Production deployment guidance requires OIDC/JWKS, TLS/mTLS at customer boundary, KMS/secret manager, pinned image digest, backup/restore evidence and database migration procedure.

## Acceptance gates

V3 is not considered customer-grade until all are true:
- existing V2 suite remains green;
- all V3 unit/integration tests pass;
- DB restart does not corrupt idempotency/artifacts;
- duplicate create cannot produce duplicate artifacts;
- cross-tenant artifact lookup is impossible;
- invalid numerical inputs create no artifacts;
- readiness returns 503 when PostgreSQL is unavailable;
- JWKS happy path and invalid/expired/unknown-kid paths are tested;
- documentation states that a passing validation gate does not guarantee future alpha.
