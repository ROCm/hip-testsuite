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

import os
import re
import tempfile
from multiprocessing import cpu_count

from hiptestsuite.common.hip_shell import *
from hiptestsuite.applications.hpc_apps.cp2k.cp2k_parser_common import Cp2kParser

class BuildRunAmd():
    def __init__(self, thistestpath, logFile, rocm_path, gpu_version):
        self.thistestpath = thistestpath
        self.logFile = logFile
        self.runlog = None
        self.rocm_path = rocm_path
        self.gpu_version = gpu_version

    def configure_build_cp2k(self):

        if not os.path.exists(self.rocm_path):
            print("Error: ROCm path does not exist. Exiting Test!")
            print("NOTE: tried path '{}'".format(self.rocm_path))
            return False

        repo_root = os.path.join(self.thistestpath, "cp2k")

        submodule_cmd = """
set -e
cd {repo_root}
git submodule update --init --recursive
""".format(repo_root=repo_root)
        print("cp2k submodule fetching in progress ..")
        with tempfile.TemporaryFile("w+") as runlogdump:
            retcode = execshellcmd_largedump(submodule_cmd, self.logFile,
                                             runlogdump, None)
        if retcode != 0:
             print("cp2k submodule fetch Failed", )
             return False

        configure_cmd = """
set -e
export ROCM_PATH={rocm_path}
export LIBRARY_PATH=$ROCM_PATH/lib:$LIBRARY_PATH
cd {repo_root}
rm -f configure.stamp
cd tools/toolchain
./install_cp2k_toolchain.sh --enable-hip --with-cmake=system \
--with-libint=system --with-libxc=system --with-fftw=system \
--with-openblas=system --with-sirius=no --with-gsl=no \
--gpu-ver={gpu_version}
cd {repo_root}
cp tools/toolchain/install/arch/* arch/
touch configure.stamp
""".format(repo_root=repo_root, rocm_path=self.rocm_path,
           gpu_version=self.gpu_version)
        print("cp2k dependency fetch and configuration in progress ..")
        with tempfile.TemporaryFile("w+") as runlogdump:
            execshellcmd_largedump(configure_cmd, self.logFile, runlogdump,
                                   None)
        if not os.path.exists(repo_root + "/configure.stamp"):
             print("cp2k dependency fetch and/or configuration Failed", )
             return False

        # The build step relies on bash shell.
        build_script = os.path.join(self.thistestpath, "cp2k_build.bash")
        build_cmd = "/bin/bash " + build_script
        build_env = os.environ.copy()
        build_env['CP2K_ROOT'] = str(repo_root)
        build_env['JOB_COUNT'] = str(cpu_count())
        print("cp2k build in progress ..")
        with tempfile.TemporaryFile("w+") as runlogdump:
            execshellcmd_largedump(build_cmd, self.logFile, runlogdump,
                                   build_env)
        if not os.path.exists(repo_root + "/build.stamp"):
            print("cp2k build Failed", )
            return False
        return True

    def buildtest(self):
        if not self.configure_build_cp2k():
            return False
        return True

    def runtest(self, testnum):
        print("Running cp2k Test" + str(testnum))
        repo_root = os.path.join(self.thistestpath, "cp2k")

        cmd = """
set -e
export LD_LIBRARY_PATH={rocm_path}/lib:$LD_LIBRARY_PATH
cd {repo_root}
make -j{job_count} TESTOPTS="--skipdir QS/regtest-rs-dhft --skipdir QS/regtest-hfx-ri" ARCH=local_hip VERSION=ssmp test
""".format(repo_root=repo_root, job_count=cpu_count(), rocm_path=self.rocm_path)

        self.runlog = tempfile.TemporaryFile("w+")
        execshellcmd_largedump(cmd, self.logFile, self.runlog, None)

    def clean(self):
        print("Cleaning cp2k..")
        if self.runlog != None:
            self.runlog.close()

    def parse_result(self, testnum):
        return Cp2kParser(self.runlog).parse(testnum)
