# Copyright (c) 2021-present Advanced Micro Devices, Inc. All rights reserved.
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

from amd.TesterRepository import Tester
from amd.Test import HIPTestData, TestResult, Test, HIPBuildData, HIP_PLATFORM
from typing import Union, List
from amd.conformance.conformance_test_classifier import CONFORMANCE
from amd.test_classifier import TestClassifier
from amd.conformance.hip_dtest_build import BuildRunAmd, BuildRunNvidia
from amd.common.hip_get_packages import HipPackages
from amd.common.hip_shell import *

import os

# Common class to clone, set up, build and run test
class PrepareTest():
    def __init__(self):
        self.hiprepo = "" # Default
        self.hipbranch = ""
        self.hipcommitId = ""
        self.rocclrrepo = "" # Default
        self.rocclrbranch = ""
        self.rocclrcommitId = ""
        self.openclrepo = "" # Default
        self.openclbranch = ""
        self.openclcommitId = ""
        self.logfd = None
        self.downloadresult = True
        self.buildresult = True
        self.buildobj = None

    # Get the GIT repo information from configuration input
    def setrepoinfo(self, test_data: HIPBuildData):
        if test_data.repos["hip"].repo_url != None:
            self.hiprepo = test_data.repos["hip"].repo_url
        else:
            return False
        if test_data.repos["hip"].branch != None:
            self.hipbranch = test_data.repos["hip"].branch
        if test_data.repos["hip"].commit_id != None:
            self.hipcommitId = test_data.repos["hip"].commit_id
        if test_data.repos["rocclr"].repo_url != None:
            self.rocclrrepo = test_data.repos["rocclr"].repo_url
        else:
            return False
        if test_data.repos["rocclr"].branch != None:
            self.rocclrbranch = test_data.repos["rocclr"].branch
        if test_data.repos["rocclr"].commit_id != None:
            self.rocclrcommitId = test_data.repos["rocclr"].commit_id
        if test_data.repos["opencl"].repo_url != None:
            self.openclrepo = test_data.repos["opencl"].repo_url
        else:
            return False
        if test_data.repos["opencl"].branch != None:
            self.openclbranch = test_data.repos["opencl"].branch
        if test_data.repos["opencl"].commit_id != None:
            self.openclcommitId = test_data.repos["opencl"].commit_id
        return True

    # Download the relevant packages from GIT for this test
    def downloadTest(self, log, platform):
        ret = HipPackages().pull_repo(log, self.hiprepo, self.hipbranch,\
        self.hipcommitId, "HIP")
        if platform == HIP_PLATFORM.amd:
            ret &= HipPackages().pull_repo(log, self.rocclrrepo, self.rocclrbranch,\
            self.rocclrcommitId, "rocclr")
            ret &= HipPackages().pull_repo(log, self.openclrepo, self.openclbranch,\
            self.openclcommitId, "opencl")
        return ret

    # Build Packages
    def build_package(self, logFile, platform):
        status = True
        if platform == HIP_PLATFORM.nvidia:
            self.buildobj = BuildRunNvidia(logFile)
        elif platform == HIP_PLATFORM.amd:
            self.buildobj = BuildRunAmd(logFile)
        else:
            print("Invalid Platform")
            return False

        return self.buildobj.build_package()

    def clean(self):
        self.buildobj.clean()

    # Run test
    def runtest(self, logFile, testcase):
        return self.buildobj.runtest(logFile, testcase)

    # Get ctest info
    def get_ctest_list(self):
        return self.buildobj.get_all_ctest()


# Test HIP Dtest/
class Hipconformance(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        PrepareTest.__init__(self)

    def getTests(self, get_tests_data: HIPBuildData) -> List[Test]:
        # Set repo info
        testlist = []
        if get_tests_data.quick:
            return testlist
        self.logfd = open(get_tests_data.log_location + "/Hipconformance.log", 'w+')
        status = self.setrepoinfo(get_tests_data)
        if not status:
            self.downloadresult = False
            return testlist

        # Download repos
        self.downloadresult = self.downloadTest(self.logfd, get_tests_data.HIP_PLATFORM)
        if not self.downloadresult:
            print("Rocm packages download failed!")
            return testlist

        print("Building HIP package ...")
        # Build Rocclr and Hip
        self.buildresult = self.build_package(self.logfd, get_tests_data.HIP_PLATFORM)
        if not self.buildresult:
            print("Rocm packages build failed!")
            return testlist

        print("Building HIP package completed")
        # Fetch all the ctests
        dtestnamelist = self.get_ctest_list()

        for testname in dtestnamelist:
            test = Test()
            test.test_name = testname
            category = CONFORMANCE()
            category.add_matched_with_names()
            test.classifiers = [category]
            test.tester = self
            testlist.append(test)
        return testlist
    
    def get_test_classifiers(self) -> Union[None, List[TestClassifier]]:
        category = CONFORMANCE()
        category.add_matched_with_names()
        return [category]

    def test(self, test_data: HIPTestData):
        if not self.downloadresult:
            test_data.test_result = TestResult.FAIL
            return

        if not self.buildresult:
            test_data.test_result = TestResult.FAIL
            return
        # Build test
        print("Running test: " + test_data.test.test_name + "..........")
        testcase = test_data.test.test_name
        status = None

        with open(test_data.log_location + "/test.log", 'w+') as testLogger:
            status = self.runtest(testLogger, testcase)

        if status == "PASSED":
            test_data.test_result = TestResult.PASS
        elif status == "SKIP":
            test_data.test_result = TestResult.SKIP
        elif status == "FAILED":
            test_data.test_result = TestResult.FAIL

    def clean(self):
        PrepareTest.clean(self)
        if self.logfd != None:
            self.logfd.close()

