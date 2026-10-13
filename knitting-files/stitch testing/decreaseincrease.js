// import the knitoutWriter code and instantiate it as an object
var knitout = require('../../knitout-frontend-js/knitout');
k = new knitout.Writer({ carriers: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"] });
 
// add some headers relevant to this job
k.addHeader('Machine', 'SWGXYZ');
k.addHeader('Gauge', '15');
k.addHeader('Width', '271');
k.addHeader('Position', 'Center');
 
// ---- bow variables ----
var width = 30;       // full width of the bow wings (needles)
var wingRows = 15;    // rows (pairs of passes) in each full-width wing
var pinchWidth = 8;   // narrowest width at the center of the bow
var pinchRows = 3;    // rows (pairs of passes) knit at the narrow width
 
// ---- waste variables ----
var waste_rib_height = 25;
if (waste_rib_height % 2 == 0) {
    throw new Error("waste rib height must be odd for +3 to be even for the tube");
}
var waste_tube_height = 10;
 
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
 
// move the back-bed waste loops to the front so every front needle
// holds a loop for the single-jersey bow
for (let s = 1; s <= width; s++) {
    if ((s % 2) != (width % 2)) {
        k.xfer("b" + s, "f" + s);
    }
}
 
// draw yarn! one pass across the whole front bed
k.inhook(draw);
k.knit("-", "f" + (width + 10), draw);
for (let s = width; s > 0; s--) {
    k.knit("-", "f" + s, draw);
}
k.knit("-", "f" + (-10), draw);
k.releasehook(draw);
k.outhook(draw);
 










var l = 1;
var r = width;
var dir = "-";        // direction of the next pass
var fresh = {};       // needles just added by an increase (tucked on first pass)
var passCount = 0;
 

// knit (or tuck, if newly added) one needle
function stitch(d, s) {
    
}
 

// one pass across the current width, then flip direction
function knitPass() {

    if (dir === "-") {
        for (let s = r; s >= l; s--){
            if (fresh[s]) {
                k.tuck(dir, "f" + s, c);
                delete fresh[s];
            } else {
                k.knit(dir, "f" + s, c);
            }
        }
        dir = "+";
    } else {
        for (let s = l; s <= r; s++){
            if (fresh[s]) {
                k.tuck(dir, "f" + s, c);
                delete fresh[s];
            } else {
                k.knit(dir, "f" + s, c);
            }
        }
        dir = "-";
    }

    passCount++;

    if (passCount == 12) {
        // release the yarn inserting hook
        k.releasehook(c);
        // drop the draw yarn anchors
        k.drop("f" + (width + 10));
        k.drop("f" + (-10));
    }
}
 
// move each edge stitch one needle inward
function decrease() {
    k.xfer("f" + l, "b" + l);
    k.xfer("f" + r, "b" + r);
    k.rack(1);
    k.xfer("b" + l, "f" + (l + 1));
    k.rack(-1);
    k.xfer("b" + r, "f" + (r - 1));
    k.rack(0);
    l++;
    r--;
}
 
// widen by one empty needle on each side; they get tucked on the next pass
function increase() {
    if (r - l + 3 < width || dir === "+") {
        l--;
        fresh[l] = true;
    }
    if (r - l + 3 < width || dir === "-") {
        r++;
        fresh[r] = true;
    }
}
 


// bring in carrier using yarn inserting hook
k.inhook(c);
k.knit("-", "f" + (width + 10), c);
 

// ---- first wing: full-width rectangle ----
for (let i = 0; i < wingRows * 2; i++) knitPass();
 
// ---- scrunch in: decrease one stitch per side every pass ----
while ((r - l + 1) - 2 >= pinchWidth) {
    decrease();
    knitPass();
}
 
// ---- center of the bow ----
for (let i = 0; i < pinchRows * 2; i++) knitPass();
 
// ---- scrunch out: increase one stitch per side every pass ----
while ((r - l + 2) < width) {
    increase();
    knitPass();
}
 
// ---- second wing: full-width rectangle ----
for (let i = 0; i < wingRows * 2; i++) knitPass();
 
// make sure the carrier is on the right before binding off leftward
if (dir === "+") knitPass();
 
// ---- bind off (single jersey, right to left) ----
for (let s = r; s > l; s--) {
    k.xfer("f" + s, "b" + s);
    k.rack(-1);
    k.xfer("b" + s, "f" + (s - 1));
    k.rack(0);
    k.knit("-", "f" + (s - 1), c);
}
 
// bring the yarn out with the yarn inserting hook
k.outhook(c);
 
k.write('out.k');