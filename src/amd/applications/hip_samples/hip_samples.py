from amd.TesterRepository import Tester, Test, TestData
from amd.Test import HIPTestData, TestResult, HIP_PLATFORM
from typing import Union, List
from amd.test_classifier import TestClassifier
from amd.applications.hip_samples.hip_samples_build import BuildRunAmd, BuildRunNvidia
from amd.common.hip_get_packages import HipPackages
from amd.common.hip_shell import execshellcmd

import os
import re
# Common class to clone, set up, build and run test
class PrepareTest():
    def __init__(self, path, binary, cwd):
        self.cwdAbs = cwd
        self.conformancePath = os.path.join(self.cwdAbs, "src/amd/conformance/")
        self.hippath = os.path.join(self.conformancePath, "HIP/")
        self.thistestpath = os.path.join(self.hippath, path)
        self.binary = binary
        self.testExecOutput = ""
        self.hiprepo = "" # Default
        self.hipbranch = ""
        self.hipcommitId = ""
        self.prepareobj = None

    def setrepoinfo(self, test_data: HIPTestData):
        validrepconfig = True
        if test_data.repos["hip"].repo_url != None:
            self.hiprepo = test_data.repos["hip"].repo_url
        else:
            validrepconfig &= False
        if test_data.repos["hip"].branch != None:
            self.hipbranch = test_data.repos["hip"].branch
        if test_data.repos["hip"].commit_id != None:
            self.hipcommitId = test_data.repos["hip"].commit_id
        return validrepconfig

    def downloadtest(self, logFile):
        return HipPackages().pull_repo(logFile, self.hiprepo, self.hipbranch,\
        self.hipcommitId, "HIP")

    def buildtest(self, logFile, platform):
        isBinaryPresent = True
        if platform == HIP_PLATFORM.nvidia:
            self.prepareobj = BuildRunNvidia(self.thistestpath, logFile)
        elif platform == HIP_PLATFORM.amd:
            self.prepareobj = BuildRunAmd(self.thistestpath, logFile)
        else:
            print("Invalid Platform")
            return False
        self.prepareobj.buildtest()

        if not os.path.isfile(\
        os.path.join(self.thistestpath, self.binary)):
            isBinaryPresent &= False
        return isBinaryPresent

    def clean(self):
        self.prepareobj.clean()

    def runtest(self, logFile):
        cmdexc = "cd " + self.thistestpath + ";" + "./" + self.binary
        self.testExecOutput += execshellcmd(cmdexc, logFile, None)


# Common class to parse the result of test execution
class LogParser():
    def __init__(self, numOfExpPassed, testPassCriteria):
        self.numOfExpPassed = numOfExpPassed
        self.testPassCriteria = testPassCriteria

    def parse_common(self, testResultLog):
        countPass = testResultLog.count(self.testPassCriteria)
        return countPass

    def utils_parser(self, testcase, testResultLog):
        pt1=re.compile(r'(Batch dispatch latency:)\s+(\d+\.\d+)\s+us,\s+std:\s+(\d+\.\d+)\s+us')
        pt2=re.compile(r' (total_time,)(\d+\.\d+)')
        pt3=re.compile(r'(memInfo.total:\s+)(\d+\.\d+) GB')
        pt4=re.compile('(Bidir_Time_pinned\s+\d+\w+\s+ms\s+)(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)')
        if testcase in 'hipDispatchLatency':
            status=re.search(pt1,testResultLog)
            if status:
                #if float(str(status.group(4)))!=0.0 and float(str(status.group(2)))!=0.0 and float(str(status.group(3)))!=0.0:
                return 'PASS'
            else:
                return'FAIL'
        if testcase in 'hipCommander':
            status=re.search(pt2,testResultLog)
            if status:
                if float(str(status.group(2)))!=0.0:
                    return 'PASS'
                else:
                    return'FAIL'
            else:
                return 'FAIL'
        if testcase in 'hipInfo':
            status=re.search(pt3,testResultLog)
            if status:
                if float(str(status.group(2)))!=0.0:
                    return 'PASS'
                else:
                    return'FAIL'
            else:
                return 'FAIL'

        if testcase in 'hipBusBandwidth':
            status=re.search(pt4,testResultLog)
            if status:
                if float(str(status.group(4)))!=0.0 and float(str(status.group(2)))!=0.0 and float(str(status.group(3)))!=0.0:
                    return 'PASS'
                else:
                    return'FAIL'
            else:
                return'FAIL'


