#!/bin/sh
#make -f tools/MRS/Makefile.build clean

#make -f tools/MRS/Makefile.clone clone_gfdl

make -f tools/MRS/Makefile.build debug_gnu -j
make -f tools/MRS/Makefile.build repro_gnu -j
make -f tools/MRS/Makefile.build static_gnu -j
#make -f tools/MRS/Makefile.build repro_intel -j
#make -f tools/MRS/Makefile.build repro_pgi -j

#export CACHE_DIR=$(pwd)/cache
#time make -f tools/MRS/Makefile MOM6_SRC=../.. pipeline-build-repro-intel
