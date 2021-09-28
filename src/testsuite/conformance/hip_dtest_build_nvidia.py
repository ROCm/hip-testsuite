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

import os, glob
import tempfile
import json
import re
from testsuite.common.hip_shell import execshellcmd_largedump, execshellcmd
from testsuite.conformance.hip_dtest_build_common import BuildRunCommon

class BuildRunNvidia(BuildRunCommon):
    '''
    In this class insert the build and execution steps specific
    for NVIDIA platform.
    '''
    def __init__(self, logfile):
        BuildRunCommon.__init__(self, logfile)

    def setenv(self):
        env = "export HIP_PLATFORM=nvidia;"
        env += "export HIP_COMPILER=nvcc;"
        env += "export HIP_RUNTIME=cuda;"
        return env

    # Build HIP Catch2 for NVIDIA platform
    def build_package(self):
        buildSuccess = True
        if not os.path.exists("/opt/rocm"):
            print("ROCm not installed. Exiting!")
            return False
        isCatchBuilt = self.validate_hipcatch_build()
        if not isCatchBuilt:
            # Build HIP
            print("Catch2 test not built. Building Catch2 ..")
            cmd = self.setenv()
            cmd += "cd " + self.hippath + "/tests/catch;"
            cmd += "patch -p0 < ../../../CMakePatch;"
            cmd += "cd " + self.hippath + ";"
            cmd += "mkdir build; cd build;"
            cmd += "cmake -DHIP_COMPILER=nvcc -DHIP_PLATFORM=nvidia -DHIP_RUNTIME=cuda -DHIP_PATH=/opt/rocm/hip ../tests/catch;"
            cmd += "make -j build_tests;"
            cmdexc = cmd
            runlogdump = tempfile.TemporaryFile("w+")
            execshellcmd_largedump(cmdexc, self.logfile, runlogdump, None)
            runlogdump.close()

            # Validate if HIP build is successful
            isCatchBuilt = self.validate_hipcatch_build()
            if not isCatchBuilt:
                print("HIP Catch2 Build Failed!")
                return False
        else:
            print("HIP Catch2 already Built")
        return True

    # Execute test cases
    def runtest(self, log, testcase):
        return BuildRunCommon.runtest(self, log, testcase, None)
