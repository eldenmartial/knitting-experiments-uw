# from enum import Enum, auto
import numpy as np

atom_names = ["knit", "tuck", "miss", "x", "edge", "diag1", "diag2", "noise"]

W = 116
H = 82

# each ROW corresponds to a swatch. Each COLUMN corresponds with an atom
X = np.array(
    [
        [
            W * H,  # knits
            (W / 2) * 2,  # tucks
            (W / 2) * 2,  # misses
            0,  # x
            (2 + H) - 1,  # edge
            0,  # diag1
            0,  # diag2
            1,  # one junk as always
        ],  # single jersey, W wide * H high AFTER cast-on
        [
            ((W - 2) * H / 2) + 2 * H,  # knits
            (W / 2) * 2 + ((W - 2) * H / 2),  # tucks (cast on PLUS checkerboard)
            (W / 2) * 2,  # misses
            0,  # x
            (2 + H) - 1,  # edge
            0,  # diag1
            0,  # diag2
            1,  # one junk as always
        ],  # tuck-stitch, W wide * H high AFTER cast-on. Knits in first and last column, with checkerboard of tucks/knits between.
        [
            W * H,  # knits
            (W / 2) * 2,  # tucks
            (W / 2) * 2,  # misses
            0,  # x
            (2 + H) - 1,  # edge
            0,  # diag1
            0,  # diag2
            1,  # one junk as always
        ],  # 1x1 rib, W wide * H high AFTER cast-on
        [
            0,  # knits
            0,  # tucks
            0,  # misses
            0,  # x
            0,  # edge
            0,  # diag1
            0,  # diag2
            1,  # one junk as always
        ],  # TODO
        [
            0,  # knits
            0,  # tucks
            0,  # misses
            0,  # x
            0,  # edge
            0,  # diag1
            0,  # diag2
            1,  # one junk as always
        ],  # TODO
        [
            0,  # knits
            0,  # tucks
            0,  # misses
            0,  # x
            0,  # edge
            0,  # diag1
            0,  # diag2
            1,  # one junk as always
        ],  # TODO
        [
            0,  # knits
            0,  # tucks
            0,  # misses
            0,  # x
            0,  # edge
            0,  # diag1
            0,  # diag2
            1,  # one junk as always
        ],  # TODO
        [
            0,  # knits
            0,  # tucks
            0,  # misses
            0,  # x
            0,  # edge
            0,  # diag1
            0,  # diag2
            1,  # one junk as always
        ],  # TODO
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
