"""Run the real Ant Colony Optimization solver from the project spreadsheets.

Unlike `run_vrp.py` (a nearest-neighbor baseline), this runs the ACO
algorithm implemented in the `vrp` package, using `config/aco_config.json`
for algorithm parameters (ants, loops, alpha, beta, evaporation rate, and
the vehicle/route constraints).
"""

from __future__ import annotations

import argparse
from pathlib import Path
from time import perf_counter

from vrp.aco import run_aco
from vrp.config import load_config
from vrp.construction import build_ant_routes_optimized, build_greedy_routes
from vrp.data import load_inputs
from vrp.routes import routes_total_cost, routes_total_distance, summarize_routes


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the ACO solver using config/aco_config.json.")
    parser.add_argument(
        "--config",
        default="config/aco_config.json",
        help="Path to the ACO configuration JSON file.",
    )
    parser.add_argument(
        "--number-of-ants",
        type=int,
        default=None,
        help="Override number_of_ants from the config file.",
    )
    parser.add_argument(
        "--number-of-loops",
        type=int,
        default=None,
        help="Override number_of_loops from the config file.",
    )
    parser.add_argument(
        "--no-export",
        action="store_true",
        help="Skip writing result CSVs to the configured output directory.",
    )
    return parser.parse_args()


def print_summary(name: str, routes, distance_matrix, config, runtime: float) -> None:
    total_distance = routes_total_distance(routes, distance_matrix)
    total_cost = routes_total_cost(routes, distance_matrix, config["fixed_cost"], config["transport_cost"])
    print(f"[{name}]")
    print(f"  Routes: {len(routes)}")
    print(f"  Total distance: {total_distance:,.2f} km")
    print(f"  Total cost: {total_cost:,.0f}")
    print(f"  Runtime: {runtime:.2f}s")
    print()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    if args.number_of_ants is not None:
        config["number_of_ants"] = args.number_of_ants
    if args.number_of_loops is not None:
        config["number_of_loops"] = args.number_of_loops

    instance = load_inputs(config)

    start = perf_counter()
    greedy_routes = build_greedy_routes(instance.distance_matrix, instance.demands, config)
    greedy_runtime = perf_counter() - start
    print_summary("greedy_baseline", greedy_routes, instance.distance_matrix, config, greedy_runtime)

    start = perf_counter()
    aco_routes, history = run_aco(
        build_ant_routes_optimized,
        instance.distance_matrix,
        instance.distance_matrix,
        instance.demands,
        config,
    )
    aco_runtime = perf_counter() - start
    print_summary("aco", aco_routes, instance.distance_matrix, config, aco_runtime)

    greedy_cost = routes_total_cost(
        greedy_routes, instance.distance_matrix, config["fixed_cost"], config["transport_cost"]
    )
    aco_cost = routes_total_cost(aco_routes, instance.distance_matrix, config["fixed_cost"], config["transport_cost"])
    improvement = ((greedy_cost - aco_cost) / greedy_cost) * 100 if greedy_cost else 0.0
    print(f"ACO improvement vs greedy baseline: {improvement:.2f}%")

    if not args.no_export:
        output_dir = Path(config["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)

        summary = summarize_routes(
            aco_routes, instance.distance_matrix, instance.demands, instance.node_names, config
        )
        summary_path = output_dir / "aco_route_summary.csv"
        summary.to_csv(summary_path, index=False)

        history_path = output_dir / "aco_history.csv"
        history.to_csv(history_path, index=False)

        print(f"Saved route summary to {summary_path}")
        print(f"Saved loop history to {history_path}")


if __name__ == "__main__":
    main()
