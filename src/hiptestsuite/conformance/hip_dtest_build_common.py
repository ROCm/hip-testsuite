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
import re
from hiptestsuite.common.hip_shell import execshellcmd_largedump, execshellcmd

class BuildRunCommon():
    '''
    In this class insert the build and execution steps for test cases
    which are identical across different platforms (amd/nvidia/intel).
    '''
    def __init__(self, logfile):
        self.logfile = logfile
        self.hippath = os.path.join(os.getcwd(), "src/hiptestsuite/conformance/HIP")
        self.ctest_file = os.path.join(self.hippath, "build/ctest.txt")
        self.builddir = os.path.join(self.hippath, "build")
        self.expected_catch_binaries = ["ABMTests","MultiProcTests","UnitTests"]

    # Validate if HIP build is successful
    def validate_hipcatch_build(self):
        status = True
        catch_binary_path = os.path.join(self.hippath, "build/hipTestMain")
        for catchbin in self.expected_catch_binaries:
            if not os.path.isfile(\
            os.path.join(catch_binary_path, catchbin)):
                print("Did not find catch2 binary " + catchbin)
                status &= False
        return status

    # Fetches all available dtests using ctest
    def get_all_ctest(self):
        if not os.path.isfile(self.ctest_file):
            cmdexc = "cd " + self.builddir + ";"
            cmdexc += "ctest -N;"
            with open(self.ctest_file, "w+") as ctestlog:
                execshellcmd_largedump(cmdexc, self.logfile, ctestlog, None)

        testlist = []
        with open(self.ctest_file, "r") as ctestlog:
            for test in ctestlog:
                if re.search("Test *#\d*:", test) != None:
                    dtest = re.sub("Test *#\d*: ", "", test)
                    dtest = re.sub("/", ".", dtest)
                    dtest = dtest.lstrip()
                    dtest = dtest.rstrip()
                    testlist.append(dtest)
        return testlist

    # Parse the test result
    def parsetest(self, log):
        log.seek(0)
        logbytes = log.read()
        logutf = logbytes.decode('utf-8', errors='ignore')
        status = None
        if re.search("100% tests passed", logutf) != None:
            status = "PASSED"
        else:
            status = "FAILED"
        return status

    # Execute the test case
    def runtest(self, log, verbosity, testcase, envtoset):
        if verbosity == 0:
            cmdtest = "ctest -R " + "\"" + testcase + "\""
        elif verbosity == 1:
            cmdtest = "ctest -R " + "\"" + testcase + "\"" + " --verbose"
        else:
            cmdtest = "ctest -R " + "\"" + testcase + "\""

        print("Executing command = " + cmdtest)
        # run test
        cmd = "cd " + self.builddir + ";"
        cmd += cmdtest + ";"
        runlogdump = tempfile.TemporaryFile("wb+")
        execshellcmd_largedump(cmd, log, runlogdump, envtoset)
        status = self.parsetest(runlogdump)
        runlogdump.close()
        return status
