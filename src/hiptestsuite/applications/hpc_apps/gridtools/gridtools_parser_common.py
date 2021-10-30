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

from hiptestsuite.common.hip_shell import execshellcmd
import re

class GridtoolsParser():
    def __init__(self, results):
        self.results = results
        self.conv_tests = ["HORIZONTAL DIFFUSION", "VERTICAL DIFFUSION", "FULL DIFFUSION",\
        "HORIZONTAL ADVECTION", "VERTICAL ADVECTION", "RUNGE-KUTTA ADVECTION", "ADVECTION-DIFFUSION"]
    def parse(self, testnum):
        test_passed = False
        if testnum == 0:
            count = 0
            for test in self.conv_tests:
                if re.search(test, self.results):
                    count = count + 1
            if count == len(self.conv_tests):
                test_passed = True

        elif testnum == 1:
            test1 = False
            test2 = False
            if re.search("Median time:\s*\d*\.\d*s", self.results):
                test1 = True
            if re.search("Columns per second:\s*\d+", self.results):
                test2 = True
            test_passed = test1 & test2

        return test_passed
