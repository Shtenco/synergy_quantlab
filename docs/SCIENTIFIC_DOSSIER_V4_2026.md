# SYNERGY QuantLab — Scientific dossier V4

## Research thesis: reproducibility is a separate authority

QuantLab is a dedicated **trading validation authority**, not a signal model and not a broker. It creates chronologically ordered folds, computes economic statistics, subtracts trading costs and issues a bounded research maturity state. This is critical for ensemble AI/RL research: an impressive in-sample equity curve does not establish independently reproducible alpha.

Real source modules: [core.py](../src/synergy_quantlab/core.py), [synergy_contracts.py](../src/synergy_quantlab/synergy_contracts.py), enterprise service/audit/adapters and [tests](../tests/).

## Implemented components

| Contract | Mathematical or engineering role |
|---|---|
| purged_walk_forward | Chronological index split with purge and embargo gaps |
| performance_report | Compounded total return, sample-volatility Sharpe, max drawdown, hit rate |
| cost_adjust | Net returns after specified basis-point costs |
| deployment_gate | RESEARCH / REJECT / PAPER / CANARY states |
| validation_decision_payload | Source candidate ID, protocol ID, frozen manifest digest, metrics and warnings |
| enterprise service | Typed API, identity, audit and connector boundary |

The split generator for test start $s$, purge $p$, test size $h$, embargo $e$ constructs training indices $[0,s-p)$, test indices $[s,\min(n,s+h))$, then advances the next start by $h+e$. This is a useful deterministic index-level control. **It does not inspect per-label time spans**, so event-overlap controls for variable-horizon targets still require an additional layer.

## Exact quantitative definitions

For periodic returns $r_t$ and no intermediate external cashflows:

$$
E_t=\prod_{i=1}^{t}(1+r_i).
$$

$$
DD_t=1-\frac{E_t}{\max_{u\le t}E_u},\qquad
MDD=\max_t DD_t.
$$

The actual implementation uses

$$
S=\frac{\overline r}{s(r)}\sqrt{A},
$$

with $A=252$ by default, and zero for undefined/zero sample volatility. It does not subtract the risk-free return, account for autocorrelation or ensure that observations are daily. These must be reflected in comparisons.

Net-return approximation:

$$
r_t^{net}=r_t^{gross}-\frac{c_t^{bps}}{10^4}.
$$

The approximation works as a cost model for an input return vector, but cannot replace slippage/fill/margin replay. Invalid prices, returns below -100%, non-finite inputs and positive/negative capital flows need explicit policies.

The default promotion gate requires at least 30 observations; it rejects excessive MDD above 20%, otherwise assigns PAPER for Sharpe below 0.5, else CANARY. **A CANARY label is not permission to place orders**: RiskGuard and operator authorization remain separate.

## Original contribution and scientific relevance

**Validation-as-a-service:** independent source, frozen dataset manifest and rule version for every candidate, regardless of whether the producer is NEXUS, RL, MIDAS or a classical formula.

**Experimental promotion discipline:** repeatability and risk-aware maturity states replace self-declared strategy quality.

**Comparable economics:** models can be evaluated on one currency base, calendar, tradable universe, execution-cost convention and portfolio notional.

## Falsifiable experimental programme

1. Create a 10,000-row deterministic fixture with overlapping 5/24/96-bar labels and explicit event windows. Compare index purge against full event-aware purge.
2. Recompute all metrics on known equity traces including zero variance, large drawdown, deposits, NaN, crashes and nonuniform sampling.
3. Repeat out-of-sample walk-forward on fixed seeds and frozen market-data hashes; include buy-and-hold, random and null-signal baselines.
4. Measure selection bias across 100 simulated strategy candidates and publish confidence intervals on actual performance improvement.
5. Export a ledger binding each assessment to code commit, dataset hash, cost assumptions, timestamps and allowed next state.

## Engineering and potential applications

Quant research teams can reuse this module as an **independent research quality gate**, and integrate its typed output with RiskGuard and MIDAS. The enterprise code supports an integration surface, but no production SLA or real-money profitability is asserted by code presence.

Reproduction entry: install declared project dependencies and run Python unit tests in a controlled environment. This dossier derives from code inspection; it does not claim that a new historical experiment has been executed.
