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
from testsuite.applications.cuda_memtest.cuda_memtest_build_amd import BuildRunAmd
from testsuite.applications.cuda_memtest.cuda_memtest_build_nvidia import BuildRunNvidia
from testsuite.common.hip_get_packages import HipPackages
from testsuite.common.hip_shell import execshellcmd

import os
import re
# Common class to clone, set up, build and run test
class PrepareTest():
    def __init__(self, cwd, binary):
        self.cwdAbs = cwd
        self.binary = binary
        self.app_path = os.path.join(self.cwdAbs,\
        "src/testsuite/applications/cuda_memtest/")
        self.app_root = os.path.join(self.app_path, "cuda_memtest/")
        self.thistestpath = self.app_root
        self.prepareobj = None
        self.apprepo = "" # Default
        self.appbranch = ""
        self.appcommitId = ""

    def set_cudamemtest_repoinfo(self, test_data: HIPTestData):
        validrepconfig = True
        if test_data.repos["cuda_memtest"].repo_url != None:
            self.apprepo = test_data.repos["cuda_memtest"].repo_url
        else:
            validrepconfig &= False
        if test_data.repos["cuda_memtest"].branch != None:
            self.appbranch = test_data.repos["cuda_memtest"].branch
        if test_data.repos["cuda_memtest"].commit_id != None:
            self.appcommitId = test_data.repos["cuda_memtest"].commit_id
        return validrepconfig

    def downloadtest(self, logFile, test_data: HIPTestData):
        ret = HipPackages().pull_repo(logFile, self.apprepo,\
        self.appbranch, self.appcommitId, "cudamemtest")
        return ret

    def buildtest(self, logFile, platform):
        isBinaryPresent = True
        if platform == HIP_PLATFORM.nvidia:
            self.prepareobj = BuildRunNvidia(self.thistestpath, logFile, self.binary)
        elif platform == HIP_PLATFORM.amd:
            self.prepareobj = BuildRunAmd(self.thistestpath, logFile, self.binary)
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

    def runtest(self, testnum):
        if self.prepareobj != None:
            self.prepareobj.runtest(testnum)

    def parse_result(self):
        if self.prepareobj != None:
            return self.prepareobj.parse_result()
        return False

class CUDA_MEMTEST(TestClassifier):
    def __init__(self):
        TestClassifier.__init__(self)

    def add_matched_with_names(self, matched_with_names: Union[None, dict] = None):
        TestClassifier.add_matched_with_names(self, {"cuda_memtest": matched_with_names})

class STRESS(CUDA_MEMTEST):
    def __init__(self):
        CUDA_MEMTEST.__init__(self)

    def add_matched_with_names(self, matched_with_names: Union[None, dict] = None):
        CUDA_MEMTEST.add_matched_with_names(self, {"stress": matched_with_names})


# Test0 cuda_memtest
class cudamemtest0(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, self.cwd, "cuda_memtest")

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        classifier = STRESS()
        classifier.add_matched_with_names()
        test.classifiers = [classifier]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== cudamemtest0 ===============")
        # Set repo info
        isrepocfgvalid =  self.set_cudamemtest_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + "/cudamemtest0.log", 'w+') as testLogger:
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
            if True == self.parse_result():
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL

# Test1 cuda_memtest
class cudamemtest1(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, self.cwd, "cuda_memtest")

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        classifier = STRESS()
        classifier.add_matched_with_names()
        test.classifiers = [classifier]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== cudamemtest1 ===============")
        # Set repo info
        isrepocfgvalid =  self.set_cudamemtest_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + "/cudamemtest1.log", 'w+') as testLogger:
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
            if True == self.parse_result():
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL

# Test2 cuda_memtest
class cudamemtest2(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, self.cwd, "cuda_memtest")

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        classifier = STRESS()
        classifier.add_matched_with_names()
        test.classifiers = [classifier]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== cudamemtest2 ===============")
        # Set repo info
        isrepocfgvalid =  self.set_cudamemtest_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + "/cudamemtest2.log", 'w+') as testLogger:
            res = self.downloadtest(testLogger, test_data)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            self.runtest(2)
            # Parse the test result
            if True == self.parse_result():
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL

# Test3 cuda_memtest
class cudamemtest3(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, self.cwd, "cuda_memtest")

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        classifier = STRESS()
        classifier.add_matched_with_names()
        test.classifiers = [classifier]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== cudamemtest3 ===============")
        # Set repo info
        isrepocfgvalid =  self.set_cudamemtest_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + "/cudamemtest3.log", 'w+') as testLogger:
            res = self.downloadtest(testLogger, test_data)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            self.runtest(3)
            # Parse the test result
            if True == self.parse_result():
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL

