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

import re

class Hip_examples_parser:
    def __init__(self):
        pass

    def rodina3(self, text, pass_string, num):
        if num == text.count(pass_string):
            return "Passed"
        return "Failed"

    def openmp_helloworld(self, text):
        status = 'Failed'
        text = text.splitlines()
        for line in text:
            if 'PASSED!' in line:
                status = 'Passed'
        return status

    def vectorAdd(self, text):
        status = 'Failed'
        text = text.splitlines()
        for line in text:
            if 'PASSED!' in line:
                status = 'Passed'
        return status

    def reduction(self, text):
        status = 'Failed'
        count = 0
        
        text = text.splitlines()
        try:
  
            for line in text:
                if 'result is CORRECT' in line:
                    count = count + 1
            if count >= 8:
                status = 'Passed'
        except:
            pass
        return status

    def rtm8(self, text):
        status = 'Failed'
        count = 0
        text = text.splitlines()
        try:
            for line in text:
                if "memory" in line:
                    count = count + 1
                if "pts" in line:
                    count = count + 1
                if "Tflops" in line:
                    count = count + 1
                if "dt" in line:
                    count = count + 1
                if "pt_rate" in line:
                    count = count + 1
                if "flop_rate" in line:
                    count = count + 1
                if "speedup" in line:
                    count = count + 1
            if count >= 7:
                status = 'Passed'
        except:
            pass
        return status

    def add4(self, text):
        status = 'Failed'
        copy_count = 0
        mul_count = 0
        add_count = 0
        triad_count = 0
        geomean_count = 0
        copy_re = re.compile('Copy\s+\d+\.\d+\s+\d+\.\d+\s+\d+\.\d+\s+\d+\.\d+')
        mul_re = re.compile('Mul\s+\d+\.\d+\s+\d+\.\d+\s+\d+\.\d+\s+\d+\.\d+')
        add_re = re.compile('Add4\s+\d+\.\d+\s+\d+\.\d+\s+\d+\.\d+\s+\d+\.\d+')
        triad_re = re.compile('Triad\s+\d+\.\d+\s+\d+\.\d+\s+\d+\.\d+\s+\d+\.\d+')
        geomean_re = re.compile('GEOMEAN\s+\d+\.\d+')
        lines = text.splitlines()
        try:
            
            for line in lines:
                copy = re.search(copy_re, line)
                mul = re.search(mul_re, line)
                add = re.search(add_re, line)
                triad = re.search(triad_re, line)
                geomean = re.search(geomean_re, line)
                if copy:
                    copy_count = copy_count + 1
                if mul:
                    mul_count = mul_count + 1
                if add:
                    add_count = add_count + 1
                if triad:
                    triad_count = triad_count + 1
                if geomean:
                    geomean_count = geomean_count + 1
            if copy_count >= 4 and mul_count >= 4 and add_count >= 4 and triad_count >= 4 and geomean_count >= 4:
                status = 'Passed'
        except:
            pass
        return status

    def gpu_burn(self, text):
        status = 'Failed'
        copy_count = 0
        mul_count = 0
        add_count = 0
        triad_count = 0
        geomean_count = 0
        lines = text.splitlines()
        gpu_re = re.compile('Total no. of GPUs found:\s+(\d)')
        gpus = 0
        for line in lines:
            copy = re.search(gpu_re, line)
            if copy:
                gpus = int(copy.group(1))
            if 'Init Burn Thread for device' in line:
                copy_count = copy_count + 1
            if 'Burn Thread using device' in line:
                mul_count = mul_count + 1
            if 'Temps:' in line:
                add_count = add_count + 1
            if 'Stopping burn thread on device' in line:
                triad_count = triad_count + 1
        if copy_count >= gpus and mul_count >= gpus and add_count >= 5 and triad_count >= gpus and gpus >= 1:
            status = 'Passed'
        return status

    def cuda_stream(self, text):
        status = 'Failed'
        copy_count = 0
        mul_count = 0
        add_count = 0
        triad_count = 0
        lines = text.splitlines()
        copy_re = re.compile(r'Copy:\s+\d+\.\d+\s+\d+\.\d+\s+\d+\.\d+\s+\d+\.\d+')
        mul_re = re.compile(r'Scale:\s+\d+\.\d+\s+\d+\.\d+\s+\d+\.\d+\s+\d+\.\d+')
        add_re = re.compile(r'Add:\s+\d+\.\d+\s+\d+\.\d+\s+\d+\.\d+\s+\d+\.\d+')
        triad_re = re.compile(r'Triad:\s+\d+\.\d+\s+\d+\.\d+\s+\d+\.\d+\s+\d+\.\d+')
        try:
            for line in lines:
                copy = re.search(copy_re, line)
                mul = re.search(mul_re, line)
                add = re.search(add_re, line)
                triad = re.search(triad_re, line)

                if copy:
                    copy_count = copy_count + 1
                if mul:
                    mul_count = mul_count + 1
                if add:
                    add_count = add_count + 1
                if triad:
                    triad_count = triad_count + 1
            if copy_count >= 1 and mul_count >= 1 and add_count >= 1 and triad_count >= 1:
                status = 'Passed'
        except:

            print('exception')
            pass
        return status

    def mini_nbody(self, text):
        hip_minibody_count = 0
        status = 'Failed'
        count = 0
        lines = text.splitlines()
        try:
            for line in lines:
                search = re.search('\d+\,\s+\d+\.\d+', line)
                if search:
                    hip_minibody_count = hip_minibody_count + 1

            if hip_minibody_count >= 26:
                status = 'Passed'
        except:
            pass
        return status

    def strided_access(self, text):
        status = 'Failed'
        count = 0
        try:
            lines = text.splitlines()
            for line in lines:
                search = re.search('\d+\s+\d+\.\d+\s+\d+\.\d+', line)
                if search:
                    count = count + 1
            if count >= 30:
                status = 'Passed'
        except:
            pass
        return status

    def gpu_stream(self, text):
        testsuccess = True
        test_status = 'Failed'
        count = 0
        search = re.search('Copy\s+\d+\.\d+\s+\d+\.\d+\s+\d+\.\d+\s+\d+\.\d', text)
        if search:
            count = count + 1
        search = re.search('Mul\s+\d+\.\d+\s+\d+\.\d+\s+\d+\.\d+\s+\d+\.\d', text)
        if search:
            count = count + 1
        search = re.search('Add\s+\d+\.\d+\s+\d+\.\d+\s+\d+\.\d+\s+\d+\.\d', text)
        if search:
            count = count + 1
        search = re.search('Triad\s+\d+\.\d+\s+\d+\.\d+\s+\d+\.\d+\s+\d+\.\d', text)
        if search:
            count = count + 1
        search = re.search('Dot\s+\d+\.\d+\s+\d+\.\d+\s+\d+\.\d+\s+\d+\.\d', text)
        if search:
            count = count + 1

        search = re.search("Validation failed", text);
        if search:
            testsuccess &= False

        if (count >= 5) and (testsuccess != False):
            test_status = 'Passed'
        else:
            test_status = 'Failed'

        return test_status

    def mix_bench(self, text):
        test_status = 'Failed'
        count = len(re.findall(' +\d+, *\d+\.\d+| +\d+, +inf', text))
        if (count >= 33):
            test_status = 'Passed'
        return test_status

    def hip_examples_applications(self, logfile):
        pass_pattern1 = 'fault'
        pass_pattern2 = 'Aborted'
        pass_pattern3 = 'Error'
        pass_pattern4 = 'failed'
        logfile.seek(0)
        for line in logfile:
            if (pass_pattern1 in line) or (pass_pattern2 in line)\
            or (pass_pattern3 in line) or (pass_pattern4 in line):
                return "Failed"
        return "Passed"
