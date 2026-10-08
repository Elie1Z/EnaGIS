import json
from copy import deepcopy
from pathlib import Path

import pytest

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "phase1.json"


def pytest_configure(config):
    # pytest creates basetemp itself, but its configured parent may not exist
    # on the first run after a clean checkout.
    if config.option.basetemp:
        Path(config.option.basetemp).resolve().parent.mkdir(parents=True, exist_ok=True)


@pytest.fixture
def raw_suite():
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


@pytest.fixture
def raw_bundle(raw_suite):
    return deepcopy(raw_suite["cases"][0]["bundle"])
