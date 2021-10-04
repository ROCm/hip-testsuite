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
from testsuite.applications.hpc_apps.gridtools.gridtools_build_amd import BuildRunAmd
from testsuite.common.hip_get_packages import HipPackages
from testsuite.common.hip_shell import execshellcmd

import os
import re
# Common class to clone, set up, build and run test
class PrepareTest():
    def __init__(self, cwd):
        self.cwdAbs = cwd
        self.app_path = os.path.join(self.cwdAbs,\
        "src/testsuite/applications/hpc_apps/gridtools")
        self.thistestpath = self.app_path
        self.prepareobj = None
        self.gridtoolsrepo = "" # Default
        self.gridtoolsbranch = ""
        self.gridtoolscommitId = ""
        self.gtbenchrepo = "" # Default
        self.gtbenchbranch = ""
        self.gtbenchcommitId = ""

    def set_gridtools_repoinfo(self, test_data: HIPTestData):
        validrepconfig = True
        if test_data.repos["gridtools"].repo_url != None:
            self.gridtoolsrepo = test_data.repos["gridtools"].repo_url
        else:
            validrepconfig &= False
        if test_data.repos["gridtools"].branch != None:
            self.gridtoolsbranch = test_data.repos["gridtools"].branch
        if test_data.repos["gridtools"].commit_id != None:
            self.gridtoolscommitId = test_data.repos["gridtools"].commit_id
        return validrepconfig

    def set_gtbench_repoinfo(self, test_data: HIPTestData):
        validrepconfig = True
        if test_data.repos["gtbench"].repo_url != None:
            self.gtbenchrepo = test_data.repos["gtbench"].repo_url
        else:
            validrepconfig &= False
        if test_data.repos["gtbench"].branch != None:
            self.gtbenchbranch = test_data.repos["gtbench"].branch
        if test_data.repos["gtbench"].commit_id != None:
            self.gtbenchcommitId = test_data.repos["gtbench"].commit_id
        return validrepconfig

    def downloadtest(self, logFile, test_data: HIPTestData):
        ret = True
        ret = ret & HipPackages().pull_repo(logFile, self.gridtoolsrepo,\
        self.gridtoolsbranch, self.gridtoolscommitId, "gridtools")
        ret = ret & HipPackages().pull_repo(logFile, self.gtbenchrepo,\
        self.gtbenchbranch, self.gtbenchcommitId, "gtbench")
        return ret

    def buildtest(self, logFile, platform):
        isBinaryPresent = True
        if platform == HIP_PLATFORM.amd:
            self.prepareobj = BuildRunAmd(self.thistestpath, logFile)
        else:
            print("Invalid Platform")
            return False
        buildstatus = self.prepareobj.buildtest()
        return buildstatus

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

class GDTOOLS(TestClassifier):
    def __init__(self):
        TestClassifier.__init__(self)

    def add_matched_with_names(self, matched_with_names: Union[None, dict] = None):
        TestClassifier.add_matched_with_names(self, {"gridtools": matched_with_names})

class PERFORMANCE(GDTOOLS):
    def __init__(self):
        GDTOOLS.__init__(self)

    def add_matched_with_names(self, matched_with_names: Union[None, dict] = None):
        GDTOOLS.add_matched_with_names(self, {"performance": matched_with_names})

# Gridtool Convergence Test
class GRIDTOOLSCONVG(Tester, PrepareTest):
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
        print("=============== Gridtool Convergence Test ===============")
        if test_data.HIP_PLATFORM == HIP_PLATFORM.nvidia:
            print("Gridtool Convergence Test is not supported on NVIDIA")
            test_data.test_result = TestResult.SKIP
            return
        # Check if Boost package exists
        if not os.path.isfile(\
        os.path.join(self.thistestpath, "boost_1_72_0.tar.bz2")):
            print("Boost Package boost_1_72_0.tar.bz2 not available under src/testsuite/applications/hpc_apps/gridtools/.")
            print("Please download and copy Boost package in src/testsuite/applications/hpc_apps/gridtools folder.")
            test_data.test_result = TestResult.ERROR
            return
        # Create GT_TREE_DIR
        gt_tree_dir = os.path.join(self.thistestpath, "GridTools")
        if not os.path.exists(gt_tree_dir):
            os.mkdir(gt_tree_dir)
        # Set repo info
        isrepocfgvalid =  self.set_gridtools_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        isrepocfgvalid =  self.set_gtbench_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + "/gridtoolsconv.log", 'w+') as testLogger:
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

# Gridtool PERFORMANCE Test
class GRIDTOOLSPERF(Tester, PrepareTest):
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
        print("=============== Gridtool Perf Test ===============")
        if test_data.HIP_PLATFORM == HIP_PLATFORM.nvidia:
            print("Gridtool Perf Test is not supported on NVIDIA")
            test_data.test_result = TestResult.SKIP
            return
        # Check if Boost package exists
        if not os.path.isfile(\
        os.path.join(self.thistestpath, "boost_1_72_0.tar.bz2")):
            print("Boost Package boost_1_72_0.tar.bz2 not available under src/testsuite/applications/hpc_apps/gridtools/.")
            print("Please download and copy Boost package in src/testsuite/applications/hpc_apps/gridtools folder.")
            test_data.test_result = TestResult.ERROR
            return

        # Create GT_TREE_DIR
        gt_tree_dir = os.path.join(self.thistestpath, "GridTools")
        if not os.path.exists(gt_tree_dir):
            os.mkdir(gt_tree_dir)

        # Set repo info
        isrepocfgvalid =  self.set_gridtools_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        isrepocfgvalid =  self.set_gtbench_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return

        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + "/gridtoolsperf.log", 'w+') as testLogger:
            res = self.downloadtest(testLogger, test_data)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            self.runtest(1)
            # Parse the test result
            if True == self.parse_result(1):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL
