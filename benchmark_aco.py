"""Benchmark ACO runtime and solution quality across (ants, loops) presets.

Runs the optimized ACO solver once per preset, then writes a comparison
table (`benchmark_summary.csv`) and a convergence chart
(`benchmark_convergence.png`) to the configured output directory, so the
runtime/quality tradeoff of ACO parameters is visible without editing
notebooks by hand.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from time import perf_counter

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None
import pandas as pd

from vrp.aco import run_aco
from vrp.config import load_config
from vrp.construction import build_ant_routes_optimized, build_greedy_routes
from vrp.data import load_inputs
from vrp.routes import routes_total_cost, routes_total_distance

DEFAULT_PRESETS = [(10, 20), (20, 50), (30, 80)]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Benchmark ACO runtime and solution quality across (ants, loops) presets."
    )
    parser.add_argument("--config", default="config/aco_config.json")
    parser.add_argument(
        "--presets",
        default=None,
        help=(
            'Comma-separated ants x loops presets, e.g. "10x20,20x50,30x80". '
            "Defaults to 10x20, 20x50, 30x80."
        ),
    )
    return parser.parse_args()


def parse_presets(raw: str | None) -> list[tuple[int, int]]:
    if raw is None:
        return list(DEFAULT_PRESETS)

    presets = []
    for chunk in raw.split(","):
        chunk = chunk.strip().lower()
        if "x" not in chunk:
            raise ValueError(f"Invalid preset {chunk!r}, expected format like '20x50'.")
        ants_str, loops_str = chunk.split("x", 1)
        presets.append((int(ants_str), int(loops_str)))
    return presets


def main() -> None:
    args = parse_args()
    base_config = load_config(args.config)
    instance = load_inputs(base_config)

    greedy_routes = build_greedy_routes(instance.distance_matrix, instance.demands, base_config)
    greedy_cost = routes_total_cost(
        greedy_routes, instance.distance_matrix, base_config["fixed_cost"], base_config["transport_cost"]
    )

    presets = parse_presets(args.presets)
    rows = []
    histories: dict[str, pd.DataFrame] = {}

    for ants, loops in presets:
        run_config = {**base_config, "number_of_ants": ants, "number_of_loops": loops}
        start = perf_counter()
        routes, history = run_aco(
            build_ant_routes_optimized,
            instance.distance_matrix,
            instance.distance_matrix,
            instance.demands,
            run_config,
        )
        runtime = perf_counter() - start

        total_distance = routes_total_distance(routes, instance.distance_matrix)
        total_cost = routes_total_cost(
            routes, instance.distance_matrix, base_config["fixed_cost"], base_config["transport_cost"]
        )
        improvement = ((greedy_cost - total_cost) / greedy_cost) * 100 if greedy_cost else 0.0

        label = f"{ants}ants_{loops}loops"
        rows.append(
            {
                "preset": label,
                "number_of_ants": ants,
                "number_of_loops": loops,
                "routes": len(routes),
                "total_distance": total_distance,
                "total_cost": total_cost,
                "improvement_vs_greedy_%": improvement,
                "runtime_seconds": runtime,
            }
        )
        histories[label] = history
        print(f"[{label}] routes={len(routes)} cost={total_cost:,.0f} runtime={runtime:.2f}s")

    summary_df = pd.DataFrame(rows)

    output_dir = Path(base_config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "benchmark_summary.csv"
    summary_df.to_csv(summary_path, index=False)
    print(f"Saved benchmark summary to {summary_path}")

    if plt is None:
        print("Matplotlib is not installed. Skipping convergence chart.")
        return

    fig, ax = plt.subplots(figsize=(9, 6))
    for label, history in histories.items():
        ax.plot(history["loop"], history["best_cost"], label=label)
    ax.set_title("ACO convergence by (ants, loops) preset")
    ax.set_xlabel("Loop")
    ax.set_ylabel("Best cost so far")
    ax.legend()
    ax.grid(True, alpha=0.3)

    chart_path = output_dir / "benchmark_convergence.png"
    fig.tight_layout()
    fig.savefig(chart_path, dpi=160, bbox_inches="tight")
    print(f"Saved convergence chart to {chart_path}")


if __name__ == "__main__":
    main()
