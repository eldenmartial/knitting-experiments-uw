from cmu_swatch import CMUSwatch


class KnitSwatch:
    diag1: int
    diag2: int
    edge: int
    knit: int
    miss: int
    tuck: int
    x: int
    junk: int

    def __init__(
        self,
        diag1: int,
        diag2: int,
        edge: int,
        knit: int,
        miss: int,
        tuck: int,
        x: int,
        junk: int,
    ):
        self.diag1 = diag1
        self.diag2 = diag2
        self.edge = edge
        self.knit = knit
        self.miss = miss
        self.tuck = tuck
        self.x = x
        self.junk = junk

    def to_list(self) -> list[int]:
        return [
            self.diag1,
            self.diag2,
            self.edge,
            self.knit,
            self.miss,
            self.tuck,
            self.x,
            self.junk,
        ]

    def to_CMU(self) -> CMUSwatch:
        return CMUSwatch(
            diag1=self.diag1,
            diag2=self.diag2,
            edge=self.edge * 2,
            knit=self.knit - 2 * self.edge - 2 * self.x,
            miss=self.miss,
            tuck=self.tuck,
            x=self.x,
        )

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
            "junk",
        ]

    @staticmethod
    def jersey(width: int, height: int):
        return KnitSwatch(
            knit=width * height,
            tuck=int((width / 2) * 2),
            miss=int((width / 2) * 2),
            x=0,
            edge=(2 + height) - 1,
            diag1=0,
            diag2=0,
            junk=1,
        )

    @staticmethod
    def correct(swatch: CMUSwatch) -> CMUSwatch:
        """
        Correct an incorrectly made CMUSwatch

        Args:
            swatch (CMUSwatch): The incorrect swatch using UW's definition.

        Returns:
            CMUSwatch: The corrected swatch using CMU's definition.
        """
        return KnitSwatch(
            diag1=swatch.diag1,
            diag2=swatch.diag2,
            edge=swatch.edge,
            knit=swatch.knit,
            miss=swatch.miss,
            tuck=swatch.tuck,
            x=swatch.x,
            junk=-1,
        ).to_CMU()
