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

import subprocess
import re

def execshellcmd(cmdexc, logfile, myenv):
    proc = subprocess.Popen(cmdexc, shell=True, env=myenv,
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            bufsize=0)
    proc.wait()
    stdoutstr = proc.stdout.read().decode('utf-8')
    if logfile != None:
        logfile.write(stdoutstr)
    return stdoutstr

def execshellcmd_largedump(cmdexc, logfile, runlog, myenv):
    runlog.seek(0)
    proc = subprocess.Popen(cmdexc, shell=True, env=myenv,
                            stdin=subprocess.PIPE, stdout=runlog, stderr=subprocess.STDOUT,
                            bufsize=0)
    proc.wait()
    runlog.seek(0)
    if logfile != None:
        for line in runlog:
            logfile.write(line)
    runlog.seek(0)

def get_gpuarch(logFile):
    # Get GPU Architecture
    cmdexc = "/opt/rocm/bin/mygpu"
    gpuarchsh = execshellcmd(cmdexc, logFile, None)
    if not re.match("gfx\d+", gpuarchsh):
        print("GPU Architecture unknown")
        return None
    gpuarch = gpuarchsh.strip()
    return gpuarch
