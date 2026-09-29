# 🧪 SYNERGY QuantLab — verified technical dossier

> **Статус:** 🟡 CANDIDATE validation laboratory.
> **Проверено по фактическому `main`:** 29.09.2026.
> **Роль:** trading validation authority, а не signal/execution engine.

## 1. 🎯 Задача

QuantLab реализует reproducible validation primitives: purged walk-forward splits, cost adjustment, performance metrics и deployment gate.

Главный принцип:

```text
backtest result
→ validation protocol
→ cost-adjusted metrics
→ gate
!= automatic deployment
```

## 2. 📦 Фактический состав

Repository содержит:

- `src/synergy_quantlab/core.py`;
- `api.py`;
- `synergy_contracts.py`;
- enterprise package;
- tests;
- Docker/deploy/loadtests/docs/examples.

## 3. 🧠 Purged walk-forward

`purged_walk_forward(n,min_train,test_size,purge,embargo)` строит последовательные folds.

Для каждого fold:

```text
train = [0 .. test_start-purge)
test  = [test_start .. test_end)
next test starts after embargo
```

Это снижает temporal leakage между train и test.

Параметры должны удовлетворять валидной split geometry; иначе `ValueError`.

## 4. 📊 Performance report

Для returns:

[
Equity_t=prod_{ile t}(1+r_i)
]

Total return:

[
R=Equity_T-1
]

Sharpe:

[
S=
rac{ar r}{s_r}sqrt{annualization}
]

если std > 0.

Drawdown:

[
DD_t=1-rac{Equity_t}{Peak_t}
]

Report:

- n;
- total return;
- Sharpe;
- max drawdown;
- hit rate.

## 5. 💸 Cost adjustment

`cost_adjust()`:

[
r^{net}_t=r^{raw}_t-rac{costBps_t}{10000}
]

При vector costs длина обязана совпадать с returns.

Это простая линейная cost model; она не включает nonlinear market impact автоматически.

## 6. 🚦 Deployment gate

Defaults:

```text
min_trades = 30
max_dd     = 0.20
min_sharpe = 0.5
```

Логика:

- n < min trades → `RESEARCH`;
- max DD > threshold → `REJECT`;
- Sharpe < threshold → `PAPER`;
- иначе → `CANARY`.

То есть gate сам по себе никогда не возвращает «FULL PRODUCTION».

## 7. 🔗 Federation contract

```text
CONTRACT_ID          = synergy.trading.validation-decision/v1
UPSTREAM_CONTRACT_ID = synergy.trading.portfolio-decision/v1
AUTHORITY            = trading_validation
```

`validate_portfolio_candidate` проверяет:

- confidence ∈ [0,1];
- positions — непустой list;
- side ∈ BUY/SELL/FLAT;
- notional >= 0.

`validation_decision_payload` связывает metrics с:

- candidate event id;
- protocol id;
- optional dataset manifest SHA-256;
- warnings;
- gate.

## 8. 🛡️ Authority boundaries

```text
CANARY != production
PAPER  != live capital
Sharpe != guaranteed future return
backtest != realized P&L
validation decision != broker authorization
dataset hash != dataset quality
```

## 9. 🧪 Validation discipline

Сильный run должен фиксировать:

- exact dataset manifest/hash;
- feature version;
- train/test indices;
- purge/embargo;
- costs;
- annualization;
- strategy commit;
- seed;
- metrics;
- warnings;
- decision.

Без этого metric snapshot трудно независимо воспроизвести.

## 10. ⚠️ Current limitations

- Sharpe uses simple sample std;
- no autocorrelation/Newey-West correction;
- no probabilistic Sharpe;
- no multiple-testing correction;
- no turnover-aware nonlinear impact;
- no bootstrap CI;
- no regime segmentation in core.

Это не ошибки, а границы текущей минимальной validation implementation.

## 11. 🧪 Required next benchmarks

- leakage unit tests;
- purged fold geometry properties;
- embargo edge cases;
- cost stress 0→large bps;
- serial-correlation-aware Sharpe;
- bootstrap confidence intervals;
- deflated Sharpe / multiple trials;
- parameter-selection nested OOS;
- dataset manifest integrity;
- paper→canary promotion audit.

## 12. 🛠️ Воспроизводимость

```bash
git clone https://github.com/Shtenco/synergy_quantlab.git
cd synergy_quantlab
python -m pip install -e .
pytest -q
```

## 13. 🗺️ Карта repository

| Path | Role |
|---|---|
| `src/.../core.py` | WFO/metrics/cost/deployment gate |
| `src/.../synergy_contracts.py` | validation decision |
| `src/.../api.py` | API |
| `src/.../enterprise/` | auth/audit |
| `tests/` | validation/product/service/deploy tests |
| `deploy/` | deployment assets |
| `loadtests/` | load tests |

## 14. 🔗 Место в SYNERGY

```text
portfolio candidate
→ QuantLab validation
→ validation-decision/v1
→ risk / deployment governance
```

QuantLab должен быть независимее от strategy producer, иначе validation теряет смысл.

## 15. 📊 Evidence maturity

| Layer | Status |
|---|---|
| purged WFO | ✅ |
| costs | ✅ simple model |
| metrics | ✅ |
| deployment gate | ✅ |
| typed contract | ✅ |
| full statistical correction suite | ❌ |
| observed federation E2E | ❌ |
| live deployment authority | intentionally bounded |

## 16. 🚀 Roadmap

1. exact dataset manifest;
2. nested WFO;
3. bootstrap/CI;
4. multiple-testing correction;
5. nonlinear costs;
6. validation evidence artifacts;
7. M5 observed execution.

## 17. 🛑 Что проект НЕ утверждает

- that Sharpe 0.5 means strategy is profitable live;
- that CANARY means production-safe;
- that backtest = future result;
- that dataset hash removes leakage;
- that validation can authorize broker orders.

---

[🧭 SYNERGY SYSTEM](https://github.com/Shtenco/synergy_system) · [📚 Atlas](https://github.com/Shtenco/synergy_system/blob/main/docs/SYNERGY_REPOSITORY_ATLAS.md)
