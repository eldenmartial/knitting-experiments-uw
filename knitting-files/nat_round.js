// import the knitoutWriter code and instantiate it as an object
var knitout = require('../knitout-frontend-js/knitout');
k = new knitout.Writer({ carriers: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"] });

// add some headers relevant to this job
k.addHeader('Machine', 'SWGXYZ');
k.addHeader('Gauge', '15');
k.addHeader('Width', '271');

// swatch variables
var height = 12;
var width = 10;
var p = "1";
var b = "5";
k.fabricPresser("auto");

// bring in carrier using yarn inserting hook
k.inhook(p);

function knitRound(c) {
    for (var s = width; s > 0; s--) {
        k.knit("-", "f" + s, c);
    }
    for (var s = width; s > 0; s--) {
        k.knit("+", "b" + s, c);
    }
}

knitRound(p);
knitRound(p);


// release the yarn inserting hook
k.releasehook(p);

k.inhook(b);

knitRound(b);

knitRound(p);
knitRound(p);

k.releasehook(b);

for (var h = 0; h < height; h++) {
    knitRound(b);
    knitRound(p);
    knitRound(p);
}

// bring the yarn out with the yarn inserting hook
k.outhook(b);
k.outhook(p);

// write the knitout to a file called "out.k"
k.write('out.k');

