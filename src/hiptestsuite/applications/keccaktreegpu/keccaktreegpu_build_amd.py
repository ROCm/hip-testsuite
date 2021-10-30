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
from hiptestsuite.applications.keccaktreegpu.keccaktreegpu_parser_common import KeccakTreeParser

class BuildRunAmd():
    def __init__(self, thistestpath, logFile, binary):
        self.thistestpath = thistestpath
        self.logFile = logFile
        self.runlog = ""
        self.binary = binary

    def getenvironmentvariables(self):
        envtoset = os.environ.copy()
        envtoset["HIP_PATH"] = "/opt/rocm"
        return envtoset

    def buildtest(self):
        if not os.path.exists("/opt/rocm"):
            print("ROCm not installed. Exiting!")
            return False
        # In this function put the build steps for test cases
        # which differ across platforms (amd/nvidia/intel)
        print("Building keccaktreegpu..")
        cmdcd = "cd " + self.thistestpath + ";"
        env = self.getenvironmentvariables()
        cmd_build = "make CFLAGS=-D__HIP_PLATFORM_AMD__ ;"
        cmdexc = cmdcd + cmd_build
        execshellcmd(cmdexc, self.logFile, env)

    def runtest(self):
        print("Running keccaktreegpu..")
        env = self.getenvironmentvariables()
        cmdexc = "cd " + self.thistestpath + ";" + "./" + self.binary + ";"
        self.runlog = execshellcmd(cmdexc, self.logFile, env)

    def clean(self):
        print("Cleaning keccaktreegpu..")
        cmdcd = "cd " + self.thistestpath + ";"
        cmdclean = "make clean;"
        cmdexc = cmdcd + cmdclean
        execshellcmd(cmdexc, None, None)

    def parse_result(self):
        return KeccakTreeParser(self.runlog).parse()
