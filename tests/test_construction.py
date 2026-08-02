from __future__ import annotations

import random

import numpy as np
import pytest

from vrp.construction import (
    build_ant_routes_optimized,
    build_ant_routes_original,
    build_greedy_routes,
    build_savings_routes,
)
from vrp.routes import routes_total_distance, validate_routes


def test_build_greedy_routes_matches_expected_nearest_neighbor_split(distance_matrix, demands, config):
    routes = build_greedy_routes(distance_matrix, demands, config)
    assert routes == [[0, 1, 2, 0], [0, 3, 0]]


def test_build_greedy_routes_output_is_valid(distance_matrix, demands, config):
    routes = build_greedy_routes(distance_matrix, demands, config)
    assert validate_routes(routes, 3, distance_matrix, demands, config) is True


def test_build_greedy_routes_raises_when_customer_exceeds_capacity(distance_matrix, config):
    oversized_demands = np.array([0.0, 15.0, 5.0, 5.0])  # customer A alone exceeds capacity 10
    with pytest.raises(ValueError, match="No feasible greedy route"):
        build_greedy_routes(distance_matrix, oversized_demands, config)


def test_build_savings_routes_merges_the_best_pair_first(distance_matrix, demands, config):
    # Savings(B, C) = 15 + 20 - 8 = 27 is the largest, so B and C should be
    # merged into one route while A is left on its own (merging A in would
    # push load to 15 > capacity 10).
    routes = build_savings_routes(distance_matrix, demands, config)
    assert routes == [[0, 1, 0], [0, 2, 3, 0]]


def test_build_savings_routes_output_is_valid(distance_matrix, demands, config):
    routes = build_savings_routes(distance_matrix, demands, config)
    assert validate_routes(routes, 3, distance_matrix, demands, config) is True


def test_build_savings_routes_beats_or_matches_greedy_distance(distance_matrix, demands, config):
    savings_routes = build_savings_routes(distance_matrix, demands, config)
    greedy_routes = build_greedy_routes(distance_matrix, demands, config)
    savings_distance = routes_total_distance(savings_routes, distance_matrix)
    greedy_distance = routes_total_distance(greedy_routes, distance_matrix)
    assert savings_distance <= greedy_distance


def test_build_savings_routes_skips_merges_that_violate_capacity(distance_matrix, demands, config):
    tight_config = {**config, "vehicle_capacity": 5.0}  # no two customers can share a route
    routes = build_savings_routes(distance_matrix, demands, tight_config)
    assert sorted(routes) == [[0, 1, 0], [0, 2, 0], [0, 3, 0]]


def test_build_savings_routes_raises_when_customer_exceeds_capacity(distance_matrix, config):
    oversized_demands = np.array([0.0, 15.0, 5.0, 5.0])
    with pytest.raises(ValueError, match="exceeds capacity"):
        build_savings_routes(distance_matrix, oversized_demands, config)


def test_build_ant_routes_optimized_output_is_valid(distance_matrix, demands, config):
    pheromone = np.ones_like(distance_matrix)
    np.fill_diagonal(pheromone, 0.0)
    random.seed(7)
    np.random.seed(7)
    routes = build_ant_routes_optimized(distance_matrix, demands, pheromone, config)
    assert validate_routes(routes, 3, distance_matrix, demands, config) is True


def test_build_ant_routes_optimized_raises_when_customer_exceeds_capacity(distance_matrix, config):
    oversized_demands = np.array([0.0, 15.0, 5.0, 5.0])
    pheromone = np.ones_like(distance_matrix)
    np.fill_diagonal(pheromone, 0.0)
    random.seed(7)
    np.random.seed(7)
    with pytest.raises(ValueError, match="No feasible optimized ACO route"):
        build_ant_routes_optimized(distance_matrix, oversized_demands, pheromone, config)


def test_optimized_and_original_style_construction_agree(distance_matrix, distance_df, demands, config):
    """The NumPy-indexed and DataFrame-lookup constructors must select the
    same routes given identical inputs and random state -- the optimized
    version is a performance change, not a behavior change.
    """
    pheromone = np.ones_like(distance_matrix)
    np.fill_diagonal(pheromone, 0.0)

    random.seed(123)
    np.random.seed(123)
    optimized_routes = build_ant_routes_optimized(distance_matrix, demands, pheromone.copy(), config)

    random.seed(123)
    np.random.seed(123)
    original_routes = build_ant_routes_original(distance_df, demands, pheromone.copy(), config)

    assert optimized_routes == original_routes
