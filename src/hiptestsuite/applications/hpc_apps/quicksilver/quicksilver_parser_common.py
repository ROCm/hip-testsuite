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

class QuicksilverParser():
    def __init__(self, results):
        self.results = results

    def parse(self):
        passed1 = False
        passed2 = False
        passed3 = False
        passed4 = False
        if re.search("PASS:: Absorption / Fission / Scatter Ratios maintained with \d+% tolerance", self.results):
            passed1 = True
        if re.search("PASS:: Collision to Facet Crossing Ratio maintained even balanced within \d+% tolerance", self.results):
            passed2 = True
        if re.search("PASS:: No Particles Lost During Run", self.results):
            passed3 = True
        if re.search("PASS:: Fluence is homogenous across cells with \d+% tolerance", self.results):
            passed4 = True

        return (passed1 & passed2 & passed3 & passed4)
