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
from hiptestsuite.applications.hpc_apps.quicksilver.quicksilver_build_amd import BuildRunAmd
from hiptestsuite.applications.hpc_apps.quicksilver.quicksilver_build_nvidia import BuildRunNvidia
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
        "src/hiptestsuite/applications/hpc_apps/quicksilver/")
        self.app_root = os.path.join(self.app_path, "Quicksilver/")
        self.thistestpath = self.app_root
        self.prepareobj = None
        self.apprepo = "" # Default
        self.appbranch = ""
        self.appcommitId = ""

    def set_quicksilver_repoinfo(self, test_data: HIPTestData):
        validrepconfig = True
        if test_data.repos["quicksilver"].repo_url != None:
            self.apprepo = test_data.repos["quicksilver"].repo_url
        else:
            validrepconfig &= False
        if test_data.repos["quicksilver"].branch != None:
            self.appbranch = test_data.repos["quicksilver"].branch
        if test_data.repos["quicksilver"].commit_id != None:
            self.appcommitId = test_data.repos["quicksilver"].commit_id
        return validrepconfig

    def downloadtest(self, logFile, test_data: HIPTestData):
        ret = True
        ret = ret & HipPackages().pull_repo(logFile, self.apprepo,\
        self.appbranch, self.appcommitId, "quicksilver")
        return ret

    def buildtest(self, logFile, platform, cuda_target):
        isBinaryPresent = True
        if platform == HIP_PLATFORM.amd:
            self.prepareobj = BuildRunAmd(self.thistestpath, logFile)
        elif platform == HIP_PLATFORM.nvidia:
            self.prepareobj = BuildRunNvidia(self.thistestpath, logFile, cuda_target)
        else:
            print("Invalid Platform")
            return False

        buildstatus = self.prepareobj.buildtest()
        if buildstatus == False:
            return False
        # Check if test binary is created
        binarypath = os.path.join(self.thistestpath, "src")
        if not os.path.isfile(\
        os.path.join(binarypath, self.binary)):
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

class QUICKSILVER(TestClassifier):
    def __init__(self):
        TestClassifier.__init__(self)

    def add_matched_with_names(self, matched_with_names: Union[None, dict] = None):
        TestClassifier.add_matched_with_names(self, {"quicksilver": matched_with_names})

class PERFORMANCE(QUICKSILVER):
    def __init__(self):
        QUICKSILVER.__init__(self)

    def add_matched_with_names(self, matched_with_names: Union[None, dict] = None):
        QUICKSILVER.add_matched_with_names(self, {"performance": matched_with_names})


# Quicksilver test
class QUICKSILVERTEST(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, self.cwd, "qs")

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        classifier = PERFORMANCE()
        classifier.add_matched_with_names()
        test.classifiers = [classifier]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== Quicksilver test ===============")
        # Set repo info
        isrepocfgvalid =  self.set_quicksilver_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + "/qs.log", 'w+') as testLogger:
            res = self.downloadtest(testLogger, test_data)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM, test_data.build_for_cuda_target)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            self.runtest()
            # Parse the test result
            if True == self.parse_result():
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL
