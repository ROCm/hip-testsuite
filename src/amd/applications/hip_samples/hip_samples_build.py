import os
from amd.common.hip_shell import execshellcmd

class BuildRunCommon():
    '''
    In this class insert the build and execution steps for test cases
    which are identical across different platforms (amd/nvidia/intel).
    '''
    def __init__(self, path, logfile):
        self.thistestpath = path
        self.logfile = logfile

    def buildtest(self, env = None):
        cmdcd = "cd " + self.thistestpath + ";"
        cmd_clean = "make clean;"
        cmd_build = "make"
        cmdexc = cmdcd + cmd_clean + cmd_build
        execshellcmd(cmdexc, self.logfile, env)

    def clean(self):
        cmdcd = "cd " + self.thistestpath + ";"
        cmd_clean = "make clean;"
        cmdexc = cmdcd + cmd_clean
        execshellcmd(cmdexc, None, None)


class BuildRunAmd(BuildRunCommon):
    def __init__(self, path, logfile):
        BuildRunCommon.__init__(self, path, logfile)

    def buildtest(self):
        # In this function put the build steps for test cases
        # which differ across platforms (amd/nvidia/intel) else
        # invoke BuildRunCommon.buildtest
        ret = BuildRunCommon.buildtest(self)
        return ret


class BuildRunNvidia(BuildRunCommon):
    def __init__(self, path, logfile):
        self.hippath = os.path.join(os.getcwd(), "src/amd/conformance/HIP/")
        BuildRunCommon.__init__(self, path, logfile)

    def getenvironmentvariables(self):
        envtoset = os.environ.copy()
        envtoset["HIP_PLATFORM"] = "nvidia"
        envtoset["HIP_COMPILER"] = "nvcc"
        envtoset["HIP_RUNTIME"] = "cuda"
        envtoset["HIP_DIR"] = self.hippath
        envtoset["HIP_PATH"] = "../../../build"
        return envtoset

    def setupenvironmentfornvcc(self):
        cmdcd = "cd " + self.hippath + ";"
        envtoset = self.getenvironmentvariables()
        cmdsetenv = "rm -Rf build/;mkdir build;cd build;"
        cmdbuildinstall = "cmake -DHIP_PLATFORM=nvidia -DCMAKE_INSTALL_PREFIX=$PWD/install ..;"
        cmdbuildinstall += "make install;"
        cmdexc = cmdcd + cmdsetenv + cmdbuildinstall
        execshellcmd(cmdexc, self.logfile, envtoset)

    def applypatch(self): # To be deleted
        cmd = "cd " + self.hippath + ";"
        cmd += "patch -p0 < ../../applications/hip_samples/Samples_Patch_4.2.x;"
        execshellcmd(cmd, self.logfile, None)

    def buildtest(self):
        buildbindirpresent = os.path.isdir(\
        os.path.join(self.hippath, "build/bin"))
        buildincludedirpresent = os.path.isdir(\
        os.path.join(self.hippath, "build/include"))
        buildinstalldirpresent = os.path.isdir(\
        os.path.join(self.hippath, "build/install"))
        if not (buildbindirpresent & buildincludedirpresent & buildinstalldirpresent):
            self.setupenvironmentfornvcc()
        envtoset = self.getenvironmentvariables()
        # In this function put the build steps for test cases
        # which differ across platforms (amd/nvidia/intel) else
        # invoke BuildRunCommon.buildtest

        # Apply Patch. This is temporary and will be removed once Hip Samples changes
        # are available in HIP public repository.
        self.applypatch()
        ret = BuildRunCommon.buildtest(self, envtoset)
        return ret
