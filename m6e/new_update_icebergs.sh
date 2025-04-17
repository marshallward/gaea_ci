#!/bin/bash
# Get hashes of submodules
model=icebergs
src_hash=$(git ls-files -s src/${model}/ | cut -d' ' -f 2)

# Print most recent log, cut the hash
git -C src/${model} log --oneline ${src_hash}..HEAD \
    | grep -v "Merge pull request #" \
    | grep -v "Merge branch '" \
    | head -n 1 \
    | cut -f 2- -d' ' \
    | awk '{print "icebergs: " $0 "\n"}'

# Print all of the logs, prepend the GitHub hash
git -C src/${model} log --oneline ${src_hash}..HEAD \
    | grep -v "Merge pull request #" \
    | grep -v "Merge branch '" \
    | awk '{print "- NOAA-GFDL/icebergs@" $0}'
