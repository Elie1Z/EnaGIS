"""Step 3: assert v1.1 frozen values and CV/model implementation agree with committed v1."""

import ast
import json
import subprocess
from pathlib import Path

BASELINE_COMMIT = "de21725"
ROOT = Path(__file__).resolve().parents[1]


def original(path):
    return subprocess.run(
        ["git", "show", f"{BASELINE_COMMIT}:{path}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    ).stdout


def run():
    v1 = json.loads(original("configs/experiments/phase4-canada-v1.json"))
    amended = json.loads((ROOT / "configs/experiments/phase4-canada-v1.1.json").read_bytes())
    keys = [
        "primary_top_fraction",
        "secondary_top_fraction",
        "bootstrap_draws",
        "seed",
        "keep_rule",
        "minimum_positive_units",
        "minimum_positive_blocks",
        "minimum_hindcast_groups",
        "logistic_c",
        "optimizer_tolerance",
        "optimizer_max_iterations",
        "confidence_level",
        "boyce_window_fraction",
        "boyce_resolution",
        "catchment_distance_m",
        "maximum_snap_distance_m",
    ]
    for key in keys:
        assert amended[key] == v1[key], f"STOP: frozen value changed: {key}"
    v1_doc = original("docs/spec/phase4-preregistration.md")
    assert "equal-weight mean CAR recall" in v1_doc
    assert "ceil(fraction × block size)" in v1_doc
    assert "ties use ascending stable CCS ID" in v1_doc
    assert "leave-one-CAR-out CV" in v1_doc
    assert amended["primary_metric"] == "equal_weight_mean_car_top_fraction_recall"
    assert amended["primary_budget"] == "ceil_fraction_times_block_size_stable_unit_id_ties"
    assert amended["cv_design"] == "leave_one_car_out"
    assert amended["logistic_regularization"] == "L2"
    old_source = original("src/enagis/siting.py")
    tree = ast.parse(old_source)
    old_parameters = next(
        {k.arg: k.value.value for k in call.keywords if isinstance(k.value, ast.Constant)}
        for call in ast.walk(tree)
        if isinstance(call, ast.Call)
        and isinstance(call.func, ast.Name)
        and call.func.id == "LogisticRegression"
    )
    assert amended["logistic_solver"] == old_parameters["solver"]
    assert amended["logistic_class_weight"] == old_parameters["class_weight"]
    current_source = (ROOT / "src/enagis/siting.py").read_text(encoding="utf-8")

    # The train/test CAR predicates must remain the original leave-one-block-out design.
    def predicates(source):
        return sorted(
            ast.dump(node, include_attributes=False)
            for node in ast.walk(ast.parse(source))
            if isinstance(node, ast.Compare)
            and isinstance(node.left, ast.Attribute)
            and node.left.attr == "block_id"
            and any(isinstance(c, ast.Name) and c.id == "block" for c in node.comparators)
        )

    assert predicates(current_source) == predicates(old_source)
    metrics = (ROOT / "src/enagis/experiment_metrics.py").read_text(encoding="utf-8")
    assert metrics == original("src/enagis/experiment_metrics.py"), (
        "STOP: metric implementation changed"
    )
    report = {
        "status": "PASS",
        "baseline_commit": BASELINE_COMMIT,
        "unchanged_config_values": {key: amended[key] for key in keys},
        "primary_metric_budget_cv_hyperparameters": "unchanged",
        "metric_implementation": "identical_to_v1",
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    run()
