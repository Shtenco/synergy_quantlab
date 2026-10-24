#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:?Usage: fetch_pinned.sh /checkout-parent}"
mkdir -p "$ROOT"
while read -r name commit; do
 [ -n "$name" ] || continue
 if [ ! -d "$ROOT/$name/.git" ]; then
   git clone "https://github.com/Shtenco/$name.git" "$ROOT/$name"
 fi
 git -C "$ROOT/$name" fetch origin "$commit"
 git -C "$ROOT/$name" checkout --detach "$commit"
 [ "$(git -C "$ROOT/$name" rev-parse HEAD)" = "$commit" ]
done <<'REPOS'
synergy_quantlab df808e3cf666b1be1f553aa28a6479b5477f4735
synergy_riskguard bc3ef1810c5d77f54b8a9ecf2f1b8adc35231f2b
synergy_market_graph 9a0952803239576c0b2d94dd5a9e82a7b0b0d01e
synergy_midas_institutional 75f646380cd0a1478e5093216615b1af8ded1fbf
synergy_relative_value 0f37ef55ac989933acd63a0954b5cf521eec4449
synergy_ai_investment_committee 7dbec0202badf1afce60ada83b5402f8d8ed9f14
synergy_market_maker 7d0988ad0f6201e5c5800a92eba5eb491bb240f7
synergy_adaptive_engine c4af6194eedfbf9b9c0824822abe42306ba9f6b8
REPOS
