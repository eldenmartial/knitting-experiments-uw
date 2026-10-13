// import the knitoutWriter code and instantiate it as an object
var knitout = require('../../knitout-frontend-js/knitout');
k = new knitout.Writer({ carriers: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"] });

// add some headers relevant to this job
k.addHeader('Machine', 'SWGXYZ');
k.addHeader('Gauge', '15');
k.addHeader('Width', '271');
k.addHeader('Position', 'Center');

// =====================================================================
// WISTERIA LOOP TUBE SWATCH
// A half-gauge tube (the "stem") with long loops hanging off both sides.
//
// How the loops work (drop-stitch fringe):
//   On loop rounds, the loop yarn knits a little column of stitches on
//   empty needles far outside the tube, then crosses in and TUCKS into a
//   few stitches at the tube's edges (the fold of the tube), then crosses
//   the inside of the tube and does the same on the other side.
//   The tube yarn knits over those tucks, locking them in.
//   At the end the fringe columns are dropped, the column unravels, and
//   each strand that ran out to it becomes a long loop hanging off the edge.
//
//   loop length ~ loop_reach needles  (gauge 15 -> ~1.7 mm per needle,
//   so loop_reach 20 -> loops hang roughly 3.5 cm)
// =====================================================================

// ---- tube variables ----
// tube is knit half gauge: front on needles with width's parity, back on the others
var width = 30;          // 30 needles across each side (test size)
var height = 40;         // rounds long

// ---- loop variables ----
var loop_reach = 20;     // how many needles out from the tube edge the fringe column sits (loop length)
var fringe_cols = 2;     // needles in each fringe column (2-3 knits more reliably than 1)
var anchor_sts = 2;      // tube stitches at each edge the loop yarn tucks into
var loop_every = 2;      // a loop round every N tube rounds (1 = densest)
var loop_start = 7;      // first round with loops (after the tube yarn hook is released)
var loop_end = height - 3; // last round with loops (leave plain rounds to lock the last tucks)

// ---- waste variables ----
var waste_rib_height = 9;
if (waste_rib_height % 2 == 0) {
    throw new Error("waste rib height must be odd for +3 to be even for the tube");
}
var waste_tube_height = 4;

// ---- carriers ----
var c = "2";      // tube / stem color
var loop = "4";   // loop / petal color
var waste = "4";  // waste (same carrier as the example, comes out and goes back in for the loops)
var draw = "6";   // draw thread

k.fabricPresser("auto");
k.addRawOperation('x-sub-roller-number 4');

// ---- needle bookkeeping ----
var frontNeedles = [];   // ascending
var backNeedles = [];    // ascending
for (let s = 1; s <= width; s++) {
    if ((s % 2) == (width % 2)) frontNeedles.push(s);
    else backNeedles.push(s);
}
var rightFringe = width + loop_reach;                       // leftmost needle of right fringe column
var leftFringe = 1 - loop_reach - (fringe_cols - 1);       // leftmost needle of left fringe column

if (anchor_sts * 2 > frontNeedles.length || anchor_sts * 2 > backNeedles.length) {
    throw new Error("anchor_sts too big for this width");
}
if (loop_reach <= 10) {
    throw new Error("loop_reach must be > 10 so the fringe doesn't hit the draw-yarn anchor needles");
}

// =====================================================================
// WASTE SECTION (same as the example)
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
// LOOP PASSES
// =====================================================================

// right-to-left: right fringe -> tuck front right edge -> (float inside tube) -> tuck front left edge -> left fringe
function loopPassLeft() {
    for (let i = fringe_cols - 1; i >= 0; i--) {
        k.knit("-", "f" + (rightFringe + i), loop);
    }
    for (let i = frontNeedles.length - 1; i >= frontNeedles.length - anchor_sts; i--) {
        k.tuck("-", "f" + frontNeedles[i], loop);
    }
    for (let i = anchor_sts - 1; i >= 0; i--) {
        k.tuck("-", "f" + frontNeedles[i], loop);
    }
    for (let i = fringe_cols - 1; i >= 0; i--) {
        k.knit("-", "f" + (leftFringe + i), loop);
    }
}

// left-to-right: left fringe -> tuck back left edge -> (float inside tube) -> tuck back right edge -> right fringe
function loopPassRight() {
    for (let i = 0; i < fringe_cols; i++) {
        k.knit("+", "f" + (leftFringe + i), loop);
    }
    for (let i = 0; i < anchor_sts; i++) {
        k.tuck("+", "b" + backNeedles[i], loop);
    }
    for (let i = backNeedles.length - anchor_sts; i < backNeedles.length; i++) {
        k.tuck("+", "b" + backNeedles[i], loop);
    }
    for (let i = 0; i < fringe_cols; i++) {
        k.knit("+", "f" + (rightFringe + i), loop);
    }
}

// =====================================================================
// LOOPY TUBE
// =====================================================================

// bring in carrier using yarn inserting hook
k.inhook(c);
k.knit("-", "f" + (width + 10), c);

var loopIn = false;        // loop yarn brought in yet?
var loopHooked = false;    // loop yarn still on the inserting hook?
var lastLoopRound = -1;

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

    // release the loop yarn hook once a tube round has locked its first tucks
    if (loopHooked) {
        k.releasehook(loop);
        loopHooked = false;
    }

    // loop round
    if (h >= loop_start && h <= loop_end && ((h - loop_start) % loop_every) == 0) {
        if (!loopIn) {
            k.inhook(loop);
            loopIn = true;
            loopHooked = true;
        }
        loopPassLeft();   // front edges
        loopPassRight();  // back edges
        lastLoopRound = h;
    }

    // take the loop yarn out after the last loop round (it ends on the right)
    if (loopIn && h == lastLoopRound && h + loop_every > loop_end) {
        if (loopHooked) { // only one loop round ever happened
            // knit one more tube round so the hook can be released safely
            for (let s = width; s > 0; s--) {
                if ((s % 2) == (width % 2)) k.knit("-", "f" + s, c);
            }
            for (let s = 1; s <= width; s++) {
                if ((s % 2) != (width % 2)) k.knit("+", "b" + s, c);
            }
            k.releasehook(loop);
            loopHooked = false;
        }
        k.outhook(loop);
        loopIn = false;
    }
}

// ---- drop the fringe columns: they unravel and the loops fall free ----
for (let i = 0; i < fringe_cols; i++) {
    k.drop("f" + (rightFringe + i));
    k.drop("f" + (leftFringe + i));
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

k.write('wisteria_loop_tube.k');
