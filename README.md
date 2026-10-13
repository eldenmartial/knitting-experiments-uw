# Knitting Experiments 

By Elden Martial

Many thanks to Nat Hurtig

A working repository of my machine-knitting experiments: metric studies, creative test swatches, and machine debugging. It also holds the notes and guides I've written along the way on running the machine, the math behind the patterns, and what I've learned.

Everything is written in [knitout](https://textiles-lab.github.io/knitout/knitout.html) using JavaScript, then compiled for our Shima Seiki SWG-series machine (15 gauge).

---

## Repository layout

```
.
├── compilers/              # knitout → machine compilers (submodule, by Nat Hurtig)
├── knitout-frontend-js/    # JavaScript knitout writer (submodule)
├── knitting-files/         # all knitout source programs
│   ├── machine debugging/  # programs for diagnosing machine/program problems
│   ├── metrics/            # swatches knit for the weight & dimension study
│   ├── stitch testing/     # creative swatches and stitch/structure tests
│   ├── small_square.js     # minimal starter swatch
│   └── waste-example.js    # reference waste section (rib + tube + draw thread)
├── data-analysis/          # Python code for predicting weight & dimensions
├── yarn-measurement-code/  # code for measuring yarn usage
├── machine-notes/          # LaTeX guide to using the machine (math, setup, references)
├── swatch-notes/           # running notes on swatches and metrics
├── to-compile/             # .k files waiting to be compiled
├── compiled/               # compiled machine files (.dat) ready to knit
└── compile.sh              # compiles knitout files into machine files
```

### `knitting-files/`

The knitout programs, written in JavaScript with `knitout-frontend-js`. Running one writes a `.k` knitout file.

- **`metrics/`** — swatches designed for the metrics study. Each one varies a controlled parameter (stitch type, width, height, structure) so its weight and dimensions can be measured and compared against predictions.
- **`stitch testing/`** — my own creative experiments: tubes, half-gauge structures, increases/decreases, and other test swatches (e.g. `half_gauge_jersey_tube.js`, `decreaseincrease.js`, `tubesmall.js`). Some files here are adapted from collaborators' examples (`amy_…`, `nat_…`).
- **`machine debugging/`** — small programs written to isolate and fix machine or program issues.
- **`waste-example.js`** — the standard waste section I reuse at the start of tube pieces: waste rib cast-on, waste tube, then a draw thread, so the real piece can be released cleanly.
- **`small_square.js`** — a simple starting point for new swatches.

### `data-analysis/`

Python code for the metrics work. It takes measurements from knit swatches and uses information from their knitout programs (stitch counts, operation types, etc.) to predict a piece's **weight** and **dimensions**.

### `yarn-measurement-code/`

Code for estimating and measuring how much yarn a program uses, which feeds into the weight predictions.

### `machine-notes/`

A LaTeX document (`main.tex`, `machine.tex`, `references.bib`) with guides on:

- how to use the machine properly (setup, carriers, yarn inserting hooks, common pitfalls)
- the math behind patterns (gauge, racking, needle parity for half-gauge tubes, etc.)
- references to the research this work builds on

Build it with any LaTeX setup, for example:

```bash
cd machine-notes
latexmk -pdf main.tex
```

### `swatch-notes/`

Plain-text notes recorded while knitting:

- `metric notes.txt` — observations and measurements for the metrics study
- `dangling threads.txt` — loose ends, open questions, and things to try next

---

## Getting started

### 1. Clone with submodules

The compilers and knitout frontend are git submodules, so clone recursively:

```bash
git clone --recurse-submodules <repo-url>
```

or, if you've already cloned:

```bash
git submodule update --init --recursive
```

### 2. Write a knitout program

Programs in `knitting-files/` import the frontend like this (adjust the path to where your file lives):

```js
var knitout = require('../../knitout-frontend-js/knitout');
k = new knitout.Writer({ carriers: ["1","2","3","4","5","6","7","8","9","10"] });
// ... knitting operations ...
k.write('out.k');
```

Run it with Node to produce a `.k` file:

```bash
node knitting-files/stitch\ testing/tubesmall.js
```

### 3. Compile for the machine

Put the `.k` file in `to-compile/` and run:

```bash
./compile.sh
```

The compiled `.dat` files are written to `compiled/` and can be loaded onto the machine.

### 4. Analyze

After knitting, record weights and measurements in `swatch-notes/` and run the Python code in `data-analysis/` to compare them against the predictions.

---

## Machine setup used

| Setting  | Value        |
| -------- | ------------ |
| Machine  | Shima Seiki SWG-series (`SWGXYZ` header) |
| Gauge    | 15           |
| Carriers | 1–10         |

---

## Credits

- **Compilers** (`compilers/`) — written by **Nat Hurtig**.
- **knitout-frontend-js** — the JavaScript knitout writer from the [CMU Textiles Lab](https://github.com/textiles-lab/knitout-frontend-js).
- **Knitout** — the knitting machine language developed by the CMU Textiles Lab ([spec](https://textiles-lab.github.io/knitout/knitout.html)).
- Example programs adapted from collaborators are noted by filename.

Everything else (creative swatches, metric experiments, analysis, and notes) is my own work, done as a research assistant at the Paul G. Allen School, University of Washington.
