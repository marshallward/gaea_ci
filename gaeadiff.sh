#!/bin/sh

for f in $(find output -type f -name "*\.stats\.*"); do
    ref=${f/output/regressions}
    ref=${ref/dynamic_symmetric//}
    diff -q $f $ref || ( \
        diff $f $ref; \
    )
done
