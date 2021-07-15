import subprocess

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
