# from enum import Enum, auto
import numpy as np

atom_names = ["knit", "tuck", "miss", "x", "edge", "diag1", "diag2", "noise"]

W = 116
H = 82

SKINNY_W = 16  # TODO
SKINNY_H = 831  # TODO

TUBE_W = 10  # TODO width of the tube as it sits on the bed (a full wraparound is 2x this in stitches)
TUBE_H = (
    148  # TODO height of the tube in courses (2 * TUBE_W * TUBE_H stitches in total)
)

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
            W * H,  # knits
            (W / 2) * 2,  # tucks
            (W / 2) * 2,  # misses
            0,  # x
            (2 + H) - 1,  # edge
            0,  # diag1
            0,  # diag2
            1,  # one junk as always
        ],  # single jersey, BUT AGAIN
        [
            SKINNY_W * SKINNY_H,  # knits
            (SKINNY_W / 2) * 2,  # tucks
            (SKINNY_W / 2) * 2,  # misses
            0,  # x
            (2 + SKINNY_H) - 1,  # edge
            0,  # diag1
            0,  # diag2
            1,  # one junk as always
        ],  # skinny jersey
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
            (W - 2) * H,  # diag1
            0,  # diag2
            1,  # one junk as always
        ],  # 1x1 rib, W wide * H high AFTER cast-on
        [
            (W / 2) * H,  # knits
            (W / 4) * 2,  # tucks
            (3 * (W / 4)) * 2,  # misses
            0,  # x
            (2 + H) - 1,  # edge
            0,  # diag1
            (W - 2) * H,  # diag2
            1,  # one junk as always
        ],  # half-gauge rib, W wide on the bed (so W/2 wales)
        [
            (W / 2) * H,  # knits
            (W / 4) * 2,  # tucks
            (3 * (W / 4)) * 2,  # misses
            0,  # x
            0,  # edge
            0,  # diag1
            0,  # diag2
            1,  # one junk as always
        ],  # half-gauge jersey, W wide on the bed (so W/2 wales)
        [
            (TUBE_W * 2) * TUBE_H,  # knits
            0,  # tucks
            0,  # misses
            (1 + H) * 2 - 1,  # x TODO check my math
            0,  # edge
            0,  # diag1
            0,  # diag2
            1,  # one junk as always
        ],  # tube jersey
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
