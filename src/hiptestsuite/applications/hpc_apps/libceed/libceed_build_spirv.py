# Copyright (c) 2021 Advanced Micro Devices, Inc. All rights reserved.
# Copyright (c) 2023 Intel Finland Oy. All rights reserved.
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
from hiptestsuite.applications.hpc_apps.libceed.libceed_parser_common import LibceedParser


class BuildRunSpirv():

    def __init__(self, thistestpath, logFile):
        self.thistestpath = thistestpath
        self.logFile = logFile
        self.runlog = None

    def configure_build_libceed(self):
        path_check = os.path.join(self.thistestpath, "lib/libceed.so")
        if os.path.exists(path_check):
            print("libceed already built at ", path_check)
            return True
        make_variables = "FORTRAN=0 "

        if os.environ.get('LLVM_DIR'):
            make_variables += " CXX="
            make_variables += os.environ.get('LLVM_DIR')
            make_variables += "/bin/clang++"
            make_variables += " CC="
            make_variables += os.environ.get('LLVM_DIR')
            make_variables += "/bin/clang"
        else:
            print("set env variable LLVM_DIR to a Clang+LLVM build usable with CHIP-SPV")
            return False

        if os.environ.get('HIP_DIR'):
            make_variables += " HIP_DIR="
            make_variables += os.environ.get('HIP_DIR')
            make_variables += " HIPBLAS_LIB_DIR="
            make_variables += os.environ.get('HIP_DIR')
            make_variables += "/lib"
        else:
            print("set env variable HIP_DIR to a CHIP-SPV build with its hipblas installed in HIP_DIR/lib")
            return False

        print("libceed build in progress ..")
        cmd = "cd " + self.thistestpath + " && "
        cmd += "make configure " + make_variables + " OPT='-O2 -march=native' && make"
        runlogdump = tempfile.TemporaryFile("w+")
        print("building using command: ", cmd)
        execshellcmd_largedump(cmd, self.logFile, runlogdump, None)
        runlogdump.close()
        if not os.path.exists(path_check):
            print("libceed Build Failed, not found at: ", path_check)
            return False
        return True

    def buildtest(self):
        if not self.configure_build_libceed():
            print("libceed configuration and build failed ..")
            return False
        return True

    def runtest(self, testnum):
        print("Running libCEED Test" + str(testnum))
        cmd = "cd " + self.thistestpath + " && "
        cmd += "make BACKENDS=/gpu/hip/shared search=t3 exclude=t319 test"
        env = os.environ.copy()
        # TODO ifdef out?
        env["CHIP_BE"] = "level0"
        env["CHIP_LOGLEVEL"] = "err"
        env["CHIP_DEVICE_TYPE"] = "gpu"
        self.runlog = tempfile.TemporaryFile("w+")
        execshellcmd_largedump(cmd, self.logFile, self.runlog, env)

    def clean(self):
        print("Cleaning libceed..")
        if self.runlog != None:
            self.runlog.close()

    def parse_result(self, testnum):
        return LibceedParser(self.runlog).parse(testnum)
