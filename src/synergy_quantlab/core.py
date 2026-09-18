from __future__ import annotations
from dataclasses import dataclass
from typing import Iterator, Sequence
import numpy as np
import pandas as pd

@dataclass(frozen=True)
class Fold:
    fold: int
    train_idx: np.ndarray
    test_idx: np.ndarray


def purged_walk_forward(n: int, *, min_train: int, test_size: int, purge: int=0, embargo: int=0) -> Iterator[Fold]:
    if min_train <= 0 or test_size <= 0 or n <= min_train:
        raise ValueError("invalid split geometry")
    fold = 0
    test_start = min_train
    while test_start < n:
        train_end = max(0, test_start - purge)
        test_end = min(n, test_start + test_size)
        if train_end < min_train - purge:
            break
        train_idx = np.arange(0, train_end, dtype=int)
        test_idx = np.arange(test_start, test_end, dtype=int)
        if len(train_idx) and len(test_idx):
            yield Fold(fold, train_idx, test_idx)
            fold += 1
        test_start = test_end + embargo


def performance_report(returns: Sequence[float], annualization: float=252.0) -> dict[str, float]:
    r = np.asarray(list(returns), dtype=float)
    if r.size == 0:
        return {"n":0,"total_return":0.0,"sharpe":0.0,"max_drawdown":0.0,"hit_rate":0.0}
    equity = np.cumprod(1.0 + r)
    peak = np.maximum.accumulate(equity)
    dd = 1.0 - np.divide(equity, peak, out=np.ones_like(equity), where=peak!=0)
    std = float(np.std(r, ddof=1)) if r.size > 1 else 0.0
    sharpe = float(np.mean(r) / std * np.sqrt(annualization)) if std > 0 else 0.0
    return {
        "n": int(r.size),
        "total_return": float(equity[-1]-1.0),
        "sharpe": sharpe,
        "max_drawdown": float(dd.max(initial=0.0)),
        "hit_rate": float(np.mean(r>0)),
    }


def cost_adjust(raw_returns: Sequence[float], costs_bps: Sequence[float] | float) -> np.ndarray:
    r=np.asarray(list(raw_returns), dtype=float)
    c=np.asarray(costs_bps if not np.isscalar(costs_bps) else np.repeat(costs_bps, len(r)), dtype=float)
    if len(c)!=len(r): raise ValueError("cost vector length mismatch")
    return r - c/10_000.0


def deployment_gate(metrics: dict[str,float], *, min_trades:int=30, max_dd:float=.20, min_sharpe:float=.5) -> str:
    if metrics.get("n",0) < min_trades: return "RESEARCH"
    if metrics.get("max_drawdown",1.0) > max_dd: return "REJECT"
    if metrics.get("sharpe",-999) < min_sharpe: return "PAPER"
    return "CANARY"
