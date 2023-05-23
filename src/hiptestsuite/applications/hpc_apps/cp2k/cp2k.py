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
from hiptestsuite.applications.hpc_apps.cp2k.cp2k_build_amd import BuildRunAmd
from hiptestsuite.common.hip_get_packages import HipPackages
from hiptestsuite.common.hip_shell import execshellcmd_largedump

import os
import re
import tempfile

# Common class to clone, set up, build and run test
class PrepareTest():
    def __init__(self, cwd):
        self.cwdAbs = cwd
        self.app_path = os.path.join(self.cwdAbs,
                                     "src/hiptestsuite/applications/hpc_apps/",
                                     "cp2k/")
        self.thistestpath = self.app_path
        self.prepareobj = None
        self.apprepo = "" # Default
        self.appbranch = ""
        self.appcommitId = ""
        self.rocm_path = os.environ.get('ROCM_PATH')
        if not self.rocm_path:
            self.rocm_path = "/opt/rocm"
        self.gpu_version = None

    def pick_gpu(self):
        """Picks a GPU supported by the CP2K"""
        if self.gpu_version:
            return self.gpu_version

        selected_gpu = None
        cmd = self.rocm_path + "/bin/rocm_agent_enumerator"
        with tempfile.TemporaryFile("w+") as output:
            ret_code = execshellcmd_largedump(cmd, None, output, None)
            if ret_code != 0:
                return None
            output.seek(0)
            for line in output:
                # See cp2k/tools/toolchain/scripts/generate_arch_files.sh
                # for supported GPUs.
                if line.startswith("gfx90a"):
                    selected_gpu = "Mi250"
                elif line.startswith("gfx908"):
                    selected_gpu = "Mi100"
                elif line.startswith("gfx906"):
                    selected_gpu = "Mi50"

        self.gpu_version = selected_gpu
        return selected_gpu

    def set_cp2k_repoinfo(self, test_data: HIPTestData):
        validrepconfig = True
        if test_data.repos["cp2k"].repo_url != None:
            self.apprepo = test_data.repos["cp2k"].repo_url
        else:
            validrepconfig &= False
        if test_data.repos["cp2k"].branch != None:
            self.appbranch = test_data.repos["cp2k"].branch
        if test_data.repos["cp2k"].commit_id != None:
            self.appcommitId = test_data.repos["cp2k"].commit_id
        return validrepconfig

    def downloadtest(self, logFile, test_data: HIPTestData):
        ret = HipPackages().pull_repo(logFile, self.apprepo,
                                      self.appbranch, self.appcommitId, "cp2k")
        return ret

    def buildtest(self, logFile, platform):
        if platform == HIP_PLATFORM.amd:
            self.prepareobj = BuildRunAmd(self.thistestpath, logFile,
                                          self.rocm_path, self.pick_gpu())
        else:
            print("Unsupported Platform")
            return False
        return self.prepareobj.buildtest() == True

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

class CP2K(TestClassifier):
    def __init__(self):
        TestClassifier.__init__(self)

    def add_matched_with_names(self, matched_with_names: Union[None, dict] = None):
        TestClassifier.add_matched_with_names(self, {"cp2k": matched_with_names})

class AllRegressionTests(CP2K):
    def __init__(self):
        CP2K.__init__(self)

    def add_matched_with_names(self, matched_with_names: Union[None, dict] = None):
        CP2K.add_matched_with_names(self, {"all-tests": matched_with_names})

# Cp2k Unit/Regression Test
class CP2K_UNIT_TEST(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        classifier = AllRegressionTests()
        classifier.add_matched_with_names()
        test.classifiers = [classifier]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== CP2K Unit test ===============")
        if test_data.HIP_PLATFORM != HIP_PLATFORM.amd:
            print("CP2K test is not supported on NVIDIA")
            test_data.test_result = TestResult.SKIP
            return
        if not self.pick_gpu():
            print("Could not find supported GPU version.")
            test_data.test_result = TestResult.SKIP
            return

        # Set repo info
        isrepocfgvalid =  self.set_cp2k_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + "/cp2k_unit.log", 'w+') as testLogger:
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

