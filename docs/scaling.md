# Scaling guide: adapt EnaGIS to a new country or commodity

**Honest time estimate.** Producing a *display* package for a new region can take a day if
the data is already prepared. A *defensible numerical screen* takes longer: you need a facility
registry, production statistics and sourced energy parameters, then the evaluation below. No
second real region has been onboarded yet, so this is a tested recipe for the software, not a
measured adaptation time.

## Path A — show prepared results in the app (hours)

1. Produce a JSON file that follows [spec/regional-view-package.md](spec/regional-view-package.md)
   (header with region, run ID, CRS `EPSG:4326`, period, coverage polygon; one record per site with
   evidence labels).
2. Open the app → **?** → *Open regional analysis*. The package is validated by
   `web/view-model.js` and replaces the built-in analysis. Synthetic packages show a "Synthetic
   data" ribbon.
3. Test: `node --test tests/test_view_model.cjs`.

This path displays results; it does not compute them.

## Path B — run the pipeline on a new region (days to weeks)

| Step | What to add | Where | Test |
|---|---|---|---|
| 1 Scope decision | Commodity, service (e.g. maize drying, milk cooling), unit of analysis, period, development vs hold-out areas | new `docs/decisions/00NN-*.md` | review |
| 2 Pin sources | Facility registry, production statistics, boundaries, roads (OSM extract) with URL, date, licence, SHA-256, redistributability | `docs/data/manifest.json` (new entries) | `python -m enagis acquire`, `verify-data` |
| 3 Region config | Copy `configs/regions/ca-prairies.json`; set `region_id`, `province_units` → your admin units, `development_units`, `transfer_units`, `province_coordinate_envelopes`, `registry_point_precision` (P1–P5), `coordinate_attribute_tolerance_degrees`, `harvest_year`, `source_ids` | `configs/regions/<id>.json` | `pytest tests/test_ingestion.py` |
| 4 Source adapter | Parse local columns into the shared contracts (`Facility`, `Node`, `Capacity`, `Production`, `SpatialMatch`); keep originals and units | `src/enagis/adapters/<country>.py` (model: `canada.py`) | fixture tests like `tests/phase2_fixture.py` |
| 5 Units | Declare crop units (t, bushel with specific mass, bags) and conversions with provenance | adapter + config | `tests/test_science_portability.py::test_bushel_conversion_*` pattern |
| 6 CRS | Choose a local projected CRS for distance and area; the code rejects inappropriate ones | config | `test_inappropriate_distance_crs_rejected` pattern |
| 7 Service model | Sourced parameters with ranges for the service (airflow, pressure, efficiency, hours; or the cooling/drying equivalent). Human approval required | `configs/scenarios/<id>.json` | `pytest tests/test_pipeline.py` |
| 8 Run | `python -m enagis run --region configs/regions/<id>.json --scenario ...` | `outputs/` | `verify-run` |
| 9 Evaluate | Report local data coverage; evaluate on **untouched spatial blocks**; compare with baselines B0/B1/B2/population | new preregistered protocol | `verify-experiment` |
| 10 Verify | Freeze a ranking, sample, collect dated field checks | `configs/verification/` | `make phase7-fixture` pattern |

## Rules that do not change between regions

- Every value keeps OBSERVED / PREDICTED / ESTIMATED / INFERRED / UNKNOWN with source, date and
  licence. UNKNOWN is never filled.
- Declare units and CRS at every interface; assert row counts after joins; conserve production.
- Siting features come only from upstream, label-free data.
- Never claim accuracy outside evaluated regions.

## Lessons from the pilot (read before choosing a region)

- Check that you can get **operating evidence** (equipment, inventory, electrical capacity),
  not only maps and registries. The pilot had registries but no electrical data, so every gap
  is UNKNOWN.
- Check **registry completeness**. An unapproved stress test found that unregistered facilities
  push their production onto documented neighbours (+72% kW at 10% missing;
  [proposal](proposals/sparse-data-stress-diagnostic.md)).
- Line up a **verification partner** before building the ranking.

See [scope-and-transfer.md](scope-and-transfer.md) for the energy-access transfer path.
