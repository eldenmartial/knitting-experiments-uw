// Do wales have memory? Idea: knit in full gauge, then transition
// to half gauge

// import the knitoutWriter code and instantiate it as an object
var knitout = require('../../knitout-frontend-js/knitout');
k = new knitout.Writer({ carriers: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"] });

// add some headers relevant to this job
k.addHeader('Machine', 'SWGXYZ');
k.addHeader('Gauge', '15');
k.addHeader('Width', '271');
k.addHeader('Position', 'Keep');

// swatch variables
var height = 20; // half the length of the wales (single, then half)
var width = 10; // in stitches on a bed in half-gauge (2x this for total stitch count in the round)
var start = 35; // lowest safe needle index


var c = "3"; // carrier
k.fabricPresser("auto");

function dropAll(back_offset) {
    for (var s = 2 * width; s > 0; s--) {
        k.drop("f" + (s + start));
    }
    for (var s = 1; s <= 2 * width; s++) {
        k.drop("b" + (s + start + back_offset));
    }
}

function dropNonHalfGauge(back_offset) {
    for (var s = width; s > 0; s--) {
        k.knit("-", "f" + (s * 2 - 1 + start), c);
    }
    for (var s = 1; s <= width; s++) {
        k.knit("+", "b" + (s * 2 - 1 + start + back_offset), c);
    }
}

function knitRoundFullGauge(c, back_offset) {
    for (var s = 2 * width; s > 0; s--) {
        k.knit("-", "f" + (s + start), c);
    }
    for (var s = 1; s <= 2 * width; s++) {
        k.knit("+", "b" + (s + start + back_offset), c);
    }
}

function knitRound(c, back_offset) {
    for (var s = width; s > 0; s--) {
        k.knit("-", "f" + (s * 2 + start), c);
    }
    for (var s = 1; s <= width; s++) {
        k.knit("+", "b" + (s * 2 + start + back_offset), c);
    }
}

for (var back_offset = 0; back_offset <= 4; back_offset++) {
    // bring in carrier using yarn inserting hook
    k.inhook(c);

    // knit two rounds as a cast-on
    knitRoundFullGauge(c, back_offset);
    knitRoundFullGauge(c, back_offset);

    // release the yarn inserting hook
    k.releasehook(c);

    for (var h = 2; h < height; h++) {
        knitRoundFullGauge(c, back_offset)
    }

    dropNonHalfGauge(back_offset);

    for (var h = 0; h < height; h++) {
        knitRound(c, back_offset)
    }

    // bring the yarn out with the yarn inserting hook
    k.outhook(c);

    dropAll(back_offset);

    // k.pause("why is there a required comment string???");
}

// write the knitout to a file called "out.k"
k.write('out.k');

