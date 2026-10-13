var knitout = require('../../knitout-frontend-js/knitout');
K = new knitout.Writer({ carriers: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"] });

// add some headers relevant to this job
K.addHeader('Machine', 'SWGXYZ');
K.addHeader('Gauge', '15');
K.addHeader('Width', '271');
K.addHeader('Position', 'Keep');

//Parameters:
let min = 34; //needle number of left edge
let max = 149; //needle number of right edge
let rows = 82; //number of rows to knit
let carrier = "3"; //carrier name

// ---- set up initial loops and yarn carrier ----
//Bring in carrier:
K.inhook(carrier);

//Set stitch table entry for cast-on:
K.stitchNumber(101);

//On SWGN2 machines, carriers start on the right,
//so will start tucking onto needles right-to-left,
//and will be sure to tuck the rightmost needle in the first pass:
for (let n = max; n >= min; n -= 1) {
	//tuck alternating needles, making sure to do the right edge:
	if ((max - n) % 2 === 0) {
		K.tuck("-", 'f' + n, carrier);
	}
}

//now, moving left-to-right, tuck the needles that were not tucked on the first pass:
for (let n = min; n <= max; n += 1) {
	if ((max - n) % 2 !== 0) {
		K.tuck("+", 'f' + n, carrier);
	}
}

//Set stitch table entry for knitting:
K.stitchNumber(105);

//knit two plain rows to allow cast-on stitches to relax:
// two isn't set in stone here -- it's just convenient
// for this example code to have the carrier end up on the right.
for (let n = max; n >= min; n -= 1) {
	K.knit("-", 'f' + n, carrier);
}
//send out yarn inserting hook; it is no longer needed to hold the yarn in place:
K.releasehook(carrier);
for (let n = min; n <= max; n += 1) {
	K.knit("+", 'f' + n, carrier);
}

// ---- rib sheet ----
//Create a 1x1 rib (alternating front- and back-knit columns) sheet.
//move every other loop to the back bed, starting from the right:
for (let n = min; n <= max; n += 1) {
	if ((max-n) % 2 !== 0) {
		K.xfer('f' + n, 'b' + n);
	}
}

//knit the main part of the sheet
for (let r = 0; r <= rows; r += 1) {
	if (r % 2 === 0) {
		//knit even rows as left-going:
		for (let n = max; n >= min; n -= 1) {
			if ((max-n) % 2 === 0) {
				K.knit("-", 'f' + n, carrier);
			} else {
				K.knit("-", 'b' + n, carrier);
			}
		}
	} else {
		//knit odd rows as right-going:
		for (let n = min; n <= max; n += 1) {
			if ((max-n) % 2 === 0) {
				K.knit("+", 'f' + n, carrier);
			} else {
				K.knit("+", 'b' + n, carrier);
			}
		}
	}
}

//return loops to the front bed (not needed if just dropping, useful if continuing to knit):
for (let n = min; n <= max; n += 1) {
	if ((max-n) % 2 !== 0) {
		K.xfer('b' + n, 'f' + n);
	}
}

// ---- take carrier out and drop remaining loops ----
//Take carrier out with yarn inserting hook:
K.outhook(carrier);

//drop loops:
for (let n = min; n <= max; n += 1) {
	K.drop('f' + n);
}

K.write('out.k');