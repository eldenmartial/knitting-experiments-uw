# from enum import Enum, auto
from training_swatches import make_training_swatches
from knit_swatch import KnitSwatch
import numpy as np

W = 116
H = 82

Wkinda = 58
Hkinda = 164

SKINNY_W = 16  # TODO
SKINNY_H = 831  # TODO

TUBE_W = 10  # TODO width of the tube as it sits on the bed (a full wraparound is 2x this in stitches)
TUBE_H = (
    148  # TODO height of the tube in courses (2 * TUBE_W * TUBE_H stitches in total)
)

training_swatches = make_training_swatches(
    W, H, Wkinda, Hkinda, SKINNY_W, SKINNY_H, TUBE_W, TUBE_H
)

print(training_swatches)

# training_swatches: list[KnitSwatch] = [
#     rib_1x1,
#     half_gauge_rib,
#     skinny_jersey,
#     single_jersey,
#     half_gauge_jersey,
#     tuck_stitch,
#     tube_jersey,
#     kinda_narrow_jersey,
# ]

weights = [
    16.204,  # rib 1x1
    8.399,  # half gauge rib
    13.466,  # skinny jersey
    13.837,  # single jersey
    9.549,  # half gauge jersey
    12.081,  # tuck stitch
    11.820,  # tube jersey
    12.511,  # kinda narrow
]

assert len(training_swatches) == len(KnitSwatch.atom_names()), (
    "We need a square matrix!"
)

A = np.array([swatch.to_list() for swatch in training_swatches])
b = np.array(weights)

# Ax = b => x = A^-1 b
cond = np.linalg.cond(A)
assert cond < 10**10, (
    f"Matrix is close to singular or badly scaled; condition {cond}. Results would be inaccurate. Matrix: {A}"
)

x = np.linalg.inv(A) @ b

print("Coefficients for each KnitUnit:")
for name, coeff in zip(KnitSwatch.atom_names(), x):
    print(f"{name:<10}: {coeff:.4f}")

print("Sanity check:")
predicted_weights = A @ x
for i, (actual, predicted) in enumerate(zip(b, predicted_weights)):
    error = abs(actual - predicted)
    print(
        f"Swatch {i + 1}: Actual={actual:.3f}, Predicted={predicted:.3f}, Error={error:.3f}"
    )
