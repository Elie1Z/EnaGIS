# Audit log (append-only)

Each entry records what was done, the command or file used as evidence, and the outcome.
Entries are never edited after they are written; corrections are new entries.

## 2026-10-09 — Pass 1 (read-only audit)

1. **Baseline state.** HEAD `63579eb` = `origin/main` (`git ls-remote origin`). The working tree
   held uncommitted changes from the earlier session in this conversation: brand assets, map
   layout fixes, tie badges, a sparse-data stress diagnostic (`src/enagis/stress.py`,
   `configs/experiments/sparse-data-stress-v1.json`), a demo preflight and documentation edits.
   These are audited as "before" state, not hidden.
2. **Recorded hashes vs working tree.** `docs/audits/phase8.json` records
   `application_manifest_sha256 = d7c8c554…`. `git show HEAD:app/manifest.json | sha256sum`
   gives `d7c8c554…`; the working tree gives `fa38bff2…`. Cause: front-end rebuild with brand and
   layout changes. `docs/phase8-acceptance.md:35` requires an empty Git diff for `src/enagis` and
   `configs`; the working tree violated that (new `stress.py`, `cli.py` edit, new config).
   → Finding F-01. To be fixed in Pass 2 without scientific change.
3. **Verifiers** (working tree): `verify-data` 32 artifacts, `verify-run outputs/phase3` 10,
   `verify-experiment outputs/phase4` 6, `build_demo.py --verify` 32, `build_mvp --verify` 43 — all
   verified. `python -m enagis.science verify outputs/phase6-synthetic` → "Phase 6 stopped: replay
   requires the recorded code and lockfile". Re-run against a pristine HEAD worktree gives the same
   message, so the cause is a stale local synthetic output dated 2026-10-08 14:44 (before later code
   commits), not the session changes. → Finding F-02.
4. **Clean-room (HEAD).** `git clone https://github.com/Elie1Z/EnaGIS.git` into
   `outputs/cleanroom-before`; `uv sync --locked --cache-dir .uv-cache` succeeded in 35 s with
   network. Executing the new `.venv\Scripts\python.exe` was blocked by the host's Windows
   Application Control policy (os error 4551) both under `%TEMP%` and inside the repo. Checks were
   then run with the identically locked interpreter (`uv.lock` SHA-256 `d0f5f242…` identical) and
   `PYTHONPATH` pointing at the clone: 227 tests passed, ruff check passed, 129 files formatted,
   smoke passed, `scripts.build_mvp` verified, rebuilt `app/manifest.json` = `d7c8c554…` (byte-
   identical to the record), `git status` clean after rebuild, 6 JS tests passed; 39 s. GitHub's
   clean Ubuntu runner passed CI on the same commit:
   https://github.com/Elie1Z/EnaGIS/actions/runs/37861220385 (conclusion `success`). → F-03.
5. **Evidence ledger.** New read-only script `scripts/evidence_ledger.py` counted labels in the
   app's embedded data → `docs/audit/evidence-ledger.json`. 261 development nodes: OBSERVED 2,088,
   PREDICTED 0, ESTIMATED 744, INFERRED 782, UNKNOWN 562.
6. **UNKNOWN root causes** (read-only checks, commands in `docs/evidence-ledger.md`):
   - 72 nodes / 288 fields: StatCan durum component status `F` in 9 AB/SK reporting regions while
     "Wheat, all" is published. Province totals minus published regional durum give a residual
     of 100,097 t (SK, 5 regions) and 32,384 t (AB, 4 regions). Regional "Wheat, all" sums match
     province controls within 11 t. → avoidable by an interval rule (proposal, not a bug).
   - 2 nodes / 8 fields: `location_conflict` (geometry vs attribute coordinate differ by 176 m
     and 468 m); both coordinates fall in the same reporting region (4870 and 4703). → avoidable
     for region-level assignment (proposal).
   - 1 node / 5 fields: Delisle, Alliance Pulse Processors, source storage = 0 t. → correct.
   - 261 fields: no documented electrical capacity in any consumed open source. → irreducible
     with current open data.
