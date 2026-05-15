from cmu_swatch import CMUSwatch
from knit_swatch import KnitSwatch


def CMU_swatches():
    W = 159
    BIG_HALF_W = 159 // 2 + 1
    SMALL_HALF_W = 159 // 2
    assert W == BIG_HALF_W + SMALL_HALF_W
    H = 60

    SKINNY_W = 18
    SKINNY_H = 530

    TUBE_W = 9
    TUBE_H = 1060

    single_jersey = CMUSwatch.jersey(width=W, height=H)

    skinny_jersey = CMUSwatch.jersey(width=SKINNY_W, height=SKINNY_H)

    tuck_stitch = CMUSwatch(
        knit=int(((W - 2) * H / 2) + 2 * H),
        tuck=int((W - 2) * H / 2),
        miss=0,
        x=0,
        edge=H - 1,
        diag1=0,
        diag2=0,
    )

    rib_1x1 = CMUSwatch(
        knit=W * H,
        tuck=0,
        miss=0,
        x=0,
        edge=H - 1,
        diag1=(W - 1) * H,
        diag2=0,
    )

    half_gauge_rib = CMUSwatch(
        knit=BIG_HALF_W * H,
        tuck=0,
        miss=0,
        x=0,
        edge=H - 1,
        diag1=0,
        diag2=(BIG_HALF_W - 1) * H,
    )

    half_gauge_jersey = CMUSwatch(
        knit=BIG_HALF_W * H,
        tuck=0,
        miss=SMALL_HALF_W * H,
        x=0,
        edge=H - 1,
        diag1=0,
        diag2=0,
    )

    tube_jersey = CMUSwatch(
        knit=(TUBE_W * 2) * TUBE_H,
        tuck=0,
        miss=0,
        x=int(TUBE_H * 2 - 1),  # TODO check my math
        edge=0,
        diag1=0,
        diag2=0,
    )

    training_swatches: list[CMUSwatch] = [
        rib_1x1,
        half_gauge_rib,
        skinny_jersey,
        single_jersey,
        half_gauge_jersey,
        tuck_stitch,
        tube_jersey,
    ]

    return [KnitSwatch.correct(swatch) for swatch in training_swatches]
