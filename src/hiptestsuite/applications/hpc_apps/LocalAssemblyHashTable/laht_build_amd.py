# Copyright (c) 2023 Advanced Micro Devices, Inc. All rights reserved.
# Copyright (c) 2023 Intel Finland Oy. All rights reserved.
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

from hiptestsuite.common.hip_shell import *
from hiptestsuite.applications.hpc_apps.LocalAssemblyHashTable.laht_parser_common import (
    LAHTParser
)

import os
import tempfile
from multiprocessing import cpu_count

class BuildRunAmd():
    def __init__(self, repo_dir, logFile):
        self.repo_dir = repo_dir
        self.logFile = logFile
        self.runlog = None
        self.rocm_path = os.environ.get('ROCM_PATH')
        if not self.rocm_path:
            self.rocm_path = "/opt/rocm"


    def buildtest(self):
        if not os.path.exists(self.rocm_path):
            print("Error: ROCm path does not exist. Exiting Test!")
            print("NOTE: tried path '{}'".format(self.rocm_path))
            return False
        return True # Nothing to build here.

    def runtest(self, testnum):
        print("Running Local Assembly Hash Table Test..")
        env = os.environ.copy()
        env['PATH'] = self.rocm_path + '/bin:' + env['PATH']
        cmd = """
set -e
cd {repo_dir}/src
mkdir -p build
bash test_script.sh
""".format(repo_dir=self.repo_dir)
        self.runlog = tempfile.TemporaryFile("w+")
        execshellcmd_largedump(cmd, self.logFile, self.runlog, env)

    def clean(self):
        print("Cleaning Local Assembly Hash Table..")
        if self.runlog != None:
            self.runlog.close()

    def parse_result(self, testnum):
        return LAHTParser(self.runlog).parse(testnum)
