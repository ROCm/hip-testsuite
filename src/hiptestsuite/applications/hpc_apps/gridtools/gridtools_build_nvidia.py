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
import tempfile
from hiptestsuite.common.hip_shell import *
from hiptestsuite.applications.hpc_apps.gridtools.gridtools_parser_common import GridtoolsParser

class BuildRunNvidia():
    def __init__(self, thistestpath, logFile, cuda_target):
        self.thistestpath = thistestpath
        self.logFile = logFile
        self.runlog = None
        self.cuda_target = cuda_target

    def setenv(self):
        env = "export HIP_PLATFORM=nvidia; export HIP_COMPILER=nvcc; export HIP_RUNTIME=cuda;"
        env += "export GT_CUDA_COMPILATION_TYPE=HIPCC-NVCC;"
        env += "export GT_ALL_DIR=$PWD/src/hiptestsuite/applications/hpc_apps/gridtools;"
        env += "export GT_TREE_DIR=$GT_ALL_DIR/GridTools;"
        env += "export BOOST_TREE_DIR=$GT_TREE_DIR/boost_1_72_0;"
        env += "export BOOST_INSTALL_DIR=$GT_ALL_DIR/boost_1_72_0;"
        env += "export GRIDTOOLS_TREE_DIR=$GT_TREE_DIR/gridtools;"
        env += "export GRIDTOOLS_BUILD_DIR=$GRIDTOOLS_TREE_DIR/build;"
        env += "export GRIDTOOLS_INSTALL_DIR=$GT_ALL_DIR/gridtools;"
        env += "export GTBENCH_TREE_DIR=$GT_TREE_DIR/gtbench;"
        env += "export GTBENCH_BUILD_DIR=$GTBENCH_TREE_DIR/build;"
        return env

    def buildtest(self):
        if not os.path.exists(os.path.join(self.thistestpath, "boost_1_72_0")):
            print("Building and Installing Boost..")
            cmdexc = self.setenv()
            cmdexc += "cd $GT_TREE_DIR;"
            cmdexc += "tar -xvjf ../boost_1_72_0.tar.bz2;cd $BOOST_TREE_DIR;"
            cmdexc += "./bootstrap.sh --prefix=$BOOST_INSTALL_DIR --with-python=python3;"
            cmdexc += "./b2 install -j8 threading=multi link=shared;"
            runlogdump = tempfile.TemporaryFile("w+")
            execshellcmd_largedump(cmdexc, self.logFile, runlogdump, None)
            runlogdump.close()
        else:
            print("Boost already installed..")
        # Build Gridtools
        if not os.path.exists(os.path.join(self.thistestpath, "GridTools/gridtools/build")):
            print("Building and Installing GridTools..")
            cmdexc = self.setenv()
            cmdexc += "export CXX=/opt/rocm/bin/hipcc;"
            cmdexc += "cd $GT_TREE_DIR;cd $GRIDTOOLS_TREE_DIR;git apply ../../gridtools.patch;mkdir -p $GRIDTOOLS_BUILD_DIR;cd $GRIDTOOLS_BUILD_DIR;"
            cmdexc += "CXX=/opt/rocm/bin/hipcc cmake .. -DBUILD_TESTING=OFF -DBoost_INCLUDE_DIR=$BOOST_INSTALL_DIR/include " +\
            "-DGT_CUDA_COMPILATION_TYPE=$GT_CUDA_COMPILATION_TYPE -DGT_CUDA_ARCH=" + self.cuda_target + " " +\
            "-DGT_ENABLE_BACKEND_CUDA=ON -DGT_ENABLE_BACKEND_MC=OFF -DGT_ENABLE_BACKEND_X86=OFF -DGT_ENABLE_BACKEND_NAIVE=OFF " +\
            "-DGT_USE_MPI=OFF -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=$GRIDTOOLS_INSTALL_DIR;"
            cmdexc += "make -j;"
            cmdexc += "make install;"
            runlogdump = tempfile.TemporaryFile("w+")
            execshellcmd_largedump(cmdexc, self.logFile, runlogdump, None)
            runlogdump.close()
        else:
            print("GridTools already built..")

        # Build Gtbench
        if not os.path.exists(os.path.join(self.thistestpath, "GridTools/gtbench/build")):
            print("Building and Installing Gtbench..")
            cmdexc = self.setenv()
            cmdexc += "export CXX=/opt/rocm/bin/hipcc;"
            cmdexc += "cd $GT_TREE_DIR;cd $GTBENCH_TREE_DIR;git apply ../../gtbench.patch;mkdir -p $GTBENCH_BUILD_DIR;cd $GTBENCH_BUILD_DIR;"
            cmdexc += "CXX=/opt/rocm/bin/hipcc cmake .. -DGridTools_DIR=$GRIDTOOLS_INSTALL_DIR/lib/cmake -DGTBENCH_BACKEND=cuda " +\
            "-DGTBENCH_RUNTIME=single_node -DCMAKE_CXX_FLAGS=--expt-relaxed-constexpr -DBoost_INCLUDE_DIR=$BOOST_INSTALL_DIR/include;"
            cmdexc += "make CFLAGS=--expt-relaxed-constexpr CXXFLAGS=--expt-relaxed-constexpr -j8;"
            runlogdump = tempfile.TemporaryFile("w+")
            execshellcmd_largedump(cmdexc, self.logFile, runlogdump, None)
            runlogdump.close()
        else:
            print("Gtbench already built..")
 
        return True

    def runtest(self, testnum):
        cmdcd = "cd " + os.path.join(self.thistestpath, "GridTools/gtbench/build") + ";"
        if testnum == 0:
            print("Testing Convergence Test")
            cmdrun = "./convergence_tests;"
        elif testnum == 1:
            print("Testing Performance Test")
            cmdrun = "./benchmark --domain-size 256 256 --runs 100;"
        cmdexc = cmdcd + cmdrun
        env = os.environ.copy()
        self.runlog = tempfile.TemporaryFile("w+")
        execshellcmd_largedump(cmdexc, self.logFile, self.runlog, env)

    def clean(self):
        print("Cleaning Gridtools..")
        if self.runlog != None:
            self.runlog.close()

    def parse_result(self, testnum):
        return GridtoolsParser(self.runlog).parse(testnum)
