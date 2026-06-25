# Branch: feature/result-comparison-visualizations

## Goal

This branch implements result comparison and visualization output for the
optimized VRP/ACO notebook.

## What Was Added

### Result Comparison

`optimized-data-processing.ipynb` compares:

- greedy baseline;
- original-style ACO;
- optimized ACO.

The comparison table includes:

- total distance;
- total cost;
- number of routes/vehicles;
- runtime;
- improvement percentage versus the greedy baseline.

The table is saved to:

```text
results/result_comparison.csv
```

### Route Summary Table

The optimized ACO route summary includes:

- route number;
- number of customers;
- route load;
- route distance;
- route duration;
- route cost;
- full route path.

The table is saved to:

```text
results/optimized_route_summary.csv
```

### Visualizations

The notebook keeps the cost-per-loop chart and adds:

- distance-per-loop chart;
- convergence chart;
- route distance summary chart.

If `matplotlib` is installed, the combined chart is saved to:

```text
results/aco_convergence_charts.png
```

If `matplotlib` is not installed, the notebook prints a clear install message
and still produces the CSV result tables.

### Optional Route Map

The notebook now checks whether the dataset contains numeric latitude and
longitude columns. If usable coordinates exist, it writes:

```text
results/optimized_route_map.html
```

If coordinates are not usable, it writes:

```text
results/route_map_status.txt
```

The current dataset uses address text in `Coordinates Valid`, so the route map
is skipped safely instead of guessing inaccurate coordinates.

## Configuration

The output directory is configured in:

```text
config/aco_config.json
```

Default:

```json
{
  "output_dir": "results"
}
```

## Why This Matters

The optimization result is easier to review when the notebook provides a small
comparison table and saved artifacts. Reviewers can compare methods without
reading raw notebook variables or rerunning every chart manually.
