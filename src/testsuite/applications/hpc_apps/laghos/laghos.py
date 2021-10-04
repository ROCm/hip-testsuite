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
from testsuite.applications.hpc_apps.laghos.laghos_build_amd import BuildRunAmd
from testsuite.common.hip_get_packages import HipPackages
from testsuite.common.hip_shell import execshellcmd

import os
import re
# Common class to clone, set up, build and run test
class PrepareTest():
    def __init__(self, cwd):
        self.cwdAbs = cwd
        self.app_path = os.path.join(self.cwdAbs,\
        "src/testsuite/applications/hpc_apps/laghos/")
        self.thistestpath = self.app_path
        self.prepareobj = None

        self.laghos_repo = "" # Default
        self.laghos_branch = ""
        self.laghos_commitId = ""

        self.openmpi_repo = "" # Default
        self.openmpi_branch = ""
        self.openmpi_commitId = ""

        self.mfem_repo = "" # Default
        self.mfem_branch = ""
        self.mfem_commitId = ""

    def set_laghos_repoinfo(self, test_data: HIPTestData):
        validrepconfig = True
        if test_data.repos["mfem"].repo_url != None:
            self.mfem_repo = test_data.repos["mfem"].repo_url
        else:
            validrepconfig &= False
        if test_data.repos["mfem"].branch != None:
            self.mfem_branch = test_data.repos["mfem"].branch
        if test_data.repos["mfem"].commit_id != None:
            self.mfem_commitId = test_data.repos["mfem"].commit_id

        if test_data.repos["Laghos"].repo_url != None:
            self.laghos_repo = test_data.repos["Laghos"].repo_url
        else:
            validrepconfig &= False
        if test_data.repos["Laghos"].branch != None:
            self.laghos_branch = test_data.repos["Laghos"].branch
        if test_data.repos["Laghos"].commit_id != None:
            self.laghos_commitId = test_data.repos["Laghos"].commit_id

        if test_data.repos["openmpi"].repo_url != None:
            self.openmpi_repo = test_data.repos["openmpi"].repo_url
        else:
            validrepconfig &= False
        if test_data.repos["openmpi"].branch != None:
            self.openmpi_branch = test_data.repos["openmpi"].branch
        if test_data.repos["openmpi"].commit_id != None:
            self.openmpi_commitId = test_data.repos["openmpi"].commit_id

        return validrepconfig

    def downloadtest(self, logFile, test_data: HIPTestData):
        ret = True
        ret = ret & HipPackages().pull_repo(logFile, self.mfem_repo,\
        self.mfem_branch, self.mfem_commitId, "mfem")
        ret = ret & HipPackages().pull_repo(logFile, self.laghos_repo,\
        self.laghos_branch, self.laghos_commitId, "Laghos")
        ret = ret & HipPackages().pull_repo(logFile, self.openmpi_repo,\
        self.openmpi_branch, self.openmpi_commitId, "openmpi")
        return ret

    def buildtest(self, logFile, test_data: HIPTestData, platform):
        if platform == HIP_PLATFORM.amd:
            self.prepareobj = BuildRunAmd(self.thistestpath, logFile)
        else:
            print("Invalid Platform")
            return False
        buildstatus = self.prepareobj.buildtest(test_data)
        if buildstatus == False:
            return False

        return True

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

class LAGHOS(TestClassifier):
    def __init__(self):
        TestClassifier.__init__(self)

    def add_matched_with_names(self, matched_with_names: Union[None, dict] = None):
        TestClassifier.add_matched_with_names(self, {"laghos": matched_with_names})

class PERFORMANCE(LAGHOS):
    def __init__(self):
        LAGHOS.__init__(self)

    def add_matched_with_names(self, matched_with_names: Union[None, dict] = None):
        LAGHOS.add_matched_with_names(self, {"performance": matched_with_names})

# cube01_hex test
class LAGHOS_CUBE01_HEX(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, self.cwd)

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
        print("=============== Laghos cube01_hex test ===============")
        if test_data.HIP_PLATFORM == HIP_PLATFORM.nvidia:
            print("Laghos test is not supported on NVIDIA")
            test_data.test_result = TestResult.SKIP
            return
        # Set repo info
        isrepocfgvalid =  self.set_laghos_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + "/cube01_hex.log", 'w+') as testLogger:
            res = self.downloadtest(testLogger, test_data)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data, test_data.HIP_PLATFORM)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            self.runtest(0)
            # Parse the test result
            if True == self.parse_result(0):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL

# cube_12_hex test
class LAGHOS_CUBE_12_HEX(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, self.cwd)

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
        print("=============== Laghos cube_12_hex test ===============")
        if test_data.HIP_PLATFORM == HIP_PLATFORM.nvidia:
            print("Laghos test is not supported on NVIDIA")
            test_data.test_result = TestResult.SKIP
            return
        # Set repo info
        isrepocfgvalid =  self.set_laghos_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + "/cube_12_hex.log", 'w+') as testLogger:
            res = self.downloadtest(testLogger, test_data)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data, test_data.HIP_PLATFORM)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            self.runtest(1)
            # Parse the test result
            if True == self.parse_result(1):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL
