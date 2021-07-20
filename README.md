# HIP Testsuite

##	Description

HIP Testsuite is a suite to test HIP on different platforms.  At high level, testsuite helps in doing below activities
-	Download required projects for tests (as mentioned in cfg.py)
-	Build all/specific tests for specified platform (as provided through command line)
-	Run all/specific tests
-	Consolidate the reports and logs
Testsuite predominantly uses python scripts that can run with python 3.x

##	Download and execute HIP-Testsuite

###	Preconditions

-	Python 3.6 or above is installed on system
-	Appropriate Rocm or Nvcc drivers are installed on system
-	Git (version 2.17.1 or more) should be installed
-	CMake (version 3.4 or more) should be installed

###	Steps
•	Clone the TestSuite repository
```
<git clone command from public github to be updated later>
$ cd hip-testsuite
```

•	One time dependency installation

```
$ pip3 install -r requirements.txt
```

•	Verify "cfg.py" contents to make sure that desired values are present
To provide input configurations like log location, platform, repos etc. "cfg.py" is used.  Please check 6.3.1 for further details.

•	Use “run.py” to run the test
To start executing the tests "run.py" is used. User inputs like test filters need to be provided via command line input to "run.py". Platform name (e.g. nvidia/amd) can also be provided via the command line input.
Some of the command line for run.py are briefly mentioned here. For detailed description of these, please refer to 6.3.2 and 6.3.3.
-h: To show all options
```
$ python3 run.py -h
```
-lstq: To list all tests quickly
```
$ python3 run.py -lstq
```
-lst: To list all the test (Note: platform should be specified if running for other than AMD platform)
```
$ python3 run.py -lst
```
Run all the tests on amd platform
```
$ python3 run.py
```
Select the test with -t <test> to run specific <test>
on amd platform 
```
$ python3 run.py -t <test>
```
on Nvidia platform
```
$ python3 run.py -t <test> --platform nvidia
```
Some examples to execute a category of tests
```
$ python3 run.py -t conformance --platform amd
$ python3 run.py -t samples --platform amd
$ python3 run.py -t examples --platform amd
```

##	Details for working with HIP-Testsuite

###	Testsuite configuration

Test suite considers contents of “cfg.py” for configurable items.  There are two types of information in cfg.py.
-	Default value for some parameters that can be over-ridden through command line while running test suite
-	Information like test repository/branch info etc.

|  Configuration  |  Explanation  |
| --------------- | ------------- |
| log_location | We can provide the location, in python string, where log files should be dumped. |
|              | If none is provided, then logs are dumped under "report" folder in the current working directory, which is "hip-testsuite/". |
| user_password	| If any password needs to be set during the execution of tests, then it can be |
|               | provided using this parameter. Currently set to None. |
| HIP_PLATFORM | Platform value (amd/nvidia) can also be passed to the test using this parameter. |
| repos | This is a Python dictionary structure to provide information on all the repos required for tests. |
|       | -	"repo_url" should contain the GIT URL of the repository to clone. |
|       | -	"branch" should contain the branch name |
|       | -	"commit_id" should contain the GIT Commit ID to test. |
|       |•	If no branch is to be specified, then keep branch = None. |
|       |•	If no commit_id is to specified, then keep commit_id = None. |


### Command line options for run.py

#### Help

To get help on "run.py" execute
```
$ python3 run.py -h
```
or
```
$ python3 run.py --help
```
#### Test selection options

"-lstq" or "--list_tests_quick": List all tests quickly. Note that this option generates only a partial list of test cases. For tests which are time consuming to generate only category:* will be displayed for them. To display the full list use "-lst" or "--list_tests".

"-lst" or "--list_tests": Gets the list of all test cases.

Note: "-lst/--list_tests" will take some time to display the results as build happens in the background to fetch the list of tests for some ctest based modules like dtest.

Note: For platforms other than "amd" be sure to provide --platform option. For example:
```
$ python3 run.py -lst --platform nvidia
```

"-t": With this option we provide testcase filter. For example, by providing a filter name like "samples" (shown in section 2) we can execute all tests cases under HIP-Samples.

Likewise, to execute all performance test cases, use "performance" as filter.

To run all performance tests under sample, use filter "samples:performance".

When "-t" option is not provided, all tests in testsuite are executed.

"--platform": With this option we provide the platform type ("amd"/"nvidia") where the testcases are run. If "--platform" is not provided, "amd" is taken as default.

### Overview of filters for run.py

All tests in the hip-testsuite are broadly classified into the following categories - "samples", "examples" and "conformance". Under "samples" and "examples" there are further 3 sub-categories - "performance", "stress", and "mini-app". HIP directed tests fall under "conformance" category while the rest of the tests use subcategories - "performance", "stress" and "mini-app".

Below are the list of filters that can be applied currently after "-t":

| Filter | Test cases executed |
| ------ | ------------------- |
| No filter options provided | All tests are executed by default. |
| “samples” | Executes all test cases under HIP-Samples |
| "samples:performance" | Executes all performance test cases under HIP-Samples |
| "samples:mini-app" | Executes all mini-app test cases under HIP-Samples |
| "examples" | Executes all test cases under HIP-Examples |
| "examples:performance" | Executes all performance test cases under HIP-Examples |
| "examples:stress" | Executes all stress test cases under HIP-Examples |
| "examples:mini-app" | Executes all mini-app test cases under HIP-Examples |
| "performance" | Executes all performance test cases in testsuite |
| "mini-app" | Executes all mini-app test cases in testsuite |
| "stress" | Executes all stress test cases in testsuite |
| "conformance" | Executes all HIP dtests |
| "testname" for e.g "BitExtract" ("testname" is typically the class name) | Executes only the specific test cases with names with “testname” |

Executing a group of tests with similar name Use wildcards like ".*testname.*". See example 2 below

Executing Multiple tests To execute multiple tests, specify the tests. The test names must be separated with a space. Check example 3 below.

Examples:

1. runs test cases "bitextract" and "directed_tests.devicelib.hip_bitextract"
```
$ python3 run.py -t BitExtract
```
2. We can use wildcards to filter test cases to execute.

To execute all test cases containing "memset" name
```
$ python3 run.py -t ".*memset.*"
```
To execute only the "memset" test cases under "directed_tests.runtimeapi.memory"
```
$ python3 run.py -t directed_tests.runtimeapi.memory.*memset.*
```
3. Specifying multiple tests
```
$ python3 run.py -t samples examples --platform amd
```
4. When no "-t" option is specified all tests,except directed tests, are executed by default.
```
$ python3 run.py --platform nvidia
```
Use "-lst" or "--list_tests" options to get the list of all test cases.

### Testsuite Report

Reports are generated under the folder mentioned in parameter "log_location" in cfg.py. The report for each run is timestamped. For example, "report/2021_07_12_23_32_04/bitextract". At the end of each run, the summary report is displayed. This summary report provides the list of test cases with result, the metric and system information. The same is available under "report/" folder as report.log. The same report also will be available in JSON format as report.json

##	Adding new tests to the testsuite
Please refer to "examples" folder for example tests 

