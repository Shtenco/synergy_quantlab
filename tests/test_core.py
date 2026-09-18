from synergy_quantlab.core import purged_walk_forward, performance_report, cost_adjust, deployment_gate

def test_purged_split_has_gap():
    folds=list(purged_walk_forward(100,min_train=40,test_size=10,purge=5,embargo=2))
    assert folds and folds[0].train_idx[-1] <= folds[0].test_idx[0]-6

def test_costs_reduce_return():
    gross=[.01,.01,-.005]
    net=cost_adjust(gross,10)
    assert sum(net) < sum(gross)

def test_gate():
    m=performance_report([.002]*40)
    assert deployment_gate(m) in {"CANARY","PAPER"}
