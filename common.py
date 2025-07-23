import os
import filecmp
import subprocess
import signal

class bcolors:
    INFO = '\033[95m'
    INFO_LOW = '\033[94m'
    SUCCES = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


def handler(signum, frame):
    print(bcolors.INFO + "Za chwilę zabiję te procesy, pamiętaj o zabiciu jeszcze wykonywanego programu." + bcolors.ENDC)
    os.system("kill " + str(os.getpid()))
    os.system("kill " + str(os.getppid()))


def shell(string, maxextime):
    signal.signal(signal.SIGALRM, handler)
    p = subprocess.Popen(string, shell=True)
    signal.alarm(int(maxextime))
    p.wait()
    signal.alarm(0)


def wykonaj(program, test, maxtime, checker=None, checkerbruteforce=None):
    if os.path.isfile(".temporary"):
        os.remove(".temporary")
    if os.path.isfile(".temporary2"):
        os.remove(".temporary2")

    out = test[:-2] + "out"

    if not os.path.isfile(out):
        print((bcolors.WARNING + "{0:20} " + ": RE - Can't find the out file" + bcolors.ENDC).format(test))
        return "RE"

    try:
        with open(test, "r") as stdin_file, open(".temporary", "w") as stdout_file:
            subprocess.run(["./" + program], stdin=stdin_file, stdout=stdout_file, timeout=float(maxtime), check=True)
    except FileNotFoundError:
        print(bcolors.FAIL + "Your program ended, but a file was not found for : " + test + bcolors.ENDC)
        return "RE"
    except subprocess.TimeoutExpired:
        print(bcolors.FAIL + "Your program took too long to execute for : " + test + bcolors.ENDC)
        return "TLE"
    except subprocess.CalledProcessError as e:
        print(bcolors.FAIL + f"Your program returned a non-zero exit code {e.returncode} for : " + test + bcolors.ENDC)
        return "RE"


    if checker:
        shell("cat " + test + "  > .temporary2; echo >> .temporary2; cat .temporary >> .temporary2", maxtime)
        shell("./" + checker + " < .temporary2 > .temporary3", maxtime)
        with open('.temporary3', 'r') as f:
            first_line = f.readline().strip()
            return first_line
    elif checkerbruteforce:
        shell("cat " + test + "  > .temporary2; echo >> .temporary2;", maxtime)
        shell("cat " + out + "  > .temporary2; echo >> .temporary2;", maxtime)
        shell("cat .temporary >> .temporary2", maxtime)
        shell("./" + checker + " < .temporary2 > .temporary3", maxtime)
        with open('.temporary3', 'r') as f:
            first_line = f.readline().strip()
            return first_line
    elif filecmp.cmp(out, ".temporary"):
        print((bcolors.SUCCES + "{0:20} " + ": OK" + bcolors.ENDC).format(test))
        return "OK"
    else:
        print((bcolors.FAIL + "{0:20} " + ": WA" + bcolors.ENDC).format(test))
        return "WA"
