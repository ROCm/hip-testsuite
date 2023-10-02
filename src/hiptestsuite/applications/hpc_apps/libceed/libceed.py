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

from hiptestsuite.TesterRepository import Tester, Test, TestData
from hiptestsuite.Test import HIPTestData, TestResult, HIP_PLATFORM
from typing import Union, List
from hiptestsuite.test_classifier import TestClassifier
from hiptestsuite.applications.hpc_apps.libceed.libceed_build_amd import BuildRunAmd
from hiptestsuite.common.hip_get_packages import HipPackages
from hiptestsuite.common.hip_shell import execshellcmd

import os
import re

# Common class to clone, set up, build and run test
class PrepareTest():
    def __init__(self, cwd):
        self.cwdAbs = cwd
        self.app_path = os.path.join(self.cwdAbs,\
        "src/hiptestsuite/applications/hpc_apps/libceed/libCEED")
        self.thistestpath = self.app_path
        self.prepareobj = None
        self.libceed_repo = "" # Default
        self.libceed_branch = ""
        self.libceed_commitId = ""

    def set_libceed_repoinfo(self, test_data: HIPTestData):
        validrepconfig = True
        if test_data.repos["libCEED"].repo_url != None:
            self.libceed_repo = test_data.repos["libCEED"].repo_url
        else:
            print("invalid config: no repo")
            validrepconfig = False
        if test_data.repos["libCEED"].branch != None:
            self.libceed_branch = test_data.repos["libCEED"].branch
        if test_data.repos["libCEED"].commit_id != None:
            self.libceed_commitId = test_data.repos["libCEED"].commit_id
        return validrepconfig

    def downloadtest(self, logFile, test_data: HIPTestData):
        return HipPackages().pull_repo(logFile, self.libceed_repo,\
        self.libceed_branch, self.libceed_commitId, "libCEED")

    def buildtest(self, logFile, platform, cuda_target):
        if platform == HIP_PLATFORM.amd:
            self.prepareobj = BuildRunAmd(self.thistestpath, logFile)
        else:
            print("Invalid/Unsupported Platform")
            return False
        if not self.prepareobj:
            return False
        return self.prepareobj.buildtest()

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

class LIBCEED(TestClassifier):
    def __init__(self):
        TestClassifier.__init__(self)

    def add_matched_with_names(self, matched_with_names: Union[None, dict] = None):
        TestClassifier.add_matched_with_names(self, {"libceed": matched_with_names})

class UNIT(TestClassifier):
    def __init__(self):
        LIBCEED.__init__(self)

    def add_matched_with_names(self, matched_with_names: Union[None, dict] = None):
        LIBCEED.add_matched_with_names(self, {"libceed": matched_with_names})

class LIBCEED_UNIT_TEST(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        classifier = UNIT()
        classifier.add_matched_with_names()
        test.classifiers = [classifier]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== libCEED UNIT test ===============")
        # Set repo info
        isrepocfgvalid =  self.set_libceed_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return

        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + "/libceed_unit.log", 'w+') as testLogger:
            res = self.downloadtest(testLogger, test_data)
            test_data.test_result = TestResult.FAIL
            if not res:
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM, test_data.build_for_cuda_target)
            if not res:
                return
            self.runtest(1)
            # Parse the test result
            if self.parse_result(1):
                test_data.test_result = TestResult.PASS

