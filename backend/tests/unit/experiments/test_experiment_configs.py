"""Pre-registered EXP-01…EXP-07 configs match docs/19 §4 (T-104)."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pytest

from roboprobe.core.settings.selection import ProbeDefaults
from roboprobe.experiments.planner import ComparabilityKey, load_design, plan
from roboprobe.scenario.hashing import canonical_json
from roboprobe.scenario.space import ScenarioSpace

pytestmark = pytest.mark.unit

_REPO = Path(__file__).resolve().parents[4]
_EXPERIMENTS = _REPO / "configs" / "experiments"
_HASH_LINE = re.compile(r"^# probe_preregistration_sha256: ([0-9a-f]{64})$", re.M)
_KEY = ComparabilityKey(
    space_version="abcdef123456",
    oracle_set_version="oracles-1",
    sut_config_hash="suthash00112233",
    backend_version="0.0.1",
    k2d_model_version="k2d-v1",
)

# strategies x seeds for the matrix in docs/19 §4.
_EXPECTED = {
    "exp01_k2d_main.yaml": (8 * 30, 200),
    "exp02_analytic.yaml": (8 * 50, 150),
    "exp02_branin.yaml": (8 * 50, 150),
    "exp03_ablation.yaml": (7 * 30, 200),
    "exp04_gazebo.yaml": (2 * 5, 80),
    "exp05_profiles.yaml": (2 * 3, 80),
    "exp06_gz_replay.yaml": (1 * 5, 1),
    "exp07_scalability.yaml": (2 * 30, 300),
    "exp07_scalability_d8.yaml": (2 * 30, 300),
    "exp07_scalability_noise2.yaml": (2 * 30, 300),
}


def _probe_hash() -> str:
    return hashlib.sha256(canonical_json(ProbeDefaults().model_dump())).hexdigest()


def test_configs_plan_to_the_documented_cell_counts() -> None:
    frozen = _probe_hash()
    for name, (cells, budget) in _EXPECTED.items():
        path = _EXPERIMENTS / name
        text = path.read_text(encoding="utf-8")
        match = _HASH_LINE.search(text)
        assert match is not None, name
        assert match.group(1) == frozen
        design = load_design(path)
        specs = plan(design, default_seeds=30, key=_KEY)
        assert len(specs) == cells, name
        assert {spec.budget for spec in specs} == {budget}
        assert len({spec.seed for spec in specs if spec.experiment_rep == 0}) == 1


def test_exp03_ablations_are_probe_param_overrides() -> None:
    design = load_design(_EXPERIMENTS / "exp03_ablation.yaml")
    labels = {variant.display_label: variant.params for variant in design.strategies}
    assert labels["PROBE-diversity"]["lambda_div"] == 0
    assert labels["PROBE-eps0"]["epsilon"] == 0
    assert labels["PROBE-boundary"]["weights"]["boundary"] == 0
    assert labels["PROBE-refine"]["weights"]["refine"] == 0


def test_exp06_is_a_replay_of_exp04() -> None:
    design = load_design(_EXPERIMENTS / "exp06_gz_replay.yaml")
    assert "exp04" in design.tags
    assert "replay" in design.tags
    assert design.seeds.count == 5
    assert "EXP-04" in (design.description or "")


def test_d8_and_noise_spaces_load() -> None:
    d8 = ScenarioSpace.from_yaml(
        _REPO / "configs/scenario_spaces/warehouse_v1_d8.yaml", base_dir=_REPO
    )
    assert d8.dim == 8
    noise = ScenarioSpace.from_yaml(
        _REPO / "configs/scenario_spaces/warehouse_v1_noise2.yaml", base_dir=_REPO
    )
    lidar = next(param for param in noise.parameters if param.id == "sensor.lidar_noise_std")
    assert lidar.high == pytest.approx(0.2)
