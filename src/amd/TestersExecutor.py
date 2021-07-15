from amd.TesterRepository import TesterRepository, Tester, Test
from amd.test_selector import TestSelector
from amd.config_processor import ConfigProcessor
from amd.Test import TestResult

import os
import traceback
import logging
import subprocess
import sys
import typing
from typing import Union, List, Dict
import json
import re
import time
import datetime


class TestersExecutor(ConfigProcessor):
    def __init__(self):
        ConfigProcessor.__init__(self)

    def executeTests(self, tester_repository: TesterRepository=None):
        start_datetime = datetime.datetime.now()
        config = self.config
        log_location = config.log_location
        if log_location is None:
            log_location = os.getcwd()
        os.makedirs(log_location, exist_ok=True)
        root_log_dir = "report"
        root_log_location = os.path.join(log_location, root_log_dir)
        os.makedirs(root_log_location, exist_ok=True)
        timestamped_log_location = os.path.join(root_log_location, start_datetime.strftime("%Y_%m_%d_%H_%M_%S"))
        os.makedirs(timestamped_log_location, exist_ok=True)
        relative_timestamped_log_location = os.path.join(root_log_dir, start_datetime.strftime("%Y_%m_%d_%H_%M_%S"))
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        fh = logging.FileHandler(filename=os.path.join(timestamped_log_location, "report.log"), mode='w+')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(ch)
        logger.addHandler(fh)

        selected_test_filter = config.run_tests
        if selected_test_filter:
            logger.info("Selected Test Filter: {selected_test_filter}".format(selected_test_filter=" ".join(selected_test_filter)))
        logger.info("Execution Logs: {log_location}".format(log_location=log_location))

        if tester_repository is None:
            tester_repository: TesterRepository = TesterRepository()
            tester_repository.addAllTesters()

        test_selector: TestSelector = TestSelector(tester_repository=tester_repository)
        test_selector.config = config
        tests: List[Test] = test_selector.select_tests(log_location=timestamped_log_location)
        tests: List[Test] = sorted(tests, key=lambda x: x.test_name)
        tests_status = dict()
        tests_logs = dict()
        tests_relative_logs = dict()

        for test in tests:
            print("Started Test: {test_name}".format(test_name=test.test_name.lower()))

            test_t = typing.get_type_hints(test.tester.test)
            test_data_t = None
            if test_t:
                test_data_t = test_t["test_data"]

            test_data = test_data_t()

            if isinstance(test_data, ConfigProcessor):
                test_data: ConfigProcessor
                test_data.config = config
                test_data.loadConfig()
            test_data.test = test
            test_data.log_location = os.path.join(timestamped_log_location, test.test_name.lower())
            os.makedirs(test_data.log_location, exist_ok=True)

            try:
                test.tester.test(test_data=test_data)
            except Exception as error:
                test_data.test_result = TestResult.ERROR
                traceback.print_exc()

            tests_status[test] = test_data.test_result
            tests_logs[test] = test_data.log_location
            tests_relative_logs[test] = os.path.join(relative_timestamped_log_location, test.test_name.lower())
            print("Completed Test: {test_name} with result {result}".format(test_name=test.test_name.lower(), result=test_data.test_result.name))

        for test in tests:
            try:
                test.tester.clean()
            except Exception as error:
                traceback.print_exc()

        end_datetime = datetime.datetime.now()

        # ### Reporting
        try:
            opt_rocm_version: Union[None, str] = get_opt_rocm_version()
        except Exception as error:
            opt_rocm_version = None
        try:
            os_name: Union[None, str] = get_os_name()
        except Exception as error:
            os_name = None
        try:
            os_version: Union[None, str] = get_os_version()
        except Exception as error:
            os_version = None
        try:
            rocm_agents: Union[None, List[str]] = get_rocm_agents()
        except Exception as error:
            rocm_agents = None

        passed_tests = get_passed_tests(tests_status=tests_status)
        failed_tests = get_failed_tests(tests_status=tests_status)
        errored_tests = get_errored_tests(tests_status=tests_status)
        skipped_tests = get_skipped_tests(tests_status=tests_status)

        logger.info("Start Time: {start_datetime}".format(start_datetime=start_datetime.strftime("%Y/%m/%d %H:%M:%S")))
        logger.info("End Time: {end_datetime}".format(end_datetime=end_datetime.strftime("%Y/%m/%d %H:%M:%S")))
        # ### prettytable
        field_names = ["Test Name", "Result", "Log"]
        system_info_field_names = ["Component", "Information"]
        test_cnt_field_names = ["PASS", "FAIL", "ERROR", "SKIP"]
        try:
            from prettytable import PrettyTable
            if tests_status:
                summary_table = PrettyTable()
                summary_table.field_names = field_names
                test_cnt_table = PrettyTable()
                test_cnt_table.field_names = test_cnt_field_names
                for test, test_status in passed_tests.items():
                    summary_table.add_row([test.test_name.lower(), test_status.name, tests_relative_logs[test]])
                for test, test_status in failed_tests.items():
                    summary_table.add_row([test.test_name.lower(), test_status.name, tests_relative_logs[test]])
                for test, test_status in errored_tests.items():
                    summary_table.add_row([test.test_name.lower(), test_status.name, tests_relative_logs[test]])
                for test, test_status in skipped_tests.items():
                    summary_table.add_row([test.test_name.lower(), test_status.name, tests_relative_logs[test]])

                logger.info('\n' + summary_table.get_string(title="Summary"))

                test_cnt_table.add_row([str(len(passed_tests)), str(len(failed_tests)), str(len(errored_tests)), str(len(skipped_tests))])
                logger.info('\n' + test_cnt_table.get_string(title="Metrics"))

            system_info_table = PrettyTable()
            system_info_table.field_names = system_info_field_names
            system_info_table.add_row(["OS", (os_name if os_name else "Can't get OS name!") + " " + (os_version if os_version else "Can't get OS version")])
            system_info_table.add_row(["ROCm Agents", ", ".join(rocm_agents) if rocm_agents else "Can't get ROCm agents"])
            system_info_table.add_row(["/opt/rocm version", opt_rocm_version if opt_rocm_version else "Can't get /opt/rocm version"])
            logger.info('\n' + system_info_table.get_string(title="System Information"))
        except Exception as error:
            logger.warning("For better UI experience, please pip3 install -r requirements.txt")

            if tests_status:
                logger.info("********Summary********")
                logger.info(" | ".join(field_names))
                for test, test_status in passed_tests.items():
                    logger.info(test.test_name.lower() + " | " + test_status.name + " | " + tests_relative_logs[test])
                for test, test_status in failed_tests.items():
                    logger.info(test.test_name.lower() + " | " + test_status.name + " | " + tests_relative_logs[test])
                for test, test_status in errored_tests.items():
                    logger.info(test.test_name.lower() + " | " + test_status.name + " | " + tests_relative_logs[test])
                for test, test_status in skipped_tests.items():
                    logger.info(test.test_name.lower() + " | " + test_status.name + " | " + tests_relative_logs[test])

                logger.info("********Metrics********")
                logger.info(" | ".join(test_cnt_field_names))
                logger.info(str(len(passed_tests)) + " | " + str(len(failed_tests)) + " | " + str(len(errored_tests)) + " | " + str(len(skipped_tests)))

            logger.info("********System Information********")
            logger.info(" | ".join(system_info_field_names))
            logger.info("OS" + " | " + (os_name if os_name else "Can't get OS name!") + " " + (os_version if os_version else "Can't get OS version"))
            logger.info("ROCm Agents" + " | " + ", ".join(rocm_agents) if rocm_agents else "Can't get ROCm agents")
            logger.info("/opt/rocm version" + " | " + opt_rocm_version if opt_rocm_version else "Can't get /opt/rocm version")

        logger.info("Note, All log locations are relative to {log_location}".format(log_location=log_location))

        # ### json
        json_root = dict()
        tests_root = json_root["tests"] = dict()
        for test, test_status in tests_status.items():
            test_root = tests_root[test.test_name.lower()] = dict()
            test_root["status"] = test_status.name
            test_root["log_location"] = tests_logs[test]

        json_root["num_passed"] = len(passed_tests)
        json_root["num_failed"] = len(failed_tests)
        json_root["num_errored"] = len(errored_tests)
        json_root["num_skipped"] = len(skipped_tests)

        json_root["opt_rocm_version"] = opt_rocm_version
        json_root["os_name"] = os_name
        json_root["os_version"] = os_version
        json_root["rocm_agents"] = rocm_agents
        json_root["start_datetime"] = start_datetime.strftime("%Y_%m_%d_%H_%M_%S")
        json_root["end_datetime"] = end_datetime.strftime("%Y_%m_%d_%H_%M_%S")
        json_root["selected_test_filter"] = selected_test_filter

        with open(os.path.join(timestamped_log_location, 'report.json'), 'w+', encoding='utf-8') as f:
            json.dump(json_root, f, ensure_ascii=False, indent=4)


