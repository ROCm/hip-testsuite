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

import os
from testsuite.common.hip_shell import execshellcmd
from testsuite.applications.hip_samples.hip_samples_build_common import BuildRunCommon

class BuildRunNvidia(BuildRunCommon):
    def __init__(self, path, logfile):
        self.hippath = os.path.join(os.getcwd(), "src/testsuite/conformance/HIP/")
        BuildRunCommon.__init__(self, path, logfile)

    def getenvironmentvariables(self):
        envtoset = os.environ.copy()
        envtoset["HIP_PLATFORM"] = "nvidia"
        envtoset["HIP_COMPILER"] = "nvcc"
        envtoset["HIP_RUNTIME"] = "cuda"
        envtoset["HIP_PATH"] = "/opt/rocm/hip"
        return envtoset

    def applypatch(self): # To be deleted
        if not os.path.isfile(\
        os.path.join(self.hippath, "patched")):
            cmd = "cd " + self.hippath + ";"
            cmd += "patch -p0 < ../../applications/hip_samples/Samples_Patch_4.2.x; touch patched;"
            execshellcmd(cmd, self.logfile, None)

    def buildtest(self):
        # In this function put the build steps for test cases
        # which differ across platforms (testsuite/nvidia/intel) else
        # invoke BuildRunCommon.buildtest
        if not os.path.exists("/opt/rocm"):
            print("ROCm not installed. Exiting!")
            return False
        # Apply Patch. This is temporary and will be removed once Hip Samples changes
        # are available in HIP public repository.
        envtoset = self.getenvironmentvariables()
        self.applypatch()
        ret = BuildRunCommon.buildtest(self, envtoset)
        return ret
