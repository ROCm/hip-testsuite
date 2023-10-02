# Copyright (c) 2023 Advanced Micro Devices, Inc. All rights reserved.
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

from hiptestsuite.TesterRepository import Tester, Test, TestData
from hiptestsuite.Test import HIPTestData, TestResult, HIP_PLATFORM
from typing import Union, List
from hiptestsuite.test_classifier import TestClassifier
from hiptestsuite.applications.hpc_apps.adept.adept_build_amd import BuildRunAmd
from hiptestsuite.common.hip_get_packages import HipPackages

import os

# Common class to clone, set up, build and run test
class PrepareTest():
    def __init__(self, cwd):
        self.cwdAbs = cwd
        self.app_path = os.path.join(self.cwdAbs, "src/hiptestsuite",
                                     "applications/hpc_apps/adept/")
        self.repo_dir = os.path.join(self.app_path, "ADEPT/")
        self.prepareobj = None
        self.apprepo = "" # Default
        self.appbranch = ""
        self.appcommitId = ""

    def set_adept_repoinfo(self, test_data: HIPTestData):
        validrepconfig = True
        if test_data.repos["ADEPT"].repo_url != None:
            self.apprepo = test_data.repos["ADEPT"].repo_url
        else:
            validrepconfig &= False
        if test_data.repos["ADEPT"].branch != None:
            self.appbranch = test_data.repos["ADEPT"].branch
        if test_data.repos["ADEPT"].commit_id != None:
            self.appcommitId = test_data.repos["ADEPT"].commit_id
        return validrepconfig

    def downloadtest(self, logFile, test_data: HIPTestData):
        return HipPackages().pull_repo(logFile, self.apprepo, self.appbranch,
                                       self.appcommitId, "ADEPT")

    def buildtest(self, logFile, platform):
        if platform == HIP_PLATFORM.amd:
            self.prepareobj = BuildRunAmd(self.repo_dir, logFile)
            buildstatus = self.prepareobj.buildtest()
            return buildstatus == True

        print("Invalid Platform")
        return False

    def clean(self):
        if self.prepareobj != None:
            self.prepareobj.clean()

    def runtest(self, testnum):
        if self.prepareobj != None:
            self.prepareobj.runtest(testnum)

    def parse_result(self, testnum):
        if self.prepareobj != None:
            return self.prepareobj.parse_result(testnum)
        return False

class ADEPT(TestClassifier):
    def __init__(self):
        TestClassifier.__init__(self)

    def add_matched_with_names(self,
                               matched_with_names: Union[None, dict] = None):
        TestClassifier.add_matched_with_names(self,
                                              {"adept": matched_with_names})

class MINIAPP(ADEPT):
    def __init__(self):
        ADEPT.__init__(self)

    def add_matched_with_names(self,
                               matched_with_names: Union[None, dict] = None):
        ADEPT.add_matched_with_names(self, {"mini-app": matched_with_names})

# Adept Unit/Regression Test
class ADEPT_UNIT_TEST(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        classifier = MINIAPP()
        classifier.add_matched_with_names()
        test.classifiers = [classifier]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== ADEPT Unit test ===============")
        if test_data.HIP_PLATFORM != HIP_PLATFORM.amd:
            print("ADEPT test is not supported on the requested platform")
            test_data.test_result = TestResult.SKIP
            return
        # Set repo info
        if not self.set_adept_repoinfo(test_data):
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + "/adept_unit.log", 'w+') as testLogger:
            res = self.downloadtest(testLogger, test_data)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            self.runtest(0)
            # Parse the test result
            if True == self.parse_result(0):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL

