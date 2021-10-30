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
from hiptestsuite.applications.hip_examples.hip_examples_parser import Hip_examples_parser
from hiptestsuite.applications.hip_examples.hip_examples_build_common import BuildRunCommon
from hiptestsuite.common.hip_shell import *

class BuildRunAmd(BuildRunCommon):
    def __init__(self, path):
        BuildRunCommon.__init__(self, path)

    def buildtest(self, logFile, testid):
        # In this function put the build steps for test cases
        # which differ across platforms (amd/nvidia/intel) else
        # invoke BuildRunCommon.buildtest
        if not os.path.exists("/opt/rocm"):
            print("ROCm not installed. Exiting!")
            return False
        ret = BuildRunCommon.buildtest(self, logFile, testid)
        return ret

    def runtest(self, logFile, testid):
        # In this function put the execution steps for test cases
        # which differ across platforms (amd/nvidia/intel) else
        # invoke BuildRunCommon.buildtest
        ret = BuildRunCommon.runtest(self, logFile, testid)
        return ret

    # Clean all generated binaries
    def clean(self, testid):
        BuildRunCommon.clean(self, testid)
