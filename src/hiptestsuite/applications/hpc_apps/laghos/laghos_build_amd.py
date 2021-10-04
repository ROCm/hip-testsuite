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

import os
import re
import tempfile
from hiptestsuite.common.hip_shell import *
from hiptestsuite.applications.hpc_apps.laghos.laghos_parser_common import LaghosParser

class BuildRunAmd():
    def __init__(self, thistestpath, logFile):
        self.thistestpath = thistestpath
        self.logFile = logFile
        self.runlog = ""

    def set_env(self):
        cmd = "export MPI_PATH=/usr/local/openmpi;"
        cmd += "export ROCM_PATH=/opt/rocm;"
        cmd += "export PATH=${MPI_PATH}/bin:$PATH;"
        cmd += "export PATH=${MPI_PATH}/bin:$PATH;"
        return cmd

    def configure_build_hypre(self):
        if os.path.exists(os.path.join(self.thistestpath, "hypre/src/lib/libHYPRE.a")):
            print("Hypre already built")
            return True
        print("Hypre build in progress ..")
        cmd = self.set_env()
        cmd += "cd " + self.thistestpath + ";"
        cmd += "wget https://github.com/hypre-space/hypre/archive/v2.16.0.tar.gz;"
        cmd += "mv v2.16.0.tar.gz hypre-2.16.0.tar.gz;tar -zxvf hypre-2.16.0.tar.gz;rm hypre-2.16.0.tar.gz;"
        cmd += "cd hypre-2.16.0/src/;"
        cmd += "./configure --disable-fortran --enable-bigint --with-MPI --with-MPI-include=${MPI_PATH}/include --with-MPI-lib-dirs=${MPI_PATH}/lib;"
        cmd += "make -j; cd ../..; ln -s hypre-2.16.0 hypre;"
        runlogdump = tempfile.TemporaryFile("w+")
        execshellcmd_largedump(cmd, self.logFile, runlogdump, None)
        runlogdump.close()
        if not os.path.exists(os.path.join(self.thistestpath, "hypre/src/lib/libHYPRE.a")):
            print("Hypre Build Failed")
            return False
        return True

    def configure_build_metis(self):
        if os.path.exists(os.path.join(self.thistestpath, "metis-4.0/libmetis.a")):
            print("Metis already built")
            return True
        print("Metis build in progress ..")
        cmd = self.set_env()
        cmd += "cd " + self.thistestpath + ";"
        cmd += "wget http://glaros.dtc.umn.edu/gkhome/fetch/sw/metis/OLD/metis-4.0.3.tar.gz;"
        cmd += "tar -zxvf metis-4.0.3.tar.gz;rm metis-4.0.3.tar.gz;"
        cmd += "cd metis-4.0.3;make -j;cd ..;"
        cmd += "ln -s metis-4.0.3 metis-4.0;"
        runlogdump = tempfile.TemporaryFile("w+")
        execshellcmd_largedump(cmd, self.logFile, runlogdump, None)
        runlogdump.close()
        if not os.path.exists(os.path.join(self.thistestpath, "metis-4.0/libmetis.a")):
            print("Metis Build Failed")
            return False
        return True

    def configure_build_mfem(self):
        if os.path.exists(os.path.join(self.thistestpath, "mfem/libmfem.a")):
            print("Mfem already built")
            return True
        print("Mfem build in progress ..")
        cmd = self.set_env()
        cmd += "cd " + self.thistestpath + "; cd mfem;"
        cmd += "make config;"
        cmd += "make phip -j CXXFLAGS=\"-O3 -std=c++11 --gpu-max-threads-per-block=256\" \
        MFEM_TPLFLAGS=\"-I./../hypre/src/hypre/include -I${MPI_PATH}/include\" MFEM_EXT_LIBS=\"-L./../hypre/src/hypre/lib \
        -lHYPRE  -L./../metis-4.0 -lmetis  -lrt -L${MPI_PATH}/lib -lmpi\";"
        runlogdump = tempfile.TemporaryFile("w+")
        execshellcmd_largedump(cmd, self.logFile, runlogdump, None)
        runlogdump.close()
        if not os.path.exists(os.path.join(self.thistestpath, "mfem/libmfem.a")):
            print("Mfem Build Failed")
            return False
        return True

    def configure_build_laghos(self):
        if os.path.exists(os.path.join(self.thistestpath, "Laghos/laghos")):
            print("Laghos already built")
            return True
        print("Laghos build in progress ..")
        cmd = self.set_env()
        cmd += "cd " + self.thistestpath + "; cd Laghos;"
        cmd += "make -j;"
        runlogdump = tempfile.TemporaryFile("w+")
        execshellcmd_largedump(cmd, self.logFile, runlogdump, None)
        runlogdump.close()
        if not os.path.exists(os.path.join(self.thistestpath, "mfem/libmfem.a")):
            print("Laghos Build Failed")
            return False
        return True

    def buildtest(self):
        # In this function put the build steps for test cases
        # which differ across platforms (amd/nvidia/intel)
        # Check if OpenMPI is already installed. Else return.
        if os.path.exists("/usr/local/openmpi/bin") and os.path.exists("/usr/local/openmpi/etc")\
        and os.path.exists("/usr/local/openmpi/lib") and os.path.exists("/usr/local/openmpi/include")\
        and os.path.exists("/usr/local/openmpi/share"):
            print("Openmpi installed.")
        else:
            print("Openmpi not installed. Exiting test!")
            return False

        if not self.configure_build_hypre():
            print("Hypre configuration and build failed ..")
            return False
        if not self.configure_build_metis():
            print("Metis configuration and build failed ..")
            return False
        if not self.configure_build_mfem():
            print("Mfem configuration and build failed ..")
            return False
        if not self.configure_build_laghos():
            print("Laghos configuration and build failed ..")
            return False

        return True

    def runtest(self, testnum):
        print("Running Laghos Test" + str(testnum))
        cmd = self.set_env()
        cmd += "cd " + self.thistestpath + "; cd Laghos;"
        cmd += "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/openmpi/lib;"
        if testnum == 0:
            cmd += "mpirun -np 1 laghos -pa -p 1 -tf 0.6 -no-vis -m data/cube01_hex.mesh --cg-tol 0 --cg-max-steps 50 --max-steps 2 -ok 2 -ot 1 -rs 5 -d hip;"
        elif testnum == 1:
            cmd += "mpirun -np 1 laghos -pa -p 1 -tf 0.6 -no-vis -m data/cube_12_hex.mesh --cg-tol 0 --cg-max-steps 50 --max-steps 2 -ok 3 -ot 2 -rs 4 -d hip;"
        self.runlog = execshellcmd(cmd, self.logFile, None)

    def clean(self):
        print("Cleaning Laghos..")

    def parse_result(self, testnum):
        return LaghosParser(self.runlog).parse(testnum)