# Test4 cuda_memtest
class cudamemtest4(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, self.cwd, "cuda_memtest")

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        classifier = STRESS()
        classifier.add_matched_with_names()
        test.classifiers = [classifier]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== cudamemtest4 ===============")
        # Set repo info
        isrepocfgvalid =  self.set_cudamemtest_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + "/cudamemtest4.log", 'w+') as testLogger:
            res = self.downloadtest(testLogger, test_data)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            self.runtest(4)
            # Parse the test result
            if True == self.parse_result():
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test5 cuda_memtest
class cudamemtest5(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, self.cwd, "cuda_memtest")

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        classifier = STRESS()
        classifier.add_matched_with_names()
        test.classifiers = [classifier]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== cudamemtest5 ===============")
        # Set repo info
        isrepocfgvalid =  self.set_cudamemtest_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + "/cudamemtest5.log", 'w+') as testLogger:
            res = self.downloadtest(testLogger, test_data)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            self.runtest(5)
            # Parse the test result
            if True == self.parse_result():
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test6 cuda_memtest
class cudamemtest6(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, self.cwd, "cuda_memtest")

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        classifier = STRESS()
        classifier.add_matched_with_names()
        test.classifiers = [classifier]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== cudamemtest6 ===============")
        if False:
            # Set repo info
            isrepocfgvalid =  self.set_cudamemtest_repoinfo(test_data)
            if not isrepocfgvalid:
                test_data.test_result = TestResult.ERROR
                return
            # Create the log directory
            resultLogDir = test_data.log_location
            with open(resultLogDir + "/cudamemtest6.log", 'w+') as testLogger:
                res = self.downloadtest(testLogger, test_data)
                if not res:
                    test_data.test_result = TestResult.FAIL
                    return
                res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
                if not res:
                    test_data.test_result = TestResult.FAIL
                    return
                self.runtest(6)
                # Parse the test result
                if True == self.parse_result():
                    test_data.test_result = TestResult.PASS
                else:
                    test_data.test_result = TestResult.FAIL
        else:
            test_data.test_result = TestResult.SKIP

# Test7 cuda_memtest
class cudamemtest7(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, self.cwd, "cuda_memtest")

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        classifier = STRESS()
        classifier.add_matched_with_names()
        test.classifiers = [classifier]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== cudamemtest7 ===============")
        # Set repo info
        isrepocfgvalid =  self.set_cudamemtest_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + "/cudamemtest7.log", 'w+') as testLogger:
            res = self.downloadtest(testLogger, test_data)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            self.runtest(7)
            # Parse the test result
            if True == self.parse_result():
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test8 cuda_memtest
class cudamemtest8(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, self.cwd, "cuda_memtest")

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        classifier = STRESS()
        classifier.add_matched_with_names()
        test.classifiers = [classifier]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== cudamemtest8 ===============")
        # Set repo info
        isrepocfgvalid =  self.set_cudamemtest_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + "/cudamemtest8.log", 'w+') as testLogger:
            res = self.downloadtest(testLogger, test_data)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            self.runtest(8)
            # Parse the test result
            if True == self.parse_result():
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test9 cuda_memtest
class cudamemtest9(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, self.cwd, "cuda_memtest")

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        classifier = STRESS()
        classifier.add_matched_with_names()
        test.classifiers = [classifier]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== cudamemtest9 ===============")
        if False:
            # Set repo info
            isrepocfgvalid =  self.set_cudamemtest_repoinfo(test_data)
            if not isrepocfgvalid:
                test_data.test_result = TestResult.ERROR
                return
            # Create the log directory
            resultLogDir = test_data.log_location
            with open(resultLogDir + "/cudamemtest9.log", 'w+') as testLogger:
                res = self.downloadtest(testLogger, test_data)
                if not res:
                    test_data.test_result = TestResult.FAIL
                    return
                res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
                if not res:
                    test_data.test_result = TestResult.FAIL
                    return
                self.runtest(9)
                # Parse the test result
                if True == self.parse_result():
                    test_data.test_result = TestResult.PASS
                else:
                    test_data.test_result = TestResult.FAIL
        else:
            test_data.test_result = TestResult.SKIP

# Test10 cuda_memtest
class cudamemtest10(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, self.cwd, "cuda_memtest")

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        classifier = STRESS()
        classifier.add_matched_with_names()
        test.classifiers = [classifier]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== cudamemtest10 ===============")
        # Set repo info
        isrepocfgvalid =  self.set_cudamemtest_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + "/cudamemtest10.log", 'w+') as testLogger:
            res = self.downloadtest(testLogger, test_data)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            self.runtest(10)
            # Parse the test result
            if True == self.parse_result():
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL

