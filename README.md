# Bhume Boundary Correction Assignment

## Overview

This repository contains my solution for the Bhume Boundary Correction Take-Home Assignment.

The task is to improve cadastral plot boundaries by aligning them more accurately with the provided satellite imagery. The starter kit includes:

* `input.geojson` – official plot boundaries
* `imagery.tif` – satellite imagery
* `boundaries.tif` – field boundary hints
* `example_truths.geojson` – a small set of manually corrected reference plots

The goal is to generate corrected plot boundaries along with confidence estimates.

---

## Approach

### 1. Analyze Known Corrections

The provided `example_truths.geojson` contains a small number of plots with known corrected boundaries.

For each truth plot:

1. Compute the centroid of the official boundary.
2. Compute the centroid of the corrected boundary.
3. Measure the displacement vector `(dx, dy)`.

These displacement vectors become calibration points describing how mapping errors vary across the village.

---

### 2. Spatial Interpolation Using IDW

Instead of applying a single global shift to all plots, I use Inverse Distance Weighting (IDW) to estimate a local correction for each plot.

For an unknown plot:

1. Find nearby calibration points.
2. Assign higher weight to closer calibration points.
3. Compute a weighted average displacement.
4. Estimate a local `(dx, dy)` correction.

This allows correction magnitude and direction to vary across the village.

---

### 3. Coordinate System Handling

Distance calculations and interpolation are performed in a projected CRS (`EPSG:3857`) so that distances and displacements are measured in meters rather than geographic degrees.

The workflow is:

1. Convert geometries to a metric CRS.
2. Compute shifts and distances.
3. Apply translations.
4. Convert results back to the original CRS before export.

---

### 4. Boundary Translation

After estimating the local displacement:

* The entire polygon is translated by `(dx, dy)`.
* Polygon shape is preserved.
* Only location is adjusted.

This is implemented using Shapely geometry translation operations.

---

### 5. Confidence Estimation

Confidence is intended to reflect the reliability of a correction.

The current implementation considers:

* Proximity to calibration plots.
* Consistency of nearby calibration shifts.

Plots with stronger supporting evidence receive higher confidence values.

Low-confidence predictions can optionally be flagged instead of force-corrected.

---

## Design Decisions

### Why IDW?

The available truth plots are sparse but provide useful spatial information.

IDW was chosen because:

* It is simple and interpretable.
* It does not require model training.
* It allows spatially varying corrections.
* It avoids overfitting associated with training machine learning models on only a handful of labeled examples.

### Why Not Train a Machine Learning Model?

The provided datasets contain only a small number of calibration plots.

A machine learning model would likely memorize those examples rather than learn a robust correction strategy.

The interpolation-based approach is more appropriate for the amount of labeled data available.

---

## Running the Solution

Generate predictions for a village:

```bash
uv run final_solution.py data/vadnerbhairav
```

or

```bash
uv run final_solution.py data/malatavadi
```

The output file:

```text
predictions.geojson
```

will be written inside the selected village directory.

---

## Repository Contents

```text
final_solution.py
README.md
requirements.txt
predictions/
transcripts/
docs/
```

---

## Future Improvements

Possible extensions include:

* Local image-based alignment using satellite imagery.
* Boundary-aware refinement using `boundaries.tif`.
* Improved confidence calibration.
* Hybrid interpolation + image matching approaches.

These were identified as promising directions but were not required for the current implementation.
