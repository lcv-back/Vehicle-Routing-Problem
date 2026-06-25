# Vehicle Routing Problem with Ant Colony Optimization

This project studies the Vehicle Routing Problem (VRP) for logistics route
planning and applies Ant Colony Optimization (ACO) to reduce delivery distance,
transportation cost, and manual planning effort.

## Problem Overview

Route planning is an important logistics problem because transportation cost,
delivery time, and vehicle utilization all depend on the quality of the route.
In this project, the target problem is to assign customers to delivery routes
while respecting operational constraints such as vehicle capacity and travel
duration.

The original workflow was developed in notebooks. The repository now also
includes a local runner so the data can be validated and a baseline result can
be produced without Google Colab or Google Drive paths.

## Dataset Description

The project uses two Excel files:

- `data.xlsx`: customer information, including customer name, province,
  capacity demand, and valid coordinate/address text.
- `distance-matrix.xlsx`: distance matrix between the depot (`Kho`) and
  customers.

Important columns in `data.xlsx`:

- `Customer_Name`: customer name used to match the distance matrix.
- `Capacity`: customer demand.
- `Coordinates Valid`: cleaned location text used by the original notebooks.

The local runner checks that every customer in `data.xlsx` exists as both a row
and a column in `distance-matrix.xlsx`.

## Algorithm

The main research direction is Ant Colony Optimization (ACO).

ACO is a metaheuristic inspired by how ant colonies find short paths. Each
artificial ant builds a candidate route by selecting the next customer based on
two signals:

- pheromone value, which represents learned route quality from previous
  iterations;
- heuristic value, usually based on distance, where shorter paths are preferred.

After each iteration, pheromone values are updated so better routes become more
likely to be selected in later iterations.

The repository also includes a reproducible nearest-neighbor baseline in
`run_vrp.py`. This baseline always chooses the nearest feasible next customer
while respecting:

- vehicle capacity;
- maximum route duration;
- average vehicle speed;
- service time per customer.

This baseline is useful as a simple comparison point before evaluating the full
ACO implementation.

## How To Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the local baseline:

```bash
python run_vrp.py
```

Useful options:

```bash
python run_vrp.py --vehicle-capacity 2000 --max-duration 48 --speed 50
```

Default values are aligned with the notebook experiment:

- vehicle capacity: `2000`
- max route duration: `48` hours
- speed: `50` km/h
- service time: `0.5` hours per customer
- fixed cost: `1000000`
- transport cost: `4492`

## Results

Current local baseline result:

- number of routes: `30`
- total distance: `11,209.79 km`
- total cost: `80,354,377`

These numbers are produced by the nearest-neighbor baseline, not the final ACO
optimizer. They provide a stable reference result for future comparison.

## Improvement Roadmap

1. Move core ACO logic from notebooks into Python modules.
2. Use the precomputed distance matrix everywhere instead of repeated lookup
   logic.
3. Add validation that each customer is visited exactly once.
4. Add route constraint checks for capacity and duration.
5. Compare greedy baseline, nearest-neighbor baseline, and ACO results.
6. Add runtime benchmarking and convergence charts.
7. Export final route summaries to CSV or Excel.
8. Clean and modularize the optimized notebook so it matches the full original
   workflow.
