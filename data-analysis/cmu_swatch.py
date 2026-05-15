class CMUSwatch:
    diag1: int
    diag2: int
    edge: int
    knit: int
    miss: int
    tuck: int
    x: int

    def __init__(
        self,
        diag1: int,
        diag2: int,
        edge: int,
        knit: int,
        miss: int,
        tuck: int,
        x: int,
    ):
        self.diag1 = diag1
        self.diag2 = diag2
        self.edge = edge
        self.knit = knit
        self.miss = miss
        self.tuck = tuck
        self.x = x

    def to_list(self) -> list[int]:
        return [
            self.diag1,
            self.diag2,
            self.edge,
            self.knit,
            self.miss,
            self.tuck,
            self.x,
        ]

    @staticmethod
    def atom_names() -> list[str]:
        return [
            "diag1",
            "diag2",
            "edge",
            "knit",
            "miss",
            "tuck",
            "x",
        ]

    @staticmethod
    def jersey(width: int, height: int):
        return CMUSwatch(
            knit=width * height,
            tuck=0,
            miss=0,
            x=0,
            edge=height - 1,
            diag1=0,
            diag2=0,
        )
