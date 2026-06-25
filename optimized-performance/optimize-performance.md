# Algorithm Performance Optimization

This document describes performance improvements for the Vehicle Routing
Problem (VRP) workflow using Ant Colony Optimization (ACO). The previous
version contained corrupted Vietnamese text, so it has been rewritten in clean
UTF-8 English.

## 1. Problem Analysis

The main processing steps are:

- initialize and update the pheromone matrix;
- calculate total route distance;
- validate vehicle capacity constraints;
- validate route duration constraints;
- split customers into vehicle routes;
- calculate total transportation cost;
- visualize cost and distance by loop.

The main performance risks are nested Python loops, repeated `DataFrame`
lookups, and recalculating or re-fetching the same pairwise distances many
times.

## 2. Use The Precomputed Distance Matrix

The original notebook repeatedly calls helper logic such as `calcDistAuto` to
look up distances. That pattern becomes slow as the number of customers grows.

The distance workbook should be converted once:

```python
name_column = df_distance.columns[0]
distance_matrix = df_distance.set_index(name_column).astype(float)
```

Then distance lookups can use direct indexing:

```python
distance = distance_matrix.loc[from_customer, to_customer]
```

For the optimized notebook, this is converted further into a NumPy matrix:

```python
distance_matrix = distance_df.to_numpy(dtype=float)
distance = distance_matrix[i, j]
```

Benefits:

- avoids repeated lookup logic;
- simplifies route distance calculations;
- makes input validation easier;
- enables faster NumPy-based calculations.

## 3. Optimize Pheromone Matrix Initialization

Loop-based version:

```python
def default_odor_matrix(value, n):
    data = [[0 for _ in range(n)] for _ in range(n)]
    odor_matrix = pd.DataFrame(data)
    for row in range(n):
        for column in range(n):
            if row != column:
                odor_matrix.iloc[row, column] = value
    return odor_matrix
```

Recommended version:

```python
def default_odor_matrix(value, n):
    odor_matrix = np.full((n, n), value)
    np.fill_diagonal(odor_matrix, 0)
    return pd.DataFrame(odor_matrix)
```

Benefits:

- less code;
- fewer Python-level loops;
- uses NumPy vectorized operations.

## 4. Optimize Total Distance Calculation

Use the distance matrix directly:

```python
def total_distance(route, distance_matrix):
    distance = 0
    for current_node, next_node in zip(route[:-1], route[1:]):
        distance += distance_matrix.loc[current_node, next_node]
    return round(distance, 2)
```

If a route must return to the depot, add that leg explicitly:

```python
distance += distance_matrix.loc[route[-1], "Kho"]
```

The key is to keep one consistent convention:

- whether the route includes the depot at the start and end;
- whether the return-to-depot leg is included in total distance.

## 5. Optimize Pheromone Evaporation

Pheromone evaporation can be written as:

```python
def evaporate_pheromone(odor_matrix, evaporation_rate=0.1):
    return odor_matrix * (1 - evaporation_rate)
```

`evaporation_rate` should come from configuration instead of being hard-coded
inside the function. This makes experiments easier to reproduce.

## 6. Optimize Edge Updates

Instead of manually creating each edge pair, use NumPy:

```python
def determine_add_edges(route):
    route_array = np.array(route)
    edges = np.column_stack((route_array[:-1], route_array[1:]))
    reverse_edges = edges[:, ::-1]
    return np.vstack((edges, reverse_edges))
```

This is useful when pheromone should be updated in both travel directions.

## 7. Improve Capacity-Based Route Splitting

Route splitting should validate data before assigning customers:

```python
def split_by_capacity(route, max_capacity, demand_by_node):
    routes = []
    current_route = []
    current_load = 0

    for node in route:
        demand = demand_by_node[node]
        if demand > max_capacity:
            raise ValueError(f"Customer {node} exceeds vehicle capacity")

        if current_load + demand <= max_capacity:
            current_route.append(node)
            current_load += demand
        else:
            routes.append(current_route)
            current_route = [node]
            current_load = demand

    if current_route:
        routes.append(current_route)

    return routes
```

Benefits:

- detects impossible customers early;
- avoids invalid generated routes;
- makes automated testing easier.

## 8. Make Algorithm Parameters Configurable

The following values should be configurable through a notebook config block or
CLI arguments:

- number of loops;
- number of ants;
- `alpha`;
- `beta`;
- pheromone evaporation rate;
- vehicle capacity;
- maximum route duration;
- vehicle speed;
- fixed cost;
- transportation cost per kilometer.

This improves reproducibility and makes scenario comparison easier.

## 9. Recommended Next Steps

1. Move ACO logic from notebooks into Python modules.
2. Use `distance-matrix.xlsx` as the only distance source.
3. Validate that each customer is visited exactly once.
4. Validate capacity and duration for every route.
5. Compare greedy, nearest-neighbor baseline, and ACO results.
6. Export final results to CSV or Excel.
7. Add convergence charts for cost and distance by loop.
