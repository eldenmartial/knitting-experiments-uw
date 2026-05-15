import numpy as np
from cmu_swatches import CMU_swatches

# As defined in the paper:
# CMU_A[0][:] is 1x1 rib
# CMU_A[:][0] is d1
CMU_A = np.array(
    [
        [9480, 0, 118, 9422, 0, 0, 0],
        [0, 4740, 118, 4682, 0, 0, 0],
        [0, 0, 1058, 8482, 0, 0, 0],
        [0, 0, 118, 9422, 0, 0, 0],
        [0, 0, 118, 4682, 4740, 0, 0],
        [0, 0, 118, 4712, 0, 4710, 0],
        [0, 0, 0, 14842, 0, 0, 2119],
    ]
)

assert np.linalg.cond(CMU_A) < 10**10, (
    "CMU's matrix is close to singular or badly scaled???"
)

CMU_x = np.array([0.10, 0.17, 0.49, 0.39, 0.14, 0.41, 0.84])

# Ax = b

CMU_b = CMU_A @ CMU_x

print(CMU_b)

swatches = CMU_swatches()

A = np.array([swatch.to_list() for swatch in swatches])

print(CMU_A)
print(A)
print(A - CMU_A)
