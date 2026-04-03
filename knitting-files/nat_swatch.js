// import the knitoutWriter code and instantiate it as an object
var knitout = require('../knitout-frontend-js/knitout');
k = new knitout.Writer({ carriers: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"] });

// add some headers relevant to this job
k.addHeader('Machine', 'SWGXYZ');
k.addHeader('Gauge', '15');
k.addHeader('Width', '271');

// swatch variables
var height = 5;
var width = 20;
var p = "1";
var b = "5";
k.fabricPresser("auto");

// bring in carrier using yarn inserting hook
k.inhook(p);
// tuck on alternate needles to cast on
for (let s = width; s > 0; s--) {
    if (s % 2 == 0) {
        k.tuck("-", "f" + s, p);
    }
    else {
        k.miss("-", "f" + s, p);
    }
}
for (let s = 1; s <= width; s++) {
    if (s % 2 != 0) {
        k.tuck("+", "f" + s, p);
    }
    else {
        k.miss("+", "f" + s, p);
    }
}

// release the yarn inserting hook
k.releasehook(p);

k.inhook(b);

for (var s = width; s > 0; s--) {
    k.knit("-", "f" + s, b);
}
for (var s = 1; s <= width; s++) {
    k.knit("+", "f" + s, b);
}

k.releasehook(b);

// knit some rows back and forth. Two pink, two black
for (var h = 0; h < height; h++) {
    for (var s = width; s > 0; s--) {
        k.knit("-", "f" + s, p);
    }
    for (var s = 1; s <= width; s++) {
        k.knit("+", "f" + s, p);
    }
    for (var s = width; s > 0; s--) {
        k.knit("-", "f" + s, b);
    }
    for (var s = 1; s <= width; s++) {
        k.knit("+", "f" + s, b);
    }
}

// knit some rows back and forth. Pink, black, pink, black
for (var h = 0; h < height; h++) {
    for (var s = width; s > 0; s--) {
        k.knit("-", "f" + s, p);
    }
    for (var s = width; s > 0; s--) {
        k.knit("-", "f" + s, b);
    }
    for (var s = 1; s <= width; s++) {
        k.knit("+", "f" + s, p);
    }
    for (var s = 1; s <= width; s++) {
        k.knit("+", "f" + s, b);
    }
}

// bring the yarn out with the yarn inserting hook
k.outhook(p);
k.outhook(b);

// write the knitout to a file called "out.k"
k.write('out.k');

