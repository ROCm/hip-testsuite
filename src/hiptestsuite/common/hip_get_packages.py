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

from hiptestsuite.common.hip_shell import execshellcmd

import os

# Common class to clone/pull dependent Packages
class HipPackages():
    def __init__(self):
        self.cwdAbs = os.getcwd()
        self.conformancePath = os.path.join(self.cwdAbs, "src/hiptestsuite/conformance/")
        # HIP & HIPAMD
        self.hippath = os.path.join(self.conformancePath, "HIP/")
        self.hipamdpath = os.path.join(self.conformancePath, "HIPAMD/")
        # HIP-Examples
        self.appPath = os.path.join(self.cwdAbs,"src/hiptestsuite/applications/hip_examples/")
        self.examplepath = os.path.join(self.appPath, "HIP-Examples/")
        self.mixbenchpath = os.path.join(self.appPath, "mixbench/")
        self.gpustrmpath = os.path.join(self.appPath, "GPU-STREAM/")
        # Vdi and OpenCL
        self.rocclrpath = os.path.join(self.conformancePath, "ROCclr/")
        self.openclpath = os.path.join(self.conformancePath, "ROCm-OpenCL-Runtime/")
        # mgbench
        self.mgbenchrootpath = os.path.join(self.cwdAbs, "src/hiptestsuite/applications/mgbench/")
        self.mgbenchapppath = os.path.join(self.mgbenchrootpath, "mgbench/")
        # CUDA-grep
        self.cudagreprootpath = os.path.join(self.cwdAbs, "src/hiptestsuite/applications/cuda_grep/")
        self.cudagrepapppath = os.path.join(self.cudagreprootpath, "CUDA-grep/")
        # cuda_memtest
        self.cudamemrootpath = os.path.join(self.cwdAbs, "src/hiptestsuite/applications/cuda_memtest/")
        self.cudamemapppath = os.path.join(self.cudamemrootpath, "cuda_memtest/")
        # Quicksilver
        self.qsrootpath = os.path.join(self.cwdAbs, "src/hiptestsuite/applications/hpc_apps/quicksilver/")
        self.qsapppath = os.path.join(self.qsrootpath, "Quicksilver/")
        # Gridtools
        self.gridtoolsrootpath = os.path.join(self.cwdAbs, "src/hiptestsuite/applications/hpc_apps/gridtools/GridTools/")
        self.gridtoolsapppath = os.path.join(self.gridtoolsrootpath, "gridtools/")
        self.gtbenchrootpath = os.path.join(self.cwdAbs, "src/hiptestsuite/applications/hpc_apps/gridtools/GridTools/")
        self.gtbenchapppath = os.path.join(self.gtbenchrootpath, "gtbench/")
        # Kokkos
        self.kokkosrootpath = os.path.join(self.cwdAbs, "src/hiptestsuite/applications/hpc_apps/kokkos/")
        self.kokkosapppath = os.path.join(self.kokkosrootpath, "kokkos/")
        # Laghos
        self.mfemrootpath = os.path.join(self.cwdAbs, "src/hiptestsuite/applications/hpc_apps/laghos/")
        self.mfemapppath = os.path.join(self.mfemrootpath, "mfem/")
        self.laghosrootpath = os.path.join(self.cwdAbs, "src/hiptestsuite/applications/hpc_apps/laghos/")
        self.laghosapppath = os.path.join(self.laghosrootpath, "Laghos/")
        # CP2K
        self.cp2krootpath = os.path.join(self.cwdAbs, "src/hiptestsuite/applications/hpc_apps/cp2k/")
        self.cp2kapppath = os.path.join(self.cp2krootpath, "cp2k/")

    def pull_repo(self, logFile, repo, branch, commitId, reponame):
        repo_root_path = ""
        repo_location = ""
        repo_dir = ""
        if  reponame == "gpu-stream":
            repo_root_path = self.gpustrmpath
            repo_location = self.appPath
            repo_dir = "GPU-STREAM"
        elif reponame == "mixbench":
            repo_root_path = self.mixbenchpath
            repo_location = self.appPath
            repo_dir = "mixbench"
        elif reponame == "hip_examples":
            repo_root_path = self.examplepath
            repo_location = self.appPath
            repo_dir = "HIP-Examples"
        elif reponame == "HIP":
            repo_root_path = self.hippath
            repo_location = self.conformancePath
            repo_dir = "HIP"
        elif reponame == "hipamd":
            repo_root_path = self.hipamdpath
            repo_location = self.conformancePath
            repo_dir = "HIPAMD"
        elif reponame == "rocclr":
            repo_root_path = self.rocclrpath
            repo_location = self.conformancePath
            repo_dir = "ROCclr"
        elif reponame == "opencl":
            repo_root_path = self.openclpath
            repo_location = self.conformancePath
            repo_dir = "ROCm-OpenCL-Runtime"
        elif reponame == "mgbench":
            repo_root_path = self.mgbenchapppath
            repo_location = self.mgbenchrootpath
            repo_dir = "mgbench"
        elif reponame == "cudagrep":
            repo_root_path = self.cudagrepapppath
            repo_location = self.cudagreprootpath
            repo_dir = "CUDA-grep"
        elif reponame == "cudamemtest":
            repo_root_path = self.cudamemapppath
            repo_location = self.cudamemrootpath
            repo_dir = "cuda_memtest"
        elif reponame == "quicksilver":
            repo_root_path = self.qsapppath
            repo_location = self.qsrootpath
            repo_dir = "Quicksilver"
        elif reponame == "gridtools":
            repo_root_path = self.gridtoolsapppath
            repo_location = self.gridtoolsrootpath
            repo_dir = "gridtools"
        elif reponame == "gtbench":
            repo_root_path = self.gtbenchapppath
            repo_location = self.gtbenchrootpath
            repo_dir = "gtbench"
        elif reponame == "kokkos":
            repo_root_path = self.kokkosapppath
            repo_location = self.kokkosrootpath
            repo_dir = "kokkos"
        elif reponame == "mfem":
            repo_root_path = self.mfemapppath
            repo_location = self.mfemrootpath
            repo_dir = "mfem"
        elif reponame == "Laghos":
            repo_root_path = self.laghosapppath
            repo_location = self.laghosrootpath
            repo_dir = "Laghos"
        elif reponame == "cp2k":
            repo_root_path = self.cp2kapppath
            repo_location = self.cp2krootpath
            repo_dir = reponame

        if  os.path.isdir(repo_root_path) and os.path.isdir(repo_root_path + "/.git"):
            print(reponame + " already exist")
            # Check if branch and commitId of local repo matches with input branch and commitId
            # if not then update local repo
            cmd = "cd " + os.path.join(repo_location, repo_dir) + ";"
            cmd += "git branch"
            currentbranch = execshellcmd(cmd, logFile, None)
            currentbranch = currentbranch.replace("* ", "")
            cmd = "cd " + os.path.join(repo_location, repo_dir) + ";"
            cmd += "git rev-parse HEAD"
            currentcommitid = execshellcmd(cmd, logFile, None)
            # Check if the local repo is upto date with input configuration
            if ((branch == "") or (branch in currentbranch)) and\
            ((commitId == "") or (commitId in currentcommitid)):
                print("This repo is up to date with config")
                return True
        else:
            print(reponame + " does not exist")

        # Update the repo
        print("Updating: " + reponame)
        cmdcd = "cd " + repo_location + ";"
        cmdcd += "rm -Rf " + repo_dir + "/;"
        cmdPull = ""
        print("Cloning " + reponame + " to " + repo_location)
        if branch == "": #No branch name provided. Clone from main branch.
            cmdPull = "git clone " + repo
        else:
            print("From branch: " + branch)
            cmdPull = "git clone -b " + branch + " " + repo
        cmdexc = cmdcd + cmdPull
        # Clone the latest version from repo
        execshellcmd(cmdexc, logFile, None)
        isRepoPresent = os.path.isdir(repo_root_path)
        if not isRepoPresent:
            return False
        else:
            print(reponame + " cloned successfully")
        # At this point check ensure git head is pointing to commitId
        if commitId != "":
            print("Resetting to commit: " + commitId)
            cmdcd = "cd " + repo_root_path + ";"
            cmdexc = cmdcd + "git reset --hard " + commitId + ";"
            execshellcmd(cmdexc, logFile, None)
        print("Updating: " + reponame + " completed")
        return True
