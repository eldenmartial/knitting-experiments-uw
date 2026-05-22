from knit_swatch import KnitSwatch


def make_training_swatches(
    W: int,
    H: int,
    Wkinda: int,
    Hkinda: int,
    SKINNY_W: int,
    SKINNY_H: int,
    TUBE_W: int,
    TUBE_H: int,
):
    single_jersey = KnitSwatch.jersey(width=W, height=H)

    kinda_narrow_jersey = KnitSwatch.jersey(width=Wkinda, height=Hkinda)

    skinny_jersey = KnitSwatch.jersey(width=SKINNY_W, height=SKINNY_H)

    tuck_stitch = KnitSwatch(
        knit=int(((W - 2) * H / 2) + 2 * H),
        tuck=int((W / 2) * 2 + ((W - 2) * H / 2)),
        miss=int((W / 2) * 2),
        x=0,
        edge=(2 + H) - 1,
        diag1=0,
        diag2=0,
        junk=1,
    )

    rib_1x1 = KnitSwatch(
        knit=W * H,
        tuck=int((W / 2) * 2),
        miss=int((W / 2) * 2),
        x=0,
        edge=(2 + H) - 1,
        diag1=(W - 1) * H,
        diag2=0,
        junk=1,
    )

    half_gauge_rib = KnitSwatch(
        knit=int((W / 2) * H),
        tuck=int((W / 4) * 2),
        miss=int((3 * (W / 4)) * 2),
        x=0,
        edge=(2 + H) - 1,
        diag1=0,
        diag2=(int(W / 2) - 1) * H,
        junk=1,
    )

    half_gauge_jersey = KnitSwatch(
        knit=int((W / 2) * H),
        tuck=int((W / 4) * 2),
        miss=int((3 * (W / 4)) * 2 + ((W / 2 - 1) * H)),
        x=0,
        edge=(2 + H) - 1,
        diag1=0,
        diag2=0,
        junk=1,
    )

    tube_jersey = KnitSwatch(
        knit=(TUBE_W * 2) * TUBE_H,
        tuck=TUBE_W * 2,
        miss=0,
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
        kinda_narrow_jersey,
    ]

    return training_swatches
