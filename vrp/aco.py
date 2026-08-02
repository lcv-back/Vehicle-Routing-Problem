"""Ant Colony Optimization loop: pheromone update and the main run loop."""

from __future__ import annotations

import math
from typing import Callable

import numpy as np
import pandas as pd

from vrp.routes import routes_total_cost, routes_total_distance, validate_routes


def initial_pheromone_matrix(node_count: int, scoring_distance_matrix: np.ndarray) -> np.ndarray:
    initial_value = 1.0 / (node_count * max(scoring_distance_matrix.mean(), 1e-9))
    pheromone = np.full((node_count, node_count), initial_value, dtype=float)
    np.fill_diagonal(pheromone, 0.0)
    return pheromone


def update_pheromone(
    pheromone: np.ndarray,
    routes: list[list[int]],
    distance_matrix: np.ndarray,
    evaporation_rate: float,
) -> np.ndarray:
    pheromone *= 1.0 - evaporation_rate
    total_distance = routes_total_distance(routes, distance_matrix)
    deposit = 1.0 / max(total_distance, 1e-9)

    for route in routes:
        for from_node, to_node in zip(route[:-1], route[1:]):
            pheromone[from_node, to_node] += deposit
            pheromone[to_node, from_node] += deposit

    return pheromone


def run_aco(
    build_ant_routes: Callable[..., list[list[int]]],
    distance_source,
    scoring_distance_matrix: np.ndarray,
    demands: np.ndarray,
    config: dict,
) -> tuple[list[list[int]], pd.DataFrame]:
    """Run the ACO main loop and return the best routes found plus per-loop history.

    ``distance_source`` is passed through to ``build_ant_routes`` unchanged, so
    it can be either a NumPy distance matrix or a ``DataFrame``-based lookup,
    depending on which construction strategy is used. ``scoring_distance_matrix``
    is always the NumPy matrix and is used for cost/validation so both
    construction styles are scored consistently.
    """
    node_count = len(demands)
    pheromone = initial_pheromone_matrix(node_count, scoring_distance_matrix)

    best_routes = None
    best_cost = math.inf
    history = []

    for loop_index in range(1, config["number_of_loops"] + 1):
        loop_best_routes = None
        loop_best_cost = math.inf
        loop_best_distance = math.inf

        for _ in range(config["number_of_ants"]):
            routes = build_ant_routes(distance_source, demands, pheromone.copy(), config)
            validate_routes(routes, len(demands) - 1, scoring_distance_matrix, demands, config)
            total_distance = routes_total_distance(routes, scoring_distance_matrix)
            total_cost = routes_total_cost(
                routes,
                scoring_distance_matrix,
                config["fixed_cost"],
                config["transport_cost"],
            )

            if total_cost < loop_best_cost:
                loop_best_routes = routes
                loop_best_cost = total_cost
                loop_best_distance = total_distance

        pheromone = update_pheromone(
            pheromone,
            loop_best_routes,
            scoring_distance_matrix,
            config["evaporation_rate"],
        )

        if loop_best_cost < best_cost:
            best_routes = loop_best_routes
            best_cost = loop_best_cost

        history.append(
            {
                "loop": loop_index,
                "best_distance": routes_total_distance(best_routes, scoring_distance_matrix),
                "best_cost": best_cost,
                "loop_best_distance": loop_best_distance,
                "loop_best_cost": loop_best_cost,
            }
        )

    validate_routes(best_routes, len(demands) - 1, scoring_distance_matrix, demands, config)
    return best_routes, pd.DataFrame(history)
