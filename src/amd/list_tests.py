import tempfile
import typing
from typing import Union, List

from amd.TesterRepository import TesterRepository, GetTests
from amd.Test import Test, Quick
from amd.test_classifier import TestClassifier


def list_tests(quick: bool, cfg):
    if not quick:
        print("Generating tests, please wait...")
        print(); print(); print()
    pretty_table_installed = False
    try:
        from prettytable import PrettyTable
        pretty_table_installed = True
    except Exception as err:
        print("For better UI experience, please pip3 install -r requirements.txt")

    tester_repository: TesterRepository = TesterRepository()
    tester_repository.addAllTesters()

    get_tests = GetTests(tester_repository=tester_repository)
    get_tests.config = cfg
    get_tests.loadConfig()

    with tempfile.TemporaryDirectory() as tmpdirname:
        tests = get_tests.get_tests(log_location=tmpdirname, quick=quick)

    field_names = ["Classifiers", "Test"]
    if pretty_table_installed:
        test_info_table = PrettyTable()
        test_info_table.field_names = field_names
    else:
        print(" | ".join(field_names))

    for test in tests:
        if not pretty_table_installed:
            classifiers_s = get_classifiers_s(test)
            print(classifiers_s, end=" | ")
            print(test.test_name)
        else:
            classifiers_s = get_classifiers_s(test)
            test_info_table.add_row([classifiers_s, test.test_name])

    if quick:
        quick_getTests_testers = list()
        all_testers = tester_repository.getTesters()

        for tester in all_testers:
            get_tests_t = typing.get_type_hints(tester.getTests)
            get_tests_data_t = None
            if get_tests_t:
                if "get_tests_data" in get_tests_t:
                    get_tests_data_t = get_tests_t["get_tests_data"]

            if get_tests_data_t and issubclass(get_tests_data_t, Quick):
                quick_getTests_testers.append(tester)

        for tester in quick_getTests_testers:
            if not pretty_table_installed:
                classifiers_s = get_classifiers_s_from_classifier(tester.get_test_classifiers())
                print(classifiers_s, end=" | ")
                print("*")
            else:
                classifiers_s = get_classifiers_s_from_classifier(tester.get_test_classifiers())
                test_info_table.add_row([classifiers_s, "*"])

    if pretty_table_installed:
        print(test_info_table.get_string(title="Test Information"))

    if quick:
        print("Note: Run python3 run.py -lst for expanding * tests")
    print("""
    1. If you want to run all tests for amd platform, python3 run.py
    If you want to select specific test(s) e.g. for
    -----------------------
    | Classifiers | Test  |
    |---------------------|
    | c1:c2:c3    | test1 |
    | c4          | test2 |
    | c1:c2       | test3 |
    | c1:c2:c3    | test4 |
    -----------------------
    c1:c2:c3 means c3 is subset of c2 is subset of c1
    e.g. selecting c2 automatically executes tests under c2 and c3
    2. test1 => python3 run.py -t test1
    3. tests with python regex test.* => -t test.*
    4. all c3 => -t c3 (i.e. test1, test4)
    5. all c1 => -t c1 (i.e. test1, test3, test4)
    6. all c1:c2 => -t c1:c2 (i.e. test1, test3, test4)
    7. all c1:c2:c3 => -t c1:c2:c3 (i.e. test1, test4)
    8. test2 and test3 => -t test2 test3
    9. c4 and test4 => -t c4 test4 (i.e. test2, test4)
    """)


def get_classifiers_s_from_classifier(classifiers: List[TestClassifier]):
    classifiers_s = ''
    for ix, classifier in enumerate(classifiers):
        matched_with_names = classifier.matched_with_names
        classifiers_s += ':'.join(get_one_sequence(matched_with_names))
        if ix != len(classifiers) - 1:
            classifiers_s += ', '
    return classifiers_s


def get_classifiers_s(test: Test):
    return get_classifiers_s_from_classifier(test.classifiers)


def get_one_sequence(d: dict):
    k = list(d.keys())[0]
    v = list(d.values())[0]

    if v is None:
        return [k]
    else:
        m = get_one_sequence(v)
        m.insert(0, k)
        return m