7. **History scan.** Regex scan of `git log -p --all` for cloud keys, tokens, private keys and
   passwords: 0 hits. Phone-keyword scan: 0 hits. E-mail addresses: author commit address and two
   public institutional contacts (CGC statistics, PAMI). Largest blob 5.45 MB (`app/index.html`).
   `data/validation_private/` is ignored (`git check-ignore`). No restricted CGC PDFs tracked.
8. **Repo metadata.** GitHub API: public, `license: null`. 15 commits. Tag
   `preregister-phase4-canada-v1.1` → `948cf2fd…`, present on the remote.

## 2026-10-09 — Pass 2 (adjust)

9. F-01 fixed: `src/enagis/cli.py` restored with `git checkout`; `stress.py` moved to
   `scripts/sparse_data_stress.py`; protocol, report and write-up moved to `docs/proposals/`;
   stress panel and data removed from the app. `git diff --stat HEAD -- src configs uv.lock demo
   docs/audits data/manual docs/data docs/spec docs/decisions tests/fixtures docs/figures` → empty.
10. Stress report re-run with the same seed: identical numbers; `hashes.code` =
    `f2b1f09541c263a23c0e2a89798956ffc72070272e253b8eeab68d6b8bf4e978`, equal to
    `scientific_source_sha256` in `docs/audits/phase8.json`.
11. F-02: `python -m enagis.science run ... --output outputs/phase6-synthetic-audit --allow-fixture`
    then `verify` → status `verified`, 8 artifacts, `scientifically_ready_to_freeze: false`.
12. Proposals written: durum residual bounds (288 fields), location-conflict region rule
    (8 fields), sparse-data stress diagnostic + decline-to-rank rule. Nothing adopted.
13. Docs, LICENSE (MIT, matching the recorded scenario licence), LICENSE-DATA, templates and
    draft issues created; see `changes.md`. `findings.md` documentation counts corrected to
    partial 11 / missing 11 (counting error in the first write-up).
14. Presenter guide fixed: its three-minute path referenced the removed stress panel.

## 2026-10-09 — Pass 3 (re-audit)

15. Final checks on the working tree: `pytest` 230 passed; `ruff check` all passed;
    `ruff format --check` 168 files formatted; smoke OK; JS 6 passed; `build_mvp --verify`
    verified; `demo_preflight.mjs` 15/15; evidence ledger counts unchanged; 0 broken relative links.
16. App manifest after this pass: `acddb73ae1fdc730c15ab598a7b0b9d7155ed0fae1a713e5b16bc006ee84b613`.
17. Correction to entry 16: 12 edited text files had CRLF line endings (Python `write_text` on
    Windows), but `.gitattributes` stores `eol=lf`. A clean clone would have failed `verify-mvp`
    because the manifest hashed CRLF bytes. Converted them to LF and rebuilt. Final app manifest:
    `ed6d360ae53f38f97aca929f96e73df5adc9e5d82b71b7a42d192f70c9830648`. Re-checked: 230 tests
    passed, ruff clean, preflight 15/15, no CRLF in changed files.
18. Push: `git push -u origin audit/final-pass-2026-10-09` → `git ls-remote` shows
    `536590eed26d8ac74846709b567938f7e25421c3`. Branch used instead of a direct push to `main`;
    merging is a fast-forward left to the maintainer.
19. Clean room after (fresh clone of the pushed branch into `outputs/cleanroom-after`, locked
    interpreter workaround as in entry 4): 230 passed, ruff clean, 168 files formatted, smoke OK,
    `build_mvp --verify` verified, rebuild verified, `app/manifest.json` = `ed6d360a…`
    (byte-identical), `git status` clean after rebuild, `code_hash` = `f2b1f095…`, JS 6 passed; 28 s.
20. GitHub CI on `536590e`: https://github.com/Elie1Z/EnaGIS/actions/runs/37961988618 → `success`.
