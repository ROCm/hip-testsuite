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

from hiptestsuite.AMD import AMDObject
from hiptestsuite.TesterRepository import TesterRepository, Test, GetTests
from typing import Union, List, Dict

import re, sys, os


class TestSelector(GetTests):
    def __init__(self, tester_repository: TesterRepository):
        AMDObject.__init__(self)
        GetTests.__init__(self, tester_repository=tester_repository)

    def to_select_this_test(self, test: Test, test_name_regexes, exclude_module_paths=None):
        test_name = test.test_name
        also_matched_with_test_names = test.also_matched_with_test_names
        applicable_for_target = test.applicable_for_target
        classifiers = test.classifiers

        select_this_test = False
        class_abs_path = os.path.abspath(sys.modules[test.tester.__class__.__module__].__file__)

        if test_name_regexes is None:
            select_this_test = True
            for exclude_module_path in exclude_module_paths:
                if exclude_module_path in class_abs_path:
                    print("Warning: Test " + test_name + " is excluded, please run selectively")
                    select_this_test = False
                    break
        else:
            for test_name_regex in test_name_regexes:
                test_name_regex: Union[str, List[str]] = test_name_regex

                if type(test_name_regex) == str:
                    asked_classifiers: List[str] = test_name_regex.split(':')
                else:  # type(test_name_regex) == list:
                    asked_classifiers: List[str] = test_name_regex

                in_dicts: List[Dict] = list()
                ret_is_sequence_in_dicts_obj = ret_is_sequence_in_dicts()
                if classifiers:
                    for classifier in classifiers:
                        in_dicts.append(classifier.matched_with_names)
                    is_sequence_in_dicts(sequence=asked_classifiers, in_dicts=in_dicts,
                                         ret_is_sequence_in_dicts_obj=ret_is_sequence_in_dicts_obj)

                if not classifiers or ret_is_sequence_in_dicts_obj.initial_matching:
                    if classifiers and ret_is_sequence_in_dicts_obj.last_also_matching:
                        select_this_test = True
                    else:
                        if re.findall(asked_classifiers[-1].lower(), test_name.lower()):
                            select_this_test = True
                        if also_matched_with_test_names:
                            for also_matched_with_test_name in also_matched_with_test_names:
                                if re.findall(asked_classifiers[-1].lower(), also_matched_with_test_name.lower()):
                                    select_this_test = True
        return select_this_test

    def check_quicktestlist(self, test_to_find, quicktestlist):
        testfound = False
        for test in quicktestlist:
            if re.search(test_to_find, test.test_name):
                testfound = True
        return testfound

    def check_classifierlist(self, test_to_find, classifierlist):
        testfound = False
        for thisclassifier in classifierlist:
            if re.search(test_to_find, thisclassifier):
                testfound = True
        return testfound

    def check_quicktestlist_sufficient(self, usertestlist, quicktestlist, classifierlist):
        testcount = 0
        for test in usertestlist:
            if self.check_classifierlist(test, classifierlist):
                # We know this test is non conformance
                testcount = testcount + 1
            elif self.check_quicktestlist(test, quicktestlist):
                testcount = testcount + 1
        isSufficient = True
        if len(usertestlist) != testcount:
            # quicktestlist is not sufficient
            isSufficient = False
        return isSufficient

    def get_all_classifierkeys(self, testclassifierdict, classifierlist):
        for key in testclassifierdict:
            classifierlist.append(key)
            if testclassifierdict[key] != None:
                if isinstance(testclassifierdict[key], dict):
                    self.get_all_classifierkeys(testclassifierdict[key], classifierlist)

    def get_all_classifiers(self, testclassifier, classifierlist):
        for myclassifier in testclassifier:
            self.get_all_classifierkeys(myclassifier.matched_with_names, classifierlist)

    def select_tests(self, log_location: str, exclude_module_paths) -> List[Test]:
        config = self.config
        tests = list()
        run_tests = config.run_tests
        if type(run_tests) == str:
            test_name_regexes = [run_tests]
        elif type(run_tests) == list:
            test_name_regexes = run_tests
        else:
            test_name_regexes = None

        if test_name_regexes is None:
            for test_of_tester in self.get_tests(log_location=log_location, quick=False):
                select_this_test = self.to_select_this_test(test=test_of_tester, test_name_regexes=test_name_regexes, exclude_module_paths=exclude_module_paths)
                if select_this_test:
                    tests.append(test_of_tester)
        else:
            for test_of_tester in self.get_tests(log_location=log_location, quick=True):
                select_this_test = self.to_select_this_test(test=test_of_tester, test_name_regexes=test_name_regexes)
                if select_this_test:
                    tests.append(test_of_tester)

            classifierlist = list()
            for thistest in tests:
                tmpclassifierlist = list()
                self.get_all_classifiers(thistest.classifiers, tmpclassifierlist)
                thistestclassification = ""
                for elem in tmpclassifierlist:
                    thistestclassification = thistestclassification + elem + ":"
                classifierlist.append(thistestclassification)
            # Check at this point if quick search is sufficient
            if False == self.check_quicktestlist_sufficient(test_name_regexes, tests, classifierlist):
                tests.clear()
            if not tests:
                for test_of_tester in self.get_tests(log_location=log_location, quick=False):
                    select_this_test = self.to_select_this_test(test=test_of_tester, test_name_regexes=test_name_regexes)
                    if select_this_test:
                        tests.append(test_of_tester)

        return tests


class ret_is_sequence_in_dicts:
    def __init__(self):
        self.initial_matching = False
        self.last_also_matching = False


def next_item_process(item, sequence: List, till_matched: List):
    if till_matched == sequence:
        return
    if sequence[len(till_matched)] == item:
        till_matched.append(item)
    else:
        till_matched.clear()


def is_sequence_in_dict(sequence: List, in_dict: Dict, ret_is_sequence_in_dict_obj: ret_is_sequence_in_dicts, till_matched: List):
    for k, v in in_dict.items():
        next_item_process(item=k, sequence=sequence, till_matched=till_matched)
        if sequence[:-1] == till_matched:
            ret_is_sequence_in_dict_obj.initial_matching = True
        if sequence == till_matched:
            ret_is_sequence_in_dict_obj.last_also_matching = True
            ret_is_sequence_in_dict_obj.initial_matching = True
        else:
            if type(v) == dict:
                is_sequence_in_dict(sequence=sequence, in_dict=v, ret_is_sequence_in_dict_obj=ret_is_sequence_in_dict_obj, till_matched=till_matched)


def is_sequence_in_dicts(sequence: List, in_dicts: List[Dict], ret_is_sequence_in_dicts_obj: ret_is_sequence_in_dicts):
    initial_matching = False
    last_also_matching = False
    for in_dict in in_dicts:
        ret_is_sequence_in_dict_obj = ret_is_sequence_in_dicts()
        is_sequence_in_dict(sequence=sequence, in_dict=in_dict, ret_is_sequence_in_dict_obj=ret_is_sequence_in_dict_obj, till_matched=list())
        seq_initial_matching = ret_is_sequence_in_dict_obj.initial_matching
        seq_last_also_matching = ret_is_sequence_in_dict_obj.last_also_matching

        if not initial_matching:
            initial_matching = seq_initial_matching
        if not last_also_matching:
            last_also_matching = seq_last_also_matching
        if seq_initial_matching and seq_last_also_matching:
            break

    ret_is_sequence_in_dicts_obj.initial_matching = initial_matching
    ret_is_sequence_in_dicts_obj.last_also_matching = last_also_matching
