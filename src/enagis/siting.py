"""Leave-one-CAR-out presence/background comparison. Never imports downstream allocation."""

import warnings

import numpy as np
from scipy.spatial.distance import cdist
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from enagis.experiment_metrics import block_intervals, continuous_boyce, top_recall

BASELINE_FEATURES = {
    "B0": "production_context",
    "B1": "euclidean_production",
    "B2": "accessible_production",
    "population": "population",
}


def fit_presence_background(x_train, presence_train, x_test, protocol):
    """Class 0 is a background sample including known presences, never an absence label."""
    protocol.require_approval()
    if not np.asarray(presence_train).any():
        raise ValueError("no training presence")
    scaler = StandardScaler().fit(np.log1p(x_train))
    background = scaler.transform(np.log1p(x_train))
    positives = background[np.asarray(presence_train, dtype=bool)]
    x = np.vstack([positives, background])
    sample_class = np.r_[np.ones(len(positives)), np.zeros(len(background))]
    model = LogisticRegression(
        C=protocol.logistic_c,
        solver="lbfgs",
        class_weight="balanced",
        max_iter=protocol.optimizer_max_iterations,
        tol=protocol.optimizer_tolerance,
        random_state=protocol.seed,
    )
    with warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        model.fit(x, sample_class)
    scores = model.decision_function(scaler.transform(np.log1p(x_test)))
    return scores, {
        "training_units": len(background),
        "training_presence_units": len(positives),
        "background_includes_presences": True,
        "scaler_mean": scaler.mean_.tolist(),
        "scaler_scale": scaler.scale_.tolist(),
        "coefficients": model.coef_[0].tolist(),
        "intercept": float(model.intercept_[0]),
        "iterations": int(model.n_iter_[0]),
        "score_definition": "Presence/background discrimination, "
        "not calibrated occurrence probability",
    }


