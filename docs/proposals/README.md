# Proposals awaiting human approval

Scientific changes are proposed here and adopted only after review, through a decision record in
`docs/decisions/` and versioned configuration. Until then, nothing in this folder affects any
output, ranking or verdict.

| Proposal | Effect if approved | UNKNOWN fields affected | Status |
|---|---|---:|---|
| [Durum residual bounds](durum-residual-bounds.md) | 72 nodes get ESTIMATED intervals instead of UNKNOWN in a new run | 288 | Open |
| [Location-conflict region rule](location-conflict-region-invariance.md) | 2 nodes assigned to the region both coordinates agree on | 8 | Open |
| [Sparse-data stress diagnostic](sparse-data-stress-diagnostic.md) | Robustness result shown in the app; decline-to-rank rule reviewed | 0 (diagnostic) | Open |

Files: `sparse-data-stress-v1.protocol.json` (seeded protocol) and
`sparse-data-stress-v1.report.json` (result; its code hash equals the unchanged scientific source).
Run with `python -m scripts.sparse_data_stress --allow-temporary-scenario`.
