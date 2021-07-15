from amd.common.hip_shell import execshellcmd
import os

# Common class to clone/pull dependent Packages
class HipPackages():
    def __init__(self):
        self.cwdAbs = os.getcwd()
        self.conformancePath = os.path.join(self.cwdAbs, "src/amd/conformance/")
        self.hippath = os.path.join(self.conformancePath, "HIP/")
        self.appPath = os.path.join(self.cwdAbs,"src/amd/applications/hip_examples/")
        self.examplepath = os.path.join(self.appPath, "HIP-Examples/")
        self.mixbenchpath = os.path.join(self.appPath, "mixbench/")
        self.gpustrmpath = os.path.join(self.appPath, "GPU-STREAM/")
        self.rocclrpath = os.path.join(self.conformancePath, "ROCclr/")
        self.openclpath = os.path.join(self.conformancePath, "ROCm-OpenCL-Runtime/")

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
        elif reponame == "rocclr":
            repo_root_path = self.rocclrpath
            repo_location = self.conformancePath
            repo_dir = "ROCclr"
        elif reponame == "opencl":
            repo_root_path = self.openclpath
            repo_location = self.conformancePath
            repo_dir = "ROCm-OpenCL-Runtime"

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
        if branch == "": #No branch name provided. Clone from main branch.
            cmdPull = "git clone " + repo
        else:
            cmdPull = "git clone -b " + branch + " " + repo
        print("Cloning the latest repo from branch = " + branch + "...")
        cmdexc = cmdcd + cmdPull
        # Clone the latest version from repo
        execshellcmd(cmdexc, logFile, None)
        isHipPresent = os.path.isdir(repo_root_path)
        if not isHipPresent:
            return False
        else:
            print(reponame + " cloned successfully")
        # At this point check ensure git head is pointing to commitId
        if commitId != "":
            cmdcd = "cd " + repo_root_path + ";"
            cmdexc = cmdcd + "git reset --hard " + commitId + ";"
            execshellcmd(cmdexc, logFile, None)
        print("Updating: " + reponame + " completed")
        return True
