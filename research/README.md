# Research runs

Registered experiments that sit outside the live app. Each one follows a protocol hashed before
it was scored and writes its result to `docs/audits/`.

| Folder | Question | Protocol | Result | Run |
|---|---|---|---|---|
| `phase4x/` | Does XGBoost beat the registered logistic siting model on the Rwanda table? | [phase4x-protocol](../docs/spec/phase4x-protocol.md) | [Not better](../docs/phase4x-results.md) | `make research-xgb` |
| `phase4n/` | Can building footprints find grain mills in Njombe, Tanzania? | [phase4n-protocol](../docs/spec/phase4n-protocol.md) | [KILL](../docs/phase4n-results.md) | `make research-njombe` |

Both need the optional `research` dependency group (`uv sync --group research`). `phase4n`
shares its metric code with `phase4x/core.py`.
