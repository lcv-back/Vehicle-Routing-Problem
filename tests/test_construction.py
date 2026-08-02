from __future__ import annotations

import random

import numpy as np
import pytest

from vrp.construction import (
    build_ant_routes_optimized,
    build_ant_routes_original,
    build_greedy_routes,
)
from vrp.routes import validate_routes


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
