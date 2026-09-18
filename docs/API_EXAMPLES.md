# API examples — SYNERGY QuantLab

`POST /enterprise/v1/validation/evaluate` — roles **researcher, risk**.

```json
{"returns":[0.002,-0.001,0.0015,0.001,0.0005,0.002,-0.001,0.0015,0.001,0.0005,0.002,-0.001,0.0015,0.001,0.0005,0.002,-0.001,0.0015,0.001,0.0005,0.002,-0.001,0.0015,0.001,0.0005,0.002,-0.001,0.0015,0.001,0.0005],"costs_bps":1.0,"min_trades":30,"max_dd":0.20,"min_sharpe":0.5}
```

Expected: `gate`, `metrics`, `request_id`. Canonical schema: `/docs`.