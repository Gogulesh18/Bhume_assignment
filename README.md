# Bhume Boundary Take Home Assignment

## Approach

The public truth plots showed that boundary errors were not uniform across the village.

Instead of using a single global shift, I:

1. Learned local drift vectors from example truths.
2. Converted geometries into UTM coordinates.
3. Used inverse-distance weighted interpolation (IDW).
4. Estimated a local correction vector for every plot.
5. Applied the translation to each polygon.
6. Generated confidence values based on proximity to known truths.
7. Flagged low-confidence predictions.

## Results

Vadnerbhairav:
- Median IoU: 0.998
- Improvement: +0.381

Malatavadi:
- Median IoU: 0.936
- Improvement: +0.322

## Files

- final_solution.py
- predictions/
- transcripts/
