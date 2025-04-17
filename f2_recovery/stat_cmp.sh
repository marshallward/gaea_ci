#!/bin/bash

for d in $(ls regressions); do
    #echo $d
    for s in $(find regressions/$d -name "*.stats.*"); do
        head="regressions\/$d\/"
        subpath=${s/${head}/}

        outpath=output/$d/dynamic_symmetric/${subpath}
        cp ${outpath} $s
        #diff $s ${outpath}
    done
done
