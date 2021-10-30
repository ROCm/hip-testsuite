#!/bin/sh

# This shell script removes all generated files/folders and cloned repositories
echo "Cleaning hip-testsuite project.."
find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
rm -Rf report
rm -Rf src/hiptestsuite/applications/cuda_grep/CUDA-grep
rm -Rf src/hiptestsuite/applications/cuda_memtest/cuda_memtest
rm -Rf src/hiptestsuite/applications/hip_examples/GPU-STREAM
rm -Rf src/hiptestsuite/applications/hip_examples/HIP-Examples
rm -Rf src/hiptestsuite/applications/hip_examples/mixbench
rm -Rf src/hiptestsuite/applications/mgbench/mgbench
rm -Rf src/hiptestsuite/applications/hpc_apps/gridtools/boost_1_72_0
rm -Rf src/hiptestsuite/applications/hpc_apps/gridtools/GridTools
rm -Rf src/hiptestsuite/applications/hpc_apps/gridtools/gridtools
rm -Rf src/hiptestsuite/applications/hpc_apps/kokkos/kokkos
rm -Rf src/hiptestsuite/applications/hpc_apps/laghos/hypre*
rm -Rf src/hiptestsuite/applications/hpc_apps/laghos/Laghos
rm -Rf src/hiptestsuite/applications/hpc_apps/laghos/metis*
rm -Rf src/hiptestsuite/applications/hpc_apps/laghos/mfem
rm -Rf src/hiptestsuite/applications/hpc_apps/quicksilver/Quicksilver
rm -Rf src/hiptestsuite/conformance/HIP
