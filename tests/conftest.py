import json
from copy import deepcopy
from pathlib import Path

import pytest

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "phase1.json"


@pytest.fixture
def raw_suite():
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


@pytest.fixture
def raw_bundle(raw_suite):
    return deepcopy(raw_suite["cases"][0]["bundle"])
