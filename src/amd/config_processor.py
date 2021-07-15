from amd.AMD import AMDObject


class ConfigProcessor(AMDObject):
    def __init__(self):
        AMDObject.__init__(self)
        self.config = None

    def loadConfig(self):
        pass
