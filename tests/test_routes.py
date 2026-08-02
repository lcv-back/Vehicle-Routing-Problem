from __future__ import annotations

import pytest

from vrp.routes import (
    explicit_route_distance,
    route_distance,
    route_duration,
    routes_total_cost,
    routes_total_distance,
    summarize_routes,
    validate_routes,
)


def test_route_distance_sums_edges(distance_matrix):
    route = [0, 1, 2, 0]  # Kho -> A -> B -> Kho
    assert route_distance(route, distance_matrix) == pytest.approx(10 + 12 + 15)


def test_explicit_route_distance_matches_route_distance(distance_matrix):
    route = [0, 1, 2, 0]
    assert explicit_route_distance(route, distance_matrix) == route_distance(route, distance_matrix)


def test_explicit_route_distance_rejects_too_short_route(distance_matrix):
    with pytest.raises(ValueError):
        explicit_route_distance([0], distance_matrix)


def test_route_duration_includes_service_time(distance_matrix, config):
    route = [0, 1, 2, 0]
    distance = route_distance(route, distance_matrix)
    expected = distance / config["speed"] + 2 * config["service_hours"]
    assert route_duration(route, distance_matrix, config["speed"], config["service_hours"]) == pytest.approx(expected)


def test_routes_total_distance_and_cost(distance_matrix, config):
    routes = [[0, 1, 2, 0], [0, 3, 0]]
    total_distance = routes_total_distance(routes, distance_matrix)
    assert total_distance == pytest.approx((10 + 12 + 15) + (20 + 20))

    total_cost = routes_total_cost(routes, distance_matrix, config["fixed_cost"], config["transport_cost"])
    assert total_cost == pytest.approx(len(routes) * config["fixed_cost"] + total_distance * config["transport_cost"])


def test_summarize_routes_columns_and_values(distance_matrix, demands, node_names, config):
    routes = [[0, 1, 2, 0]]
    summary = summarize_routes(routes, distance_matrix, demands, node_names, config)

    assert list(summary.columns) == ["route", "customers", "load", "distance", "duration", "cost", "path"]
    row = summary.iloc[0]
    assert row["route"] == 1
    assert row["customers"] == 2
    assert row["load"] == pytest.approx(10.0)
    assert row["path"] == "Kho -> A -> B -> Kho"


def test_validate_routes_accepts_full_feasible_coverage(distance_matrix, demands, config):
    routes = [[0, 1, 2, 0], [0, 3, 0]]
    assert validate_routes(routes, 3, distance_matrix, demands, config) is True


def test_validate_routes_rejects_capacity_violation(distance_matrix, demands, config):
    routes = [[0, 1, 2, 3, 0]]  # load = 15 > capacity 10
    with pytest.raises(ValueError, match="exceeds capacity"):
        validate_routes(routes, 3, distance_matrix, demands, config)


def test_validate_routes_rejects_duration_violation(distance_matrix, demands, config):
    tight_config = {**config, "max_duration": 0.01}
    routes = [[0, 1, 2, 0], [0, 3, 0]]
    with pytest.raises(ValueError, match="exceeds duration"):
        validate_routes(routes, 3, distance_matrix, demands, tight_config)


def test_validate_routes_rejects_missing_customers(distance_matrix, demands, config):
    routes = [[0, 1, 0]]  # customers 2 and 3 never visited
    with pytest.raises(ValueError, match="Invalid customer coverage"):
        validate_routes(routes, 3, distance_matrix, demands, config)


def test_validate_routes_rejects_duplicate_visits(distance_matrix, demands, config):
    routes = [[0, 1, 0], [0, 1, 0], [0, 3, 0]]  # customer 1 visited twice
    with pytest.raises(ValueError, match="visited more than once"):
        validate_routes(routes, 3, distance_matrix, demands, config)


def test_validate_routes_rejects_route_not_starting_at_depot(distance_matrix, demands, config):
    routes = [[1, 2, 0]]
    with pytest.raises(ValueError, match="must start and end at depot"):
        validate_routes(routes, 3, distance_matrix, demands, config)


def test_validate_routes_rejects_depot_inside_route(distance_matrix, demands, config):
    routes = [[0, 1, 0, 2, 0]]
    with pytest.raises(ValueError, match="contains depot inside"):
        validate_routes(routes, 3, distance_matrix, demands, config)


def test_validate_routes_rejects_empty_routes(distance_matrix, demands, config):
    with pytest.raises(ValueError, match="At least one route is required"):
        validate_routes([], 3, distance_matrix, demands, config)
