"""Route utilities: distance/duration/cost calculations and validation.

Every route is a list of node indices starting and ending at the depot
(index 0), e.g. ``[0, 3, 7, 0]``.
"""

from __future__ import annotations

import math
from collections import Counter

import numpy as np
import pandas as pd

DEPOT_INDEX = 0
DISTANCE_TOLERANCE = 1e-9


def route_edges(route: list[int]) -> list[tuple[int, int]]:
    return list(zip(route[:-1], route[1:]))


def route_distance(route: list[int], distance_matrix: np.ndarray) -> float:
    return float(sum(distance_matrix[from_node, to_node] for from_node, to_node in route_edges(route)))


def explicit_route_distance(route: list[int], distance_matrix: np.ndarray) -> float:
    """Recompute distance from explicit legs, including depot start and depot return."""
    if len(route) < 2:
        raise ValueError("A route must contain at least a start and end node.")
    return float(sum(float(distance_matrix[from_node, to_node]) for from_node, to_node in route_edges(route)))


def route_duration(route: list[int], distance_matrix: np.ndarray, speed: float, service_hours: float) -> float:
    travel_time = route_distance(route, distance_matrix) / speed
    customer_count = max(len(route) - 2, 0)
    return float(travel_time + customer_count * service_hours)


def routes_total_distance(routes: list[list[int]], distance_matrix: np.ndarray) -> float:
    return float(sum(route_distance(route, distance_matrix) for route in routes))


def routes_total_cost(
    routes: list[list[int]],
    distance_matrix: np.ndarray,
    fixed_cost: float,
    transport_cost: float,
) -> float:
    total_distance = routes_total_distance(routes, distance_matrix)
    return float(len(routes) * fixed_cost + total_distance * transport_cost)


def summarize_routes(
    routes: list[list[int]],
    distance_matrix: np.ndarray,
    demands: np.ndarray,
    node_names: list[str],
    config: dict,
) -> pd.DataFrame:
    rows = []
    for route_index, route in enumerate(routes, start=1):
        customer_indices = route[1:-1]
        distance = route_distance(route, distance_matrix)
        duration = route_duration(route, distance_matrix, config["speed"], config["service_hours"])
        load = float(demands[customer_indices].sum()) if customer_indices else 0.0
        rows.append(
            {
                "route": route_index,
                "customers": len(customer_indices),
                "load": load,
                "distance": distance,
                "duration": duration,
                "cost": config["fixed_cost"] + distance * config["transport_cost"],
                "path": " -> ".join(node_names[i] for i in route),
            }
        )
    return pd.DataFrame(rows)


def validate_route_shape(route: list[int], route_index: int, node_count: int) -> None:
    if len(route) < 3:
        raise ValueError(f"Route {route_index} must include depot, at least one customer, and depot return")
    if route[0] != DEPOT_INDEX or route[-1] != DEPOT_INDEX:
        raise ValueError(f"Route {route_index} must start and end at depot index {DEPOT_INDEX}")
    if DEPOT_INDEX in route[1:-1]:
        raise ValueError(f"Route {route_index} contains depot inside the customer sequence")

    invalid_nodes = [
        node for node in route if not isinstance(node, (int, np.integer)) or node < 0 or node >= node_count
    ]
    if invalid_nodes:
        raise ValueError(f"Route {route_index} contains invalid node indices: {invalid_nodes}")


def validate_route_distances(route: list[int], route_index: int, distance_matrix: np.ndarray) -> None:
    for from_node, to_node in route_edges(route):
        leg_distance = float(distance_matrix[from_node, to_node])
        if not np.isfinite(leg_distance):
            raise ValueError(f"Route {route_index} has a non-finite distance leg: {from_node}->{to_node}")
        if leg_distance < 0:
            raise ValueError(f"Route {route_index} has a negative distance leg: {from_node}->{to_node}")

    calculated_distance = route_distance(route, distance_matrix)
    explicit_distance = explicit_route_distance(route, distance_matrix)
    if not math.isclose(calculated_distance, explicit_distance, rel_tol=0, abs_tol=DISTANCE_TOLERANCE):
        raise ValueError(
            f"Route {route_index} distance mismatch: calculated={calculated_distance}, explicit={explicit_distance}"
        )


def validate_routes(
    routes: list[list[int]],
    customer_count: int,
    distance_matrix: np.ndarray,
    demands: np.ndarray,
    config: dict,
) -> bool:
    if not routes:
        raise ValueError("At least one route is required")

    node_count = customer_count + 1
    expected_customers = set(range(1, customer_count + 1))
    visited: list[int] = []

    for route_index, route in enumerate(routes, start=1):
        validate_route_shape(route, route_index, node_count)
        validate_route_distances(route, route_index, distance_matrix)

        customer_indices = route[1:-1]
        visited.extend(customer_indices)

        load = float(demands[customer_indices].sum())
        duration = route_duration(route, distance_matrix, config["speed"], config["service_hours"])

        if load > config["vehicle_capacity"] + DISTANCE_TOLERANCE:
            raise ValueError(f"Route {route_index} exceeds capacity: {load}")
        if duration > config["max_duration"] + DISTANCE_TOLERANCE:
            raise ValueError(f"Route {route_index} exceeds duration: {duration}")

    visit_counts = Counter(visited)
    duplicates = sorted(node for node, count in visit_counts.items() if count > 1)
    missing = sorted(expected_customers.difference(visit_counts))
    extra = sorted(set(visit_counts).difference(expected_customers))

    if duplicates:
        raise ValueError(f"Customers visited more than once: {duplicates}")
    if missing or extra:
        raise ValueError(f"Invalid customer coverage. Missing={missing}, extra={extra}")

    return True
