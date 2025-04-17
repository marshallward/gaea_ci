n=0
types=$(ls output)
for t in ${types}; do
    for f in $(find output/${t}/dynamic_symmetric -name chksum_diag.gnu); do
        cmp ${f} ${f/_symmetric/}
    done
done
