# Branch: feature/complete-optimized-notebook

## Goal

This branch implements the next optimization proposal:

- complete `optimized-data-processing.ipynb`;
- use a NumPy distance matrix throughout the optimized algorithm;
- move ACO parameters into one configuration block;
- add route correctness validation;
- add result comparison;
- add visualization cells.

## Problem Before The Change

The previous `optimized-data-processing.ipynb` improved a few isolated helper
functions, such as pheromone initialization and distance calculation, but it
did not include the downstream workflow needed for full comparison:

- route splitting by vehicle capacity;
- total cost calculation;
- full ACO loop evaluation;
- validation that each customer is visited exactly once;
- comparison between greedy, original-style ACO, and optimized ACO;
- cost, distance, and convergence charts.

The previous approach also still relied on repeated `DataFrame` lookups or
intermediate helper calls for distance access. That is one of the largest
performance bottlenecks when the customer count grows.

## Changes Applied

### 1. Rebuilt The Notebook As A Complete Workflow

The notebook now includes:

- Configuration
- Load dataset and build NumPy distance matrix
- Shared route utilities
- Greedy baseline
- Original-style ACO
- Optimized ACO with NumPy distance matrix
- Result comparison
- Route summary table
- Visualizations
- Notes for future route map

### 2. Added NumPy Distance Matrix Usage

`distance-matrix.xlsx` is read once and converted into:

```python
distance_matrix = distance_df.to_numpy(dtype=float)
```

The optimized algorithm accesses distances directly:

```python
distance_matrix[i, j]
```

This is much faster than repeated `DataFrame.loc` lookups.

### 3. Added ACO Configuration

The following parameters are now grouped in `CONFIG`:

- `number_of_ants`
- `number_of_loops`
- `alpha`
- `beta`
- `evaporation_rate`
- `vehicle_capacity`
- `max_duration`
- `speed`
- `service_hours`
- `fixed_cost`
- `transport_cost`
- `random_seed`

This makes experiments easier to reproduce and avoids scattered hard-coded
values.

### 4. Added Validation

The notebook now checks that:

- every customer is visited exactly once;
- no customer is missing;
- no customer is duplicated;
- every route starts and ends at the depot `Kho`;
- no route exceeds vehicle capacity;
- no route exceeds maximum duration.

### 5. Added Result Comparison

The notebook creates `comparison_df` with:

- total distance;
- total cost;
- number of routes/vehicles;
- runtime;
- improvement percentage versus the greedy baseline.

Current verification result:

| Method | Total distance | Total cost | Routes | Runtime | Improvement |
| --- | ---: | ---: | ---: | ---: | ---: |
| greedy_baseline | 11,209.79 | 80,354,376.68 | 30 | 0.0016s | 0.00% |
| original_style_aco | 9,775.28 | 71,910,557.76 | 28 | 81.44s | 10.51% |
| optimized_aco | 9,712.64 | 71,629,178.88 | 28 | 3.31s | 10.86% |

### 6. Added Visualizations

The notebook includes charts for:

- cost per loop;
- distance per loop;
- convergence;
- route distance by route.

If `matplotlib` is not installed, the notebook prints:

```bash
pip install -r requirements.txt
```

## Result

The notebook runs end-to-end for loading data, building routes, validating
solutions, and generating the comparison table.

In the current environment, `matplotlib` is not installed, so charts do not
render during verification. The visualization cell includes a clear fallback
message and will render once dependencies are installed from `requirements.txt`.

## Notes

This branch focuses on completing the optimized notebook. A route map was not
added because `Coordinates Valid` currently contains address text rather than
stable latitude/longitude coordinates.
