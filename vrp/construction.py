"""Route construction strategies: greedy baseline and ant-based construction."""

from __future__ import annotations

import random

import numpy as np
import pandas as pd

from vrp.routes import route_duration, validate_routes

DISTANCE_TOLERANCE = 1e-9


def build_savings_routes(distance_matrix: np.ndarray, demands: np.ndarray, config: dict) -> list[list[int]]:
    """Construct routes with the Clarke-Wright parallel savings heuristic.

    Starts with one route per customer, then repeatedly merges the pair of
    routes with the highest "savings" (the distance saved by visiting both
    customers on one route instead of two separate depot round trips),
    as long as the merge keeps both endpoints adjacent to the depot and
    respects capacity/duration constraints. This is a stronger baseline
    than nearest-neighbor because it reasons about pairs of customers
    instead of only the single nearest one.
    """
    customer_count = len(demands) - 1
    if customer_count == 0:
        raise ValueError("No customers to route.")

    routes: dict[int, list[int]] = {customer: [0, customer, 0] for customer in range(1, customer_count + 1)}
    route_id_of = {customer: customer for customer in range(1, customer_count + 1)}

    savings = []
    for i in range(1, customer_count + 1):
        for j in range(i + 1, customer_count + 1):
            saving = distance_matrix[0, i] + distance_matrix[0, j] - distance_matrix[i, j]
            if saving > 0:
                savings.append((saving, i, j))
    savings.sort(key=lambda item: item[0], reverse=True)

    for _, i, j in savings:
        route_i_id = route_id_of[i]
        route_j_id = route_id_of[j]
        if route_i_id == route_j_id:
            continue

        route_i = routes[route_i_id]
        route_j = routes[route_j_id]

        i_is_tail = route_i[-2] == i
        j_is_head = route_j[1] == j
        if not (i_is_tail and j_is_head):
            continue

        merged = route_i[:-1] + route_j[1:]
        merged_load = float(demands[merged[1:-1]].sum())
        if merged_load > config["vehicle_capacity"] + DISTANCE_TOLERANCE:
            continue
        merged_duration = route_duration(merged, distance_matrix, config["speed"], config["service_hours"])
        if merged_duration > config["max_duration"] + DISTANCE_TOLERANCE:
            continue

        routes[route_i_id] = merged
        del routes[route_j_id]
        for customer in merged[1:-1]:
            route_id_of[customer] = route_i_id

    final_routes = list(routes.values())
    validate_routes(final_routes, customer_count, distance_matrix, demands, config)
    return final_routes


def build_greedy_routes(distance_matrix: np.ndarray, demands: np.ndarray, config: dict) -> list[list[int]]:
    """Repeatedly select the nearest feasible next customer."""
    unvisited = set(range(1, len(demands)))
    routes: list[list[int]] = []

    while unvisited:
        route = [0]
        current = 0
        current_load = 0.0
        current_duration_without_return = 0.0

        while True:
            feasible = []
            for candidate in unvisited:
                next_distance = distance_matrix[current, candidate]
                return_distance = distance_matrix[candidate, 0]
                projected_load = current_load + demands[candidate]
                projected_duration = (
                    current_duration_without_return
                    + next_distance / config["speed"]
                    + config["service_hours"]
                    + return_distance / config["speed"]
                )

                if projected_load <= config["vehicle_capacity"] and projected_duration <= config["max_duration"]:
                    feasible.append((next_distance, candidate))

            if not feasible:
                break

            _, selected = min(feasible)
            route.append(selected)
            unvisited.remove(selected)
            current_duration_without_return += (
                distance_matrix[current, selected] / config["speed"] + config["service_hours"]
            )
            current_load += demands[selected]
            current = selected

        if len(route) == 1:
            raise ValueError("No feasible greedy route can be built. Check constraints.")

        route.append(0)
        routes.append(route)

    validate_routes(routes, len(demands) - 1, distance_matrix, demands, config)
    return routes


def get_distance_original(distance_df: pd.DataFrame, from_index: int, to_index: int) -> float:
    from_name = distance_df.index[from_index]
    to_name = distance_df.index[to_index]
    return float(distance_df.loc[from_name, to_name])


