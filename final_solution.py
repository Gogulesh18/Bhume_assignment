from bhume import load, score, write_predictions
from shapely.affinity import translate
import geopandas as gpd
import math
import sys


def build_predictions(village_path):
    village = load(village_path)

    if village.example_truths is None:
        raise ValueError("No example truths found")

    utm = "EPSG:32643"

    official = village.plots.to_crs(utm)
    truth = village.example_truths.to_crs(utm)

    samples = []

    # Learn drift from public truths
    for pn in truth.index:

        if pn in official.index:

            official_centroid = official.loc[pn, "geometry"].centroid
            truth_centroid = truth.loc[pn, "geometry"].centroid

            samples.append(
                {
                    "x": official_centroid.x,
                    "y": official_centroid.y,
                    "dx": truth_centroid.x - official_centroid.x,
                    "dy": truth_centroid.y - official_centroid.y,
                }
            )

    if len(samples) == 0:
        raise ValueError("No matching example truths")

    new_geometries = []
    confidences = []
    statuses = []

    for _, row in official.iterrows():

        centroid = row.geometry.centroid

        neighbors = []

        for sample in samples:

            dist = math.hypot(
                centroid.x - sample["x"],
                centroid.y - sample["y"]
            )

            neighbors.append((dist, sample))

        neighbors.sort(key=lambda x: x[0])

        k = min(5, len(neighbors))
        nearest = neighbors[:k]

        total_weight = 0.0
        dx_sum = 0.0
        dy_sum = 0.0

        for dist, sample in nearest:

            weight = 1.0 / ((dist + 1.0) ** 2)

            total_weight += weight
            dx_sum += sample["dx"] * weight
            dy_sum += sample["dy"] * weight

        dx = dx_sum / total_weight
        dy = dy_sum / total_weight

        corrected_geom = translate(
            row.geometry,
            dx,
            dy
        )

        new_geometries.append(corrected_geom)

        nearest_distance = nearest[0][0]

        confidence = max(
            0.25,
            min(
                0.99,
                1.0 - (nearest_distance / 5000.0)
            )
        )

        if nearest_distance > 4500:
            status = "flagged"
            confidence = 0.20
        else:
            status = "corrected"

        confidences.append(round(confidence, 3))
        statuses.append(status)

    preds = official.copy()

    preds["geometry"] = new_geometries

    preds = preds.to_crs("EPSG:4326")

    preds["status"] = statuses
    preds["confidence"] = confidences
    preds["method_note"] = (
        "local drift interpolation using inverse-distance weighting"
    )

    preds = preds[
        [
            "plot_number",
            "status",
            "confidence",
            "method_note",
            "geometry",
        ]
    ]

    output_file = village.dir / "predictions.geojson"

    write_predictions(output_file, preds)

    print("\nPredictions saved to:")
    print(output_file)

    if village.example_truths is not None:
        print()
        print(score(preds, village))


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage:")
        print("python final_solution.py <village_folder>")
        sys.exit(1)

    build_predictions(sys.argv[1])