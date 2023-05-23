#!/bin/bash
set -eu
cd ${CP2K_ROOT}
rm -f build.stamp
set +eu
source ./tools/toolchain/install/setup
set -eu
make -j${JOB_COUNT:-1} ARCH=local_hip VERSION=ssmp
touch build.stamp
