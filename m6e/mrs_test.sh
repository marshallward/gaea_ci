#!/bin/sh
set -x

module load git

make -f tools/MRS/Makefile.tests clean

make -j -f tools/MRS/Makefile.tests gnu_non_symmetric
make -j -f tools/MRS/Makefile.tests gnu_symmetric
make -j -f tools/MRS/Makefile.tests gnu_memory
make -j -f tools/MRS/Makefile.tests gnu_static
# pip-j eline-test-gnu_restarts ?
make -j -f tools/MRS/Makefile.tests params_gnu_symmetric
make -j -f tools/MRS/Makefile.tests intel_non_symmetric
make -j -f tools/MRS/Makefile.tests intel_symmetric
make -j -f tools/MRS/Makefile.tests intel_memory
make -j -f tools/MRS/Makefile.tests pgi_non_symmetric
make -j -f tools/MRS/Makefile.tests pgi_symmetric
make -j -f tools/MRS/Makefile.tests pgi_memory

# Restarts
bash tools/MRS/generate_manifest.sh . tools/MRS/excluded-expts.txt > manifest.mk
