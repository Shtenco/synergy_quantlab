"""Source-pinned federated read-only smoke. No broker orders; synthetic data only."""
from __future__ import annotations
import argparse, hashlib, importlib, json, math, random, sys
from pathlib import Path

PINS = {
"synergy_quantlab":"df808e3cf666b1be1f553aa28a6479b5477f4735",
"synergy_riskguard":"bc3ef1810c5d77f54b8a9ecf2f1b8adc35231f2b",
"synergy_market_graph":"9a0952803239576c0b2d94dd5a9e82a7b0b0d01e",
"synergy_midas_institutional":"75f646380cd0a1478e5093216615b1af8ded1fbf",
"synergy_relative_value":"0f37ef55ac989933acd63a0954b5cf521eec4449",
"synergy_ai_investment_committee":"7dbec0202badf1afce60ada83b5402f8d8ed9f14",
"synergy_market_maker":"7d0988ad0f6201e5c5800a92eba5eb491bb240f7",
"synergy_adaptive_engine":"c4af6194eedfbf9b9c0824822abe42306ba9f6b8",
}
def market(seed=20261024):
    rng=random.Random(seed); a=1.15; residual=0.; rows=[]
    for i in range(600):
        regime=0 if i<240 else 1 if i<360 else 2
        a*=1+(0.00002,-0.00003,0)[regime]+rng.gauss(0,(.0008,.0012,.0018)[regime])
        residual=(.86,.73,1.015)[regime]*residual+rng.gauss(0,(.0009,.0010,.0014)[regime])
        rows.append(dict(i=i,x=round(a,9),y=round(.08+.94*a+residual,9),
                         spread=round(1.8+.5*rng.random()+.12*regime,5)))
    return rows
def modules(parent):
    mapping={"relative":("synergy_relative_value","synergy_relative_value.core"),
             "graph":("synergy_market_graph","synergy_market_graph.core"),
             "committee":("synergy_ai_investment_committee","synergy_ai_committee.core"),
             "maker":("synergy_market_maker","synergy_market_maker.core"),
             "midas":("synergy_midas_institutional","synergy_midas.core"),
             "risk":("synergy_riskguard","synergy_riskguard.core"),
             "adaptive":("synergy_adaptive_engine","synergy_adaptive_engine.core"),
             "quantlab":("synergy_quantlab","synergy_quantlab.core")}
    for repo,_ in mapping.values():
        source=parent/repo/"src"
        if not source.is_dir():raise FileNotFoundError(source)
        sys.path.insert(0,str(source.resolve()))
    return {key:importlib.import_module(mod) for key,(_,mod) in mapping.items()}
def signals(rows, model, threshold, a, b):
    for i in range(a,b):
        z=model.zscore(rows[i]["x"],rows[i]["y"])
        side=-1 if z>threshold else 1 if z< -threshold else 0
        yield i, side
def experiment(parent, destination):
    ms=modules(parent); rows=market()
    raw=json.dumps(rows,sort_keys=True,separators=(",",":")).encode()
    digest=hashlib.sha256(raw).hexdigest()
    relative=ms["relative"];ql=ms["quantlab"];risk=ms["risk"]
    fit=relative.fit_pair([r["x"] for r in rows[:240]],[r["y"] for r in rows[:240]])
    trials=[]
    for threshold in (.35,.65,1.,1.4):
        s=list(signals(rows,fit,threshold,240,359))
        values=[side*(rows[i+1]["y"]/rows[i]["y"]-1)-abs(side)*(rows[i]["spread"]+4)/10000 for i,side in s]
        trials.append((threshold,sum(values),sum(bool(side) for _,side in s)))
    eligible=[x for x in trials if x[2]>=30]
    picked=max(eligible,key=lambda x:x[1]) if eligible else max(trials,key=lambda x:x[2])
    threshold=picked[0]
    vals=[side*(rows[i+1]["y"]/rows[i]["y"]-1)-abs(side)*(rows[i]["spread"]+4)/10000 for i,side in signals(rows,fit,threshold,240,359)]
    val_metrics=ql.performance_report(vals,annualization=24*252)
    val_metrics["n"]=picked[2]
    gate=ql.deployment_gate(val_metrics)
    result={"kind":"SYNTHETIC_SOURCE_PINNED_SMOKE_NOT_LIVE","sha256":digest,"pins":PINS,
            "train":[0,240],"validation":[240,360],"oos":[360,600],
            "selection":trials,"selected_threshold":threshold,"validation_gate":gate}
    if gate not in ("PAPER","CANARY"):
        result["status"]="NOT_PROMOTED"
    else:
        equity=100000.;high=equity;day=equity;rets=[];trades=[]
        ensemble=ms["adaptive"].AdaptiveEnsemble(["pair","momentum"])
        for i,pside in signals(rows,fit,threshold,360,599):
            if (i-360)%24==0:day=equity
            r=rows[i];next_r=rows[i+1];mom=1 if r["y"]>rows[i-3]["y"] else -1
            score=ensemble.score([pside,mom]);side=1 if score>.30 else -1 if score<-.30 else 0
            g=ms["graph"].MarketGraph([ms["graph"].Edge("USD","Y",1/r["y"],fee_bps=r["spread"]/2+1)])
            fv=g.fair_value("USD","Y")
            if fv is None:raise ValueError("graph did not return rate")
            quote=ms["maker"].quote(r["y"],0,.01)
            council=ms["committee"].deliberate(ms["committee"].MarketContext("Y",mom*.1,.01))
            if council.capital_guardian!="PASS" or quote.status!="QUOTE":side=0
            sig=ms["midas"].Signal("pair_momentum","Y","BUY" if side>0 else "SELL",abs(score),.01,equity*.15 if side else 0)
            dec=ms["midas"].MidasOrchestrator(lambda _:bool(side),lambda _:equity*.25).decide(sig)
            amount=0.
            if dec.stage==ms["midas"].Stage.EXECUTION_READY:
                state=risk.AccountState(equity,day,high,0.,tuple(rets[-100:]))
                d=risk.decide(state,risk.OrderIntent("Y",dec.approved_notional,sig.side))
                if d.action in (risk.Action.ALLOW,risk.Action.RESIZE):amount=d.approved_notional
            gross=side*amount*(next_r["y"]/r["y"]-1)
            costs=amount*(r["spread"]+4)/10000
            prev=equity;equity+=gross-costs;rets.append((equity-prev)/prev);high=max(high,equity)
            friction=(r["spread"]+4)/10000
            forward=next_r["y"]/r["y"]-1
            ensemble.update([pside*forward-abs(pside)*friction,mom*forward-friction])
            trades.append({"i":i,"side":side,"notional":amount,"net":gross-costs,"equity":equity})
        result["status"]="SOURCE_PINNED_SYNTHETIC_EXECUTED"
        result["oos"]={"n":len(trades),"trade_count":sum(bool(t["notional"]) for t in trades),
                       "net_usd":equity-100000,"metrics":ql.performance_report(rets,annualization=24*252)}
        destination.mkdir(parents=True,exist_ok=True)
        (destination/"ledger.json").write_text(json.dumps(trades,indent=2)+"\n")
    destination.mkdir(parents=True,exist_ok=True)
    (destination/"report.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    return result
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--sibling-root",type=Path,required=True)
    ap.add_argument("--output",type=Path,default=Path("benchmarks/federated_v1/artifacts"))
    args=ap.parse_args();print(json.dumps(experiment(args.sibling_root,args.output),indent=2))
