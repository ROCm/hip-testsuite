# Copyright (c) 2021 Advanced Micro Devices, Inc. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

version = "1.0.0"

user_password = None
log_location = None

# None/amd/nvidia
HIP_PLATFORM = None

# None/0/1/2/3
Optimization_Level = None

# None/0/1/2/4
HIPCC_VERBOSE = None

# None/cuda directory
CUDA_PATH = None

# None/rocm directory
ROCM_PATH = None

# None/offload target
build_for_target = None

# -I.
# None/List of paths
includes_path = None

# -l
# None/List of -l
link_libs = None

# L.
# None/list of -L
link_libs_path = None

# None/(test_name/test_suite/regex OR list of test_names/test_suites/regex)
# e.g.1 run_tests = ["bitextract", "matrixtranspose"]
# e.g.2 run_tests = "hip_samples"
# e.g.3 run_tests = ".*samples.*"

# If ts: test suite, tc: test case
# e.g.4 run_tests = [[ts1,tc1], [ts1,tc2], [tc3], [ts2,tc4], [ts3]]
# e.g.4 run_tests = [ts1:tc1, ts1:tc2, tc3, ts2:tc4, ts3]
run_tests = None


branch = None
repos = {
    "hip_examples": {
        "repo_url": "https://github.com/ROCm-Developer-Tools/HIP-Examples",
        "branch": None,
        "commit_id": "8a3b04c9b10bae344c7483a63c13034869da184b"
    },
    "hip": {
        "repo_url": "https://github.com/ROCm-Developer-Tools/HIP",
        "branch": None,
        "commit_id": "865b40d8bd8b26a7dfe4d9719e8dcf26f4b3afc6"
    },
    "mixbench": {
        "repo_url": "https://github.com/ekondis/mixbench.git",
        "branch": None,
        "commit_id": "e1d6c00bd86d7d904b658213370ddb780a116d1f"
    },
    "gpu_stream": {
        "repo_url": "https://github.com/UoB-HPC/GPU-STREAM.git",
        "branch": None,
        "commit_id": "6fe81e19556ac26761a1c7247ae29fa88fb4e0ab"
    },
    "mgbench": {
        "repo_url": "https://github.com/tbennun/mgbench.git",
        "branch": None,
        "commit_id": "6f12d3848020af8f718074a30c68e6f0b232bfb3"
    },
    "cuda_grep": {
        "repo_url": "https://github.com/bkase/CUDA-grep.git",
        "branch": None,
        "commit_id": "fa6630eb0c3e782620ec3eaf989873dadc9a036b"
    },
    "cuda_memtest": {
        "repo_url": "https://github.com/ComputationalRadiationPhysics/cuda_memtest.git",
        "branch": None,
        "commit_id": "0cd3a996ce82682fcf50fa6f433b6f1f2ce1353d"
    },
    "quicksilver": {
        "repo_url": "https://github.com/LLNL/Quicksilver.git",
        "branch": "AMD-HIP",
        "commit_id": "bf073887bf73ef34de8025adaba51c6ad7fb15be"
    },
    "gridtools": {
        "repo_url": "https://github.com/GridTools/gridtools.git",
        "branch": None,
        "commit_id": "d33fa6fecee0a7bd9e080212c1038f0dbd31fe97"
    },
    "gtbench": {
        "repo_url": "https://github.com/GridTools/gtbench.git",
        "branch": None,
        "commit_id": "42687cce5085e0e175cb02fefe87fbb3d952fd5c"
    },
    "kokkos": {
        "repo_url": "https://github.com/kokkos/kokkos.git",
        "branch": None,
        "commit_id": "c28a8b03288b185f846ddfb1b7c08213e12e2634"
    },
    "mfem": {
        "repo_url": "https://github.com/mfem/mfem.git ./mfem",
        "branch": None,
        "commit_id": "a3f0a5bb7ca874ec260d6f85afa3693cd6542497"
    },
    "Laghos": {
        "repo_url": "https://github.com/CEED/Laghos.git",
        "branch": None,
        "commit_id": "a7f6123d42847f6bdbdb614f5af876541f49cd16"
    },
    "openmpi": {
        "repo_url": "http://github.com/open-mpi/ompi.git openmpi",
        "branch": "v4.0.x",
        "commit_id": "4dc196d8c60aadeb34b0df9d226ab4c341004704"
    }
}