class SAMPLES(TestClassifier):
    def __init__(self):
        TestClassifier.__init__(self)

    def add_matched_with_names(self, matched_with_names: Union[None, dict] = None):
        TestClassifier.add_matched_with_names(self, {"samples": matched_with_names})


class INTRO(SAMPLES):
    def __init__(self):
        SAMPLES.__init__(self)

    def add_matched_with_names(self, matched_with_names: Union[None, dict] = None):
        SAMPLES.add_matched_with_names(self, {"mini-app": matched_with_names})

class COOKBOOK(SAMPLES):
    def __init__(self):
        SAMPLES.__init__(self)

    def add_matched_with_names(self, matched_with_names: Union[None, dict] = None):
        SAMPLES.add_matched_with_names(self, {"mini-app": matched_with_names})


class UTILS(SAMPLES):
    def __init__(self):
        SAMPLES.__init__(self)

    def add_matched_with_names(self, matched_with_names: Union[None, dict] = None):
        SAMPLES.add_matched_with_names(self, {"performance": matched_with_names})


# Test samples/0_Intro/bit_extract
class BitExtract(Tester, PrepareTest, LogParser):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "samples/0_Intro/bit_extract/", "bit_extract", self.cwd)
        LogParser.__init__(self, 1, "PASSED") # Number of expected PASSED

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = INTRO()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== BitExtract Test ===============")
        # Set repo info
        isrepocfgvalid =  self.setrepoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + "/BitExtract.log", 'w+') as testLogger:
            res = self.downloadtest(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            self.runtest(testLogger)
            if self.numOfExpPassed == self.parse_common(self.testExecOutput):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test samples/0_Intro/module_api/defaultDriver.hip.out
class ModuleApiDefaultDriver(Tester, PrepareTest, LogParser):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "samples/0_Intro/module_api/", "defaultDriver.hip.out", self.cwd)
        LogParser.__init__(self, 1, "PASSED") # Number of expected PASSED

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = INTRO()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== ModuleApiDefaultDriver Test ===============")
        # Set repo info
        isrepocfgvalid =  self.setrepoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + "/ModuleApiDefaultDriver.log", 'w+') as testLogger:
            res = self.downloadtest(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            self.runtest(testLogger)
            if self.numOfExpPassed == self.parse_common(self.testExecOutput):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test samples/0_Intro/module_api/launchKernelHcc.hip.out
class ModuleApiLaunchKernelHcc(Tester, PrepareTest, LogParser):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "samples/0_Intro/module_api/",
                             "launchKernelHcc.hip.out", self.cwd)
        LogParser.__init__(self, 1, "PASSED") # Number of expected PASSED

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = INTRO()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== ModuleApiLaunchKernelHcc Test ===============")
        # Set repo info
        if test_data.HIP_PLATFORM == HIP_PLATFORM.amd:
            isrepocfgvalid =  self.setrepoinfo(test_data)
            if not isrepocfgvalid:
                test_data.test_result = TestResult.ERROR
                return
            # Create the log directory
            resultLogDir = test_data.log_location
            with open(resultLogDir + "/ModuleApiLaunchKernelHcc.log", 'w+') as testLogger:
                res = self.downloadtest(testLogger)
                if not res:
                    test_data.test_result = TestResult.FAIL
                    return
                res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
                if not res:
                    test_data.test_result = TestResult.FAIL
                    return
                self.runtest(testLogger)
                if self.numOfExpPassed == self.parse_common(self.testExecOutput):
                    test_data.test_result = TestResult.PASS
                else:
                    test_data.test_result = TestResult.FAIL
        else:
            test_data.test_result = TestResult.SKIP


