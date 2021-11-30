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
import re
import tempfile
from hiptestsuite.common.hip_shell import *
from hiptestsuite.applications.hpc_apps.kokkos.kokkos_parser_common import KokkosParser

class BuildRunAmd():
    def __init__(self, thistestpath, logFile):
        self.thistestpath = thistestpath
        self.logFile = logFile
        self.runlog = None

    def buildtest(self):
        # In this function put the build steps for test cases
        # which differ across platforms (amd/nvidia/intel)
        gpuarch = get_gpuarch(self.logFile)
        if gpuarch is None:
            return False
        # extract the gpu architecture number
        arch_num = re.search("\d+", gpuarch).group(0)
        if not os.path.exists(os.path.join(self.thistestpath, "build")):
            print("Building Kokkos..")
            cmdcd = "cd " + self.thistestpath + "; mkdir build; cd build;"
            cmd_cmake = "cmake -DKokkos_ARCH_SKX=ON -DKokkos_ARCH_VEGA" + arch_num + "=ON -DCMAKE_CXX_COMPILER=/opt/rocm/bin/hipcc " +\
            "-DKokkos_ENABLE_HIP=ON -DKokkos_ENABLE_SERIAL=ON -DKokkos_ENABLE_TESTS=ON -DKokkos_CXX_STANDARD=14 -DCMAKE_CXX_STANDARD=14 " +\
            "-DCMAKE_INSTALL_PREFIX=../install -DKokkos_ENABLE_HIP_RELOCATABLE_DEVICE_CODE=OFF " +\
            "-DCMAKE_CXX_FLAGS=\"-O3 -DNDEBUG --amdgpu-target=gfx" + arch_num + "\" ..;"
            cmd_build = "make -j; make -j install;"
            cmdexc = cmdcd + cmd_cmake + cmd_build
            runlogdump = tempfile.TemporaryFile("w+")
            execshellcmd_largedump(cmdexc, self.logFile, runlogdump, None)
            runlogdump.close()
        else:
            print("Kokkos already built..")

        return True

    def runtest(self, testnum):
        print("Running Kokkos Test..")
        cmdcd = "cd " + self.thistestpath + "/build;"
        if testnum == 0:
            cmdrun = "ctest -R;"
        elif testnum == 1:
            cmdrun = "./core/perf_test/KokkosCore_PerfTestExec;"
        cmdexc = cmdcd + cmdrun        
        env = os.environ.copy()
        self.runlog = tempfile.TemporaryFile("w+")
        execshellcmd_largedump(cmdexc, self.logFile, self.runlog, env)

    def clean(self):
        print("Cleaning Kokkos..")
        if self.runlog != None:
            self.runlog.close()

    def parse_result(self, testnum):
        return KokkosParser(self.runlog).parse(testnum)
