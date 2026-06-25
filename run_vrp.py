"""Run a local Vehicle Routing Problem baseline from the project spreadsheets.

This script intentionally avoids Colab and Google Drive paths. It loads the
local Excel files, validates that all customers exist in the distance matrix,
and computes a nearest-neighbor route baseline with capacity and duration
constraints.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


DEPOT_NAME = "Kho"


@dataclass(frozen=True)
class Customer:
    name: str
    capacity: float


@dataclass(frozen=True)
class Route:
    customers: list[str]
    load: float
    distance: float
    duration: float
    cost: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a reproducible local VRP nearest-neighbor baseline."
    )
    parser.add_argument("--data", default="data.xlsx", help="Customer data workbook.")
    parser.add_argument(
        "--distance",
        default="distance-matrix.xlsx",
        help="Distance matrix workbook.",
    )
    parser.add_argument("--vehicle-capacity", type=float, default=2000)
    parser.add_argument("--max-duration", type=float, default=48)
    parser.add_argument("--speed", type=float, default=50, help="Average speed in km/h.")
    parser.add_argument(
        "--service-hours",
        type=float,
        default=0.5,
        help="Service time added for each customer.",
    )
    parser.add_argument("--fixed-cost", type=float, default=1_000_000)
    parser.add_argument("--transport-cost", type=float, default=4492)
    return parser.parse_args()


def load_customers(path: Path) -> list[Customer]:
    df = pd.read_excel(path)
    required_columns = {"Customer_Name", "Capacity"}
    missing = required_columns.difference(df.columns)
    if missing:
        raise ValueError(f"{path} is missing required columns: {sorted(missing)}")

    rows = df[["Customer_Name", "Capacity"]].dropna(subset=["Customer_Name"])
    customers = [
        Customer(str(row.Customer_Name), float(row.Capacity))
        for row in rows.itertuples(index=False)
    ]
    if not customers:
        raise ValueError(f"{path} does not contain any customers.")
    return customers


def load_distance_matrix(path: Path, customers: list[Customer]) -> pd.DataFrame:
    df = pd.read_excel(path)
    name_column = df.columns[0]
    matrix = df.set_index(name_column)

    expected_names = [DEPOT_NAME] + [customer.name for customer in customers]
    missing_rows = [name for name in expected_names if name not in matrix.index]
    missing_columns = [name for name in expected_names if name not in matrix.columns]
    if missing_rows or missing_columns:
        problems = []
        if missing_rows:
            problems.append(f"missing rows: {missing_rows}")
        if missing_columns:
            problems.append(f"missing columns: {missing_columns}")
        raise ValueError(f"{path} does not match customer data; " + "; ".join(problems))

    return matrix.loc[expected_names, expected_names].astype(float)


def travel_hours(distance_km: float, speed: float) -> float:
    if speed <= 0:
        raise ValueError("speed must be greater than zero.")
    return distance_km / speed


def build_nearest_neighbor_routes(
    customers: list[Customer],
    distances: pd.DataFrame,
    vehicle_capacity: float,
    max_duration: float,
    speed: float,
    service_hours: float,
    fixed_cost: float,
    transport_cost: float,
) -> list[Route]:
    demand_by_customer = {customer.name: customer.capacity for customer in customers}
    oversized = [
        name for name, demand in demand_by_customer.items() if demand > vehicle_capacity
    ]
    if oversized:
        raise ValueError(
            "Customers exceed vehicle capacity and cannot be routed: "
            + ", ".join(oversized)
        )

    unvisited = set(demand_by_customer)
    routes: list[Route] = []

    while unvisited:
        current = DEPOT_NAME
        route_customers: list[str] = []
        route_load = 0.0
        route_distance = 0.0
        route_duration = 0.0

        while True:
            feasible: list[tuple[float, str]] = []
            for candidate in unvisited:
                next_distance = float(distances.loc[current, candidate])
                return_distance = float(distances.loc[candidate, DEPOT_NAME])
                projected_load = route_load + demand_by_customer[candidate]
                projected_duration = (
                    route_duration
                    + travel_hours(next_distance, speed)
                    + service_hours
                    + travel_hours(return_distance, speed)
                )

                if (
                    projected_load <= vehicle_capacity
                    and projected_duration <= max_duration
                ):
                    feasible.append((next_distance, candidate))

            if not feasible:
                break

            leg_distance, selected = min(feasible)
            unvisited.remove(selected)
            route_customers.append(selected)
            route_load += demand_by_customer[selected]
            route_distance += leg_distance
            route_duration += travel_hours(leg_distance, speed) + service_hours
            current = selected

        if not route_customers:
            raise ValueError(
                "No feasible customer could be assigned. Check max duration settings."
            )

        return_to_depot = float(distances.loc[current, DEPOT_NAME])
        route_distance += return_to_depot
        route_duration += travel_hours(return_to_depot, speed)
        routes.append(
            Route(
                customers=route_customers,
                load=route_load,
                distance=route_distance,
                duration=route_duration,
                cost=fixed_cost + route_distance * transport_cost,
            )
        )

    return routes


def print_summary(routes: list[Route]) -> None:
    total_distance = sum(route.distance for route in routes)
    total_cost = sum(route.cost for route in routes)
    print(f"Routes: {len(routes)}")
    print(f"Total distance: {total_distance:,.2f} km")
    print(f"Total cost: {total_cost:,.0f}")
    print()

    for index, route in enumerate(routes, start=1):
        stops = " -> ".join([DEPOT_NAME] + route.customers + [DEPOT_NAME])
        print(f"Route {index}")
        print(f"  Stops: {stops}")
        print(f"  Load: {route.load:,.2f}")
        print(f"  Distance: {route.distance:,.2f} km")
        print(f"  Duration: {route.duration:,.2f} hours")
        print(f"  Cost: {route.cost:,.0f}")


def main() -> None:
    args = parse_args()
    customers = load_customers(Path(args.data))
    distances = load_distance_matrix(Path(args.distance), customers)
    routes = build_nearest_neighbor_routes(
        customers=customers,
        distances=distances,
        vehicle_capacity=args.vehicle_capacity,
        max_duration=args.max_duration,
        speed=args.speed,
        service_hours=args.service_hours,
        fixed_cost=args.fixed_cost,
        transport_cost=args.transport_cost,
    )
    print_summary(routes)


if __name__ == "__main__":
    main()
