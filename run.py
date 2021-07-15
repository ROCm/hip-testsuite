import sys
import os
import argparse

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(__file__), "src"))


from amd.TestersExecutor import TestersExecutor
from amd.list_tests import list_tests
import cfg


def parse_args():
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
        list_tests(quick=False, cfg=cfg)
        return False

    if args.list_tests_quick:
        list_tests(quick=True, cfg=cfg)
        return False

    if args.tests:
        cfg.run_tests = args.tests

    return True


def main():
    if parse_args():
        tester_executor: TestersExecutor = TestersExecutor()
        tester_executor.config = cfg
        tester_executor.executeTests()


if __name__ == "__main__":
    main()
