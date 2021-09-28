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

import re
from testsuite.common.hip_shell import execshellcmd

class KeccakTreeParser():
    def __init__(self, results):
        self.results = results

    def parse(self):
        passedts1 = False
        passedts2 = False
        passedts3 = False
        passedts4 = False

        if re.search("CPU_2stg speed :\s*\d+\.\d+\s*kB/s", self.results):
            passedts1 = True
        if re.search("GPU_2stg speed :\s*\d+\.\d+\s*kB/s", self.results):
            passedts2 = True
        if re.search("GPU_2stg Stream OverlapCPU speed :\s*\d+\.\d+\s*kB/s", self.results):
            passedts3 = True
        if re.search("GPU SCipher speed :\s*\d+\.\d+\s*kB/s", self.results):
            passedts4 = True

        return (passedts1 & passedts2 & passedts3 & passedts4)
