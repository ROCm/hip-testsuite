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
from testsuite.applications.cuda_grep.cuda_grep_parser_common import CudaGrepParser

class BuildRunAmd():
    def __init__(self, thistestpath, logFile, binary):
        self.thistestpath = thistestpath
        self.logFile = logFile
        self.runpath = os.path.join(self.thistestpath, "testbench")
        self.runlog = os.path.join(self.thistestpath, "testbench/RESULTS")
        self.binary = binary

    def buildtest(self):
        # In this function put the build steps for test cases
        # which differ across platforms (amd/nvidia/intel)
        if not os.path.exists("/opt/rocm"):
            print("ROCm not installed. Exiting!")
            return False
        print("Building cuda_grep..")
        cmdcd = "cd " + self.thistestpath + ";"
        cmd_hipify = ""
        cmd_modify = ""
        if not os.path.isfile(os.path.join(self.thistestpath, "hipified")):
            cmd_hipify = "find . -type f \( -iname \*.h -o -iname \*.cpp -o -iname \*.cu -o -iname \*.cuh \) | sed 's|^./||'\
            | xargs -t -I % sh -c '/opt/rocm/bin/hipify-perl % > hip_%; rm %; mv hip_% %;';"
            cmd_modify = "sed -i 's/#include <driver_functions.h>//g' putil.cu; touch hipified;"
        cmd_build = "/opt/rocm/bin/hipcc -O3 -m64 pnfa.cu putil.cu nfa.cpp nfautil.cpp regex.cpp -o " + self.binary + ";"
        cmdexc = cmdcd + cmd_hipify + cmd_modify + cmd_build
        execshellcmd(cmdexc, self.logFile, None)
        return True

    def runtest(self):
        print("Running cuda_grep..")
        cmdexc = "cd " + self.runpath + ";" + "./runtests.sh;"
        execshellcmd(cmdexc, self.logFile, None)

    def clean(self):
        print("Cleaning cuda_grep..")
        cmdcd = "cd " + self.thistestpath + ";"
        cmdrm = "rm -f " + self.binary + ";"
        cmdrmres = "rm -f " + self.runlog + ";"
        cmdexc = cmdcd + cmdrm + cmdrmres
        execshellcmd(cmdexc, None, None)

    def parse_result(self):
        return CudaGrepParser(self.runlog).parse()
