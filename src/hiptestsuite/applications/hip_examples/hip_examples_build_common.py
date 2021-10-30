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

from hiptestsuite.applications.hip_examples.hip_examples_parser import Hip_examples_parser
from hiptestsuite.common.hip_shell import *

class BuildRunCommon():
    '''
    In this class insert the build and execution steps for test cases
    which are identical across different platforms (amd/nvidia/intel).
    '''
    def __init__(self, path):
        self.thistestpath = path
        self.runlogdump = tempfile.TemporaryFile("w+")
        self.runlog = ""
        self.genbinaryname = None
        self.binarydic = {"vectorAdd":["vectoradd_hip.exe"],\
                     "gpu-burn":["/build/gpuburn-hip"],\
                     "strided-access":["strided-access"],\
                     "rtm8":["rtm8_hip"],\
                     "reduction":["reduction"],\
                     "mini-nbody":["/hip/nbody-block", "/hip/nbody-orig", "/hip/nbody-soa"],\
                     "add4":["gpu-stream-hip"],\
                     "cuda-stream":["stream"],\
                     "openmp-helloworld":["openmp_helloworld.exe"],\
                     "rodinia_3.bfs":["bfs"],\
                     "rodinia_3.cfd":["euler3d"],\
                     "rodinia_3.dwt2d":["dwt2d"],\
                     "rodinia_3.gaussian":["gaussian"],\
                     "rodinia_3.heartwall":["heartwall"],\
                     "rodinia_3.hotspot":["hotspot"],\
                     "rodinia_3.hybridsort":["hybridsort"],\
                     "rodinia_3.kmeans":["kmeans"],\
                     "rodinia_3.lavaMD":["lavaMD"],\
                     "rodinia_3.lud":["lud"],\
                     "rodinia_3.myocyte":["myocyte"],\
                     "rodinia_3.nn":["nn"],\
                     "rodinia_3.nw":["nw"],\
                     "rodinia_3.particlefilter":["particlefilter_naive","particlefilter_float"],\
                     "rodinia_3.pathfinder":["pathfinder"],\
                     "rodinia_3.srad":["/srad_v1/srad"],\
                     "rodinia_3.streamcluster":["streamcluster"],\
                     "rodinia_3.b+tree":["b+tree"],\
                     "rodinia_3.backprop":["backprop"],\
                     "HIP-Examples-Applications.BinomialOption":["BinomialOption"],\
                     "HIP-Examples-Applications.BitonicSort":["BitonicSort"],\
                     "HIP-Examples-Applications.dct":["dct"],\
                     "HIP-Examples-Applications.dwtHaar1D":["dwtHaar1D"],\
                     "HIP-Examples-Applications.FastWalshTransform":["FastWalshTransform"],\
                     "HIP-Examples-Applications.FloydWarshall":["FloydWarshall"],\
                     "HIP-Examples-Applications.HelloWorld":["HelloWorld"],\
                     "HIP-Examples-Applications.Histogram":["Histogram"],\
                     "HIP-Examples-Applications.MatrixMultiplication":["MatrixMultiplication"],\
                     "HIP-Examples-Applications.PrefixSum":["PrefixSum"],\
                     "HIP-Examples-Applications.RecursiveGaussian":["RecursiveGaussian"],\
                     "HIP-Examples-Applications.SimpleConvolution":["SimpleConvolution"],\
                     "GPU-STREAM-DOUBLE":["hip-stream"],\
                     "GPU-STREAM-FLOAT":["hip-stream"],\
                     "mixbench-hip-alt":["mixbench-hip-alt", "mixbench-hip-ro"],\
                     "mixbench-hip-ro":["mixbench-hip-alt", "mixbench-hip-ro"]
                     }

    def buildtest(self, logFile, testid, env = None):
        # Prepare the shell command to execute
        cmdcd = "cd "+self.thistestpath+";"
        cmd_build = ""
        if testid == "vectorAdd" or\
        testid == "gpu-burn" or\
        testid == "strided-access" or\
        testid == "cuda-stream" or\
        testid == "rodinia_3.bfs" or\
        testid == "rodinia_3.cfd" or\
        testid == "rodinia_3.dwt2d" or\
        testid == "rodinia_3.gaussian" or\
        testid == "rodinia_3.heartwall" or\
        testid == "rodinia_3.hotspot" or\
        testid == "rodinia_3.hybridsort" or\
        testid == "rodinia_3.kmeans" or\
        testid == "rodinia_3.lavaMD" or\
        testid == "rodinia_3.lud" or\
        testid == "rodinia_3.myocyte" or\
        testid == "rodinia_3.nn" or\
        testid == "rodinia_3.nw" or\
        testid == "rodinia_3.particlefilter" or\
        testid == "rodinia_3.pathfinder" or\
        testid == "rodinia_3.srad" or\
        testid == "rodinia_3.streamcluster" or\
        testid == "rodinia_3.b+tree" or\
        testid == "rodinia_3.backprop" or\
        testid == "HIP-Examples-Applications.BinomialOption" or\
        testid == "HIP-Examples-Applications.BitonicSort" or\
        testid == "HIP-Examples-Applications.dct" or\
        testid == "HIP-Examples-Applications.dwtHaar1D" or\
        testid == "HIP-Examples-Applications.FastWalshTransform" or\
        testid == "HIP-Examples-Applications.FloydWarshall" or\
        testid == "HIP-Examples-Applications.HelloWorld" or\
        testid == "HIP-Examples-Applications.Histogram" or\
        testid == "HIP-Examples-Applications.MatrixMultiplication" or\
        testid == "HIP-Examples-Applications.PrefixSum" or\
        testid == "HIP-Examples-Applications.RecursiveGaussian" or\
        testid == "HIP-Examples-Applications.SimpleConvolution":
            cmd_build = "make clean;make;"
        elif testid == "rtm8":
            cmd_build = "./build_hip.sh;"
        elif testid == "reduction":
            cmd_build = "make clean;make;"
        elif testid == "mini-nbody":
            cmd_build = "cd hip;\
                         bash ./HIP-nbody-block.sh;\
                         bash ./HIP-nbody-orig.sh;\
                         bash ./HIP-nbody-soa.sh;"
        elif testid == "add4":
            cmd_build = "make clean;./buildit.sh;"
        elif testid == "openmp-helloworld":
            cmd_build = "cd openmp-helloworld;make clean;make;"
        elif testid == "GPU-STREAM-DOUBLE" or testid == "GPU-STREAM-FLOAT":
            cmd_build = "make -f HIP.make clean;make -f HIP.make;"
        elif testid == "mixbench-hip-alt" or testid == "mixbench-hip-ro":
            cmd_build = "make clean;rm -Rf Makefile;cmake .;make;"

        cmdexc = cmdcd + cmd_build
        # Execute the command on shell
        if "HIP-Examples-Applications" in testid:
            execshellcmd_largedump(cmdexc, logFile, self.runlogdump, env)
        else:
            self.runlog = execshellcmd(cmdexc, logFile, env)
        # Check if the test binary/ies is/are generated
        for binary in self.binarydic[testid]:
            if not os.path.isfile(self.thistestpath + binary):
                return False

        return True

    def runtest(self, logFile, testid, env = None):
        res = True
        if testid == "vectorAdd":
            # Test already executed during make
            # Run Parser
            ret = Hip_examples_parser().vectorAdd(self.runlog)
            if ret == "Failed":
                res &= False
        elif testid == "gpu-burn":
            cmdexc = "cd " + self.thistestpath + ";" + "." +\
            self.binarydic[testid][0] + " -t 5"
            self.runlog = execshellcmd(cmdexc, logFile, env)
            ret = Hip_examples_parser().gpu_burn(self.runlog)
            if ret == "Failed":
                res &= False
        elif testid == "strided-access":
            cmdexc = "cd " + self.thistestpath + ";" + "./" +\
            self.binarydic[testid][0]
            self.runlog = execshellcmd(cmdexc, logFile, env)
            ret = Hip_examples_parser().strided_access(self.runlog)
            if ret == "Failed":
                res &= False
        elif testid == "rtm8":
            cmdexc = "cd " + self.thistestpath + ";" + "./" +\
            self.binarydic[testid][0]
            self.runlog = execshellcmd(cmdexc, logFile, env)
            ret = Hip_examples_parser().rtm8(self.runlog)
            if ret == "Failed":
                res &= False
        elif testid == "reduction":
            cmdexc = "cd " + self.thistestpath + ";" +\
            "bash ./run.sh"
            self.runlog = execshellcmd(cmdexc, logFile, env)
            ret = Hip_examples_parser().reduction(self.runlog)
            if ret == "Failed":
                res &= False
        elif testid == "mini-nbody":
            # Test already executed during make
            # Run Parser
            ret = Hip_examples_parser().mini_nbody(self.runlog)
            if ret == "Failed":
                res &= False
        elif testid == "add4":
            cmdexc = "cd " + self.thistestpath + ";" +\
            "./runhip.sh"
            self.runlog = execshellcmd(cmdexc, logFile, env)
            ret = Hip_examples_parser().add4(self.runlog)
            if ret == "Failed":
                res &= False
        elif testid == "cuda-stream":
            cmdexc = "cd " + self.thistestpath + ";" + "./" +\
            self.binarydic[testid][0]
            self.runlog = execshellcmd(cmdexc, logFile, env)
            ret = Hip_examples_parser().cuda_stream(self.runlog)
            if ret == "Failed":
                res &= False
        elif testid == "openmp-helloworld":
            # Test already executed during make
            # Run Parser
            ret = Hip_examples_parser().openmp_helloworld(self.runlog)
            if ret == "Failed":
                res &= False
        elif testid == "rodinia_3.bfs" or testid == "rodinia_3.cfd" or \
        testid == "rodinia_3.dwt2d" or testid == "rodinia_3.particlefilter":
            cmdexc = "cd " + self.thistestpath + ";" + "make test;"
            self.runlog = execshellcmd(cmdexc, logFile, env)
            ret = Hip_examples_parser().rodina3(self.runlog, "PASSED", 2)
            if ret == "Failed":
                res &= False
        elif testid == "rodinia_3.gaussian" or testid == "rodinia_3.lavaMD":
            cmdexc = "cd " + self.thistestpath + ";" + "make test;"
            self.runlog = execshellcmd(cmdexc, logFile, env)
            ret = Hip_examples_parser().rodina3(self.runlog, "PASSED", 5)
            if ret == "Failed":
                res &= False
        elif testid == "rodinia_3.heartwall" or testid == "rodinia_3.hotspot"\
        or testid == "rodinia_3.hybridsort" or testid == "rodinia_3.lud"\
        or testid == "rodinia_3.myocyte" or testid == "rodinia_3.nn"\
        or testid == "rodinia_3.nn" or testid == "rodinia_3.pathfinder"\
        or testid == "rodinia_3.srad" or testid == "rodinia_3.streamcluster"\
        or testid == "rodinia_3.b+tree" or testid == "rodinia_3.backprop":
            cmdexc = "cd " + self.thistestpath + ";" + "make test;"
            self.runlog = execshellcmd(cmdexc, logFile, env)
            ret = Hip_examples_parser().rodina3(self.runlog, "PASSED", 1)
            if ret == "Failed":
                res &= False
        elif testid == "rodinia_3.kmeans":
            cmdexc = "cd " + self.thistestpath + ";" + "make test;"
            self.runlog = execshellcmd(cmdexc, logFile, env)
            ret = Hip_examples_parser().rodina3(self.runlog, "PASSED", 4)
            if ret == "Failed":
                res &= False
        elif testid == "HIP-Examples-Applications.BinomialOption" or\
        testid == "HIP-Examples-Applications.BitonicSort" or\
        testid == "HIP-Examples-Applications.dct" or\
        testid == "HIP-Examples-Applications.dwtHaar1D" or\
        testid == "HIP-Examples-Applications.FastWalshTransform" or\
        testid == "HIP-Examples-Applications.FloydWarshall" or\
        testid == "HIP-Examples-Applications.HelloWorld" or\
        testid == "HIP-Examples-Applications.Histogram" or\
        testid == "HIP-Examples-Applications.MatrixMultiplication" or\
        testid == "HIP-Examples-Applications.PrefixSum" or\
        testid == "HIP-Examples-Applications.RecursiveGaussian" or\
        testid == "HIP-Examples-Applications.SimpleConvolution":
            # Test already executed during make
            # Run Parser
            ret = Hip_examples_parser().hip_examples_applications(self.runlogdump)
            if ret == "Failed":
                res &= False
        elif testid == "GPU-STREAM-DOUBLE":
            cmdexc = "cd " + self.thistestpath + ";" +\
            "./hip-stream"
            self.runlog = execshellcmd(cmdexc, logFile, env)
            ret = Hip_examples_parser().gpu_stream(self.runlog)
            if ret == "Failed":
                res &= False
        elif testid == "GPU-STREAM-FLOAT":
            cmdexc = "cd " + self.thistestpath + ";" +\
            "./hip-stream --float"
            self.runlog = execshellcmd(cmdexc, logFile, env)
            ret = Hip_examples_parser().gpu_stream(self.runlog)
            if ret == "Failed":
                res &= False
        elif testid == "mixbench-hip-alt":
            cmdexc = "cd " + self.thistestpath + ";" +\
            "./mixbench-hip-alt"
            self.runlog = execshellcmd(cmdexc, logFile, env)
            ret = Hip_examples_parser().mix_bench(self.runlog)
            if ret == "Failed":
                res &= False
        elif testid == "mixbench-hip-ro":
            cmdexc = "cd " + self.thistestpath + ";" +\
            "./mixbench-hip-ro"
            self.runlog = execshellcmd(cmdexc, logFile, env)
            ret = Hip_examples_parser().mix_bench(self.runlog)
            if ret == "Failed":
                res &= False

        return res

    def clean(self, testid):
        for binary in self.binarydic[testid]:
            if os.path.exists(self.thistestpath + binary):
                os.remove(self.thistestpath + binary)
