// import the knitoutWriter code and instantiate it as an object
var knitout = require('../knitout-frontend-js/knitout');
k = new knitout.Writer({ carriers: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"] });

// add some headers relevant to this job
k.addHeader('Machine', 'SWGXYZ');
k.addHeader('Gauge', '15');
k.addHeader('Width', '271');
k.addHeader('Position', 'Center')

// swatch variables
var height = 30;
var width = 30;
var waste_rib_height = 25;
if (waste_rib_height % 2 == 0) {
    throw new Error("waste rib height must be odd for +3 to be even for the tube");
}
var waste_tube_height = 10;
var c = "5";
var waste = "1";
var draw = "4";
// k.fabricPresser("auto");
k.addRawOperation('x-sub-roller-number 4');


// anchor!
// k.inhook(draw);
// k.knit("-", "f" + (width + 10), draw);
// k.knit("-", "b" + (-10), draw);
// k.releasehook(draw);
// k.outhook(draw);

// waste RIB cast on! evens will be on front bed, odds will be on back. 2 rounds
k.inhook(waste);
// first round: if width mod 6, front. If width + 3 mod 6, back
for (let s = width; s > 0; s--) {
    if ((s % 6) == (width % 6)) {
        k.tuck("-", "f" + s, waste);
    }
    if ((s % 6) == ((width + 3) % 6)) {
        k.knit("-", "b" + s, waste);
    }
}
// second round: If width + 4 mod 6, front. if width + 1 mod 6, back. 
for (let s = 1; s <= width; s++) {
    if ((s % 6) == ((width + 4) % 6)) {
        k.tuck("+", "f" + s, waste);
    }
    if ((s % 6) == ((width + 1) % 6)) {
        k.knit("+", "b" + s, waste);
    }

}
// third round: if width + 2 mod 6, front. If width + 5 mod 6, back
for (let s = width; s > 0; s--) {
    if ((s % 6) == ((width + 2) % 6)) {
        k.tuck("-", "f" + s, waste);
    }
    if ((s % 6) == ((width + 5) % 6)) {
        k.knit("-", "b" + s, waste);
    }
}

// for (let s = width; s > 0; s--) {
//     if ((s % 6) == ((width + 4) % 6)) {
//         k.tuck("-", "f" + s, waste);
//     }
// }
// for (let s = 1; s <= width; s++) {
//     if ((s % 6) == ((width + 1) % 6)) {
//         k.tuck("+", "b" + s, waste);
//     }
// }

// waste rib!
for (let h = 0; h < waste_rib_height; h++) {
    if ((h % 2) == 0) { // right pass
        for (let s = 1; s <= width; s++) {
            if ((s % 2) == (width % 2)) {
                k.knit("+", "f" + s, waste);
            } else {
                k.knit("+", "b" + s, waste);
            }
        }
    } else { // left pass
        for (let s = width; s > 0; s--) {
            if ((s % 2) == (width % 2)) {
                k.knit("-", "f" + s, waste);
            } else {
                k.knit("-", "b" + s, waste);
            }
        }
    }
    if (h == 4) {
        // release the waste yarn inserting hook
        k.releasehook(waste);
    }
}

// waste tube!
for (var h = 0; h < waste_tube_height; h++) {
    for (var s = width; s > 0; s--) {
        if ((s % 2) == (width % 2)) {
            k.knit("-", "f" + s, waste);
        }
    }
    for (var s = 1; s <= width; s++) {
        if ((s % 2) != (width % 2)) {
            k.knit("+", "b" + s, waste);
        }
    }
}
k.outhook(waste);

// draw yarn!
k.inhook(draw);
k.knit("-", "f" + (width + 10), draw);

for (let s = width; s > 0; s--) {
    if ((s % 2) == (width % 2)) {
        k.knit("-", "f" + s, draw);
    } else {
        k.knit("-", "b" + s, draw);
    }
}

k.knit("-", "f" + (-10), draw);
k.releasehook(draw);
k.outhook(draw);

// bring in carrier using yarn inserting hook
k.inhook(c);
k.knit("-", "f" + (width + 10), c);


// main body
for (var h = 0; h < height; h++) {
    for (var s = width; s > 0; s--) {
        if ((s % 2) == (width % 2)) {
            k.knit("-", "f" + s, c);
        } else {
            k.knit("-", "b" + s, c);
        }
    }
    for (var s = 1; s <= width; s++) {
        if ((s % 2) == (width % 2)) {
            k.knit("+", "f" + s, c);
        } else {
            k.knit("+", "b" + s, c);
        }
    }
    if (h == 5) {
        // release the yarn inserting hook
        k.releasehook(c);
        // drop the draw yarn
        k.drop("f" + (width + 10));
        k.drop("f" + (-10));
    }

}

// bind off
for (var s = width; s > 1; s--) {
    if ((s % 2) == (width % 2)) { // front bed
        k.rack(1);
        k.xfer("f" + s, "b" + (s - 1));
        k.knit("-", "b" + (s - 1), c);
    } else { // back bed
        k.rack(-1);
        k.xfer("b" + s, "f" + (s - 1));
        k.knit("+", "f" + (s - 1), c);
    }
}

// bring the yarn out with the yarn inserting hook
k.outhook(c);

k.write('good_rib_7.k');

