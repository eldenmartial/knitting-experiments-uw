// wales are disappearing in rib. Why? An attempt to demonstrate the issue
// using a narrow rib on top of a narrow jersey (the jersey shall be "stable")

// import the knitoutWriter code and instantiate it as an object
var knitout = require('../../knitout-frontend-js/knitout');
k = new knitout.Writer({ carriers: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"] });

// add some headers relevant to this job
k.addHeader('Machine', 'SWGXYZ');
k.addHeader('Gauge', '15');
k.addHeader('Width', '271');
k.addHeader('Position', 'Keep');

// swatch variables
let w = 5;
let rib_height = 4;
let jersey_height = 4;
let safety_length = 3;
var start = 35 + safety_length; // lowest safe needle index

var c1 = "5"; // carrier
k.fabricPresser("auto");

k.inhook(c1);

k.stitchNumber(7); // idk, man

// k.tuck("-", "f" + ((w + safety_length) + start), c1);

function safetyAfterLeft() {
    // safety tucks
    for (var s = 0; s > -safety_length; s--) {
        // k.miss("-", "f" + (s + start), c1);
    }
    for (var s = -safety_length + 1; s <= 0; s++) {
        // k.miss("+", "f" + (s + start), c1);
    }
}

function safetyAfterRight() {
    // safety tucks
    for (var s = w + 1; s <= w + safety_length; s++) {
        k.tuck("+", "f" + (s + start), c1);
    }
    for (var s = w + safety_length; s > w; s--) {
        // TODO crash when these are drops and the outgoing are tucks
        k.drop("f" + (s + start));
    }
}


// cast on
for (var s = w; s > 0; s--) {
    if (s % 2 == 0) {
        k.knit("-", "f" + (s + start), c1);
    }
}
safetyAfterLeft()
for (var s = 1; s <= w; s++) {
    if (s % 2 == 1) {
        k.knit("+", "f" + (s + start), c1);
    }
}
safetyAfterRight()

// apparently jersey stabilizes
for (let h = 0; h < jersey_height; h++) {
    for (var s = w; s > 0; s--) {
        k.knit("-", "f" + (s + start), c1);
    }
    safetyAfterLeft()
    for (var s = 1; s <= w; s++) {
        k.knit("+", "f" + (s + start), c1);
    }
    safetyAfterRight()
    if (h == 2) {
        k.releasehook(c1);
    }
}

// now transfer the even stitches to back
for (var s = w; s > 0; s--) {
    if (s % 2 == 0) {
        k.xfer("f" + (s + start), "b" + (s + start));
    }
}



function knitRib(w, h, c1) {
    // w, h need to be even
    // body
    while (h > 0) {
        if (h % 2 == 0) {
            for (var s = w; s > 0; s--) {
                if (s % 2 == 1) {
                    k.knit("-", "f" + (s + start), c1);
                } else {
                    k.knit("-", "b" + (s + start), c1);
                }
            }
            safetyAfterLeft()
        } else {
            for (var s = 1; s <= w; s++) {
                if (s % 2 == 1) {
                    k.knit("+", "f" + (s + start), c1);
                } else {
                    k.knit("+", "b" + (s + start), c1);
                }
            }
            safetyAfterRight()
        }
        h -= 1;
    }
}

knitRib(w, rib_height, c1);

k.outhook(c1);

// write the knitout to a file called "out.k"
k.write('out.k');

