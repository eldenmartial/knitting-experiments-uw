// Do wales have memory? Idea: knit in half gauge widely, then
// transition to regular tube half gauge

// import the knitoutWriter code and instantiate it as an object
let knitout = require('../knitout-frontend-js/knitout');
k = new knitout.Writer({ carriers: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"] });

// add some headers relevant to this job
k.addHeader('Machine', 'SWGXYZ');
k.addHeader('Gauge', '15');
k.addHeader('Width', '271');
k.addHeader('Position', 'Keep');

// swatch variables
let height = 30; // half the length of the wales (single, then half)
let width = 14; // in stitches on a bed in half-gauge (2x this for total stitch count in the round)
let start = 35; // lowest safe needle index
let padding = 3; // offset on either side

let c = "3"; // carrier
k.fabricPresser("auto");


function dropJustSmall(back_offset) {
    for (var s = width + padding; s > padding; s--) {
        k.drop("f" + (s * 2 + start));
    }
    for (var s = padding + 1; s <= width + padding; s++) {
        k.drop("b" + (s * 2 + start + back_offset));
    }
}

function dropJustBig(back_offset) {
    for (var s = width + 2 * padding; s > 0; s--) {
        if (s <= padding || s > width + padding) {
            k.drop("f" + (s * 2 + start));
        }
    }

    for (var s = 1; s <= width + 2 * padding; s++) {
        if (s <= padding || s > width + padding) {
            k.drop("b" + (s * 2 + start + back_offset));
        }
    }
}


function knitRoundBig(c, back_offset) {
    for (var s = width + 2 * padding; s > 0; s--) {
        k.knit("-", "f" + (s * 2 + start), c);
    }
    for (var s = 1; s <= width + 2 * padding; s++) {
        k.knit("+", "b" + (s * 2 + start + back_offset), c);
    }
}

function knitRound(c, back_offset) {
    for (var s = width + padding; s > padding; s--) {
        k.knit("-", "f" + (s * 2 + start), c);
    }
    for (var s = padding + 1; s <= width + padding; s++) {
        k.knit("+", "b" + (s * 2 + start + back_offset), c);
    }
}

for (var back_offset = 0; back_offset <= 4; back_offset++) {
    // bring in carrier using yarn inserting hook
    k.inhook(c);

    // knit two rounds as a cast-on
    knitRoundBig(c, back_offset);
    knitRoundBig(c, back_offset);

    // release the yarn inserting hook
    k.releasehook(c);

    for (var h = 2; h < height; h++) {
        knitRoundBig(c, back_offset)
    }

    // start the small bit:
    knitRound(c, back_offset);
    knitRound(c, back_offset);

    // drop the big stuff:
    dropJustBig(back_offset);

    // finish it off:
    for (var h = 2; h < height; h++) {
        knitRound(c, back_offset)
    }

    // bring the yarn out with the yarn inserting hook
    k.outhook(c);

    dropJustSmall(back_offset);

    // k.pause("why is there a required comment string???");
}

// write the knitout to a file called "out.k"
k.write('out.k');

