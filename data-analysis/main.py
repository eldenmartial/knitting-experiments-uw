# from enum import Enum, auto
import numpy as np

atom_names = ["knit", "tuck", "miss", "x", "edge", "diag1", "diag2", "noise"]

# each ROW corresponds to a swatch. Each COLUMN corresponds with an atom
X = np.array(
    [
        [
            116 * 82,  # knits (from bulk)
            116,  # tucks (83 + 83 from cast-on)
            116,  # misses (83 + 83 from cast-on)
            0,  # x (all front bed)
            83,  # edge (2 cast on rows + 82 regular rows => 84 rows, so 83 edges)
            0,  # no diag1 (all front bed)
            0,  # no diag2 (all front bed)
            1,  # one junk as always
        ],  # single jersey, 116 wide * 82 high AFTER cast-on
        [
            (114 * 82 / 2) + 2 * 82,  # knits
            1,
            0,
            0,
            0,
            0,
            0,
            1,
        ],  # tuck-stitch, 116 wide * 82 high AFTER cast-on. Knits in first and last column, with checkerboard of tucks/knits between.
        # [0, 0, 1, 0, 0, 0, 0, 0],
        # [0, 0, 0, 1, 0, 0, 0, 0],
        # [0, 0, 0, 0, 1, 0, 0, 0],
        # [0, 0, 0, 0, 0, 1, 0, 0],
        # [0, 0, 0, 0, 0, 0, 1, 0],
        # [0, 0, 0, 0, 0, 0, 0, 1],
    ]
)
# one for each row
weights = np.array(
    [1.2, 2.3, 0.7, 1.8, 2.0, 1.1, 0.9, 1.5]
)  # Example scalar measurements

# Solve for coefficients (least squares solution)
coeffs, *_ = np.linalg.lstsq(X, weights, rcond=None)

print("Coefficients for each KnitUnit:")
for name, coeff in zip(atom_names, coeffs):
    print(f"{name:<10}: {coeff:.4f}")
