"""Load and validate ACO configuration."""

from __future__ import annotations

import json
import random
from pathlib import Path

import numpy as np

REQUIRED_CONFIG_KEYS = {
    "data_path",
    "distance_path",
    "depot_name",
    "number_of_ants",
    "number_of_loops",
    "alpha",
    "beta",
    "evaporation_rate",
    "vehicle_capacity",
    "max_duration",
    "speed",
    "fixed_cost",
    "transport_cost",
}


def load_config(path: str | Path, *, seed_random: bool = True) -> dict:
    """Load ACO configuration from JSON, apply defaults, and validate required keys."""
    config_path = Path(path)
    with config_path.open(encoding="utf-8") as config_file:
        config = json.load(config_file)

    missing_keys = REQUIRED_CONFIG_KEYS.difference(config)
    if missing_keys:
        raise ValueError(f"Missing ACO config keys: {sorted(missing_keys)}")

    config.setdefault("service_hours", 0.5)
    config.setdefault("output_dir", "results")
    config.setdefault("random_seed", 42)

    if seed_random:
        random.seed(config["random_seed"])
        np.random.seed(config["random_seed"])

    return config
