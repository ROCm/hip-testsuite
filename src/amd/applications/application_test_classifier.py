from amd.test_classifier import TestClassifier

from typing import Union


class APPLICATIONS(TestClassifier):
    def __init__(self):
        TestClassifier.__init__(self)

    def add_matched_with_names(self, matched_with_names: Union[None, dict] = None):
        TestClassifier.add_matched_with_names(self, {"applications": matched_with_names})
