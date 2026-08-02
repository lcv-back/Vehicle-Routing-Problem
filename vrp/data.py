"""Load and validate VRP input data: customers, demands, and distance matrix."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ProblemInstance:
    customers_df: pd.DataFrame
    distance_df: pd.DataFrame
    distance_matrix: np.ndarray
    demands: np.ndarray
    node_names: list[str]
    node_to_index: dict[str, int]


def load_inputs(config: dict) -> ProblemInstance:
    """Load customers and distance matrix from the paths in config.

    Node index 0 is always the depot. Every other index maps 1:1 to a row in
    the customers data, in file order.
    """
    customers_df = pd.read_excel(config["data_path"])
    raw_distance_df = pd.read_excel(config["distance_path"])

    required_columns = {"Customer_Name", "Capacity"}
    missing_columns = required_columns.difference(customers_df.columns)
    if missing_columns:
        raise ValueError(f"Missing required customer columns: {sorted(missing_columns)}")

    customers_df = customers_df.dropna(subset=["Customer_Name"]).copy()
    customers_df["Customer_Name"] = customers_df["Customer_Name"].astype(str)
    customers_df["Capacity"] = customers_df["Capacity"].astype(float)

    node_names = [config["depot_name"]] + customers_df["Customer_Name"].tolist()
    distance_df = raw_distance_df.set_index(raw_distance_df.columns[0])

    missing_rows = [name for name in node_names if name not in distance_df.index]
    missing_cols = [name for name in node_names if name not in distance_df.columns]
    if missing_rows or missing_cols:
        raise ValueError(
            f"Distance matrix mismatch. Missing rows={missing_rows}, missing columns={missing_cols}"
        )

    distance_df = distance_df.loc[node_names, node_names].astype(float)
    distance_matrix = distance_df.to_numpy(dtype=float)
    demands = np.array([0.0] + customers_df["Capacity"].tolist(), dtype=float)
    node_to_index = {name: index for index, name in enumerate(node_names)}

    return ProblemInstance(
        customers_df=customers_df,
        distance_df=distance_df,
        distance_matrix=distance_matrix,
        demands=demands,
        node_names=node_names,
        node_to_index=node_to_index,
    )
