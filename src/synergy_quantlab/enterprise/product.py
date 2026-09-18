from __future__ import annotations
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from ..core import cost_adjust, deployment_gate, performance_report
from .models import Principal, Role
from .service import EnterpriseRuntime, principal_dependency, request_id_header

class EvaluateRequest(BaseModel):
    returns:list[float]
    costs_bps:float|list[float]=1.0
    annualization:float=252.0
    min_trades:int=30
    max_dd:float=.20
    min_sharpe:float=.5

def build_product_router(runtime:EnterpriseRuntime)->APIRouter:
    router=APIRouter(prefix="/enterprise/v1/validation",tags=["enterprise-quantlab"])
    @router.post("/evaluate")
    async def evaluate(req:EvaluateRequest, principal:Principal=Depends(principal_dependency(runtime,{Role.RESEARCHER,Role.RISK})), request_id:str=Depends(request_id_header)):
        adjusted=cost_adjust(req.returns,req.costs_bps)
        metrics=performance_report(adjusted,req.annualization)
        gate=deployment_gate(metrics,min_trades=req.min_trades,max_dd=req.max_dd,min_sharpe=req.min_sharpe)
        runtime.record(principal,action="quantlab.validation.evaluate",request_id=request_id,payload={"gate":gate,"n":metrics["n"],"sharpe":metrics["sharpe"],"max_drawdown":metrics["max_drawdown"]})
        runtime.metrics.inc("product_requests_total",labels={"action":"validation"})
        return {"request_id":request_id,"gate":gate,"metrics":metrics}
    return router
