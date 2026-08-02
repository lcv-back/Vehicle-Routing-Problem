"""Shared fixtures for vrp tests.

The fixture instance is a small 4-node problem (1 depot + 3 customers) with
capacity tight enough to force the vehicle to split into more than one
route, so route-splitting and constraint logic get exercised.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

NODE_NAMES = ["Kho", "A", "B", "C"]

DISTANCE_MATRIX = np.array(
    [
        [0.0, 10.0, 15.0, 20.0],
        [10.0, 0.0, 12.0, 18.0],
        [15.0, 12.0, 0.0, 8.0],
        [20.0, 18.0, 8.0, 0.0],
    ],
    dtype=float,
)

DEMANDS = np.array([0.0, 5.0, 5.0, 5.0])


@pytest.fixture
def distance_matrix() -> np.ndarray:
    return DISTANCE_MATRIX.copy()


@pytest.fixture
def distance_df() -> pd.DataFrame:
    return pd.DataFrame(DISTANCE_MATRIX, index=NODE_NAMES, columns=NODE_NAMES)


@pytest.fixture
def demands() -> np.ndarray:
    return DEMANDS.copy()


@pytest.fixture
def node_names() -> list[str]:
    return list(NODE_NAMES)


@pytest.fixture
def config() -> dict:
    return {
        "depot_name": "Kho",
        "speed": 50.0,
        "service_hours": 0.1,
        "vehicle_capacity": 10.0,
        "max_duration": 100.0,
        "fixed_cost": 100.0,
        "transport_cost": 1.0,
        "alpha": 1.0,
        "beta": 2.0,
        "evaporation_rate": 0.1,
        "number_of_ants": 5,
        "number_of_loops": 3,
        "random_seed": 42,
    }
