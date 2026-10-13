// import the knitoutWriter code and instantiate it as an object
var knitout = require('../../knitout-frontend-js/knitout');
k = new knitout.Writer({ carriers: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"] });

// add some headers relevant to this job
k.addHeader('Machine', 'SWGXYZ');
k.addHeader('Gauge', '15');
k.addHeader('Width', '271');
k.addHeader('Position', 'Center');

// ---- tube variables ----
// a bow wing was 30 needles wide and 30 passes long
// tube is knit half gauge: front on needles with width's parity, back on the others
var width = 30;        // 30 needles across each side (test size)
var height = 20;       // 20 rounds long (test size)

// ---- waste variables ----
var waste_rib_height = 9;
if (waste_rib_height % 2 == 0) {
    throw new Error("waste rib height must be odd for +3 to be even for the tube");
}
var waste_tube_height = 4;

var c = "2";
var waste = "4";
var draw = "6";
k.fabricPresser("auto");
k.addRawOperation('x-sub-roller-number 4');

// =====================================================================
// WASTE SECTION
// =====================================================================

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
for (let h = 0; h < waste_tube_height; h++) {
    for (let s = width; s > 0; s--) {
        if ((s % 2) == (width % 2)) {
            k.knit("-", "f" + s, waste);
        }
    }
    for (let s = 1; s <= width; s++) {
        if ((s % 2) != (width % 2)) {
            k.knit("+", "b" + s, waste);
        }
    }
}
k.outhook(waste);

// draw yarn! one round on the same needles as the tube
k.inhook(draw);
k.knit("-", "f" + (width + 10), draw);
for (let s = width; s > 0; s--) {
    if ((s % 2) == (width % 2)) {
        k.knit("-", "f" + s, draw);
    }
}
k.knit("-", "f" + (-10), draw);
for (let s = 1; s <= width; s++) {
    if ((s % 2) != (width % 2)) {
        k.knit("+", "b" + s, draw);
    }
}
k.releasehook(draw);
k.outhook(draw);

// =====================================================================
// STRAIGHT TUBE
// =====================================================================

// bring in carrier using yarn inserting hook
k.inhook(c);
k.knit("-", "f" + (width + 10), c);

for (let h = 0; h < height; h++) {
    // front of the tube, right to left
    for (let s = width; s > 0; s--) {
        if ((s % 2) == (width % 2)) {
            k.knit("-", "f" + s, c);
        }
    }
    // back of the tube, left to right
    for (let s = 1; s <= width; s++) {
        if ((s % 2) != (width % 2)) {
            k.knit("+", "b" + s, c);
        }
    }
    if (h == 5) {
        // release the yarn inserting hook
        k.releasehook(c);
        // drop the draw yarn anchors
        k.drop("f" + (width + 10));
        k.drop("f" + (-10));
    }
}

// ---- bind off around the tube so the top stays open ----
// front, right to left: each stitch goes through the empty back needle onto the next front stitch
for (let s = width; s > 2; s -= 2) {
    k.xfer("f" + s, "b" + s);
    k.rack(-2);
    k.xfer("b" + s, "f" + (s - 2));
    k.rack(0);
    k.knit("-", "f" + (s - 2), c);
}
// turn the corner: last front stitch onto the first back stitch
k.rack(1);
k.xfer("f2", "b1");
k.rack(0);
k.knit("+", "b1", c);
// back, left to right: each stitch goes through the empty front needle onto the next back stitch
for (let s = 1; s < width - 1; s += 2) {
    k.xfer("b" + s, "f" + s);
    k.rack(-2);
    k.xfer("f" + s, "b" + (s + 2));
    k.rack(0);
    k.knit("+", "b" + (s + 2), c);
}

// bring the yarn out with the yarn inserting hook
k.outhook(c);

k.write('out.k');