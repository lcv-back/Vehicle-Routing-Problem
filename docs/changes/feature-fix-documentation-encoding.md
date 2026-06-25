# Branch: feature/fix-documentation-encoding

## Goal

This branch addresses the improvement: **Fix documentation encoding**.

The main goal is to remove corrupted text from the documentation and rewrite
the README with a clearer structure so readers can understand the project,
dataset, execution steps, and improvement roadmap.

## Problem Before The Change

Some Markdown files contained mojibake, which happens when UTF-8 text is read
or saved with the wrong encoding. Accented letters were displayed as broken
multi-byte sequences instead of readable text.

Affected files:

- `README.md`
- `optimized-performance/optimize-performance.md`

## Changes Applied

### README.md

The README was rewritten in clean UTF-8 and reorganized into:

- Problem overview
- Dataset description
- Algorithm
- How to run
- Results
- Improvement roadmap

The README also documents local execution:

```bash
python run_vrp.py
```

### optimized-performance/optimize-performance.md

The performance notes were rewritten in clear English. The new content focuses
on:

- using the precomputed distance matrix;
- optimizing pheromone matrix initialization;
- optimizing total distance calculation;
- optimizing pheromone evaporation;
- improving route splitting by capacity;
- making algorithm parameters configurable;
- listing recommended next steps.

## Result

The documentation no longer contains visible corrupted encoding sequences. The
README is easier to read and can be used as the main project overview.

The local runner was verified with:

```bash
python run_vrp.py
```

Baseline result:

- routes: `30`
- total distance: `11,209.79 km`
- total cost: `80,354,377`

## Notes

This branch changes documentation only. It does not change algorithm logic or
data files.