def build_ant_routes_original(
    distance_df: pd.DataFrame,
    demands: np.ndarray,
    pheromone: np.ndarray,
    config: dict,
) -> list[list[int]]:
    """Ant route construction that looks up distances via ``DataFrame.loc``.

    Kept alongside :func:`build_ant_routes_optimized` to benchmark the
    NumPy-indexed version against the original DataFrame-lookup style.
    """
    unvisited = set(range(1, len(demands)))
    routes: list[list[int]] = []

    while unvisited:
        route = [0]
        current = 0
        current_load = 0.0
        current_duration_without_return = 0.0

        while True:
            candidates = []
            weights = []

            for candidate in unvisited:
                next_distance = get_distance_original(distance_df, current, candidate)
                return_distance = get_distance_original(distance_df, candidate, 0)
                projected_load = current_load + demands[candidate]
                projected_duration = (
                    current_duration_without_return
                    + next_distance / config["speed"]
                    + config["service_hours"]
                    + return_distance / config["speed"]
                )

                if projected_load <= config["vehicle_capacity"] and projected_duration <= config["max_duration"]:
                    heuristic = 1.0 / max(next_distance, 1e-9)
                    weight = (pheromone[current, candidate] ** config["alpha"]) * (heuristic ** config["beta"])
                    candidates.append(candidate)
                    weights.append(weight)

            if not candidates:
                break

            weights_array = np.array(weights, dtype=float)
            if weights_array.sum() == 0 or not np.isfinite(weights_array).all():
                selected = random.choice(candidates)
            else:
                probabilities = weights_array / weights_array.sum()
                selected = int(np.random.choice(candidates, p=probabilities))

            route.append(selected)
            unvisited.remove(selected)
            current_duration_without_return += (
                get_distance_original(distance_df, current, selected) / config["speed"] + config["service_hours"]
            )
            current_load += demands[selected]
            current = selected

        if len(route) == 1:
            raise ValueError("No feasible original-style ACO route can be built. Check constraints.")

        route.append(0)
        routes.append(route)

    return routes


def build_ant_routes_optimized(
    distance_matrix: np.ndarray,
    demands: np.ndarray,
    pheromone: np.ndarray,
    config: dict,
) -> list[list[int]]:
    """Ant route construction using direct NumPy distance-matrix indexing."""
    unvisited = set(range(1, len(demands)))
    routes: list[list[int]] = []

    while unvisited:
        route = [0]
        current = 0
        current_load = 0.0
        current_duration_without_return = 0.0

        while True:
            candidates = np.array(sorted(unvisited), dtype=int)
            if candidates.size == 0:
                break

            next_distances = distance_matrix[current, candidates]
            return_distances = distance_matrix[candidates, 0]
            projected_loads = current_load + demands[candidates]
            projected_durations = (
                current_duration_without_return
                + next_distances / config["speed"]
                + config["service_hours"]
                + return_distances / config["speed"]
            )
            feasible_mask = (projected_loads <= config["vehicle_capacity"]) & (
                projected_durations <= config["max_duration"]
            )
            feasible_candidates = candidates[feasible_mask]

            if feasible_candidates.size == 0:
                break

            feasible_distances = distance_matrix[current, feasible_candidates]
            heuristic = 1.0 / np.maximum(feasible_distances, 1e-9)
            weights = (pheromone[current, feasible_candidates] ** config["alpha"]) * (
                heuristic ** config["beta"]
            )

            if weights.sum() == 0 or not np.isfinite(weights).all():
                selected = int(np.random.choice(feasible_candidates))
            else:
                probabilities = weights / weights.sum()
                selected = int(np.random.choice(feasible_candidates, p=probabilities))

            route.append(selected)
            unvisited.remove(selected)
            current_duration_without_return += (
                distance_matrix[current, selected] / config["speed"] + config["service_hours"]
            )
            current_load += demands[selected]
            current = selected

        if len(route) == 1:
            raise ValueError("No feasible optimized ACO route can be built. Check constraints.")

        route.append(0)
        routes.append(route)

    return routes
