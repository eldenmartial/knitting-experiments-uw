// wales are disappearing in rib. Why? An attempt to demonstrate the issue
// using a narrow rib on top of a narrow jersey (the jersey shall be "stable")

// import the knitoutWriter code and instantiate it as an object
var knitout = require('../knitout-frontend-js/knitout');
k = new knitout.Writer({ carriers: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"] });

// add some headers relevant to this job
k.addHeader('Machine', 'SWGXYZ');
k.addHeader('Gauge', '15');
k.addHeader('Width', '271');
k.addHeader('Position', 'Keep');

// swatch variables
let w = 20;
let other_w = 14;
let jersey_height = 8;
var start = 35;  // lowest safe needle index

var c1 = "5"; // carrier
k.fabricPresser("auto");

k.inhook(c1);

k.stitchNumber(7); // idk, man

// k.tuck("-", "f" + ((w + safety_length) + start), c1);

// cast on
for (var s = w; s > 0; s--) {
    if (s % 2 == 0) {
        k.knit("-", "f" + (s + start), c1);
    }
}
for (var s = 1; s <= w; s++) {
    if (s % 2 == 1) {
        k.knit("+", "f" + (s + start), c1);
    }
}

// apparently jersey stabilizes
for (let h = 0; h < jersey_height; h++) {
    for (var s = w; s > 0; s--) {
        k.knit("-", "f" + (s + start), c1);
    }
    for (var s = 1; s <= w; s++) {
        k.knit("+", "f" + (s + start), c1);
    }
}


for (var s = w; s > other_w; s--) {
    k.drop("f" + (s + start));
}

k.releasehook(c1);

for (let h = 0; h < jersey_height; h++) {
    for (var s = other_w; s > 0; s--) {
        k.knit("-", "f" + (s + start), c1);
    }
    for (var s = 1; s <= other_w; s++) {
        k.knit("+", "f" + (s + start), c1);
    }
}

k.outhook(c1);

// write the knitout to a file called "out.k"
k.write('out.k');

