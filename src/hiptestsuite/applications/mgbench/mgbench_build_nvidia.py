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
import tempfile
from hiptestsuite.common.hip_shell import *
from hiptestsuite.applications.mgbench.mgbench_parser_common import MgbenchParser

class BuildRunNvidia():
    def __init__(self, app_root, thistestpath, logFile, mgtestfile, binary):
        self.app_root = app_root
        self.thistestpath = thistestpath
        self.logFile = logFile
        self.mgtestfile = mgtestfile
        self.binary = binary
        self.runlog = None

    def getenvironmentvariables(self):
        envtoset = os.environ.copy()
        envtoset["HIP_PLATFORM"] = "nvidia"
        envtoset["HIP_COMPILER"] = "nvcc"
        envtoset["HIP_RUNTIME"] = "cuda"
        return envtoset

    def buildtest(self):
        if not os.path.exists("/opt/rocm"):
            print("ROCm not installed. Exiting!")
            return False
        # In this function put the build steps for test cases
        # which differ across platforms (amd/nvidia/intel)
        # Build dependencies
        print("Building mgbench..")
        depfolder = os.path.join(self.app_root, "deps/gflags/")
        cmdcd = "cd " + depfolder + ";"
        cmdbuild = "cmake .; make clean; make;"
        cmdexcdep = cmdcd + cmdbuild
        execshellcmd(cmdexcdep, self.logFile, None)
        if not os.path.isfile(depfolder + "lib/libgflags.a"):
            print("Dependency (gflags) build failed")
            return False
        env = self.getenvironmentvariables()
        mgtestfile_hipified = "hip_" + self.mgtestfile
        cmdcd = "cd " + self.thistestpath + ";"
        cmd_hipify = "/opt/rocm/bin/hipify-perl " + self.mgtestfile + ">> " + mgtestfile_hipified + ";"
        cmd_build = "/opt/rocm/bin/hipcc " + mgtestfile_hipified +\
        " -lgflags -L../../deps/gflags/lib/ -I ../../deps/gflags/include/ -o " + self.binary + ";"
        cmd_clean = "rm -f " + mgtestfile_hipified + ";"
        cmdexc = cmdcd + cmd_hipify + cmd_build + cmd_clean
        execshellcmd(cmdexc, self.logFile, env)
        return True

    def runtest(self):
        print("Running mgbench..")
        env = self.getenvironmentvariables()
        cmdexc = "cd " + self.thistestpath + ";" + "./" + self.binary + ";"
        self.runlog = tempfile.TemporaryFile("w+")
        execshellcmd_largedump(cmdexc, self.logFile, self.runlog, env)

    def clean(self):
        print("Cleaning mgbench..")
        cmdcd = "cd " + self.thistestpath + ";"
        cmdrm = "rm -f " + self.binary + ";"
        cmdexc = cmdcd + cmdrm
        if self.runlog != None:
            self.runlog.close()
        execshellcmd(cmdexc, None, None)

    def parse_result(self, test):
        return MgbenchParser(self.runlog).parse(test)