# Test samples/0_Intro/module_api/runKernel.hip.out
class ModuleApiRunKernel(Tester, PrepareTest, LogParser):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "samples/0_Intro/module_api/", "runKernel.hip.out", self.cwd)
        LogParser.__init__(self, 1, "PASSED") # Number of expected PASSED

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = INTRO()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== ModuleApiRunKernel Test ===============")
        # Set repo info
        isrepocfgvalid =  self.setrepoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + "/ModuleApiRunKernel.log", 'w+') as testLogger:
            res = self.downloadtest(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            self.runtest(testLogger)
            if self.numOfExpPassed == self.parse_common(self.testExecOutput):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test samples/0_Intro/module_api_global
class ModuleApiGlobal(Tester, PrepareTest, LogParser):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "samples/0_Intro/module_api_global/",
                             "runKernel.hip.out", self.cwd)
        LogParser.__init__(self, 2, "PASSED") # Number of expected PASSED

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = INTRO()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== ModuleApiGlobal Test ===============")
        # Set repo info
        isrepocfgvalid =  self.setrepoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + "/ModuleApiGlobal.log", 'w+') as testLogger:
            res = self.downloadtest(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            self.runtest(testLogger)
            if self.numOfExpPassed == self.parse_common(self.testExecOutput):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test samples/0_Intro/square/
class Square(Tester, PrepareTest, LogParser):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "samples/0_Intro/square/", "square.out", self.cwd)
        LogParser.__init__(self, 1, "PASSED") # Number of expected PASSED

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = INTRO()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== Square Test ===============")
        # Set repo info
        isrepocfgvalid =  self.setrepoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + "/Square.log", 'w+') as testLogger:
            res = self.downloadtest(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            self.runtest(testLogger)
            if self.numOfExpPassed == self.parse_common(self.testExecOutput):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test samples/2_Cookbook/0_MatrixTranspose
class MatrixTranspose(Tester, PrepareTest, LogParser):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "samples/2_Cookbook/0_MatrixTranspose/",
                             "MatrixTranspose", self.cwd)
        LogParser.__init__(self, 1, "PASSED") # Number of expected PASSED

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        cookbook = COOKBOOK()
        cookbook.add_matched_with_names()
        test.classifiers = [cookbook]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== MatrixTranspose Test ===============")
        # Set repo info
        isrepocfgvalid =  self.setrepoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        if not os.path.exists(resultLogDir):
            os.makedirs(resultLogDir)
        with open(resultLogDir + '/MatrixTranspose.log', 'w+') as testLogger:
            res = self.downloadtest(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            self.runtest(testLogger)
            if self.numOfExpPassed == self.parse_common(self.testExecOutput):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test samples/2_Cookbook/10_inline_asm
class InlineAsm(Tester, PrepareTest, LogParser):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "samples/2_Cookbook/10_inline_asm/", "inline_asm", self.cwd)
        LogParser.__init__(self, 1, "PASSED") # Number of expected PASSED

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        cookbook = COOKBOOK()
        cookbook.add_matched_with_names()
        test.classifiers = [cookbook]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== InlineAsm Test ===============")
        # Set repo info
        if test_data.HIP_PLATFORM == HIP_PLATFORM.amd:
            isrepocfgvalid =  self.setrepoinfo(test_data)
            if not isrepocfgvalid:
                test_data.test_result = TestResult.ERROR
                return
            # Create the log directory
            resultLogDir = test_data.log_location
            with open(resultLogDir + '/InlineAsm.log', 'w+') as testLogger:
                res = self.downloadtest(testLogger)
                if not res:
                    test_data.test_result = TestResult.FAIL
                    return
                res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
                if not res:
                    test_data.test_result = TestResult.FAIL
                    return
                self.runtest(testLogger)
                if self.numOfExpPassed == self.parse_common(self.testExecOutput):
                    test_data.test_result = TestResult.PASS
                else:
                    test_data.test_result = TestResult.FAIL
        else:
            test_data.test_result = TestResult.SKIP


# Test samples/2_Cookbook/16_assembly_to_executable
class SquareAsm(Tester, PrepareTest, LogParser):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "samples/2_Cookbook/16_assembly_to_executable/",
                             "square_asm.out", self.cwd)
        LogParser.__init__(self, 1, "PASSED") # Number of expected PASSED

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        cookbook = COOKBOOK()
        cookbook.add_matched_with_names()
        test.classifiers = [cookbook]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== SquareAsm Test ===============")
        if test_data.HIP_PLATFORM == HIP_PLATFORM.amd:
            # Set repo info
            isrepocfgvalid =  self.setrepoinfo(test_data)
            if not isrepocfgvalid:
                test_data.test_result = TestResult.ERROR
                return
            # Create the log directory
            resultLogDir = test_data.log_location
            with open(resultLogDir + '/SquareAsm.log', 'w+') as testLogger:
                res = self.downloadtest(testLogger)
                if not res:
                    test_data.test_result = TestResult.FAIL
                    return
                res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
                if not res:
                    test_data.test_result = TestResult.FAIL
                    return
                self.runtest(testLogger)
                if self.numOfExpPassed == self.parse_common(self.testExecOutput):
                    test_data.test_result = TestResult.PASS
                else:
                    test_data.test_result = TestResult.FAIL
        else:
            test_data.test_result = TestResult.SKIP


