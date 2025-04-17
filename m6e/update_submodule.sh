#!/bin/bash
# Get hashes of submodules
declare ${1}_hash=$(git ls-files -s src/${1}/ | cut -d' ' -f 2)
submodule_hash=${1}_hash

# Print most recent log, cut the hash
git -C src/${1} log --oneline ${!submodule_hash}..HEAD \
    | grep -v "Merge pull request #" \
    | grep -v "Merge branch '" \
    | head -n 1 \
    | cut -f 2- -d' ' \
    | awk "{print \"${1}: \" \$0 \"\\n\"}"

# Print all of the logs, prepend the GitHub hash
git -C src/${1} log --oneline ${!submodule_hash}..HEAD \
    | grep -v "Merge pull request #" \
    | grep -v "Merge branch '" \
    | awk "{print \"- NOAA-GFDL/${1}@\" \$0}"
