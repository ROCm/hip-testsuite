# Copyright (c) 2021-present Advanced Micro Devices, Inc. All rights reserved.
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

user_password = "AH64_uh1"
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


branch = "rocm-4.2.x"
repos = {
    "hip_examples": {
        "repo_url": "https://github.com/ROCm-Developer-Tools/HIP-Examples",
        "branch": branch,
        # "commit_id": ""
    },
    "hip": {
        "repo_url": "https://github.com/ROCm-Developer-Tools/HIP",
        "branch": branch,
        # "commit_id": ""
    },
    "mixbench": {
        "repo_url": "https://github.com/ekondis/mixbench.git",
        "branch": None,
        # "commit_id": ""
    },
    "gpu_stream": {
        "repo_url": "https://github.com/UoB-HPC/GPU-STREAM.git",
        "branch": None,
        # "commit_id": ""
    },
    "rocclr": {
        "repo_url": "https://github.com/ROCm-Developer-Tools/ROCclr.git",
        "branch": branch,
        # "commit_id": ""
    },
    "opencl": {
        "repo_url": "https://github.com/RadeonOpenCompute/ROCm-OpenCL-Runtime.git",
        "branch": branch,
        # "commit_id": ""
    }
}
