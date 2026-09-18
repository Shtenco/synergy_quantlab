# SYNERGY QuantLab

**Leakage-safe strategy validation, purged walk-forward, OOS scoring and deployment gates**

Version: `2.0.0` · Python 3.11+ · REST API · Docker · CI · automated tests

## Why this exists
Most trading teams cannot reliably distinguish alpha from leakage, overfit and cost-blind backtests.

## Commercial buyer
Quant funds, prop firms, broker research desks, systematic asset managers.

## Core guarantee
The software guarantees deterministic interface behavior covered by tests. **It does not guarantee trading profit.** Live-market deployment requires customer-specific OOS validation, fees/spread/slippage/latency/capacity modelling, security review and legal/compliance approval.

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest -q
python -m synergy_quantlab.api
```

Then open `http://localhost:8000/docs`.

## Commercial package
- standalone installable Python package;
- versioned FastAPI boundary;
- deterministic reference core;
- Dockerfile and GitHub Actions CI;
- sales one-pager, security boundary, deployment notes and provenance;
- proprietary evaluation licence ready for a paid pilot.

## Research lineage
Shtenco/crypto_pump V2; Shtenco/midas_ai_trading_system walk-forward lineage; MQL5 cross-fitting / CatBoost / VaR research

See `docs/PRODUCT_STATUS.md`, `docs/SALES_ONE_PAGER.md`, `docs/SECURITY.md` and `docs/PROVENANCE.md`.

## Enterprise v2.0.0

The repository now includes a separate enterprise boundary around the product core:

- JWT/RBAC roles (`viewer`, `researcher`, `trader`, `risk`, `operator`, `admin`);
- request-id propagation and auditable product actions;
- PostgreSQL and ClickHouse audit stores;
- Bybit V5, CCXT multi-CEX and MetaTrader 5 adapters with live execution disabled by default;
- retry/circuit breaker controls;
- health and Prometheus-compatible metrics;
- Docker Compose deployment reference;
- deterministic synthetic customer dataset and HTTP/k6 load harnesses.

See `docs/ENTERPRISE_ARCHITECTURE.md`, `docs/ENTERPRISE_DEPLOYMENT.md` and `docs/CUSTOMER_ACCEPTANCE.md` before any customer deployment.
