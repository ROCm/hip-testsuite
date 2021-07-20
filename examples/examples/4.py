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

from amd.TesterRepository import Tester
from amd.Test import TestResult, TestData, LogLocation, UserAccess


class MyTestData(TestData, LogLocation, UserAccess):
    """
    Custom Test Input Data
    """
    def __init__(self):
        self.user_value = None
        UserAccess.__init__(self)
        LogLocation.__init__(self)
        TestData.__init__(self)

    def loadConfig(self):
        UserAccess.loadConfig(self)
        self.user_value = self.config.user_value


class CustomTestData(Tester):
    """
    This is example for accessing creating custom test data, here of type MyTestData
    that can be constructed using user input values
    """
    def __init__(self):
        Tester.__init__(self)

    def test(self, test_data: MyTestData):
        if test_data.user_value == 5:
            test_data.test_result = TestResult.PASS
        else:
            test_data.test_result = TestResult.FAIL
