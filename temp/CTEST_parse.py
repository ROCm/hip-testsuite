#from parser.test.parser import Parser
import re
from parser.test.prerequisites_failed import prerequisite_failed


class CTESTParser:#(Parser):

    def __init__(self, buildNo=None):
        self.buildNo = None
        self.template = None
        #Parser.__init__(self, buildNo)

    def parse(self, fileName=None, text=None):
        if fileName and not text:
            with open(fileName, "r") as fp:
                text = fp.read()

        if not text:
            raise AttributeError("filename and text empty")

        n_testsuites=self.getTotalTestSuites(text)
        n_testcases=self.getTotalTestCases(text)

        if n_testcases is None:
            return prerequisite_failed()

        final_status=self.getFinalStatus(text)
        #total_time=self.getTotalTime(text)

        p2 = re.compile(r'(\d+) tests? from (\w+\/?\d*)$')
        p1 = re.compile(r'(\d+) tests? from (\w+\/?\d*)(\,)')
        p4 = re.compile(r'(\d+) tests? from (\w+\/?\d*) \(\d+ ms total\)')
        testSuiteInfo=self.getTestSuitesInfo(text)

        global_testInfo = {}
        global_testInfo["testSuiteInfo"]=testSuiteInfo
        global_testInfo["nTestSuites"]=n_testsuites
        global_testInfo["nTestCases"]=n_testcases
        global_testInfo["status"]=final_status
        #global_testInfo["total_time"]=str(total_time)
        return global_testInfo


    def getFinalStatus(self, text):
        if '100% tests passed' not in text:
            return False
        else:
            return True

    def getTestSuitesInfo(self, text):
        testsuite_to_testcaes = {}
        testsuite_to_testcaes["default"]=self.getTestSuiteInfo(text)
        return testsuite_to_testcaes

    def getTestSuiteInfo(self, text):
        from result.test_result import Multi_Test_Status

        # regex = r'Test\s+#\d+:\s+(\S+)\s+\.+(.+)\s*(\d+)\.(\d+) sec'
        # regex = r'Test\s+#\d+:\s+(\S+)\s+\.+\s*([^\d\W]+)\s*(\d+)\.(\d+) sec'
        regex = r'Test\s+#\d+:\s+(\S+)\s+\.+\s*([^\d]+)\s*(\d+)\.(\d+) sec'
        m = re.findall(regex,text)

        """
        34/229 Test  #34: thrust.hip.merge_by_key .................................***Exception: Other171.94 sec
        [('thrust.hip.merge_by_key', '***Exception: Other', '171', '94')]
        [('hip.device_api', 'Passed', '0', '20')]
        
        2/9 Test  #6: hipcub.BlockLoadStore .............   Passed   10.72 sec
        [('hipcub.BlockLoadStore', 'Passed   ', '10', '72')]
        
        Start  72: directed_tests/g++/hipMalloc.tst
        72/335 Test  #72: directed_tests/g++/hipMalloc.tst ........***Skipped   0.00 sec
        """

        testcases_info={}

        for testcase in m:
            testcase_status = testcase[1].strip()
            testcase_name = testcase[0].strip()
            time = testcase[2]+'.'+testcase[3]
            testcases_info[testcase_name]={}
            if testcase_status=="Passed":
                testcases_info[testcase_name]['status']=True
            elif "Skipped" in testcase_status:
                testcases_info[testcase_name]['status'] = Multi_Test_Status.SKIP
            else:
                testcases_info[testcase_name]['status']=False
            testcases_info[testcase_name]['time']=time
        return testcases_info


    def getTotalTestSuites(self, text):
        #testcase_testsuite_regex = r" Running (\d+) tests? from (\d+) test cases?."
        #[(m.start(), m.end()) for m in re.finditer(testcase_testsuite_regex, text)]
        #m=re.match(testcase_testsuite_regex, text)
        #return m.groups()[1]
        return 1

    def getTotalTestCases(self, text):
        #testcase_testsuite_regex = r" Running (\d+) tests? from (\d+) test cases?."
        #m = re.match(testcase_testsuite_regex, text)
        #return m.groups()[0]
        m = re.findall(r'(\d+) tests failed out of (\d+)', text)
        if m:
            return m[0][1]
        else:
            return None

    def getTotalTime(self, text):
        "Total Test time (real) = 100.39 sec"
        m = re.findall(r'Total Test time \(real\) = (\d+)\.(\d+) sec', text)
        return m[0][0]+'.'+m[0][1]


if __name__ == '__main__':
    pass
