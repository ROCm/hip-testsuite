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

from testsuite.TesterRepository import Tester, Test, TestData
from testsuite.Test import HIPTestData, TestResult, HIP_PLATFORM
from typing import Union, List
from testsuite.test_classifier import TestClassifier
from testsuite.applications.mgbench.mgbench_build_amd import BuildRunAmd
from testsuite.applications.mgbench.mgbench_build_nvidia import BuildRunNvidia
from testsuite.common.hip_get_packages import HipPackages
from testsuite.common.hip_shell import execshellcmd

import os
import re
# Common class to clone, set up, build and run test
class PrepareTest():
    def __init__(self, cwd, testpath, mgtestfile, binary):
        self.cwdAbs = cwd
        self.mgtestfile = mgtestfile
        self.binary = binary
        self.app_path = os.path.join(self.cwdAbs,\
        "src/testsuite/applications/mgbench/")
        self.app_root = os.path.join(self.app_path, "mgbench/")
        self.thistestpath = os.path.join(self.app_root, testpath)
        self.prepareobj = None
        self.apprepo = "" # Default
        self.appbranch = ""
        self.appcommitId = ""

    def set_mgbench_repoinfo(self, test_data: HIPTestData):
        validrepconfig = True
        if test_data.repos["mgbench"].repo_url != None:
            self.apprepo = test_data.repos["mgbench"].repo_url
        else:
            validrepconfig &= False
        if test_data.repos["mgbench"].branch != None:
            self.appbranch = test_data.repos["mgbench"].branch
        if test_data.repos["mgbench"].commit_id != None:
            self.appcommitId = test_data.repos["mgbench"].commit_id
        return validrepconfig

    def downloadtest(self, logFile, test_data: HIPTestData):
        ret = HipPackages().pull_repo(logFile, self.apprepo,\
        self.appbranch, self.appcommitId, "mgbench")
        return ret

    def buildtest(self, logFile, platform):
        isBinaryPresent = True
        if platform == HIP_PLATFORM.nvidia:
            self.prepareobj = BuildRunNvidia(self.app_root, self.thistestpath, logFile, self.mgtestfile, self.binary)
        elif platform == HIP_PLATFORM.amd:
            self.prepareobj = BuildRunAmd(self.app_root, self.thistestpath, logFile, self.mgtestfile, self.binary)
        else:
            print("Invalid Platform")
            return False
        buildstatus = self.prepareobj.buildtest()
        if buildstatus == False:
            return False
        # Check if test binary is created
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

    def parse_result(self, test):
        if self.prepareobj != None:
            return self.prepareobj.parse_result(test)
        return False

class MGBENCH(TestClassifier):
    def __init__(self):
        TestClassifier.__init__(self)

    def add_matched_with_names(self, matched_with_names: Union[None, dict] = None):
        TestClassifier.add_matched_with_names(self, {"mgbench": matched_with_names})

class PERFORMANCE(MGBENCH):
    def __init__(self):
        MGBENCH.__init__(self)

    def add_matched_with_names(self, matched_with_names: Union[None, dict] = None):
        MGBENCH.add_matched_with_names(self, {"performance": matched_with_names})


# Test src/L1/fullduplex
class mgbench_fullduplex(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, self.cwd, "src/L1/", "fullduplex.cpp", "fullduplex")

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
        print("=============== mgbench_fullduplex Test ===============")
        # Set repo info
        isrepocfgvalid =  self.set_mgbench_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + "/mgbench_fullduplex.log", 'w+') as testLogger:
            res = self.downloadtest(testLogger, test_data)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            self.runtest()
            # Parse the test result
            if True == self.parse_result("fullduplex"):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test src/L1/halfduplex
class mgbench_halfduplex(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, self.cwd, "src/L1/", "halfduplex.cpp", "halfduplex")

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
        print("=============== mgbench_halfduplex Test ===============")
        # Set repo info
        isrepocfgvalid =  self.set_mgbench_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + "/mgbench_halfduplex.log", 'w+') as testLogger:
            res = self.downloadtest(testLogger, test_data)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            self.runtest()
            # Parse the test result
            if True == self.parse_result("halfduplex"):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test src/L1/uva
class mgbench_uva(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, self.cwd, "src/L1/", "uva.cu", "uva")

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
        print("=============== mgbench_uva Test ===============")
        # Set repo info
        isrepocfgvalid =  self.set_mgbench_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + "/mgbench_uva.log", 'w+') as testLogger:
            res = self.downloadtest(testLogger, test_data)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            self.runtest()
            # Parse the test result
            if True == self.parse_result("uva"):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL
