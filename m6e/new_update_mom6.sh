#!/bin/bash
# Get hashes of submodules
MOM6_hash=$(git ls-files -s src/MOM6/ | cut -d' ' -f 2)

# Print most recent log, cut the hash
git -C src/MOM6 log --oneline ${MOM6_hash}..HEAD \
    | grep -v "Merge pull request #" \
    | grep -v "Merge branch '" \
    | head -n 1 \
    | cut -f 2- -d' ' \
    | awk '{print "MOM6: " $0 "\n"}'

# Print all of the logs, prepend the GitHub hash
git -C src/MOM6 log --oneline ${MOM6_hash}..HEAD \
    | grep -v "Merge pull request #" \
    | grep -v "Merge branch '" \
    | awk '{print "- NOAA-GFDL/MOM6@" $0}'
