from amd.AMD import AMDObject

from typing import Union


class TestClassifier(AMDObject):
    def __init__(self):
        self.matched_with_names = dict()
        AMDObject.__init__(self)

    def add_matched_with_names(self, matched_with_names: Union[None, dict] = None):
        if matched_with_names is None:
            matched_with_names = dict()
        self.matched_with_names.update(matched_with_names)
