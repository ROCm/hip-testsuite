from amd.TesterRepository import Tester, Test, TestData
from amd.Test import HIPTestData, TestResult, HIP_PLATFORM
from typing import Union, List
from amd.test_classifier import TestClassifier
from amd.applications.hip_examples.hip_examples_build import BuildRunAmd, BuildRunNvidia
from amd.common.hip_get_packages import HipPackages
from amd.common.hip_shell import *

import os

# Common class to clone, set up, build and run test
class PrepareTest():
    def __init__(self, path, cwd):
        self.cwdAbs = cwd
        self.appPath = os.path.join(self.cwdAbs,\
        "src/amd/applications/hip_examples/")
        self.examplepath = os.path.join(self.appPath, "HIP-Examples/")
        self.thistestpath = os.path.join(self.examplepath, path)
        self.prepareobj = None
        self.apprepo = "" # Default
        self.appbranch = ""
        self.appcommitId = ""
        self.hiprepo = "" # Default
        self.hipbranch = ""
        self.hipcommitId = ""
        self.gpustrm_repo = ""
        self.gpustrm_branch = ""
        self.gpustrm_commitId = ""
        self.mixbn_repo = ""
        self.mixbn_branch = ""
        self.mixbn_commitId = ""

    def set_hip_repoinfo(self, test_data: HIPTestData):
        if test_data.repos["hip"].repo_url != None:
            self.hiprepo = test_data.repos["hip"].repo_url
        else:
            return False
        if test_data.repos["hip"].branch != None:
            self.hipbranch = test_data.repos["hip"].branch
        if test_data.repos["hip"].commit_id != None:
            self.hipcommitId = test_data.repos["hip"].commit_id
        return True

    def set_hipex_repoinfo(self, test_data: HIPTestData):
        validrepconfig = True
        if test_data.repos["hip_examples"].repo_url != None:
            self.apprepo = test_data.repos["hip_examples"].repo_url
        else:
            validrepconfig &= False
        if test_data.repos["hip_examples"].branch != None:
            self.appbranch = test_data.repos["hip_examples"].branch
        if test_data.repos["hip_examples"].commit_id != None:
            self.appcommitId = test_data.repos["hip_examples"].commit_id

        validrepconfig &= self.set_hip_repoinfo(test_data)
        return validrepconfig

    def set_mixben_repoinfo(self, test_data: HIPTestData):
        validrepconfig = True
        if test_data.repos["mixbench"].repo_url != None:
            self.mixbn_repo = test_data.repos["mixbench"].repo_url
        else:
            validrepconfig &= False
        if test_data.repos["mixbench"].branch != None:
            self.mixbn_branch = test_data.repos["mixbench"].branch
        if test_data.repos["mixbench"].commit_id != None:
            self.mixbn_commitId = test_data.repos["mixbench"].commit_id

        validrepconfig &= self.set_hip_repoinfo(test_data)
        return validrepconfig

    def set_gpustr_repoinfo(self, test_data: HIPTestData):
        validrepconfig = True
        if test_data.repos["gpu_stream"].repo_url != None:
            self.gpustrm_repo = test_data.repos["gpu_stream"].repo_url
        else:
            validrepconfig &= False
        if test_data.repos["gpu_stream"].branch != None:
            self.gpustrm_branch = test_data.repos["gpu_stream"].branch
        if test_data.repos["gpu_stream"].commit_id != None:
            self.gpustrm_commitId = test_data.repos["gpu_stream"].commit_id

        validrepconfig &= self.set_hip_repoinfo(test_data)
        return validrepconfig

    def download_deppackage(self, logFile):
        return HipPackages().pull_repo(logFile, self.hiprepo, self.hipbranch,\
        self.hipcommitId, "HIP")

    def download_hipexample(self, logFile):
        ret = self.download_deppackage(logFile)
        ret &= HipPackages().pull_repo(logFile, self.apprepo,\
        self.appbranch, self.appcommitId, "hip_examples")
        return ret

    def download_gpustream(self, logFile):
        ret = self.download_deppackage(logFile)
        ret &= HipPackages().pull_repo(logFile, self.gpustrm_repo,\
        self.gpustrm_branch, self.gpustrm_commitId, "gpu-stream")
        return ret

    def download_mixbench(self, logFile):
        ret = self.download_deppackage(logFile)
        ret &= HipPackages().pull_repo(logFile, self.mixbn_repo,\
        self.mixbn_branch, self.mixbn_commitId, "mixbench")
        return ret

    def buildtest(self, logFile, platform, testid):
        if platform == HIP_PLATFORM.nvidia:
            self.prepareobj = BuildRunNvidia(self.thistestpath)
        elif platform == HIP_PLATFORM.amd:
            self.prepareobj = BuildRunAmd(self.thistestpath)
        else:
            print("Invalid Platform")
            return False
        return self.prepareobj.buildtest(logFile, testid)

    def clean(self, testid):
        self.prepareobj.clean(testid)

    def runtest(self, logFile, testid):
        return self.prepareobj.runtest(logFile, testid)


