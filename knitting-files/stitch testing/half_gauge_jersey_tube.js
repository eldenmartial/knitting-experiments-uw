// Should the back bed needles be offset or no?

// import the knitoutWriter code and instantiate it as an object
var knitout = require('../../knitout-frontend-js/knitout');
k = new knitout.Writer({ carriers: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"] });

// add some headers relevant to this job
k.addHeader('Machine', 'SWGXYZ');
k.addHeader('Gauge', '15');
k.addHeader('Width', '271');
k.addHeader('Position', 'Keep');

// swatch variables
var height = 30; // length of the wales
var width = 10; // in stitches on a bed (2x this for total stitch count in the round)
var start = 35; // lowest safe needle index


var c = "3"; // carrier
k.fabricPresser("auto");

var back_offset = 4; // set to 0 for no offset, or 1 for a half-gauge offset

// bring in carrier using yarn inserting hook
k.inhook(c);

function knitRound(c) {
    for (var s = width; s > 0; s--) {
        k.knit("-", "f" + (s * 2 + start), c);
    }
    for (var s = 1; s <= width; s++) {
        k.knit("+", "b" + (s * 2 + start + back_offset), c);
    }
}

// knit two rounds as a cast-on
knitRound(c);
knitRound(c);

// release the yarn inserting hook
k.releasehook(c);

for (var h = 2; h < height; h++) {
    knitRound(c)
}

// bring the yarn out with the yarn inserting hook
k.outhook(c);

// write the knitout to a file called "out.k"
k.write('out.k');

