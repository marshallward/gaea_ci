#!/bin/bash
# Get hashes of submodules
SIS2_hash=$(git ls-files -s src/SIS2/ | cut -d' ' -f 2)
git -C src/SIS2 log --oneline ${SIS2_hash}..HEAD \
    | awk '{print "- NOAA-GFDL/SIS2@" $0}'
