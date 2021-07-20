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

from amd.Test import Test, TestData, GetTestsData, LogLocation, Quick
from amd.test_classifier import TestClassifier
from amd.AMD import AMDObject
from amd.config_processor import ConfigProcessor
from amd.match_fun_args_call import match_fun_args_call
import amd

from typing import List, Union
import pkgutil
import traceback
import typing


class Tester(AMDObject):
    def __init__(self):
        AMDObject.__init__(self)

    def getTests(self, get_tests_data: GetTestsData) -> List[Test]:
        test = Test()
        test.tester = self
        test.test_name = self.__class__.__name__
        return [test]

    def test(self, test_data: TestData):
        pass

    def get_test_classifiers(self) -> Union[None, List[TestClassifier]]:
        return None

    def clean(self):
        pass


class TesterRepository(AMDObject):
    def __init__(self):
        AMDObject.__init__(self)
        self.getTestersFrom = [amd]
        self.testers: Union[None, List[Tester]] = None

    def getTesters(self) -> List[Tester]:
        return self.testers

    def addTesterFrom(self, pkgs: List):
        self.getTestersFrom.extend(pkgs)

    def clearTesterFrom(self):
        self.getTestersFrom.clear()

    def addAllTesters(self):
        if self.testers is None:
            self.testers = list()
        tester_children = get_cls_children_from_pkgs(cls=Tester, pkgs=self.getTestersFrom)
        for tester_child in tester_children:
            self.testers.append(tester_child())

    def addTester(self, tester: Tester):
        if self.testers is None:
            self.testers = list()
        self.testers.append(tester)


class GetTests(ConfigProcessor):
    def __init__(self, tester_repository: TesterRepository):
        ConfigProcessor.__init__(self)
        self.tester_repository = tester_repository

    def get_tests(self, log_location=None, quick=None):
        config = self.config
        testers: List[Tester] = self.tester_repository.getTesters()
        tests = list()

        for tester in testers:
            get_tests_t = typing.get_type_hints(tester.getTests)
            get_tests_data_t = None
            if get_tests_t:
                if "get_tests_data" in get_tests_t:
                    get_tests_data_t = get_tests_t["get_tests_data"]

            if get_tests_data_t is not None:
                get_tests_data = get_tests_data_t()
            else:
                get_tests_data = None

            if isinstance(get_tests_data, LogLocation):
                get_tests_data: LogLocation
                get_tests_data.log_location = log_location

            if isinstance(get_tests_data, ConfigProcessor):
                get_tests_data.config = config
                get_tests_data.loadConfig()

            if isinstance(get_tests_data, Quick):
                get_tests_data: Quick
                get_tests_data.quick = quick

            try:
                tests_of_tester = match_fun_args_call(fun=tester.getTests, args={"get_tests_data": get_tests_data})
                tests.extend(tests_of_tester)
            except Exception as err:
                print("{tester} failed to generate tests".format(tester=tester.__class__.__name__))
                traceback.print_exc()
                continue
        return tests


def get_cls_children_from_pkgs(cls, pkgs: List) -> set:
    import_all_scripts_from(pkgs=pkgs)
    cls_children = get_cls_children(cls=cls)
    return cls_children


def get_cls_children(cls) -> set:
    cls_children = set()

    for subclass in cls.__subclasses__():
        cls_children.add(subclass)
        cls_children.union(get_cls_children(subclass))

    return cls_children


def import_all_scripts_from(pkgs: List):
    for pkg in pkgs:
        for importer, modname, ispkg in pkgutil.iter_modules(pkg.__path__):
            if ispkg:
                import_all_scripts_from([importer.find_module(modname).load_module(modname)])
            else:
                importer.find_module(modname).load_module(modname)
