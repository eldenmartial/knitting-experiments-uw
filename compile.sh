#!/bin/bash
# hello
# compile everything in knitting-files
find knitting-files -type f -exec cp {} to-compile/ \;

rm -rf compiled
mkdir -p compiled

shopt -s nullglob

js_files=(to-compile/*.js)
knitout_files=(to-compile/*.knitout)
dat_files=(to-compile/*.dat)

log() { echo "    $*"; }

log "Compiling files in \`to-compile\` -- Errors are unindented and logs are indented"

if [ ${#js_files[@]} -ne 0 ]; then
    for file in "${js_files[@]}"; do
        log "Expanding $(basename "$file")"
        (cd to-compile && node "$(basename "$file")")
        log "Compiling $(basename "$file")"
        (cd compilers && cargo run --release --quiet -- "../to-compile/out.k" "../compiled/$(basename "$file" .js).dat")
        rm to-compile/out.k
    done
fi

if [ ${#knitout_files[@]} -ne 0 ]; then
    for file in "${knitout_files[@]}"; do
        log "Compiling $(basename "$file")"
        (cd compilers && cargo run --release --quiet -- "../to-compile/$(basename "$file")" "../compiled/$(basename "$file" .knitout).dat")
    done
fi

if [ ${#dat_files[@]} -ne 0 ]; then
    for file in "${dat_files[@]}"; do
        log "Copying $(basename "$file")"
        cp "$file" "compiled/$(basename "$file")"
    done
fi

log "Results are in \`compiled\`."