# Test samples/2_Cookbook/11_texture_driver
class Texture2dDrv(Tester, PrepareTest, LogParser):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "samples/2_Cookbook/11_texture_driver/",
                             "texture2dDrv.out", self.cwd)
        LogParser.__init__(self, 1, "PASSED") # Number of expected PASSED

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        cookbook = COOKBOOK()
        cookbook.add_matched_with_names()
        test.classifiers = [cookbook]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== Texture2dDrv Test ===============")
        # Set repo info
        isrepocfgvalid =  self.setrepoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + '/Texture2dDrv.log', 'w+') as testLogger:
            res = self.downloadtest(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            self.runtest(testLogger)
            if self.numOfExpPassed == self.parse_common(self.testExecOutput):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test samples/2_Cookbook/9_unroll
class Unroll(Tester, PrepareTest, LogParser):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "samples/2_Cookbook/9_unroll/", "unroll", self.cwd)
        LogParser.__init__(self, 1, "PASSED") # Number of expected PASSED

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        cookbook = COOKBOOK()
        cookbook.add_matched_with_names()
        test.classifiers = [cookbook]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== Unroll Test ===============")
        # Set repo info
        isrepocfgvalid =  self.setrepoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + '/Unroll.log', 'w+') as testLogger:
            res = self.downloadtest(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            self.runtest(testLogger)
            if self.numOfExpPassed == self.parse_common(self.testExecOutput):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test samples/2_Cookbook/14_gpu_arch
# class GpuArch(Tester, PrepareTest, LogParser):
    # def __init__(self):
        # Tester.__init__(self)
        # self.cwd = os.getcwd()
        # PrepareTest.__init__(self, "samples/2_Cookbook/14_gpu_arch/", "gpuarch", self.cwd)
        # LogParser.__init__(self, 1, "success") # Number of expected PASSED

    # def getTests(self) -> List[Test]:
        # test = Test()
        # test.test_name = self.__class__.__name__
        # cookbook = COOKBOOK()
        # cookbook.add_matched_with_names()
        # test.classifiers = [cookbook]
        # test.tester = self
        # return [test]

    # def clean(self):
        # PrepareTest.clean(self)

    # def test(self, test_data: HIPTestData):
        # print("=============== GpuArch Test ===============")
        # # Set repo info
        # isrepocfgvalid =  self.setrepoinfo(test_data)
        # if not isrepocfgvalid:
            # test_data.test_result = TestResult.ERROR
            # return
        # # Create the log directory
        # resultLogDir = test_data.log_location
        # with open(resultLogDir + '/GpuArch.log', 'w+') as testLogger:
            # res = self.downloadtest(testLogger)
            # if not res:
                # test_data.test_result = TestResult.FAIL
                # return
            # res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
            # if not res:
                # test_data.test_result = TestResult.FAIL
                # return
            # self.runtest(testLogger)
            # if self.numOfExpPassed == self.parse_common(self.testExecOutput):
                # test_data.test_result = TestResult.PASS
            # else:
                # test_data.test_result = TestResult.FAIL


# Test samples/2_Cookbook/4_shfl
class Shfl(Tester, PrepareTest, LogParser):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "samples/2_Cookbook/4_shfl/", "shfl", self.cwd)
        LogParser.__init__(self, 1, "PASSED") # Number of expected PASSED

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        cookbook = COOKBOOK()
        cookbook.add_matched_with_names()
        test.classifiers = [cookbook]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== Shfl Test ===============")
        # Set repo info
        isrepocfgvalid =  self.setrepoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + '/Shfl.log', 'w+') as testLogger:
            res = self.downloadtest(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            self.runtest(testLogger)
            if self.numOfExpPassed == self.parse_common(self.testExecOutput):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test samples/2_Cookbook/3_shared_memory
class SharedMemory(Tester, PrepareTest, LogParser):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "samples/2_Cookbook/3_shared_memory/", "sharedMemory", self.cwd)
        LogParser.__init__(self, 1, "PASSED") # Number of expected PASSED

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        cookbook = COOKBOOK()
        cookbook.add_matched_with_names()
        test.classifiers = [cookbook]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== SharedMemory Test ===============")
        # Set repo info
        isrepocfgvalid =  self.setrepoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + '/SharedMemory.log', 'w+') as testLogger:
            res = self.downloadtest(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            self.runtest(testLogger)
            if self.numOfExpPassed == self.parse_common(self.testExecOutput):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test samples/2_Cookbook/17_llvm_ir_to_executable
class Square_Ir(Tester, PrepareTest, LogParser):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "samples/2_Cookbook/17_llvm_ir_to_executable/",
                             "square_ir.out", self.cwd)
        LogParser.__init__(self, 1, "PASSED") # Number of expected PASSED

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        cookbook = COOKBOOK()
        cookbook.add_matched_with_names()
        test.classifiers = [cookbook]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== Square_Ir Test ===============")
        if test_data.HIP_PLATFORM == HIP_PLATFORM.amd:
            # Set repo info
            isrepocfgvalid =  self.setrepoinfo(test_data)
            if not isrepocfgvalid:
                test_data.test_result = TestResult.ERROR
                return
            # Create the log directory
            resultLogDir = test_data.log_location
            with open(resultLogDir + '/Square_Ir.log', 'w+') as testLogger:
                res = self.downloadtest(testLogger)
                if not res:
                    test_data.test_result = TestResult.FAIL
                    return
                res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
                if not res:
                    test_data.test_result = TestResult.FAIL
                    return
                self.runtest(testLogger)
                if self.numOfExpPassed == self.parse_common(self.testExecOutput):
                    test_data.test_result = TestResult.PASS
                else:
                    test_data.test_result = TestResult.FAIL
        else:
            test_data.test_result = TestResult.SKIP

