from knit_swatch import KnitSwatch


def make_training_swatches(
    W: int,
    H: int,
    W2: int,
    H2: int,
    SKINNY_W: int,
    SKINNY_H: int,
    TUBE_W: int,
    TUBE_H: int,
):
    single_jersey = KnitSwatch.jersey(width=W, height=H)

    single_jersey_again = KnitSwatch.jersey(width=W2, height=H2)

    skinny_jersey = KnitSwatch.jersey(width=SKINNY_W, height=SKINNY_H)

    tuck_stitch = KnitSwatch(
        knits=int(((W - 2) * H / 2) + 2 * H),
        tucks=int((W / 2) * 2 + ((W - 2) * H / 2)),
        misses=int((W / 2) * 2),
        x=0,
        edge=(2 + H) - 1,
        diag1=0,
        diag2=0,
        junk=1,
    )

    rib_1x1 = KnitSwatch(
        knits=W * H,
        tucks=int((W / 2) * 2),
        misses=int((W / 2) * 2),
        x=0,
        edge=(2 + H) - 1,
        diag1=(W - 1) * H,
        diag2=0,
        junk=1,
    )

    half_gauge_rib = KnitSwatch(
        knits=int((W / 2) * H),
        tucks=int((W / 4) * 2),
        misses=int((3 * (W / 4)) * 2),
        x=0,
        edge=(2 + H) - 1,
        diag1=0,
        diag2=(int(W / 2) - 1) * H,
        junk=1,
    )

    half_gauge_jersey = KnitSwatch(
        knits=int((W / 2) * H),
        tucks=int((W / 4) * 2),
        misses=int((3 * (W / 4)) * 2 + ((W / 2 - 1) * H)),
        x=0,
        edge=(2 + H) - 1,
        diag1=0,
        diag2=0,
        junk=1,
    )

    tube_jersey = KnitSwatch(
        knits=(TUBE_W * 2) * TUBE_H,
        tucks=TUBE_W * 2,
        misses=0,
        x=(1 + TUBE_H) * 2 - 1,  # TODO check my math
        edge=0,
        diag1=0,
        diag2=0,
        junk=1,
    )

    training_swatches: list[KnitSwatch] = [
        rib_1x1,
        half_gauge_rib,
        skinny_jersey,
        single_jersey,
        half_gauge_jersey,
        tuck_stitch,
        tube_jersey,
        single_jersey_again,
    ]

    return training_swatches
