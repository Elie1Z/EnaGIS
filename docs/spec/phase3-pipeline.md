# Phase 3: offline pipeline and trace exports

## Invocation

Prepare/ingest the pinned open [Phase 2 inputs](phase2-ingestion.md), then run from the repository root:

```sh
uv run --offline --locked --cache-dir .uv-cache python -m enagis run --allow-temporary-scenario
uv run --offline --locked --cache-dir .uv-cache python -m enagis verify-run outputs/phase3
```

`make pipeline` and `make verify-run` are equivalents where Make is installed. `run` accepts `--root`, `--input`, `--region`, `--scenario`, `--manifest` and `--output`. Output must be a subdirectory of project `outputs`; raw/input/config directories cannot be overwritten. It reads and hashes the seven consumed indexed tables, with no network, routing service or downloads. Roads and shipping-point outcomes are unused.

Without the flag, the supplied temporary scenario is refused. All coefficients and assignment/inventory/ranking/gap choices are in [versioned configuration](../../configs/scenarios/phase3-engineering-v1.json). [Decision 0005](../decisions/0005-phase3-walking-skeleton.md) records formulas, limits and the approval boundary.

## Artifacts

| File under `outputs/phase3` | Meaning |
|---|---|
| `engineering-shortlist.csv` | First ten calculable positive development nodes, with scenario warning, units, labels, CRS/precision, source dates/licences and verification question. |
| `engineering-ranking.csv` | All ranks; no final score, viability probability or inclusion frequency. |
| `nodes.json` | `Artifact[NodeTrace]`, including unranked UNKNOWN/review records and nested facility/node/storage, production, assignments, inventory, airflow, requirements, supply and gap. |
| `production_inputs.json` | All development reporting origins including UNKNOWN, source evidence, periods/units and geometry references. Province controls excluded. |
| `production_lineage.json` | Exact published all/durum component rows, vectors, status flags and province for those origins. |
| `allocations.json` | Typed assignments in tonnes per production period, with node or explicit unserved destination. |
| `production_balances.json` | Known input/assigned/unserved/residual per origin; unknown balances have null quantities and reasons. |
| `scenario.json` | Exact validated scenario, including null human approvals. |
| `source_snapshots.json` | Permitted upstream hashes, dates, publisher, URL and licence; scenario provenance lives in its configuration. |
| `audit.json` | Conservation, counts, assignment dispositions, transfer exclusions and reproducibility hashes. |
| `index.json` | Completion marker/hashes for the ten artifacts above, written last. |

`verify-run` checks checksums, schemas, identities, metadata, source references, origin/node mass balances, capacity limits, physical equations, gap classification, rank order and CSV equality with typed traces. Semantic corruption fails even if a checksum is updated. This validates a produced run; it does not approve scientific assumptions or replace field/source review.

Storage is tonnes of all commodities; throughput is tonnes per **production reporting period**; inventory is tonnes; airflow is m³/s; concurrent requirement is kW; electricity is kWh for **one hypothetical cooling cycle**. No cross-dimension conversion is implicit. Zero and UNKNOWN differ. Null margin is labelled UNKNOWN, not zero.

## Trace a node

Read its ID from the CSV:

```sh
uv run --offline --locked --cache-dir .uv-cache python -m enagis trace outputs/phase3 --node-id NODE_ID
```

The command verifies the run and prints the node trace, snapshots, raw crop-component lineage and exact scenario. Follow AAFC record/storage/P2 location → SADR membership and crop components → bounded assignment → residence inventory → flow/pressure/efficiency power → registry-only supply documentation → gap → initial rank. Inspect missing reasons and `assignment_status` for unranked nodes. Manitoba IDs are absent.

## Scientific boundary

Real locations and published production are combined with hypothetical assignments and coefficients. No grid audit, installed-fan evidence, operating confirmation, field verification, crop disaggregation or fitted siting model is established. Do not publish this engineering ranking as a scientific screening result or use it as siting features.

A later reviewed scenario must record sourced parameters and human approval of both methods and parameters. Runtime requires pinned permitted evidence and rejects scenario-only scientific parameter provenance. The Phase 0/2 gates remain applicable. New regions enter through adapters/configuration; this benchmark alone establishes no accuracy elsewhere.
