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

import sys
import os
import argparse

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))


from hiptestsuite.TestersExecutor import TestersExecutor
from hiptestsuite.TesterRepository import TesterRepository
from hiptestsuite.list_tests import list_tests
import cfg
import examples


def parse_args(tester_repository):
    parser = argparse.ArgumentParser()
    parser.add_argument('--platform', help="On which hip_platform to test? amd/nvidia/ default:amd")
    parser.add_argument('-t', '--tests', nargs='+',
        # required=True,
        # choices=TESTS_CHOICES,
        metavar='', help="Test name/Regex/Category/Category:<Test name/Regex/Category>*/List of those separated by space")
    parser.add_argument('-lst', '--list_tests', default=False, action='store_true', help="List all tests")
    parser.add_argument('-lstq', '--list_tests_quick', default=False, action='store_true', help="List all tests quickly, Warning: This may not list some tests which are time consuming to generate, and only category:* will be displayed for them, use -lst for listing all tests")

    args = parser.parse_args()

    if args.platform:
        cfg.HIP_PLATFORM = args.platform

    if args.list_tests:
        list_tests(quick=False, cfg=cfg, tester_repository=tester_repository)
        return False

    if args.list_tests_quick:
        list_tests(quick=True, cfg=cfg, tester_repository=tester_repository)
        return False

    if args.tests:
        cfg.run_tests = args.tests

    return True


def main():
    tester_repository = TesterRepository()
    tester_repository.clearTesterFrom()
    tester_repository.addTesterFrom(pkgs=[examples])
    tester_repository.addAllTesters()
    tester_executor: TestersExecutor = TestersExecutor()
    tester_executor.config = cfg

    if parse_args(tester_repository=tester_repository):
        tester_executor.executeTests(tester_repository=tester_repository)


if __name__ == "__main__":
    main()
