// import the knitoutWriter code and instantiate it as an object
var knitout = require('../../knitout-frontend-js/knitout');
k = new knitout.Writer({ carriers: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"] });

// add some headers relevant to this job
k.addHeader('Machine', 'SWGXYZ');
k.addHeader('Gauge', '15');
k.addHeader('Width', '270');
k.addHeader('Position', 'Keep');

// swatch variables
var height = 100;
var c = "4";
k.fabricPresser("auto");

// bring in carrier using yarn inserting hook
for (var h = 0; h < height; h++) {
    k.inhook(c);
    for (var i = 0; i < 10; i++) {
        k.tuck("-", "b" + (200 - i), c);
    }
    k.releasehook(c);
    k.outhook(c);
}

// write the knitout to a file called "out.k"
k.write('out.k');

