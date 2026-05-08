// import the knitoutWriter code and instantiate it as an object
var knitout = require('../knitout-frontend-js/knitout');
k = new knitout.Writer({ carriers: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"] });

// add some headers relevant to this job
k.addHeader('Machine', 'SWGXYZ');
k.addHeader('Gauge', '15');
k.addHeader('Width', '270');
k.addHeader('Position', 'Left');

// swatch variables
var height = 20;
var width = 140;
var c = "3";
k.fabricPresser("auto");

// bring in carrier using yarn inserting hook
k.inhook(c);
// tuck on alternate needles to cast on
for (let s = width; s > 0; s--) {
    if (s % 2 == 0) {
        k.tuck("-", "b" + s, c);
    }
    else {
        k.miss("-", "b" + s, c);
    }
}
for (let s = 1; s <= width; s++) {
    if (s % 2 != 0) {
        k.tuck("+", "b" + s, c);
    }
    else {
        k.miss("+", "b" + s, c);
    }
}

// release the yarn inserting hook
k.releasehook(c);

for (var h = 0; h < height; h++) {
    for (var s = width; s > 0; s--) {
        k.knit("-", "b" + s, c);
    }
    for (var s = 1; s <= width; s++) {
        k.knit("+", "b" + s, c);
    }
}

// bring the yarn out with the yarn inserting hook
k.outhook(c);

// write the knitout to a file called "out.k"
k.write('out.k');

