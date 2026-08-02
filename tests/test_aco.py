from __future__ import annotations

import random

import numpy as np
import pytest

from vrp.aco import run_aco, update_pheromone
from vrp.construction import build_ant_routes_optimized, build_ant_routes_original
from vrp.routes import validate_routes


def test_update_pheromone_evaporates_and_deposits_on_route_edges(distance_matrix):
    pheromone = np.full((4, 4), 1.0)
    np.fill_diagonal(pheromone, 0.0)

    routes = [[0, 1, 2, 0]]  # total distance 10 + 12 + 15 = 37
    updated = update_pheromone(pheromone, routes, distance_matrix, evaporation_rate=0.1)

    deposit = 1.0 / 37.0
    for from_node, to_node in [(0, 1), (1, 2), (2, 0)]:
        assert updated[from_node, to_node] == pytest.approx(0.9 + deposit)
        assert updated[to_node, from_node] == pytest.approx(0.9 + deposit)

    # Edges not on the route only evaporate.
    assert updated[0, 3] == pytest.approx(0.9)
    assert updated[1, 3] == pytest.approx(0.9)
    assert np.all(np.diag(updated) == 0.0)


def test_run_aco_produces_valid_routes_and_history(distance_matrix, demands, config):
    random.seed(config["random_seed"])
    np.random.seed(config["random_seed"])

    best_routes, history = run_aco(build_ant_routes_optimized, distance_matrix, distance_matrix, demands, config)

    assert validate_routes(best_routes, 3, distance_matrix, demands, config) is True
    assert list(history.columns) == ["loop", "best_distance", "best_cost", "loop_best_distance", "loop_best_cost"]
    assert len(history) == config["number_of_loops"]
    # best_cost is a running minimum, so it must never increase between loops.
    assert history["best_cost"].is_monotonic_decreasing or history["best_cost"].nunique() == 1 or (
        history["best_cost"].diff().dropna() <= 0
    ).all()


def test_run_aco_is_deterministic_given_same_seed(distance_matrix, demands, config):
    def run_once():
        random.seed(config["random_seed"])
        np.random.seed(config["random_seed"])
        return run_aco(build_ant_routes_optimized, distance_matrix, distance_matrix, demands, config)

    routes_a, history_a = run_once()
    routes_b, history_b = run_once()

    assert routes_a == routes_b
    assert history_a["best_cost"].tolist() == history_b["best_cost"].tolist()


def test_run_aco_optimized_and_original_style_agree(distance_matrix, distance_df, demands, config):
    random.seed(config["random_seed"])
    np.random.seed(config["random_seed"])
    optimized_routes, optimized_history = run_aco(
        build_ant_routes_optimized, distance_matrix, distance_matrix, demands, config
    )

    random.seed(config["random_seed"])
    np.random.seed(config["random_seed"])
    original_routes, original_history = run_aco(
        build_ant_routes_original, distance_df, distance_matrix, demands, config
    )

    assert optimized_routes == original_routes
    assert optimized_history["best_cost"].tolist() == original_history["best_cost"].tolist()
