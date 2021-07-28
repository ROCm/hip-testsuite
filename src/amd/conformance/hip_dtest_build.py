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

import os, glob
import tempfile
import json
import re
from amd.common.hip_shell import execshellcmd_largedump, execshellcmd

class BuildRunCommon():
    '''
    In this class insert the build and execution steps for test cases
    which are identical across different platforms (amd/nvidia/intel).
    '''
    def __init__(self, logfile):
        self.logfile = logfile
        self.hippath = os.path.join(os.getcwd(), "src/amd/conformance/HIP")
        self.hipamdpath = os.path.join(os.getcwd(),"src/amd/conformance/HIPAMD")
        self.rclrpath = os.path.join(os.getcwd(), "src/amd/conformance/ROCclr")
        self.oclpath = os.path.join(os.getcwd(), "src/amd/conformance/ROCm-OpenCL-Runtime")

    # Fetches all available dtests using ctest
    def get_all_ctest(self):
        cmdexc = "cd " + self.hipamdpath + "/build;"
        cmdexc += "ctest -N;"
        with open("ctest.txt", "w+") as ctestlog:
            execshellcmd_largedump(cmdexc, self.logfile, ctestlog, None)
        testlist = []
        with open("ctest.txt", "r") as ctestlog:
            for test in ctestlog:
                if re.search("Test *#\d*:", test) != None:
                    dtest = re.sub("Test *#\d*: ", "", test)
                    dtest = re.sub("/", ".", dtest)
                    dtest = dtest.lstrip()
                    dtest = dtest.rstrip()
                    testlist.append(dtest)
        os.remove("ctest.txt")
        return testlist

    # Parse the test result
    def parsetest(self, log):
        log.seek(0)
        text = log.read()
        status = None
        if re.search("100% tests passed", text) != None:
            status = "PASSED"
        else:
            status = "FAILED"
        return status

    # Execute the test case
    def runtest(self, log, testcase, envtoset):
        cmdtest = "ctest -R " + testcase
        print("Executing command = " + cmdtest)
        # run test
        cmd = "cd " + os.path.join(self.hipamdpath, "build") + ";"
        cmd += cmdtest + ";"
        runlogdump = tempfile.TemporaryFile("w+")
        execshellcmd_largedump(cmd, log, runlogdump, envtoset)
        status = self.parsetest(runlogdump)
        runlogdump.close()
        return status


class BuildRunAmd(BuildRunCommon):
    '''
    In this class insert the build and execution steps specific
    for AMD platform.
    '''
    def __init__(self, logfile):
        BuildRunCommon.__init__(self, logfile)

    # Create the environment variables to set for build and execution
    def get_envvar(self):
        envtoset = os.environ.copy()
        envtoset["ROCclr_DIR"] = self.rclrpath
        envtoset["OPENCL_DIR"] = self.oclpath
        envtoset["HIP_DIR"] = self.hippath
        envtoset["HIP_AMD_DIR"] = self.hipamdpath
        return envtoset

    # Validate if rocclr build is successful
    def validate_rocclr_build(self):
        status = True
        rocclr_install_inc = os.path.join(os.getcwd(), "src/amd/conformance/opt/rocm/rocclr/include")
        rocclr_install_lib = os.path.join(os.getcwd(), "src/amd/conformance/opt/rocm/rocclr/lib")
        status &= os.path.isdir(rocclr_install_lib)
        status &= os.path.isdir(rocclr_install_inc)
        rocclr_binaries = glob.glob(rocclr_install_lib + "/*.a")
        if len(rocclr_binaries) > 0:
            status &= True
        else:
            status &= False
        return status

    # Validate if HIP build is successful
    def validate_hip_build(self):
        status = True
        hip_install_inc = os.path.join(self.hipamdpath, "build/install/include")
        hip_install_lib = os.path.join(self.hipamdpath, "build/install/lib")
        hip_install_bin = os.path.join(self.hipamdpath, "build/install/bin")
        hip_binaries = glob.glob(hip_install_lib + "/*.so*")
        status &= os.path.isdir(hip_install_inc)
        status &= os.path.isdir(hip_install_lib)
        status &= os.path.isdir(hip_install_bin)
        if len(hip_binaries) > 0:
            status &= True
        else:
            status &= False
        return status

    # Build Rocclr and HIP for AMD
    def build_package(self, env = None):
        buildSuccess = True
        # Set environment
        envtoset = self.get_envvar()
        # Build HIP
        cmd = "cd \"$HIP_AMD_DIR\";"
        cmd += "rm -Rf build;"
        cmd += "mkdir -p build;cd build;"
        cmd += "cmake -DHIP_COMPILER=clang -DHIP_PLATFORM=rocclr -DCMAKE_VERBOSE_MAKEFILE=ON -DCMAKE_INSTALL_PREFIX=$PWD/install" +\
        " -DROCCLR_PATH=\"$ROCclr_DIR\" -DAMD_OPENCL_PATH=\"$OPENCL_DIR\" -DHIP_COMMON_DIR=\"$HIP_DIR\"" +\
        " -DCMAKE_PREFIX_PATH=\"/opt/rocm/lib/cmake/hsa-runtime64;/opt/rocm/lib/cmake/amd_comgr\" ..;"
        cmd += "make -j8;make install;"

        cmdexc = cmd
        runlogdump = tempfile.TemporaryFile("w+")
        execshellcmd_largedump(cmdexc, self.logfile, runlogdump, envtoset)
        runlogdump.close()

        # Validate if HIP build is successful
        buildSuccess = self.validate_hip_build()
        if buildSuccess == False:
            print("HIP build failed!")
            return False

        # Build Dtest
        cmd = "cd \"$HIP_AMD_DIR\";cd build;"
        cmd += "make -j8 build_tests;"
        cmdexc = cmd
        runlogdump = tempfile.TemporaryFile("w+")
        execshellcmd_largedump(cmdexc, self.logfile, runlogdump, envtoset)
        runlogdump.close()
        return True

    # Execute test cases
    def runtest(self, log, testcase):
        envtoset = self.get_envvar()
        return BuildRunCommon.runtest(self, log, testcase, envtoset)

    # Clean the test
    def clean(self):
        envtoset = self.get_envvar()
        cmd = "cd \"$HIP_AMD_DIR\";"
        cmd += "rm -Rf build;"
        execshellcmd(cmd, None, envtoset)