class EXAMPLES(TestClassifier):
    def __init__(self):
        TestClassifier.__init__(self)

    def add_matched_with_names(self, matched_with_names: Union[None, dict] = None):
        TestClassifier.add_matched_with_names(self, {"examples": matched_with_names})


class MINIAPP(EXAMPLES):
    def __init__(self):
        EXAMPLES.__init__(self)

    def add_matched_with_names(self, matched_with_names: Union[None, dict] = None):
        EXAMPLES.add_matched_with_names(self, {"mini-app": matched_with_names})


class STRESS(EXAMPLES):
    def __init__(self):
        EXAMPLES.__init__(self)

    def add_matched_with_names(self, matched_with_names: Union[None, dict] = None):
        EXAMPLES.add_matched_with_names(self, {"stress": matched_with_names})


class PERFORMANCE(EXAMPLES):
    def __init__(self):
        EXAMPLES.__init__(self)

    def add_matched_with_names(self, matched_with_names: Union[None, dict] = None):
        EXAMPLES.add_matched_with_names(self, {"performance": matched_with_names})


# Test vectorAdd/
class VectorAdd(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "vectorAdd/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = MINIAPP()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "vectorAdd")

    def test(self, test_data: HIPTestData):
        print("=============== vectorAdd test start ===============")
        # Set repo info
        isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        testid = "vectorAdd"
        with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            res = self.download_hipexample(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            if True == self.runtest(testLogger, testid):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test gpu-burn/
class GpuBurn(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "gpu-burn/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = STRESS()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "gpu-burn")

    def test(self, test_data: HIPTestData):
        print("=============== gpu-burn test ===============")
        # Set repo info
        isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        testid = "gpu-burn"
        with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            res = self.download_hipexample(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            if True == self.runtest(testLogger, testid):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test strided-access/
class StridedAccess(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "strided-access/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = MINIAPP()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "strided-access")

    def test(self, test_data: HIPTestData):
        print("=============== strided-access test ===============")
        # Set repo info
        isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        testid = "strided-access"
        with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            res = self.download_hipexample(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            if True == self.runtest(testLogger, testid):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test rtm8/
class Rtm8(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "rtm8/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = PERFORMANCE()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "rtm8")

    def test(self, test_data: HIPTestData):
        print("=============== rtm8 test ===============")
        # Set repo info
        isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        testid = "rtm8"
        with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            res = self.download_hipexample(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            if True == self.runtest(testLogger, testid):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL

# Test reduction/
class Reduction(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "reduction/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = PERFORMANCE()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "reduction")

    def test(self, test_data: HIPTestData):
        print("=============== reduction test ===============")
        # Set repo info
        isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        testid = "reduction"
        with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            res = self.download_hipexample(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            if True == self.runtest(testLogger, testid):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test mini-nbody/
class Mini_nbody(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "mini-nbody/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = PERFORMANCE()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "mini-nbody")

    def test(self, test_data: HIPTestData):
        print("=============== mini-nbody test ===============")
        # Set repo info
        isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        testid = "mini-nbody"
        with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            res = self.download_hipexample(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            if True == self.runtest(testLogger, testid):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test add4/
class Add4(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "add4/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = PERFORMANCE()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "add4")

    def test(self, test_data: HIPTestData):
        print("=============== add4 test ===============")
        # Set repo info
        isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        testid = "add4"
        with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            res = self.download_hipexample(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            if True == self.runtest(testLogger, testid):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test cuda-stream/
class Cuda_stream(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "cuda-stream/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = PERFORMANCE()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "cuda-stream")

    def test(self, test_data: HIPTestData):
        print("=============== cuda-stream test ===============")
        # Set repo info
        isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        testid = "cuda-stream"
        with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            res = self.download_hipexample(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return
            res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            if True == self.runtest(testLogger, testid):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test openmp-helloworld/
# class Openmp_helloworld(Tester, PrepareTest):
    # def __init__(self):
        # Tester.__init__(self)
        # self.cwd = os.getcwd()
        # PrepareTest.__init__(self, "openmp-helloworld/", self.cwd)

    # def getTests(self) -> List[Test]:
        # test = Test()
        # test.test_name = self.__class__.__name__
        # intro = MINIAPP()
        # intro.add_matched_with_names()
        # test.classifiers = [intro]
        # test.tester = self
        # return [test]

    # def clean(self):
        # PrepareTest.clean(self, "openmp-helloworld")

    # def test(self, test_data: HIPTestData):
        # print("=============== openmp-helloworld test ===============")
        # # Set repo info
        # isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
        # if not isrepocfgvalid:
            # test_data.test_result = TestResult.ERROR
            # return
        # # Create the log directory
        # resultLogDir = test_data.log_location
        # testid = "openmp-helloworld"
        # with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            # res = self.download_hipexample(testLogger)
            # if not res:
                # test_data.test_result = TestResult.FAIL
                # return
            # res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            # if not res:
                # test_data.test_result = TestResult.FAIL
                # return

            # if True == self.runtest(testLogger, testid):
                # test_data.test_result = TestResult.PASS
            # else:
                # test_data.test_result = TestResult.FAIL


# Test rodinia_3.0/hip/bfs/
class Bfs(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "rodinia_3.0/hip/bfs/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = PERFORMANCE()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "rodinia_3.bfs")

    def test(self, test_data: HIPTestData):
        print("=============== rodinia_3.0/hip/bfs test start ===============")
        # Set repo info
        isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        testid = "rodinia_3.bfs"
        with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            res = self.download_hipexample(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            if True == self.runtest(testLogger, testid):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL
                

# Test rodinia_3.0/hip/cfd/
class Cfd(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "rodinia_3.0/hip/cfd/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = PERFORMANCE()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "rodinia_3.cfd")

    def test(self, test_data: HIPTestData):
        print("=============== rodinia_3.0/hip/cfd test start ===============")
        # Set repo info
        isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        testid = "rodinia_3.cfd"
        with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            res = self.download_hipexample(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            if True == self.runtest(testLogger, testid):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL
                

# Test rodinia_3.0/hip/dwt2d/
class Dwt2d(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "rodinia_3.0/hip/dwt2d/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = PERFORMANCE()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "rodinia_3.dwt2d")

    def test(self, test_data: HIPTestData):
        print("=============== rodinia_3.0/hip/dwt2d test start ===============")
        if test_data.HIP_PLATFORM == HIP_PLATFORM.amd:
            # Set repo info
            isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
            if not isrepocfgvalid:
                test_data.test_result = TestResult.ERROR
                return
            # Create the log directory
            resultLogDir = test_data.log_location
            testid = "rodinia_3.dwt2d"
            with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
                res = self.download_hipexample(testLogger)
                if not res:
                    test_data.test_result = TestResult.FAIL
                    return

                res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
                if not res:
                    test_data.test_result = TestResult.FAIL
                    return

                if True == self.runtest(testLogger, testid):
                    test_data.test_result = TestResult.PASS
                else:
                    test_data.test_result = TestResult.FAIL
        else:
            test_data.test_result = TestResult.SKIP

# Test rodinia_3.0/hip/gaussian/
class Gaussian(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "rodinia_3.0/hip/gaussian/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = PERFORMANCE()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "rodinia_3.gaussian")

    def test(self, test_data: HIPTestData):
        print("=============== rodinia_3.0/hip/gaussian test start ===============")
        # Set repo info
        isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        testid = "rodinia_3.gaussian"
        with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            res = self.download_hipexample(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            if True == self.runtest(testLogger, testid):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test rodinia_3.0/hip/heartwall/
class Heartwall(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "rodinia_3.0/hip/heartwall/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = PERFORMANCE()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "rodinia_3.heartwall")

    def test(self, test_data: HIPTestData):
        print("=============== rodinia_3.0/hip/heartwall test start ===============")
        # Set repo info
        isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        testid = "rodinia_3.heartwall"
        with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            res = self.download_hipexample(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            if True == self.runtest(testLogger, testid):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test rodinia_3.0/hip/hotspot/
class Hotspot(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "rodinia_3.0/hip/hotspot/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = PERFORMANCE()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "rodinia_3.hotspot")

    def test(self, test_data: HIPTestData):
        print("=============== rodinia_3.0/hip/hotspot test start ===============")
        # Set repo info
        isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        testid = "rodinia_3.hotspot"
        with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            res = self.download_hipexample(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            if True == self.runtest(testLogger, testid):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test rodinia_3.0/hip/hybridsort/
class Hybridsort(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "rodinia_3.0/hip/hybridsort/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = PERFORMANCE()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "rodinia_3.hybridsort")

    def test(self, test_data: HIPTestData):
        print("=============== rodinia_3.0/hip/hybridsort test start ===============")
        # Set repo info
        isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        testid = "rodinia_3.hybridsort"
        with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            res = self.download_hipexample(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            if True == self.runtest(testLogger, testid):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test rodinia_3.0/hip/kmeans/
class Kmeans(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "rodinia_3.0/hip/kmeans/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = PERFORMANCE()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "rodinia_3.kmeans")

    def test(self, test_data: HIPTestData):
        print("=============== rodinia_3.0/hip/kmeans test start ===============")
        # Set repo info
        isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        testid = "rodinia_3.kmeans"
        with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            res = self.download_hipexample(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            if True == self.runtest(testLogger, testid):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test rodinia_3.0/hip/lavaMD/
class LavaMD(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "rodinia_3.0/hip/lavaMD/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = PERFORMANCE()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "rodinia_3.lavaMD")

    def test(self, test_data: HIPTestData):
        print("=============== rodinia_3.0/hip/lavaMD test start ===============")
        # Set repo info
        isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        testid = "rodinia_3.lavaMD"
        with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            res = self.download_hipexample(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            if True == self.runtest(testLogger, testid):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test rodinia_3.0/hip/lud/
class Lud(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "rodinia_3.0/hip/lud/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = PERFORMANCE()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "rodinia_3.lud")

    def test(self, test_data: HIPTestData):
        print("=============== rodinia_3.0/hip/lud test start ===============")
        # Set repo info
        isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        testid = "rodinia_3.lud"
        with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            res = self.download_hipexample(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            if True == self.runtest(testLogger, testid):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test rodinia_3.0/hip/myocyte/
class Myocyte(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "rodinia_3.0/hip/myocyte/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = PERFORMANCE()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "rodinia_3.myocyte")

    def test(self, test_data: HIPTestData):
        print("=============== rodinia_3.0/hip/myocyte test start ===============")
        # Set repo info
        isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        testid = "rodinia_3.myocyte"
        with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            res = self.download_hipexample(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            if True == self.runtest(testLogger, testid):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test rodinia_3.0/hip/nn/
class Nn(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "rodinia_3.0/hip/nn/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = PERFORMANCE()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "rodinia_3.nn")

    def test(self, test_data: HIPTestData):
        print("=============== rodinia_3.0/hip/nn test start ===============")
        # Set repo info
        isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        testid = "rodinia_3.nn"
        with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            res = self.download_hipexample(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            if True == self.runtest(testLogger, testid):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test rodinia_3.0/hip/nw/
class Nw(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "rodinia_3.0/hip/nw/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = PERFORMANCE()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "rodinia_3.nw")

    def test(self, test_data: HIPTestData):
        print("=============== rodinia_3.0/hip/nw test start ===============")
        # Set repo info
        isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        testid = "rodinia_3.nw"
        with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            res = self.download_hipexample(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            if True == self.runtest(testLogger, testid):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test rodinia_3.0/hip/particlefilter/
class Particlefilter(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "rodinia_3.0/hip/particlefilter/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = PERFORMANCE()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "rodinia_3.particlefilter")

    def test(self, test_data: HIPTestData):
        print("=============== rodinia_3.0/hip/particlefilter test start ===============")
        if test_data.HIP_PLATFORM == HIP_PLATFORM.nvidia:
            # Set repo info
            isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
            if not isrepocfgvalid:
                test_data.test_result = TestResult.ERROR
                return
            # Create the log directory
            resultLogDir = test_data.log_location
            testid = "rodinia_3.particlefilter"
            with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
                res = self.download_hipexample(testLogger)
                if not res:
                    test_data.test_result = TestResult.FAIL
                    return

                res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
                if not res:
                    test_data.test_result = TestResult.FAIL
                    return

                if True == self.runtest(testLogger, testid):
                    test_data.test_result = TestResult.PASS
                else:
                    test_data.test_result = TestResult.FAIL
        else:
            test_data.test_result = TestResult.SKIP


# Test rodinia_3.0/hip/pathfinder/
class pathfinder(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "rodinia_3.0/hip/pathfinder/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = PERFORMANCE()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "rodinia_3.pathfinder")

    def test(self, test_data: HIPTestData):
        print("=============== rodinia_3.0/hip/pathfinder test start ===============")
        # Set repo info
        isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        testid = "rodinia_3.pathfinder"
        with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            res = self.download_hipexample(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            if True == self.runtest(testLogger, testid):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test rodinia_3.0/hip/srad/
class Srad(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "rodinia_3.0/hip/srad/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = PERFORMANCE()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "rodinia_3.srad")

    def test(self, test_data: HIPTestData):
        print("=============== rodinia_3.0/hip/srad test start ===============")
        # Set repo info
        isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        testid = "rodinia_3.srad"
        with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            res = self.download_hipexample(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            if True == self.runtest(testLogger, testid):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test rodinia_3.0/hip/streamcluster/
class Streamcluster(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "rodinia_3.0/hip/streamcluster/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = PERFORMANCE()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "rodinia_3.streamcluster")

    def test(self, test_data: HIPTestData):
        print("=============== rodinia_3.0/hip/streamcluster test start ===============")
        # Set repo info
        isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        testid = "rodinia_3.streamcluster"
        with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            res = self.download_hipexample(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            if True == self.runtest(testLogger, testid):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test rodinia_3.0/hip/b+tree/
# class Btree(Tester, PrepareTest):
    # def __init__(self):
        # Tester.__init__(self)
        # self.cwd = os.getcwd()
        # PrepareTest.__init__(self, "rodinia_3.0/hip/b+tree/", self.cwd)

    # def getTests(self) -> List[Test]:
        # test = Test()
        # test.test_name = self.__class__.__name__
        # intro = PERFORMANCE()
        # intro.add_matched_with_names()
        # test.classifiers = [intro]
        # test.tester = self
        # return [test]

    # def clean(self):
        # PrepareTest.clean(self, "rodinia_3.b+tree")

    # def test(self, test_data: HIPTestData):
        # print("=============== rodinia_3.0/hip/b+tree test start ===============")
        # # Set repo info
        # isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
        # if not isrepocfgvalid:
            # test_data.test_result = TestResult.ERROR
            # return
        # # Create the log directory
        # resultLogDir = test_data.log_location
        # testid = "rodinia_3.b+tree"
        # with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            # res = self.download_hipexample(testLogger)
            # if not res:
                # test_data.test_result = TestResult.FAIL
                # return

            # res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            # if not res:
                # test_data.test_result = TestResult.FAIL
                # return

            # if True == self.runtest(testLogger, testid):
                # test_data.test_result = TestResult.PASS
            # else:
                # test_data.test_result = TestResult.FAIL


# Test rodinia_3.0/hip/backprop/
class Backprop(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "rodinia_3.0/hip/backprop/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = PERFORMANCE()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "rodinia_3.backprop")

    def test(self, test_data: HIPTestData):
        print("=============== rodinia_3.0/hip/backprop test start ===============")
        if test_data.HIP_PLATFORM == HIP_PLATFORM.nvidia:
            # Set repo info
            isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
            if not isrepocfgvalid:
                test_data.test_result = TestResult.ERROR
                return
            # Create the log directory
            resultLogDir = test_data.log_location
            testid = "rodinia_3.backprop"
            with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
                res = self.download_hipexample(testLogger)
                if not res:
                    test_data.test_result = TestResult.FAIL
                    return

                res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
                if not res:
                    test_data.test_result = TestResult.FAIL
                    return

                if True == self.runtest(testLogger, testid):
                    test_data.test_result = TestResult.PASS
                else:
                    test_data.test_result = TestResult.FAIL
        else:
            test_data.test_result = TestResult.SKIP

# Test HIP-Examples-Applications/BinomialOption/
class BinomialOption(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "HIP-Examples-Applications/BinomialOption/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = MINIAPP()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "HIP-Examples-Applications.BinomialOption")

    def test(self, test_data: HIPTestData):
        print("=============== HIP-Examples-Applications/BinomialOption test start ===============")
        # Set repo info
        isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        testid = "HIP-Examples-Applications.BinomialOption"
        with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            res = self.download_hipexample(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            if True == self.runtest(testLogger, testid):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test HIP-Examples-Applications/BitonicSort/
class BitonicSort(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "HIP-Examples-Applications/BitonicSort/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = MINIAPP()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "HIP-Examples-Applications.BitonicSort")

    def test(self, test_data: HIPTestData):
        print("=============== HIP-Examples-Applications/BitonicSort test start ===============")
        # Set repo info
        isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        testid = "HIP-Examples-Applications.BitonicSort"
        with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            res = self.download_hipexample(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            if True == self.runtest(testLogger, testid):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test HIP-Examples-Applications/dct/
class Dct(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "HIP-Examples-Applications/dct/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = MINIAPP()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "HIP-Examples-Applications.dct")

    def test(self, test_data: HIPTestData):
        print("=============== HIP-Examples-Applications/dct test start ===============")
        # Set repo info
        isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        testid = "HIP-Examples-Applications.dct"
        with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            res = self.download_hipexample(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            if True == self.runtest(testLogger, testid):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test HIP-Examples-Applications/dwtHaar1D/
class DwtHaar1D(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "HIP-Examples-Applications/dwtHaar1D/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = MINIAPP()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "HIP-Examples-Applications.dwtHaar1D")

    def test(self, test_data: HIPTestData):
        print("=============== HIP-Examples-Applications/dwtHaar1D test start ===============")
        # Set repo info
        isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        testid = "HIP-Examples-Applications.dwtHaar1D"
        with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            res = self.download_hipexample(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            if True == self.runtest(testLogger, testid):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test HIP-Examples-Applications/FastWalshTransform/
class FastWalshTransform(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "HIP-Examples-Applications/FastWalshTransform/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = MINIAPP()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "HIP-Examples-Applications.FastWalshTransform")

    def test(self, test_data: HIPTestData):
        print("=============== HIP-Examples-Applications/FastWalshTransform test start ===============")
        # Set repo info
        isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        testid = "HIP-Examples-Applications.FastWalshTransform"
        with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            res = self.download_hipexample(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            if True == self.runtest(testLogger, testid):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test HIP-Examples-Applications/FloydWarshall/
class FloydWarshall(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "HIP-Examples-Applications/FloydWarshall/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = MINIAPP()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "HIP-Examples-Applications.FloydWarshall")

    def test(self, test_data: HIPTestData):
        print("=============== HIP-Examples-Applications/FloydWarshall test start ===============")
        # Set repo info
        isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        testid = "HIP-Examples-Applications.FloydWarshall"
        with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            res = self.download_hipexample(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            if True == self.runtest(testLogger, testid):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test HIP-Examples-Applications/HelloWorld/
class HelloWorld(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "HIP-Examples-Applications/HelloWorld/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = MINIAPP()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "HIP-Examples-Applications.HelloWorld")

    def test(self, test_data: HIPTestData):
        print("=============== HIP-Examples-Applications/HelloWorld test start ===============")
        # Set repo info
        isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        testid = "HIP-Examples-Applications.HelloWorld"
        with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            res = self.download_hipexample(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            if True == self.runtest(testLogger, testid):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test HIP-Examples-Applications/Histogram/
class Histogram(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "HIP-Examples-Applications/Histogram/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = MINIAPP()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "HIP-Examples-Applications.Histogram")

    def test(self, test_data: HIPTestData):
        print("=============== HIP-Examples-Applications/Histogram test start ===============")
        # Set repo info
        isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        testid = "HIP-Examples-Applications.Histogram"
        with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            res = self.download_hipexample(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            if True == self.runtest(testLogger, testid):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test HIP-Examples-Applications/MatrixMultiplication/
class MatrixMultiplication(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "HIP-Examples-Applications/MatrixMultiplication/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = MINIAPP()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "HIP-Examples-Applications.MatrixMultiplication")

    def test(self, test_data: HIPTestData):
        print("=============== HIP-Examples-Applications/MatrixMultiplication test start ===============")
        # Set repo info
        isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        testid = "HIP-Examples-Applications.MatrixMultiplication"
        with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            res = self.download_hipexample(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            if True == self.runtest(testLogger, testid):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test HIP-Examples-Applications/PrefixSum/
class PrefixSum(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "HIP-Examples-Applications/PrefixSum/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = MINIAPP()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "HIP-Examples-Applications.PrefixSum")

    def test(self, test_data: HIPTestData):
        print("=============== HIP-Examples-Applications/PrefixSum test start ===============")
        # Set repo info
        isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        testid = "HIP-Examples-Applications.PrefixSum"
        with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            res = self.download_hipexample(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            if True == self.runtest(testLogger, testid):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test HIP-Examples-Applications/RecursiveGaussian/
class RecursiveGaussian(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "HIP-Examples-Applications/RecursiveGaussian/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = MINIAPP()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "HIP-Examples-Applications.RecursiveGaussian")

    def test(self, test_data: HIPTestData):
        print("=============== HIP-Examples-Applications/RecursiveGaussian test start ===============")
        # Set repo info
        isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        testid = "HIP-Examples-Applications.RecursiveGaussian"
        with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            res = self.download_hipexample(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            if True == self.runtest(testLogger, testid):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test HIP-Examples-Applications/SimpleConvolution/
class SimpleConvolution(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "HIP-Examples-Applications/SimpleConvolution/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = MINIAPP()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "HIP-Examples-Applications.SimpleConvolution")

    def test(self, test_data: HIPTestData):
        print("=============== HIP-Examples-Applications/SimpleConvolution test start ===============")
        # Set repo info
        isrepocfgvalid =  self.set_hipex_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        testid = "HIP-Examples-Applications.SimpleConvolution"
        with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            res = self.download_hipexample(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            if True == self.runtest(testLogger, testid):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test GPU-STREAM Double
class GpuStreamDouble(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "../GPU-STREAM/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = PERFORMANCE()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "GPU-STREAM-DOUBLE")

    def test(self, test_data: HIPTestData):
        print("=============== GPU-STREAM Double start ===============")
        # Set repo info
        isrepocfgvalid =  self.set_gpustr_repoinfo(test_data)
        if not isrepocfgvalid:
            test_data.test_result = TestResult.ERROR
            return
        # Create the log directory
        resultLogDir = test_data.log_location
        testid = "GPU-STREAM-DOUBLE"
        with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            res = self.download_gpustream(testLogger)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            if not res:
                test_data.test_result = TestResult.FAIL
                return

            if True == self.runtest(testLogger, testid):
                test_data.test_result = TestResult.PASS
            else:
                test_data.test_result = TestResult.FAIL


# Test GPU-STREAM Float
# class GpuStreamFloat(Tester, PrepareTest):
    # def __init__(self):
        # Tester.__init__(self)
        # self.cwd = os.getcwd()
        # PrepareTest.__init__(self, "../GPU-STREAM/", self.cwd)

    # def getTests(self) -> List[Test]:
        # test = Test()
        # test.test_name = self.__class__.__name__
        # intro = PERFORMANCE()
        # intro.add_matched_with_names()
        # test.classifiers = [intro]
        # test.tester = self
        # return [test]

    # def clean(self):
        # PrepareTest.clean(self, "GPU-STREAM-FLOAT")

    # def test(self, test_data: HIPTestData):
        # print("=============== GPU-STREAM Float start ===============")
        # # Set repo info
        # isrepocfgvalid =  self.set_gpustr_repoinfo(test_data)
        # if not isrepocfgvalid:
            # test_data.test_result = TestResult.ERROR
            # return
        # # Create the log directory
        # resultLogDir = test_data.log_location
        # testid = "GPU-STREAM-FLOAT"
        # with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
            # res = self.download_gpustream(testLogger)
            # if not res:
                # test_data.test_result = TestResult.FAIL
                # return

            # res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
            # if not res:
                # test_data.test_result = TestResult.FAIL
                # return

            # if True == self.runtest(testLogger, testid):
                # test_data.test_result = TestResult.PASS
            # else:
                # test_data.test_result = TestResult.FAIL


# Test mixbench-hip-alt
class MixBenchAlt(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "../mixbench/mixbench-hip/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = PERFORMANCE()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "mixbench-hip-alt")

    def test(self, test_data: HIPTestData):
        print("=============== mixbench-hip-alt start ===============")
        if test_data.HIP_PLATFORM == HIP_PLATFORM.amd:
            # Set repo info
            isrepocfgvalid =  self.set_mixben_repoinfo(test_data)
            if not isrepocfgvalid:
                test_data.test_result = TestResult.ERROR
                return
            # Create the log directory
            resultLogDir = test_data.log_location
            testid = "mixbench-hip-alt"
            with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
                res = self.download_mixbench(testLogger)
                if not res:
                    test_data.test_result = TestResult.FAIL
                    return

                res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
                if not res:
                    test_data.test_result = TestResult.FAIL
                    return

                if True == self.runtest(testLogger, testid):
                    test_data.test_result = TestResult.PASS
                else:
                    test_data.test_result = TestResult.FAIL
        else:
            test_data.test_result = TestResult.SKIP

# Test mixbench-hip-ro
class MixBenchRO(Tester, PrepareTest):
    def __init__(self):
        Tester.__init__(self)
        self.cwd = os.getcwd()
        PrepareTest.__init__(self, "../mixbench/mixbench-hip/", self.cwd)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        intro = PERFORMANCE()
        intro.add_matched_with_names()
        test.classifiers = [intro]
        test.tester = self
        return [test]

    def clean(self):
        PrepareTest.clean(self, "mixbench-hip-ro")

    def test(self, test_data: HIPTestData):
        print("=============== GPU-STREAM Float start ===============")
        if test_data.HIP_PLATFORM == HIP_PLATFORM.amd:
            # Set repo info
            isrepocfgvalid =  self.set_mixben_repoinfo(test_data)
            if not isrepocfgvalid:
                test_data.test_result = TestResult.ERROR
                return
            # Create the log directory
            resultLogDir = test_data.log_location
            testid = "mixbench-hip-ro"
            with open(resultLogDir + "/" + testid + ".log", 'w+') as testLogger:
                res = self.download_mixbench(testLogger)
                if not res:
                    test_data.test_result = TestResult.FAIL
                    return

                res = self.buildtest(testLogger, test_data.HIP_PLATFORM, testid)
                if not res:
                    test_data.test_result = TestResult.FAIL
                    return

                if True == self.runtest(testLogger, testid):
                    test_data.test_result = TestResult.PASS
                else:
                    test_data.test_result = TestResult.FAIL
        else:
            test_data.test_result = TestResult.SKIP


