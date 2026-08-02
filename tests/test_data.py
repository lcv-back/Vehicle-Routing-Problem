from __future__ import annotations

import pandas as pd
import pytest

from vrp.data import load_inputs

NODE_NAMES = ["Kho", "A", "B", "C"]

DISTANCE_MATRIX = [
    [0.0, 10.0, 15.0, 20.0],
    [10.0, 0.0, 12.0, 18.0],
    [15.0, 12.0, 0.0, 8.0],
    [20.0, 18.0, 8.0, 0.0],
]


def _write_data_xlsx(path):
    df = pd.DataFrame(
        {
            "Customer_Name": ["A", "B", "C"],
            "Capacity": [5.0, 5.0, 5.0],
        }
    )
    df.to_excel(path, index=False)


def _write_distance_xlsx(path, node_names=NODE_NAMES, matrix=DISTANCE_MATRIX):
    df = pd.DataFrame(matrix, columns=node_names)
    df.insert(0, "Name", node_names)
    df.to_excel(path, index=False)


def test_load_inputs_happy_path(tmp_path):
    data_path = tmp_path / "data.xlsx"
    distance_path = tmp_path / "distance-matrix.xlsx"
    _write_data_xlsx(data_path)
    _write_distance_xlsx(distance_path)

    config = {"data_path": str(data_path), "distance_path": str(distance_path), "depot_name": "Kho"}
    instance = load_inputs(config)

    assert instance.node_names == NODE_NAMES
    assert instance.distance_matrix.shape == (4, 4)
    assert instance.demands.tolist() == [0.0, 5.0, 5.0, 5.0]
    assert instance.node_to_index == {"Kho": 0, "A": 1, "B": 2, "C": 3}


def test_load_inputs_raises_on_missing_customer_column(tmp_path):
    data_path = tmp_path / "data.xlsx"
    distance_path = tmp_path / "distance-matrix.xlsx"
    pd.DataFrame({"Customer_Name": ["A"]}).to_excel(data_path, index=False)  # missing Capacity
    _write_distance_xlsx(distance_path)

    config = {"data_path": str(data_path), "distance_path": str(distance_path), "depot_name": "Kho"}
    with pytest.raises(ValueError, match="Missing required customer columns"):
        load_inputs(config)


def test_load_inputs_raises_on_distance_matrix_mismatch(tmp_path):
    data_path = tmp_path / "data.xlsx"
    distance_path = tmp_path / "distance-matrix.xlsx"
    _write_data_xlsx(data_path)
    # Distance matrix is missing customer "C".
    _write_distance_xlsx(distance_path, node_names=["Kho", "A", "B"], matrix=[[0, 10, 15], [10, 0, 12], [15, 12, 0]])

    config = {"data_path": str(data_path), "distance_path": str(distance_path), "depot_name": "Kho"}
    with pytest.raises(ValueError, match="Distance matrix mismatch"):
        load_inputs(config)
