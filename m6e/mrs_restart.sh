#!/bin/sh

#make -f tools/MRS/Makefile.restart gnu_ocean_only -s -j RESTART_STAGE=02
#make -f tools/MRS/Makefile.restart gnu_ocean_only -s -j RESTART_STAGE=01
#make -f tools/MRS/Makefile.restart gnu_ocean_only -s -j RESTART_STAGE=12
#make -f tools/MRS/Makefile.restart gnu_ice_ocean_SIS2 -s -j RESTART_STAGE=02
#make -f tools/MRS/Makefile.restart gnu_ice_ocean_SIS2 -s -j RESTART_STAGE=01
#make -f tools/MRS/Makefile.restart gnu_ice_ocean_SIS2 -s -j RESTART_STAGE=12
make -f tools/MRS/Makefile.restart restart_gnu_ocean_only -s -j
make -f tools/MRS/Makefile.restart restart_gnu_ice_ocean_SIS2 -s -j
#make -f tools/MRS/Makefile.restart gnu_ocean_only gnu_ice_ocean_SIS2 -s -j RESTART_STAGE=02
#make -f tools/MRS/Makefile.restart gnu_ocean_only gnu_ice_ocean_SIS2 -s -j RESTART_STAGE=01
#make -f tools/MRS/Makefile.restart gnu_ocean_only gnu_ice_ocean_SIS2 -s -j RESTART_STAGE=12
#make -f tools/MRS/Makefile.restart restart_gnu_ocean_only restart_gnu_ice_ocean_SIS2 -s -j
