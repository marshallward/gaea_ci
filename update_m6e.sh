#!/bin/bash
# Get hashes of submodules
M6E_hash=$(git ls-files -s MOM6-examples | cut -d' ' -f 2)

# Print most recent log, cut the hash
git -C MOM6-examples log --oneline ${M6E_hash}..HEAD \
    | grep -v "Merge pull request #" \
    | grep -v "Merge branch '" \
    | head -n 1 \
    | cut -f 2- -d' ' \
    | awk '{print "MOM6-examples: " $0 "\n"}'

# Print all of the logs, prepend the GitHub hash
git -C MOM6-examples log --oneline ${M6E_hash}..HEAD \
    | grep -v "Merge pull request #" \
    | grep -v "Merge branch '" \
    | awk '{print "- NOAA-GFDL/MOM6-examples@" $0}'
