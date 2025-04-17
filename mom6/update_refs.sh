#!/bin/sh
COMPILERS="gnu intel pgi"

for c in ${COMPILERS}; do
  RUNS="tmp-MOM6-examples-${c}/results/${c}-all-dynamic_symmetric-repro-def-stats/"

  for f in $(find ${RUNS} -name *.stats.${c}); do
    echo cp $f regressions/${f/${RUNS}/}
  done
done
