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

class BuildRunAmd(BuildRunCommon):
    def __init__(self, path, logfile):
        BuildRunCommon.__init__(self, path, logfile)

    def buildtest(self):
        # In this function put the build steps for test cases
        # which differ across platforms (amd/nvidia/intel) else
        # invoke BuildRunCommon.buildtest
        if not os.path.exists("/opt/rocm"):
            print("ROCm not installed. Exiting!")
            return False
        ret = BuildRunCommon.buildtest(self)
        return ret
