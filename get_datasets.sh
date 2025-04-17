#!/bin/sh
ocn_stats=$(find regressions -name "ocean\.stats\.gnu")

expt_dirs=""
for f in $ocn_stats
do
    reg_dir=$(dirname $f)
    expt_dir+=" ${reg_dir/regressions/MOM6-examples}"
done

#echo ${expt_dir}

nclinks=""
for d in ${expt_dir}
do
    #nclinks+=" $(find ${d} -type l -name "*\.nc" | xargs readlink)"
    nclinks+=" $(find ${d} -type l | xargs readlink)"
done
echo -e "${nclinks// /\\n}" | sort -u | grep "^\.datasets"
