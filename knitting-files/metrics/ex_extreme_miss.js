


// import the knitoutWriter code and instantiate it as an object
var knitout = require('../../knitout-frontend-js/knitout');
k = new knitout.Writer({ carriers: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"] });

// add some headers relevant to this job
k.addHeader('Machine', 'SWGXYZ');
k.addHeader('Gauge', '15');
k.addHeader('Width', '271');
k.addHeader('Position', 'Keep');

// swatch variables
var height = 82;
var width = 116;
var offset = 34;
var c = "3";
k.fabricPresser("auto"); // (trying to keep it the same as)

// bring in carrier using yarn inserting hook
k.inhook(c);

// cast on (even width)
// alternate tucks and misses 
for (let s = width; s > 0; s--) {

    if (s % 8 == 0) {
        k.tuck("-", "f" + (s + offset), c);
    }
    else {
        k.miss("-", "f" + (s + offset), c);
    }
}

for (let s = 1; s <= width; s++) {

    if (s % 8 == 4) {
        k.tuck("+", "f" + (s + offset), c);
    }
    else {
        k.miss("+", "f" + (s + offset), c);
    }
}

k.releasehook(c);


for (var h = 0; h < height / 2; h++) {

    // RIGHT TO LEFT
    for (var s = width; s > 0; s--) {

        if (s % 4 === 0) {
            k.knit("-", "f" + (s + offset), c);
        } else {
            k.miss("-", "f" + (s + offset), c);
        }
    }

    // LEFT TO RIGHT
    for (var s = 1; s <= width; s++) {

        if (s % 4 === 0) {
            k.knit("+", "f" + (s + offset), c);
        } else {
            k.miss("+", "f" + (s + offset), c);
        }
    }
}

k.outhook(c);

// write the knitout to a file called "out.k"
k.write('out.k');

