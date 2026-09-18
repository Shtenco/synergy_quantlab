# Sales one-pager

## Problem
Most trading teams cannot reliably distinguish alpha from leakage, overfit and cost-blind backtests.

## Product
**SYNERGY QuantLab** — Leakage-safe strategy validation, purged walk-forward, OOS scoring and deployment gates.

## Buyer
Quant funds, prop firms, broker research desks, systematic asset managers.

## Commercial delivery
- paid technical pilot;
- source-code licence or binary/service licence;
- OEM / white-label integration;
- enterprise support and customer-specific adapters.

## Proof package
- runnable demo;
- automated tests;
- architecture and API specification;
- validation protocol;
- provenance back to the underlying SYNERGY research lineage.

## Commercial claim boundary
The product is sold as trading/research infrastructure, not as a guarantee of future profit. Any alpha or execution benefit must be established in the customer’s own OOS/paper/canary environment.

## Enterprise v2 delivery
- tenant-scoped JWT/RBAC boundary and request-id correlation;
- PostgreSQL operational audit + ClickHouse analytical mirror;
- Bybit V5, CCXT multi-CEX and MetaTrader 5 integration layer, dry-run by default;
- retry/circuit-breaker controls and client order identity;
- health + Prometheus text metrics;
- Docker Compose reference stack;
- 64-record deterministic synthetic customer demo plus load-test harnesses;
- customer acceptance checklist separating “sellable technology” from “customer production approval”.

## Recommended first engagement
Run a paid technical evaluation against customer-owned data/accounts in paper or sandbox mode. Success criteria are agreed before the pilot and recorded as measurable acceptance gates; no performance or profit claim is inferred from the synthetic demo.
