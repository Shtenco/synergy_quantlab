from fastapi import FastAPI
from pydantic import BaseModel, Field
import uvicorn
from .core import performance_report, cost_adjust, deployment_gate
app=FastAPI(title="SYNERGY QuantLab",version="2.0.0")
class EvalRequest(BaseModel):
    returns:list[float]
    costs_bps:float=Field(default=0,ge=0)
@app.get("/health")
def health(): return {"ok":True,"service":"quantlab","version":"2.0.0"}
@app.post("/v1/evaluate")
def evaluate(req:EvalRequest):
    net=cost_adjust(req.returns,req.costs_bps)
    m=performance_report(net)
    return {"metrics":m,"gate":deployment_gate(m)}

# Enterprise v2 control/data plane
from .enterprise.service import EnterpriseRuntime, build_enterprise_router, install_observability
from .enterprise.product import build_product_router
enterprise_runtime=EnterpriseRuntime.from_env(service_name='synergy-quantlab')
install_observability(app,enterprise_runtime)
app.include_router(build_enterprise_router(enterprise_runtime))
app.include_router(build_product_router(enterprise_runtime))

if __name__=='__main__': uvicorn.run(app,host='0.0.0.0',port=8000)
