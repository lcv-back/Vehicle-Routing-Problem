# Branch: feature/improve-algorithm-correctness

## Goal

This branch implements the correctness proposal for route validation.

The goal is to make route mistakes fail loudly instead of allowing incorrect
distance, cost, or customer coverage results to pass unnoticed.

## Changes Applied

### optimized-data-processing.ipynb

The notebook route validation was strengthened to check:

- every route contains depot, at least one customer, and depot return;
- every route starts and ends at depot index `0`;
- depot does not appear inside the customer sequence;
- all route node indices are valid;
- every distance leg is finite and nonnegative;
- route distance matches an explicit recomputation from each leg;
- every customer is visited exactly once;
- no customer is missing;
- no customer is duplicated;
- no route exceeds vehicle capacity;
- no route exceeds max duration.

This also makes depot start/end distance handling consistent because every
route is represented as:

```text
Depot -> customers -> Depot
```

### run_vrp.py

The local runner now validates generated routes before printing the summary.
It checks:

- every customer from `data.xlsx` is visited exactly once;
- no route exceeds vehicle capacity;
- no route exceeds max duration;
- route distance matches an explicit `Kho -> customers -> Kho` recomputation;
- route cost matches the recomputed distance and configured cost parameters.

## Why This Matters

VRP results are easy to miscount when depot return legs, capacity checks, or
customer coverage checks are spread across multiple functions. Centralized
validation makes the notebook and local runner safer to modify.

## Verification

Run:

```bash
python run_vrp.py
```

Also execute the code cells in `optimized-data-processing.ipynb`. Both should
complete without validation errors.
