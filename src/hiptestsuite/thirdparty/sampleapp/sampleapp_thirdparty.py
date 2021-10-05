from hiptestsuite.TesterRepository import Tester, Test, TestData
from hiptestsuite.Test import HIPTestData, TestResult, HIP_PLATFORM
from typing import Union, List
from hiptestsuite.thirdparty.thirdparty_classifier import THIRDPARTY_CLASSIFIER

class SAMPLEAPP(THIRDPARTY_CLASSIFIER):
    def __init__(self):
        THIRDPARTY_CLASSIFIER.__init__(self)

    def add_matched_with_names(self, matched_with_names: Union[None, dict] = None):
        THIRDPARTY_CLASSIFIER.add_matched_with_names(self, {"sampleapp": matched_with_names})

# Sample App for 3rd party
class sampleapp_test(Tester):
    def __init__(self):
        Tester.__init__(self)

    def getTests(self) -> List[Test]:
        test = Test()
        test.test_name = self.__class__.__name__
        classifier = SAMPLEAPP()
        classifier.add_matched_with_names()
        test.classifiers = [classifier]
        test.tester = self
        return [test]

    def clean(self):
        pass

    def test(self, test_data: HIPTestData):
        print("=============== Running Sample Third Party App ===============")
        test_data.test_result = TestResult.PASS