class BuildRunNvidia(BuildRunCommon):
    '''
    In this class insert the build and execution steps specific
    for NVIDIA platform.
    '''
    def __init__(self, logfile):
        BuildRunCommon.__init__(self, logfile)

    # Create the environment variables to set for build and execution
    def get_envvar(self):
        envtoset = os.environ.copy()
        envtoset["HIP_PLATFORM"] = "nvidia"
        envtoset["HIP_COMPILER"] = "nvcc"
        envtoset["HIP_RUNTIME"] = "cuda"
        envtoset["HIP_DIR"] = self.hippath
        envtoset["HIP_AMD_DIR"] = self.hipamdpath
        return envtoset

    # Validate if HIP build is successful
    def validate_hip_build(self):
        status = True
        hip_install_inc = os.path.join(self.hipamdpath, "build/install/include")
        hip_install_bin = os.path.join(self.hipamdpath, "build/install/bin")
        status &= os.path.isdir(hip_install_inc)
        status &= os.path.isdir(hip_install_bin)
        return status

    # Build for NVIDIA
    def build_package(self, env = None):
        buildSuccess = True
        # Set environment
        envtoset = self.get_envvar()
        # Build HIP
        cmd = "cd \"$HIP_AMD_DIR\";"
        cmd += "rm -Rf build;"
        cmd += "mkdir -p build;cd build;"
        cmd += "cmake -DHIP_PLATFORM=nvidia -DCMAKE_INSTALL_PREFIX=$PWD/install -DHIP_COMMON_DIR=\"$HIP_DIR\"" + \
        " -DHIP_AMD_BACKEND_SOURCE_DIR=\"$HIP_AMD_DIR\" .. ;"
        cmd += "make install;"
        cmdexc = cmd
        runlogdump = tempfile.TemporaryFile("w+")
        execshellcmd_largedump(cmdexc, self.logfile, runlogdump, envtoset)
        runlogdump.close()
        # Validate if HIP build is successful
        buildSuccess = self.validate_hip_build()
        if buildSuccess == False:
            print("HIP build failed!")
            return False
        # Build Dtest
        cmd = "cd \"$HIP_AMD_DIR\";cd build;"
        cmd += "make -j8 build_tests;"
        cmdexc = cmd
        runlogdump = tempfile.TemporaryFile("w+")
        execshellcmd_largedump(cmdexc, self.logfile, runlogdump, envtoset)
        runlogdump.close()

        return True

    # Execute test cases
    def runtest(self, log, testcase):
        envtoset = self.get_envvar()
        return BuildRunCommon.runtest(self, log, testcase, envtoset)

    # Clean the test
    def clean(self):
        envtoset = self.get_envvar()
        cmd = "cd \"$HIP_AMD_DIR\";"
        cmd += "rm -Rf build;"
        execshellcmd(cmd, None, envtoset)
