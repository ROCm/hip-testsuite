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

from hiptestsuite.TesterRepository import Tester
from hiptestsuite.Test import TestData, TestResult, Test
from hiptestsuite.test_classifier import TestClassifier

from typing import List, Union


class C1(TestClassifier):
    def __init__(self):
        TestClassifier.__init__(self)

    def add_matched_with_names(self, matched_with_names: Union[None, dict] = None):
        TestClassifier.add_matched_with_names(self, {"c1": matched_with_names})


class C2(C1):
    def __init__(self):
        C1.__init__(self)

    def add_matched_with_names(self, matched_with_names: Union[None, dict] = None):
        C1.add_matched_with_names(self, {"c2": matched_with_names})


class Test2(Tester):
    """
    This assigns classifier to test, so it can be invoked with c1, c1:test2_1, test2_1 like 1.py.
    In addition to that, it adds test2_2, and assigns classifier c2, which is subset of c1
    """
    def __init__(self):
        Tester.__init__(self)

    def getTests(self) -> List[Test]:
        test2_1 = Test()
        test2_1.test_name = "test2_1"
        c1 = C1()
        c1.add_matched_with_names()
        test2_1.classifiers = [c1]
        test2_1.tester = self

        test2_2 = Test()
        test2_2.test_name = "test2_2"
        c2 = C2()
        c2.add_matched_with_names()
        test2_2.classifiers = [c2]
        test2_2.tester = self

        return [test2_1, test2_2]

    def test(self, test_data: TestData):
        print("called for {test_name}".format(test_name=test_data.test.test_name))
        test_data.test_result = TestResult.PASS
