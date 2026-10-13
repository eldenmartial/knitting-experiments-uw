// import the knitoutWriter code and instantiate it as an object
var knitout = require('../knitout-frontend-js/knitout');
k = new knitout.Writer({ carriers: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"] });

// add some headers relevant to this job
k.addHeader('Machine', 'SWGXYZ');
k.addHeader('Gauge', '15');
k.addHeader('Width', '271');
k.addHeader('Position', 'Keep');

// swatch variables
var width = 10;
var height = 952; // +8 stitches
var offset = 34; 
var c = "3";
k.fabricPresser("auto"); // (trying to keep it the same as)

// bring in carrier using yarn inserting hook
k.inhook(c);

// cast on (even width)
// alternate tucks and misses 
for (let s = width; s > 0; s--) {
        k.tuck("-", "f" + (s + offset), c);
}

for (let s = 1; s <= width; s++) {
        k.tuck("+", "b" + (s + offset), c);
}

// release hook
k.releasehook(c);

for (var h = 0; h < height; h++) {

    if (h % 2 === 0) {
        // front bed row
        for (var s = width; s > 0; s--) {
            k.knit("-", "f" + (s + offset), c);
        }
    } else {
        // back bed row
        for (var s = 1; s <= width; s++) {
            k.knit("+", "b" + (s + offset), c);
        }
    }
}

k.outhook(c);

// write the knitout to a file called "out.k"
k.write('out.k');

