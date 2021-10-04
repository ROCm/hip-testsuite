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

from hiptestsuite.TesterRepository import Tester, Test, TestData
from hiptestsuite.Test import HIPTestData, TestResult, HIP_PLATFORM
from typing import Union, List
from hiptestsuite.test_classifier import TestClassifier
from hiptestsuite.applications.keccaktreegpu.keccaktreegpu_build_amd import BuildRunAmd
from hiptestsuite.applications.keccaktreegpu.keccaktreegpu_build_nvidia import BuildRunNvidia
from hiptestsuite.common.hip_get_packages import HipPackages
from hiptestsuite.common.hip_shell import execshellcmd

import os
import re
# Common class to clone, set up, build and run test
class PrepareTest():
    def __init__(self, cwd, binary):
        self.cwdAbs = cwd
        self.binary = binary
        self.app_path = os.path.join(self.cwdAbs,\
        "src/hiptestsuite/applications/keccaktreegpu/KeccakTreeGpu/")
        self.thistestpath = self.app_path
        self.prepareobj = None

    def buildtest(self, logFile, platform):
        isBinaryPresent = True
        if platform == HIP_PLATFORM.nvidia:
            self.prepareobj = BuildRunNvidia(self.thistestpath, logFile, self.binary)
        elif platform == HIP_PLATFORM.amd:
            self.prepareobj = BuildRunAmd(self.thistestpath, logFile, self.binary)
        else:
            print("Invalid Platform")
            return False
        self.prepareobj.buildtest()

        if not os.path.isfile(\
        os.path.join(self.thistestpath, self.binary)):
            isBinaryPresent &= False
        return isBinaryPresent

    def clean(self):
        if self.prepareobj != None:
            self.prepareobj.clean()

    def runtest(self):
        if self.prepareobj != None:
            self.prepareobj.runtest()

    def parse_result(self):
        if self.prepareobj != None:
            return self.prepareobj.parse_result()
        return False

class KECCAKTREEGPU(TestClassifier):
    def __init__(self):
        TestClassifier.__init__(self)

    def add_matched_with_names(self, matched_with_names: Union[None, dict] = None):
        TestClassifier.add_matched_with_names(self, {"keccaktreegpu": matched_with_names})

class PERFORMANCE(KECCAKTREEGPU):
    def __init__(self):
        KECCAKTREEGPU.__init__(self)

    def add_matched_with_names(self, matched_with_names: Union[None, dict] = None):
        KECCAKTREEGPU.add_matched_with_names(self, {"performance": matched_with_names})


# Test keccaktreetest
class keccaktreetest(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, self.cwd, "LinKeccakTree")

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        perf = PERFORMANCE()
        perf.add_matched_with_names()
        test.classifiers = [perf]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== keccaktreetest Test ===============")
        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + "/keccaktreetest.log", 'w+') as testLogger:
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            self.runtest()
            # Parse the test result
            if True == self.parse_result():
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL
