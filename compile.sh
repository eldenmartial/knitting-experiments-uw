#!/bin/bash

mkdir -p compiled

for file in to-compile/*.knitout; do
  echo "Compiling $file"
  cd compilers && cargo run --release --quiet -- "../to-compile/$(basename "$file")" "../compiled/$(basename "$file" .knitout).dat"
done

echo "Results are in \`compiled\`."