def get_os_name() -> str:
    cmd = "awk -F= '/^NAME=/{print $2}' /etc/os-release"
    o, e = subprocess.Popen([cmd], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True).communicate()
    o = o.decode('utf-8')
    os_version = o.strip('\n')
    os_version = os_version.replace('"', '')
    return os_version


def get_os_version() -> str:
    cmd = "awk -F= '/^VERSION_ID=/{print $2}' /etc/os-release"
    o, e = subprocess.Popen([cmd], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True).communicate()
    o = o.decode('utf-8')
    os_version = o.strip('\n')
    os_version = os_version.replace('"', '')
    return os_version


class NoROCmAgentsFound(Exception):
    def __init__(self):
        Exception.__init__(self)


def get_rocm_agents() -> List[str]:
    gpus = list()
    cmd = "/opt/rocm/bin/rocminfo"
    o, e = subprocess.Popen([cmd], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True).communicate()
    o = o.decode('utf-8')
    for l in o.splitlines():
        gpus_match = re.findall("^  Name:\s+(.+)", l)
        if gpus_match:
            gpus.append(gpus_match[0].strip())
    if not gpus:
        raise NoROCmAgentsFound()
    return gpus


def get_opt_rocm_version() -> str:
    cmd = "cat /opt/rocm/.info/version"
    o, e = subprocess.Popen([cmd], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True).communicate()
    o = o.decode('utf-8')
    opt_rocm_version = o.strip('\n')
    return opt_rocm_version


def get_passed_tests(tests_status: Dict[Test, TestResult]) -> Dict[Test, TestResult]:
    return get_status_filtered_tests(tests_status=tests_status, status=TestResult.PASS)


def get_failed_tests(tests_status: Dict[Test, TestResult]) -> Dict[Test, TestResult]:
    return get_status_filtered_tests(tests_status=tests_status, status=TestResult.FAIL)


def get_errored_tests(tests_status: Dict[Test, TestResult]) -> Dict[Test, TestResult]:
    return get_status_filtered_tests(tests_status=tests_status, status=TestResult.ERROR)


def get_skipped_tests(tests_status: Dict[Test, TestResult]) -> Dict[Test, TestResult]:
    return get_status_filtered_tests(tests_status=tests_status, status=TestResult.SKIP)


def get_status_filtered_tests(tests_status: Dict[Test, TestResult], status: TestResult) -> Dict[Test, TestResult]:
    filtered_tests = dict()
    for test, test_status in tests_status.items():
        if test_status == status:
            filtered_tests[test] = test_status
    return filtered_tests
