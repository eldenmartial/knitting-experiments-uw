# from enum import Enum, auto
import numpy as np

W = 116
H = 82

W2 = 116
H2 = 164

SKINNY_W = 16  # TODO
SKINNY_H = 831  # TODO

TUBE_W = 10  # TODO width of the tube as it sits on the bed (a full wraparound is 2x this in stitches)
TUBE_H = (
    148  # TODO height of the tube in courses (2 * TUBE_W * TUBE_H stitches in total)
)


class KnitSwatch:
    knits: int
    tucks: int
    misses: int
    x: int
    edge: int
    diag1: int
    diag2: int
    junk: int

    def __init__(
        self,
        knits: int,
        tucks: int,
        misses: int,
        x: int,
        edge: int,
        diag1: int,
        diag2: int,
        junk: int,
    ):
        self.knits = knits
        self.tucks = tucks
        self.misses = misses
        self.x = x
        self.edge = edge
        self.diag1 = diag1
        self.diag2 = diag2
        self.junk = junk

    def to_list(self) -> list[int]:
        return [
            self.knits,
            self.tucks,
            self.misses,
            self.x,
            self.edge,
            self.diag1,
            self.diag2,
            self.junk,
        ]

    @staticmethod
    def from_array(arr: list[int]):
        assert len(arr) == len(KnitSwatch.atom_names()), (
            "Array must have 8 elements corresponding to the KnitUnit atoms"
        )
        return KnitSwatch(
            knits=arr[0],
            tucks=arr[1],
            misses=arr[2],
            x=arr[3],
            edge=arr[4],
            diag1=arr[5],
            diag2=arr[6],
            junk=arr[7],
        )

    @staticmethod
    def atom_names() -> list[str]:
        return [
            "knits",
            "tucks",
            "misses",
            "x",
            "edge",
            "diag1",
            "diag2",
            "junk",
        ]


def jersey(width: int, height: int) -> KnitSwatch:
    return KnitSwatch(
        knits=width * height,
        tucks=int((width / 2) * 2),
        misses=int((width / 2) * 2),
        x=0,
        edge=(2 + height) - 1,
        diag1=0,
        diag2=0,
        junk=1,
    )


single_jersey = (14.520, jersey(width=W, height=H))

single_jersey_again = (
    14.520,  # TODO
    jersey(width=W2, height=H2),
)

skinny_jersey = (
    13.064,
    KnitSwatch(
        knits=SKINNY_W * SKINNY_H,
        tucks=int((SKINNY_W / 2) * 2),
        misses=int((SKINNY_W / 2) * 2),
        x=0,
        edge=(2 + SKINNY_H) - 1,
        diag1=0,
        diag2=0,
        junk=1,
    ),
)

tuck_stitch = (
    12.149,
    KnitSwatch(
        knits=int(((W - 2) * H / 2) + 2 * H),
        tucks=int((W / 2) * 2 + ((W - 2) * H / 2)),
        misses=int((W / 2) * 2),
        x=0,
        edge=(2 + H) - 1,
        diag1=0,
        diag2=0,
        junk=1,
    ),
)

rib_1x1 = (
    0.0,  # TODO
    KnitSwatch(
        knits=W * H,
        tucks=int((W / 2) * 2),
        misses=int((W / 2) * 2),
        x=0,
        edge=(2 + H) - 1,
        diag1=(W - 2) * H,
        diag2=0,
        junk=1,
    ),
)

half_gauge_rib = (
    8.502,
    KnitSwatch(
        knits=int((W / 2) * H),
        tucks=int((W / 4) * 2),
        misses=int((3 * (W / 4)) * 2),
        x=0,
        edge=(2 + H) - 1,
        diag1=0,
        diag2=(W - 2) * H,
        junk=1,
    ),
)

half_gauge_jersey = (
    9.243,
    KnitSwatch(
        knits=int((W / 2) * H),
        tucks=int((W / 4) * 2),
        misses=int((3 * (W / 4)) * 2),
        x=0,
        edge=0,
        diag1=0,
        diag2=0,
        junk=1,
    ),
)

tube_jersey = (
    10.803,
    KnitSwatch(
        knits=(TUBE_W * 2) * TUBE_H,
        tucks=0,
        misses=0,
        x=int((1 + H) * 2 - 1),  # TODO check my math
        edge=0,
        diag1=0,
        diag2=0,
        junk=1,
    ),
)

training_swatches: list[tuple[float, KnitSwatch]] = [
    single_jersey,
    single_jersey_again,
    skinny_jersey,
    tuck_stitch,
    rib_1x1,
    half_gauge_rib,
    half_gauge_jersey,
    tube_jersey,
]

assert len(training_swatches) == len(KnitSwatch.atom_names()), (
    "We need a square matrix!"
)

A = np.array([swatch.to_list() for _, swatch in training_swatches])
b = np.array([weight for weight, _ in training_swatches])

# Ax = b => x = A^-1 b
if np.linalg.cond(A) > 10**10:
    raise ValueError(
        "Matrix is close to singular or badly scaled. Results would be inaccurate."
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