# Test samples/2_Cookbook/5_2dshfl
class Dshfl(Tester, PrepareTest, LogParser):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "samples/2_Cookbook/5_2dshfl/", "2dshfl", self.cwd)
        LogParser.__init__(self, 1, "PASSED") # Number of expected PASSED

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        cookbook = COOKBOOK()
        cookbook.add_matched_with_names()
        test.classifiers = [cookbook]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== Dshfl Test ===============")
        # Set repo info
        isrepocfgvalid =  self.setrepoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + '/Dshfl.log', 'w+') as testLogger:
            res = self.downloadtest(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            self.runtest(testLogger)
            if self.numOfExpPassed == self.parse_common(self.testExecOutput):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test samples/2_Cookbook/1_hipEvent
class HipEvent(Tester, PrepareTest, LogParser):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "samples/2_Cookbook/1_hipEvent/", "hipEvent", self.cwd)
        LogParser.__init__(self, 1, "PASSED") # Number of expected PASSED

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        cookbook = COOKBOOK()
        cookbook.add_matched_with_names()
        test.classifiers = [cookbook]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== HipEvent Test ===============")
        # Set repo info
        isrepocfgvalid =  self.setrepoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + '/HipEvent.log', 'w+') as testLogger:
            res = self.downloadtest(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            self.runtest(testLogger)
            if self.numOfExpPassed == self.parse_common(self.testExecOutput):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test samples/2_Cookbook/6_dynamic_shared
class Dynamic_Shared(Tester, PrepareTest, LogParser):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "samples/2_Cookbook/6_dynamic_shared/",
                             "dynamic_shared", self.cwd)
        LogParser.__init__(self, 1, "PASSED") # Number of expected PASSED

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        cookbook = COOKBOOK()
        cookbook.add_matched_with_names()
        test.classifiers = [cookbook]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== Dynamic_Shared Test ===============")
        # Set repo info
        isrepocfgvalid =  self.setrepoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + '/Dynamic_Shared.log', 'w+') as testLogger:
            res = self.downloadtest(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            self.runtest(testLogger)
            if self.numOfExpPassed == self.parse_common(self.testExecOutput):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test samples/2_Cookbook/8_peer2peer
class Peer2peer(Tester, PrepareTest, LogParser):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "samples/2_Cookbook/8_peer2peer/", "peer2peer", self.cwd)
        LogParser.__init__(self, 1, "PASSED") # Number of expected PASSED

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        cookbook = COOKBOOK()
        cookbook.add_matched_with_names()
        test.classifiers = [cookbook]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== Peer2peer Test ===============")
        # Set repo info
        isrepocfgvalid =  self.setrepoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + '/Peer2peer.log', 'w+') as testLogger:
            res = self.downloadtest(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            self.runtest(testLogger)
            if self.numOfExpPassed == self.parse_common(self.testExecOutput):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test samples/2_Cookbook/7_streams
class Stream(Tester, PrepareTest, LogParser):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "samples/2_Cookbook/7_streams/", "stream", self.cwd)
        LogParser.__init__(self, 1, "PASSED") # Number of expected PASSED

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        cookbook = COOKBOOK()
        cookbook.add_matched_with_names()
        test.classifiers = [cookbook]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== Stream Test ===============")
        # Set repo info
        isrepocfgvalid =  self.setrepoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + '/Stream.log', 'w+') as testLogger:
            res = self.downloadtest(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            self.runtest(testLogger)
            if self.numOfExpPassed == self.parse_common(self.testExecOutput):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test samples/2_Cookbook/13_occupancy
class Occupancy(Tester, PrepareTest, LogParser):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "samples/2_Cookbook/13_occupancy/", "occupancy", self.cwd)
        LogParser.__init__(self, 2, "PASSED") # Number of expected PASSED

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        cookbook = COOKBOOK()
        cookbook.add_matched_with_names()
        test.classifiers = [cookbook]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== Occupancy Test ===============")
        # Set repo info
        isrepocfgvalid =  self.setrepoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + '/Occupancy.log', 'w+') as testLogger:
            res = self.downloadtest(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            self.runtest(testLogger)
            if self.numOfExpPassed == self.parse_common(self.testExecOutput):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test samples/1_Utils/hipBusBandwidth
class HipBusBandwidth(Tester, PrepareTest, LogParser):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "samples/1_Utils/hipBusBandwidth/", "hipBusBandwidth", self.cwd)
        LogParser.__init__(self, 2, "PASSED") # Number of expected PASSED

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        utils = UTILS()
        utils.add_matched_with_names()
        test.classifiers = [utils]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== HipBusBandwidth Test ===============")
        # Set repo info
        isrepocfgvalid =  self.setrepoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + '/hipBusBandwidth.log', 'w+') as testLogger:
            res = self.downloadtest(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            self.runtest(testLogger)
            if "PASS" == self.utils_parser("hipBusBandwidth", self.testExecOutput):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test samples/1_Utils/hipCommander
class HipCommander(Tester, PrepareTest, LogParser):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "samples/1_Utils/hipCommander/", "hipCommander", self.cwd)
        LogParser.__init__(self, 2, "PASSED") # Number of expected PASSED

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        utils = UTILS()
        utils.add_matched_with_names()
        test.classifiers = [utils]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== HipCommander Test ===============")
        # Set repo info
        isrepocfgvalid =  self.setrepoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + '/hipCommander.log', 'w+') as testLogger:
            res = self.downloadtest(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            self.runtest(testLogger)
            if "PASS" == self.utils_parser("hipCommander", self.testExecOutput):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test samples/1_Utils/hipDispatchLatency
class HipDispatchLatency(Tester, PrepareTest, LogParser):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "samples/1_Utils/hipDispatchLatency/", "hipDispatchLatency.out", self.cwd)
        LogParser.__init__(self, 2, "PASSED") # Number of expected PASSED

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        utils = UTILS()
        utils.add_matched_with_names()
        test.classifiers = [utils]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== HipDispatchLatency Test ===============")
        # Set repo info
        isrepocfgvalid =  self.setrepoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + '/hipDispatchLatency.log', 'w+') as testLogger:
            res = self.downloadtest(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            self.runtest(testLogger)
            if "PASS" == self.utils_parser("hipDispatchLatency", self.testExecOutput):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test samples/1_Utils/hipInfo
class HipInfo(Tester, PrepareTest, LogParser):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "samples/1_Utils/hipInfo/", "hipInfo", self.cwd)
        LogParser.__init__(self, 2, "PASSED") # Number of expected PASSED

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        utils = UTILS()
        utils.add_matched_with_names()
        test.classifiers = [utils]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self)

    def test(self, test_data: HIPTestData):
        print("=============== HipInfo Test ===============")
        # Set repo info
        isrepocfgvalid =  self.setrepoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        with open(resultLogDir + '/hipInfo.log', 'w+') as testLogger:
            res = self.downloadtest(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            self.runtest(testLogger)
            if "PASS" == self.utils_parser("hipInfo", self.testExecOutput):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL
