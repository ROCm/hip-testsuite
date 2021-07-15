from amd.AMD import AMDObject
from amd.TesterRepository import TesterRepository, Test, GetTests
from typing import Union, List, Dict

import re


class TestSelector(GetTests):
    def __init__(self, tester_repository: TesterRepository):
        AMDObject.__init__(self)
        GetTests.__init__(self, tester_repository=tester_repository)

    def to_select_this_test(self, test: Test, test_name_regexes):
        test_name = test.test_name
        also_matched_with_test_names = test.also_matched_with_test_names
        applicable_for_target = test.applicable_for_target
        classifiers = test.classifiers

        select_this_test = False

        if test_name_regexes is None:
            select_this_test = True
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

    def select_tests(self, log_location: str) -> List[Test]:
        config = self.config
        tests = list()
        run_tests = config.run_tests
        if type(run_tests) == str:
            test_name_regexes = [run_tests]
        elif type(run_tests) == list:
            test_name_regexes = run_tests
        else:
            test_name_regexes = None

        for test_of_tester in self.get_tests(log_location=log_location, quick=True):
            select_this_test = self.to_select_this_test(test=test_of_tester, test_name_regexes=test_name_regexes)
            if select_this_test:
                tests.append(test_of_tester)

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
