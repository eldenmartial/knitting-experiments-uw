# from enum import Enum, auto
from training_swatches import make_training_swatches
from knit_swatch import KnitSwatch
import numpy as np

W = 116  # checked
H = 82  # checked

Wkinda = 58  # checked
Hkinda = 164  # checked

SKINNY_W = 18  # checked
SKINNY_H = 530  # checked (but is this a little high?)

TUBE_W = 10  # checked, width of the tube as it sits on the bed (a full wraparound is 2x this in stitches)
TUBE_H = 476  # checked, height of the tube in courses (2 * TUBE_W * TUBE_H stitches in total)

training_swatches = make_training_swatches(
    W, H, Wkinda, Hkinda, SKINNY_W, SKINNY_H, TUBE_W, TUBE_H
)

training_swatches_2 = make_training_swatches(
    40, 100, Wkinda, Hkinda, SKINNY_W, SKINNY_H, TUBE_W, TUBE_H
)

print(training_swatches)
training_swatches = training_swatches + training_swatches_2
print(KnitSwatch.atom_names())

# on Thu 2026-05-28
weights = [
    11.627,  # skinny jersey
    12.965,  # single jersey
    12.622,  # kinda narrow
    5.425,  # small (40 x 100)
]

# assert len(training_swatches) == len(KnitSwatch.atom_names()), (
#     "We need a square matrix!"
# )

names = [
    "rib 1x1",
    "half gauge rib",
    "skinny jersey",
    "single jersey",
    "half gauge jersey",
    "tuck stitch",
    "tube jersey",
    "kinda narrow",
]
for name, swatch, weight in zip(names, training_swatches, weights):
    print(f"{name:<20}: {weight:.3f}g, {swatch}")

A = np.array([swatch.to_list() for swatch in training_swatches])
print("bef", A)
A = A[np.ix_([2, 3, 7, 8], [2, 3, 4, 7])]
print("aft", A)
b = np.array(weights)

# A = np.hstack([A, np.ones((A.shape[0], 1))])
# A = A[:7, :7]
# b = b[:7]

print(A)
print(b)

# Ax = b => x = A^-1 b
cond = np.linalg.cond(A)
assert cond < 10**10, (
    f"Matrix is close to singular or badly scaled; condition {cond}. Results would be inaccurate. Matrix: {A}"
)

x = np.linalg.inv(A) @ b

print("Coefficients for each KnitUnit:")
for name, coeff in zip(["edge", "knit", "misstuck", "junk", "IDKHELP"], x):
    print(f"{name:<10}: {coeff * 1000:.2f}mg")

print("Sanity check:")
predicted_weights = A @ x
for i, (actual, predicted) in enumerate(zip(b, predicted_weights)):
    error = abs(actual - predicted)
    print(
        f"Swatch {i + 1}: Actual={actual:.3f}, Predicted={predicted:.3f}, Error={error:.3f}"
    )
