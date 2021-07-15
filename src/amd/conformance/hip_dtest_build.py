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
        self.rclrpath = os.path.join(os.getcwd(), "src/amd/conformance/ROCclr")
        self.oclpath = os.path.join(os.getcwd(), "src/amd/conformance/ROCm-OpenCL-Runtime")

    # Fetches all available dtests using ctest
    def get_all_ctest(self):
        buildpath = self.hippath + "/build/";
        cmdexc = "cd " + self.hippath + "/build;"
        cmdexc += "ctest -N --show-only=\"json-v1\";"
        with open("ctest.json", "w+") as jsonlog:
            execshellcmd_largedump(cmdexc, self.logfile, jsonlog, None)
        testlist = []
        with open("ctest.json", "r") as jsonlog:
            json_string = jsonlog.read()
            ctest_json = json.loads(json_string)
            all_tests = ctest_json["tests"]
            for test in all_tests:
                dtest = ""
                for param in test["command"]:
                    dtest += param + " "
                dtest = re.sub(buildpath, "", dtest)
                dtest = re.sub("/", ".", dtest)
                testlist.append(dtest)

        os.remove("ctest.json")
        return testlist

    # Parse the test result
    def parsetest(self, log):
        log.seek(0)
        passed = 0
        failed = 0
        skipped = 0
        for line in log:
            if "PASSED" in line:
                passed = passed + 1
            elif "FAILED" in line:
                failed = failed + 1
            elif "SKIP" in line:
                skipped = skipped + 1
            else:
                pass
        status = None
        if failed > 0:
            status = "FAILED"
        elif passed > 0:
            status = "PASSED"
        elif skipped > 0:
            status = "SKIP"
        else:
            # No Passed, Failed or Skipped Found
            # Result is indeterminate. Hence failing
            # this test.
            status = "FAILED"
        return status

    # Execute the test case
    def runtest(self, log, testcase, envtoset):
        status = True
        testcase[0] = re.sub("\.", "/", testcase[0])
        #Check if the test binary exists
        if not os.path.isfile(os.path.join(\
        self.hippath, "build", testcase[0])):
            print(testcase[0] + "does not exist")
            return "FAILED"

        cmdtest = ""
        for param in testcase:
            cmdtest += param + " "
        print("Executing command = " + cmdtest)
        # run test
        cmd = "cd " + os.path.join(self.hippath, "build") + ";"
        cmd += cmdtest
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
        hip_install_inc = os.path.join(self.hippath, "build/install/include")
        hip_install_lib = os.path.join(self.hippath, "build/install/lib")
        hip_install_bin = os.path.join(self.hippath, "build/install/bin")
        hip_install_rocclr = os.path.join(self.hippath, "build/install/rocclr")
        hip_binaries = glob.glob(hip_install_lib + "/*.so*")
        status &= os.path.isdir(hip_install_inc)
        status &= os.path.isdir(hip_install_lib)
        status &= os.path.isdir(hip_install_bin)
        status &= os.path.isdir(hip_install_rocclr)
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
        # build rocclr
        cmd = "cd \"$ROCclr_DIR\";"
        cmd += "rm -Rf build;"
        cmd += "mkdir -p build;cd build;"
        cmd += "cmake -DOPENCL_DIR=\"$OPENCL_DIR\" -DCMAKE_INSTALL_PREFIX=\"$ROCclr_DIR/../opt/rocm/rocclr\" ..;"
        cmd += "cmake -j;make install;"
        cmdexc = cmd
        runlogdump = tempfile.TemporaryFile("w+")
        execshellcmd_largedump(cmdexc, self.logfile, runlogdump, envtoset)
        runlogdump.close()
        # Validate if rocclr build is successful
        buildSuccess = self.validate_rocclr_build()
        if buildSuccess == False:
            print("rocclr build failed!")
            return False
        # Build HIP
        cmd = "cd \"$HIP_DIR\";"
        cmd += "rm -Rf build;"
        cmd += "mkdir -p build;cd build;"
        cmd += "cmake -DCMAKE_PREFIX_PATH=\"$ROCclr_DIR/build;/opt/rocm;$ROCclr_DIR/../opt/rocm/rocclr\" -DCMAKE_INSTALL_PREFIX=$PWD/install ..;"
        cmd += "cmake -j;make install;"
        cmd += "make -j8 build_tests"
        cmdexc = cmd
        runlogdump = tempfile.TemporaryFile("w+")
        execshellcmd_largedump(cmdexc, self.logfile, runlogdump, envtoset)
        runlogdump.close()
        # Validate if HIP build is successful
        buildSuccess = self.validate_hip_build()
        if buildSuccess == False:
            print("HIP build failed!")
            return False
        return True

    # Execute test cases
    def runtest(self, log, testcase):
        envtoset = self.get_envvar()
        return BuildRunCommon.runtest(self, log, testcase, envtoset)

    # Clean the test
    def clean(self):
        envtoset = self.get_envvar()
        cmd = "cd \"$ROCclr_DIR\";"
        cmd += "rm -Rf build;rm -Rf $ROCclr_DIR/../opt;"
        cmd += "cd \"$HIP_DIR\";"
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
        return envtoset

    # Validate if HIP build is successful
    def validate_hip_build(self):
        status = True
        hip_install_inc = os.path.join(self.hippath, "build/install/include")
        hip_install_bin = os.path.join(self.hippath, "build/install/bin")
        status &= os.path.isdir(hip_install_inc)
        status &= os.path.isdir(hip_install_bin)
        return status

    # Build for NVIDIA
    def build_package(self, env = None):
        buildSuccess = True
        # Set environment
        envtoset = self.get_envvar()
        # Build HIP
        cmd = "cd \"$HIP_DIR\";"
        cmd += "rm -Rf build;"
        cmd += "mkdir -p build;cd build;"
        cmd += "cmake -DHIP_PLATFORM=nvidia -DCMAKE_INSTALL_PREFIX=$PWD/install ..;"
        cmd += "make install;"
        cmd += "make -j8 build_tests"
        cmdexc = cmd
        runlogdump = tempfile.TemporaryFile("w+")
        execshellcmd_largedump(cmdexc, self.logfile, runlogdump, envtoset)
        runlogdump.close()
        # Validate if HIP build is successful
        buildSuccess = self.validate_hip_build()
        if buildSuccess == False:
            print("HIP build failed!")
            return False
        return True

    # Execute test cases
    def runtest(self, log, testcase):
        envtoset = self.get_envvar()
        return BuildRunCommon.runtest(self, log, testcase, envtoset)

    # Clean the test
    def clean(self):
        envtoset = self.get_envvar()
        cmd = "cd \"$HIP_DIR\";"
        cmd += "rm -Rf build;"
        execshellcmd(cmd, None, envtoset)
