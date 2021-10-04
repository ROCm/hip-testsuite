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

from typing import List, Union, Set, Dict
from hiptestsuite.AMD import AMDObject
from hiptestsuite.targets import Target
from enum import Enum, auto
from hiptestsuite.test_classifier import TestClassifier
from hiptestsuite.config_processor import ConfigProcessor


class Test(AMDObject):
    def __init__(self):
        # Cycle Import
        from hiptestsuite.TesterRepository import Tester

        AMDObject.__init__(self)
        self.test_name: Union[None, str] = None
        self.also_matched_with_test_names: Union[None, List[str]] = None
        self.classifiers: Union[None, List[TestClassifier]] = None
        self.tester: Union[None, Tester] = None
        self.applicable_for_target: Union[None, Set[Target]] = None


class TestResult(Enum):
    PASS = auto()
    FAIL = auto()
    SKIP = auto()
    ERROR = auto()


class UserAccess(ConfigProcessor):
    def __init__(self):
        ConfigProcessor.__init__(self)
        self.user_password: Union[None, str] = None

    def loadConfig(self):
        self.user_password = self.config.user_password


class LogLocation(AMDObject):
    def __init__(self):
        AMDObject.__init__(self)
        self.log_location: Union[None, str] = None


class TestData(AMDObject):
    def __init__(self):
        AMDObject.__init__(self)
        self.test: Union[None, Test] = None
        self.test_result: Union[None, TestResult] = None


class CompileData(AMDObject):
    def __init__(self):
        AMDObject.__init__(self)
        self.build_for_target: Union[None, Set[Target]] = None


class GitData(AMDObject):
    def __init__(self):
        AMDObject.__init__(self)
        self.repo_url: Union[None, str] = None
        self.branch: Union[None, str] = None
        self.commit_id: Union[None, str] = None


class AllGitData(ConfigProcessor):
    def __init__(self):
        ConfigProcessor.__init__(self)
        self.repos: Union[None, Dict[str, GitData]] = None

    def loadConfig(self):
        repos = dict()
        for repo_key, repo_detail in self.config.repos.items():
            git_data = GitData()
            git_data.repo_url = repo_detail["repo_url"]
            if "branch" in repo_detail:
                git_data.branch = repo_detail["branch"]
            if "commit_id" in repo_detail:
                git_data.commit_id = repo_detail["commit_id"]
            repos[repo_key] = git_data
        self.repos = repos


class HIPCCVerbose(Enum):
    ZERO = auto()
    ONE = auto()
    TWO = auto()
    FOUR = auto()


class Optimization_Level(Enum):
    ZERO = auto()
    ONE = auto()
    TWO = auto()
    THREE = auto()


class HIP_PLATFORM(Enum):
    nvidia = auto()
    amd = auto()


class HIPCCCompileData(CompileData, ConfigProcessor):
    def __init__(self):
        CompileData.__init__(self)
        ConfigProcessor.__init__(self)

        self.Optimization_Level: Union[None, Optimization_Level] = None

        self.HIPCC_VERBOSE: Union[None, HIPCCVerbose] = None
        self.HIP_PLATFORM: Union[None, HIP_PLATFORM] = None

        self.CUDA_PATH: Union[None, str] = None
        self.ROCM_PATH: Union[None, str] = None

        # if self.build_for_target, then --offload_arch=

        # -I ./
        self.includes_path: Union[None, List[str]] = None
        # -lm
        self.link_libs: Union[None, List[str]] = None
        # -L.
        self.link_libs_path: Union[None, List[str]] = None

    def loadConfig(self):
        if self.config.HIP_PLATFORM == "amd":
            print("Platform selected: amd")
            self.HIP_PLATFORM = HIP_PLATFORM.amd
        elif self.config.HIP_PLATFORM == "nvidia":
            print("Platform selected: nvidia")
            self.HIP_PLATFORM = HIP_PLATFORM.nvidia
        elif self.config.HIP_PLATFORM is None:
            print("Platform selected: amd")
            self.HIP_PLATFORM = HIP_PLATFORM.amd
        else:
            print("Warning: Platform " + self.config.HIP_PLATFORM + " is not supported, defaulting to AMD")
            self.HIP_PLATFORM = HIP_PLATFORM.amd

        if self.config.Optimization_Level == 0:
            self.Optimization_Level = Optimization_Level.ZERO
        elif self.config.Optimization_Level == 1:
            self.Optimization_Level = Optimization_Level.ONE
        elif self.config.Optimization_Level == 2:
            self.Optimization_Level = Optimization_Level.TWO
        elif self.config.Optimization_Level == 3:
            self.Optimization_Level = Optimization_Level.THREE
        else:
            self.Optimization_Level = None

        if self.config.HIPCC_VERBOSE == 0:
            self.HIPCC_VERBOSE = HIPCCVerbose.ZERO
        elif self.config.HIPCC_VERBOSE == 1:
            self.HIPCC_VERBOSE = HIPCCVerbose.ONE
        elif self.config.HIPCC_VERBOSE == 2:
            self.HIPCC_VERBOSE = HIPCCVerbose.TWO
        elif self.config.HIPCC_VERBOSE == 4:
            self.HIPCC_VERBOSE = HIPCCVerbose.FOUR
        else:
            self.HIPCC_VERBOSE = None

        self.ROCM_PATH = self.config.ROCM_PATH
        self.CUDA_PATH = self.config.CUDA_PATH

        self.build_for_target = self.config.build_for_target
        self.includes_path = self.config.includes_path
        self.link_libs = self.config.link_libs
        self.link_libs_path = self.config.link_libs_path

        # ToDo offload_target


class HIPTestData(TestData, HIPCCCompileData, AllGitData, LogLocation, UserAccess):
    def __init__(self):
        UserAccess.__init__(self)
        LogLocation.__init__(self)
        TestData.__init__(self)
        HIPCCCompileData.__init__(self)
        AllGitData.__init__(self)

    def loadConfig(self):
        UserAccess.loadConfig(self)
        AllGitData.loadConfig(self)
        HIPCCCompileData.loadConfig(self)


class Quick(AMDObject):
    def __init__(self):
        AMDObject.__init__(self)
        self.quick: bool = False


class GetTestsData(Quick):
    def __init__(self):
        Quick.__init__(self)


class HIPBuildData(GetTestsData, HIPCCCompileData, UserAccess, AllGitData, LogLocation):
    def __init__(self):
        GetTestsData.__init__(self)
        HIPCCCompileData.__init__(self)
        UserAccess.__init__(self)
        AllGitData.__init__(self)
        LogLocation.__init__(self)

    def loadConfig(self):
        UserAccess.loadConfig(self)
        AllGitData.loadConfig(self)
        HIPCCCompileData.loadConfig(self)
