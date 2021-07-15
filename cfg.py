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
