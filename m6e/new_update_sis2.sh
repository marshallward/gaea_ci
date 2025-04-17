#!/bin/bash
# Get hashes of submodules
SIS2_hash=$(git ls-files -s src/SIS2/ | cut -d' ' -f 2)

# Print most recent log, cut the hash
git -C src/SIS2 log --oneline ${SIS2_hash}..HEAD \
    | grep -v "Merge pull request #" \
    | grep -v "Merge branch '" \
    | head -n 1 \
    | cut -f 2- -d' ' \
    | awk '{print "SIS2: " $0 "\n"}'

# Print all of the logs, prepend the GitHub hash
git -C src/SIS2 log --oneline ${SIS2_hash}..HEAD \
    | grep -v "Merge pull request #" \
    | grep -v "Merge branch '" \
    | awk '{print "- NOAA-GFDL/SIS2@" $0}'