def evaluate_siting(features, labels, units, protocol):
    protocol.require_approval()
    label_by_id = {r.unit_id: r for r in labels}
    unit_by_id = {u.unit_id: u for u in units}
    if len(label_by_id) != len(labels) or len(unit_by_id) != len(units):
        raise ValueError("duplicate study identity")
    if set(label_by_id) != set(unit_by_id) or {r.unit_id for r in features} != set(unit_by_id):
        raise ValueError("feature/label/unit join changes study universe")
    if len(features) != len(units) or any(
        r.province not in protocol.development_units for r in features
    ):
        raise ValueError("duplicate features or transfer rows entered development")
    if any(
        row.block_id != unit_by_id[row.unit_id].block_id
        or row.province != unit_by_id[row.unit_id].province
        for row in features
    ):
        raise ValueError("feature geography differs from the study unit")
    required = set(protocol.full_features) | set(BASELINE_FEATURES.values())
    rows, exclusions = [], []
    for row in sorted(features, key=lambda r: r.unit_id):
        missing = [
            key
            for key in sorted(required)
            if key not in row.features or row.features[key].value is None
        ]
        if missing or label_by_id[row.unit_id].status == "spatial_review_required":
            exclusions.append(
                {
                    "unit_id": row.unit_id,
                    "missing_features": missing,
                    "label_status": label_by_id[row.unit_id].status,
                }
            )
        else:
            rows.append(row)
    presence = np.asarray([label_by_id[r.unit_id].status == "documented_presence" for r in rows])
    blocks = sorted({r.block_id for r in rows})
    positive_blocks = {r.block_id for r, p in zip(rows, presence, strict=True) if p}
    report = {
        "cohort_units": len(rows),
        "documented_positive_units": int(presence.sum()),
        "positive_blocks": len(positive_blocks),
        "excluded_units": exclusions,
        "background_definition": "All training CCS including known presences; "
        "never verified negatives",
        "transfer_evaluated": False,
        "protocol_id": protocol.protocol_id,
    }
    if (
        presence.sum() < protocol.minimum_positive_units
        or len(positive_blocks) < protocol.minimum_positive_blocks
    ):
        return (
            report
            | {
                "status": "feasibility_failed",
                "decision": "not_testable",
                "reason": "Complete common cohort below preregistered positive/block minimum",
            },
            [],
            [],
        )
    predictions, fold_models, block_primary, block_secondary, block_boyce = [], [], [], [], []
    boyce_diagnostics = []
    for block in blocks:
        train = np.asarray([i for i, r in enumerate(rows) if r.block_id != block], dtype=int)
        test = np.asarray([i for i, r in enumerate(rows) if r.block_id == block], dtype=int)
        scores = {
            arm: np.asarray([rows[i].features[key].value for i in test])
            for arm, key in BASELINE_FEATURES.items()
        }
        training_positive_points = [
            unit_by_id[rows[i].unit_id].point_xy for i in train if presence[i]
        ]
        test_points = [unit_by_id[rows[i].unit_id].point_xy for i in test]
        scores["nearest_presence"] = -cdist(test_points, training_positive_points).min(axis=1)
        for name, keys in (
            ("base_model", protocol.base_features),
            ("full_model", protocol.full_features),
        ):
            x = np.asarray([[r.features[k].value for k in keys] for r in rows])
            scores[name], artifact = fit_presence_background(
                x[train], presence[train], x[test], protocol
            )
            fold_models.append(
                {
                    "held_out_block": block,
                    "arm": name,
                    "features": keys,
                    "training_blocks": sorted({rows[i].block_id for i in train}),
                    **artifact,
                }
            )
        ids = [rows[i].unit_id for i in test]
        primary, secondary, boyce = {"block_id": block}, {"block_id": block}, {"block_id": block}
        for arm, values in scores.items():
            primary[arm] = top_recall(ids, values, presence[test], protocol.primary_top_fraction)[
                "recall"
            ]
            secondary[arm] = top_recall(
                ids, values, presence[test], protocol.secondary_top_fraction
            )["recall"]
            boyce_result = continuous_boyce(
                values, presence[test], protocol.boyce_window_fraction, protocol.boyce_resolution
            )
            boyce[arm] = boyce_result["value"]
            boyce_diagnostics.append({"block_id": block, "arm": arm, **boyce_result})
            for i, score in zip(test, values, strict=True):
                predictions.append(
                    {
                        "unit_id": rows[i].unit_id,
                        "held_out_block": block,
                        "arm": arm,
                        "score": float(score),
                        "label": "PREDICTED" if "model" in arm else "ESTIMATED",
                        "documented_presence": bool(presence[i]),
                        "calibrated_probability": False,
                    }
                )
        block_primary.append(primary)
        block_secondary.append(secondary)
        block_boyce.append(boyce)
    inference = block_intervals(
        block_primary,
        protocol.comparison_arms,
        protocol.bootstrap_draws,
        protocol.confidence_level,
        protocol.seed,
    )
    report.update(
        status="evaluated",
        decision=inference["decision"],
        primary=inference,
        primary_top_fraction=protocol.primary_top_fraction,
        block_primary=block_primary,
        secondary_top_fraction=protocol.secondary_top_fraction,
        secondary=block_intervals(
            block_secondary,
            protocol.comparison_arms,
            protocol.bootstrap_draws,
            protocol.confidence_level,
            protocol.seed,
        ),
        boyce=block_intervals(
            block_boyce,
            protocol.comparison_arms,
            protocol.bootstrap_draws,
            protocol.confidence_level,
            protocol.seed,
        ),
        block_boyce=block_boyce,
        boyce_diagnostics=boyce_diagnostics,
        uncertainty_scope="Paired empirical block bootstrap conditional on this CV procedure;"
        " no retraining per bootstrap and no geographic transfer claim",
    )
    for diagnostic in ("secondary", "boyce"):
        report[diagnostic].pop("decision", None)
        report[diagnostic]["role"] = "Diagnostic only; cannot override primary keep/kill"
    return report, predictions, fold_models
