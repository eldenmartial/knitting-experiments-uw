// import the knitoutWriter code and instantiate it as an object
var knitout = require('../../knitout-frontend-js/knitout');
k = new knitout.Writer({ carriers: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"] });

// add some headers relevant to this job
k.addHeader('Machine', 'SWGXYZ');
k.addHeader('Gauge', '15');
k.addHeader('Width', '271');
k.addHeader('Position', 'Keep');

// swatch variables
var start = 35; // lowest safe needle index
let width = 112;
let height = 84;
WH = [[width, height], [width / 2, height], [width, height / 2], [width / 2, height / 2], [width / 2, height * 2]];
RUNS = 3; // each

var c = "5"; // carrier
k.fabricPresser("auto");


function knitRib(w, h, c) {
    k.inhook(c);

    // w, h need to be even
    // assert(w % 2 == 0, "width needs to be even");
    // assert(h % 2 == 0, "height needs to be even");

    // cast on
    for (var s = w; s > 0; s--) {
        if (s % 2 == 0) {
            k.knit("-", "f" + (s + start), c);
        }
    }
    for (var s = 1; s <= w; s++) {
        if (s % 2 == 1) {
            k.knit("+", "f" + (s + start), c);
        }
    }

    // apparently two courses of jersey stabilize
    for (var s = w; s > 0; s--) {
        k.knit("-", "f" + (s + start), c);
    }
    k.releasehook(c);
    for (var s = 1; s <= w; s++) {
        k.knit("+", "f" + (s + start), c);
    }

    // now transfer the even stitches to back
    for (var s = w; s > 0; s--) {
        if (s % 2 == 0) {
            k.xfer("f" + (s + start), "b" + (s + start));
        }
    }


    // body
    while (h > 0) {
        if (h % 2 == 0) {
            for (var s = w; s > 0; s--) {
                if (s % 2 == 1) {
                    k.knit("-", "f" + (s + start), c);
                } else {
                    k.knit("-", "b" + (s + start), c);
                }
            }
        } else {
            for (var s = 1; s <= w; s++) {
                if (s % 2 == 1) {
                    k.knit("+", "f" + (s + start), c);
                } else {
                    k.knit("+", "b" + (s + start), c);
                }
            }
        }
        h -= 1;
    }

    // drop (front first, b/c most recent right stitch is on the back)
    for (var s = w; s > 0; s--) {
        k.drop("f" + (s + start));
    }
    for (var s = 1; s <= w; s++) {
        k.drop("b" + (s + start));
    }

    k.outhook(c);
}

for (var i = 0; i < RUNS; i++) {
    for (var j = 0; j < WH.length; j++) {
        knitRib(WH[j][0], WH[j][1], c);
    }
}

// write the knitout to a file called "out.k"
k.write('out.k');

