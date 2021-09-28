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

from testsuite.AMD import AMDObject


class Target:
    def __init__(self):
        pass


class AMDTarget(AMDObject, Target):
    def __init__(self):
        AMDObject.__init__(self)
        Target.__init__(self)


class IntelTarget(AMDObject, Target):
    def __init__(self):
        AMDObject.__init__(self)
        Target.__init__(self)


class NvidiaTarget(AMDObject, Target):
    def __init__(self):
        AMDObject.__init__(self)
        Target.__init__(self)


class gfx700(AMDTarget):
    def __init__(self):
        AMDTarget.__init__(self)


class gfx701(AMDTarget):
    def __init__(self):
        AMDTarget.__init__(self)


class gfx702(AMDTarget):
    def __init__(self):
        AMDTarget.__init__(self)


class gfx703(AMDTarget):
    def __init__(self):
        AMDTarget.__init__(self)


class gfx704(AMDTarget):
    def __init__(self):
        AMDTarget.__init__(self)


class gfx705(AMDTarget):
    def __init__(self):
        AMDTarget.__init__(self)


class gfx801(AMDTarget):
    def __init__(self):
        AMDTarget.__init__(self)


class gfx802(AMDTarget):
    def __init__(self):
        AMDTarget.__init__(self)


class gfx803(AMDTarget):
    def __init__(self):
        AMDTarget.__init__(self)


class gfx805(AMDTarget):
    def __init__(self):
        AMDTarget.__init__(self)


class gfx810(AMDTarget):
    def __init__(self):
        AMDTarget.__init__(self)


class gfx900(AMDTarget):
    def __init__(self):
        AMDTarget.__init__(self)


class gfx902(AMDTarget):
    def __init__(self):
        AMDTarget.__init__(self)


class gfx904(AMDTarget):
    def __init__(self):
        AMDTarget.__init__(self)


class gfx906(AMDTarget):
    def __init__(self):
        AMDTarget.__init__(self)


class gfx908(AMDTarget):
    def __init__(self):
        AMDTarget.__init__(self)


class gfx909(AMDTarget):
    def __init__(self):
        AMDTarget.__init__(self)


class gfx90a(AMDTarget):
    def __init__(self):
        AMDTarget.__init__(self)


class gfx1010(AMDTarget):
    def __init__(self):
        AMDTarget.__init__(self)


class gfx1011(AMDTarget):
    def __init__(self):
        AMDTarget.__init__(self)


class gfx1012(AMDTarget):
    def __init__(self):
        AMDTarget.__init__(self)


class gfx1030(AMDTarget):
    def __init__(self):
        AMDTarget.__init__(self)


class gfx1031(AMDTarget):
    def __init__(self):
        AMDTarget.__init__(self)


class gfx1032(AMDTarget):
    def __init__(self):
        AMDTarget.__init__(self)
