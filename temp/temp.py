from amd.TesterRepository import Tester
from amd.Test import HIPTestData, TestResult, Test, HIPBuildData
from typing import List


class Temp(Tester):
    def __init__(self):
        Tester.__init__(self)

    def getTests(self, get_tests_data: HIPBuildData) -> List[Test]:
        print("In getTests starts")
        print(get_tests_data.log_location)
        print(get_tests_data.user_password)
        print(get_tests_data.repos)
        print(get_tests_data.HIP_PLATFORM)

        test1 = Test()
        test1.test_name = "temp1"
        test1.tester = self

        test2 = Test()
        test2.test_name = "temp2"
        test2.tester = self

        print("In getTests end")

        return [test1, test2]

    def test(self, test_data: HIPTestData):
        print("called for {test_name}".format(test_name=test_data.test.test_name))
        test_data.test_result = TestResult.PASS
