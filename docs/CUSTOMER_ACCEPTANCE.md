# Customer acceptance plan — QuantLab

This repository is **ready to sell as an enterprise technology/pilot**. It becomes a customer production deployment only after the customer's own technical, security, risk, legal and operational acceptance gates are passed.

## Mandatory acceptance gates

1. **Identity and RBAC** — map customer IdP/OIDC roles to the service role model and verify denied-role tests.
2. **Audit** — PostgreSQL backup/restore test, ClickHouse retention review, request-id trace from API request to stored event.
3. **Secrets** — move all credentials to customer secret manager/KMS; repository and image scans must contain no live credentials.
4. **Venue certification** — run adapters against sandbox/paper first, then a bounded canary approved by Trading/Risk/Ops.
5. **Failure drills** — timeout, venue 5xx/429, circuit open, process restart, database outage and kill-switch/rollback procedures.
6. **Load/SLO** — measure p50/p95/p99 and error rate on target hardware; repository thresholds are targets, not pre-measured claims.
7. **Domain acceptance** — Customer OOS dataset is frozen; purge/embargo geometry is agreed; transaction-cost model is customer-approved; acceptance compares baseline vs candidate without changing the holdout after review.
8. **Change control** — pin release commit/image digest and require review for model/limit/adapter changes.

## Sale package

- source-code repository and tagged release;
- Docker/Compose deployment reference;
- REST/OpenAPI boundary;
- RBAC/JWT reference implementation;
- PostgreSQL + ClickHouse audit schema;
- Bybit V5 + CCXT + MT5 adapter layer;
- synthetic customer demo dataset;
- unit/acceptance/load-test harnesses;
- security, provenance and claim-boundary documentation.
