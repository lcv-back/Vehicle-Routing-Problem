from __future__ import annotations

import json

import pytest

from vrp.config import REQUIRED_CONFIG_KEYS, load_config

MINIMAL_CONFIG = {
    "data_path": "data.xlsx",
    "distance_path": "distance-matrix.xlsx",
    "depot_name": "Kho",
    "number_of_ants": 10,
    "number_of_loops": 5,
    "alpha": 1.0,
    "beta": 2.0,
    "evaporation_rate": 0.1,
    "vehicle_capacity": 2000.0,
    "max_duration": 48.0,
    "speed": 50.0,
    "fixed_cost": 1_000_000.0,
    "transport_cost": 4492.0,
}


def write_config(tmp_path, overrides=None):
    config = {**MINIMAL_CONFIG, **(overrides or {})}
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    return path


def test_load_config_applies_defaults(tmp_path):
    path = write_config(tmp_path)
    config = load_config(path)

    assert config["service_hours"] == 0.5
    assert config["output_dir"] == "results"
    assert config["random_seed"] == 42


def test_load_config_keeps_explicit_values(tmp_path):
    path = write_config(tmp_path, {"service_hours": 0.25, "output_dir": "out", "random_seed": 7})
    config = load_config(path)

    assert config["service_hours"] == 0.25
    assert config["output_dir"] == "out"
    assert config["random_seed"] == 7


def test_load_config_raises_on_missing_required_key(tmp_path):
    config = MINIMAL_CONFIG.copy()
    del config["alpha"]
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config), encoding="utf-8")

    with pytest.raises(ValueError, match="Missing ACO config keys"):
        load_config(path)


def test_required_config_keys_are_all_present_in_minimal_config():
    assert REQUIRED_CONFIG_KEYS.issubset(MINIMAL_CONFIG)
