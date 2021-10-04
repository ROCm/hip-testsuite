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
from hiptestsuite.common.hip_shell import execshellcmd
from hiptestsuite.applications.cuda_memtest.cuda_memtest_parser_common import CudaMemtestParser

class BuildRunAmd():
    def __init__(self, thistestpath, logFile, binary):
        self.thistestpath = thistestpath
        self.logFile = logFile
        self.runlog = ""
        self.binary = binary

    def buildtest(self):
        if not os.path.exists("/opt/rocm"):
            print("ROCm not installed. Exiting!")
            return False
        # In this function put the build steps for test cases
        # which differ across platforms (amd/nvidia/intel)
        print("Building cuda_memtest..")
        cmdcd = "cd " + self.thistestpath + ";"
        cmd_hipify = ""
        cmd_modify = ""
        if not os.path.isfile(os.path.join(self.thistestpath, "hipified")):
            cmd_hipify = "ls cuda_memtest.* misc.* tests.cu | xargs -t -I % sh -c '/opt/rocm/bin/hipify-perl % > hip_%; rm %; mv hip_% %;';"
            cmd_modify = "patch -p0 < ../cuda_memtest_patch; touch hipified;"
        cmd_build = "/opt/rocm/bin/hipcc -DENABLE_NVML=0 cuda_memtest.cu misc.cpp tests.cu -o " + self.binary + ";"
        cmdexc = cmdcd + cmd_hipify + cmd_modify + cmd_build
        execshellcmd(cmdexc, self.logFile, None)
        return True

    def runtest(self, testnum):
        print("Running cuda_memtest " + str(testnum) + "..")
        cmdcd = "cd " + self.thistestpath + ";"
        cmdrun = "./" + self.binary + " --disable_all --enable_test " + str(testnum) + " --num_passes 1"
        cmdexc = cmdcd + cmdrun
        self.runlog = execshellcmd(cmdexc, self.logFile, None)

    def clean(self):
        print("Cleaning cuda_memtest..")
        cmdcd = "cd " + self.thistestpath + ";"
        cmdrm = "rm -f " + self.binary + ";"
        cmdexc = cmdcd + cmdrm
        execshellcmd(cmdexc, None, None)

    def parse_result(self):
        return CudaMemtestParser(self.runlog).parse()
