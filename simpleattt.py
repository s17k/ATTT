#!/usr/bin/env python3

import subprocess
import os.path
import sys
import fnmatch
import argparse
import textwrap
from multiprocessing import Process
from common import bcolors, wykonaj


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            r"""Tiger is a command-line tool for input-output tasks.
On default it reads the tests from the disk

                       ___......----:'":--....(\
               .-':'"":   :  :  :   :  :  :.(1\.`-.
             .'`.  `.  :  :  :   :   : : : : : :  .';
            :-`. :   .  : :  `.  :   : :.   : :`.`. a;
            : ;-. `-.-._.  :  :   :  ::. .' `. `., =  ;
            :-:.` .-. _-.,  :  :  : ::,.'.-' ;-. ,'''"
          .'.' ;`. .-' `-.:  :  : : :;.-'.-.'   `-'
   :.   .'.'.-' .'`-.' -._;..:---'''''._.-/
   :`--'.'  : :'     ;`-.;            :.`.-'`.
    `'''    : :      ;`.;             :=; `.-'`.
            : '.    :  ;              :-:   `._-`.
             `'\"'    `. `.            `--'     '._'
                       `'\"'
"""
        )
    )

    parser.add_argument(
        "ShortTaskName",
        help="Short Task Name (for example : swo for task Swords) "
             "Default setting require : (for Swords) "
             "Tests in form swoX.in and swoX.out, binary code in swo or source in swo.cpp"
    )

    parser.add_argument(
        "-gui",
        "--graphicaluserinterface",
        action="store_true",
        help="Open graphical user interface. If this option is used all other options are ignored."
    )

    binary_source_group = parser.add_mutually_exclusive_group()
    binary_source_group.add_argument(
        "-b",
        "--binarycode",
        help="Exceptional binary code to run against the common one",
        default=""
    )

    binary_source_group.add_argument(
        "-s",
        "--sourcecode",
        help="Exceptional source code to compile and run against the common one",
        default=""
    )

    generate_group = parser.add_mutually_exclusive_group()
    generate_group.add_argument(
        "-g",
        "--generate",
        action="store_true",
        help="Generate and run tests but save only those on which the program failed."
    )

    generate_group.add_argument(
        "-gs",
        "--generateandsave",
        action="store_true",
        help="Generate, run tests and save all tests."
    )

    generate_group.add_argument(
        "-tf",
        "--testfolder",
        help="Change the folder with tests which will be executed",
        default=""
    )
    parser.add_argument(
        "-op",
        "--otherprefix",
        help="Change the default prefix for tests",
        default=""
    )

    checker_group = parser.add_mutually_exclusive_group()
    checker_group.add_argument(
        "-c",
        "--checker",
        help="For tasks, which have several acceptable answers (checker gets the input and the output - joined in one file) "
             "This chcecker needs to get the input from stdin and return OK or WA to stdout",
        default=""
    )

    checker_group.add_argument(
        "-cb",
        "--checkerbruteforce",
        help="For tasks, which have several acceptable answers (checker gets the input, bruteforceprogram output, the output - joined in one file)\n"
             "This chcecker needs to get the input from stdin and return OK or WA to stdout",
        default=""
    )

    parser.add_argument(
        "-mt",
        "--maxtime",
        help="Change the time after the program will be killed",
        default="5"
    )

    args = parser.parse_args()

    if args.graphicaluserinterface:
        from guiattt import buildGui
        buildGui()
        sys.exit()

    stn = args.ShortTaskName
    binary_code_name = get_binary_code_name(args, stn)

    result = ""
    if args.generate or args.generateandsave:
        result = run_generator(args, binary_code_name, stn)
    else:
        result = run_tests_from_disk(args, binary_code_name, stn)

    cleanup(result)


def get_binary_code_name(args, stn):
    if args.binarycode:
        return args.binarycode

    if os.path.isfile(stn):
        print(bcolors.INFO + "Successfully read the binary file: " + bcolors.INFO_LOW + stn + bcolors.ENDC)
        return stn

    print(bcolors.WARNING + "Couldn't find the binary file: " + bcolors.INFO_LOW + stn + bcolors.ENDC)
    source_code_name = args.sourcecode or f"{stn}.cpp"

    if not os.path.exists(source_code_name):
        print(bcolors.FAIL + f"Couldn't find the source file: {bcolors.INFO_LOW}{source_code_name}{bcolors.FAIL}, nor was another specified." + bcolors.ENDC)
        sys.exit()

    print(bcolors.INFO + "So let's try to compile your program (C++): " + bcolors.INFO_LOW + source_code_name + bcolors.ENDC)
    compile_program(source_code_name, stn)
    return stn


def compile_program(source_code_name, stn):
    compilation_command = ["g++", "-o", stn, source_code_name, "-O2", "-Wall", "-static", "-std=c++11", "-g"]
    try:
        subprocess.run(compilation_command, check=True)
        print(bcolors.SUCCES + "Compiled successfully." + bcolors.ENDC)
    except subprocess.CalledProcessError:
        print(bcolors.FAIL + "There were some errors during the compilation process." + bcolors.ENDC)
        sys.exit()


def run_generator(args, binary_code_name, stn):
    print(bcolors.WARNING + "This option is not fully implemented yet." + bcolors.ENDC)
    generator = stn + "gen"
    zrodlo = stn + "zrodlo"
    brut = stn + "brut"
    nr = 1
    wa = 0
    ac = 0
    while True:
        subprocess.run(f"cp {zrodlo} zrodlo2", shell=True, timeout=10)
        subprocess.run(f"echo {nr} >> zrodlo2", shell=True, timeout=10)
        test = f"{stn}{nr}.in"
        testout = f"{stn}{nr}.out"
        subprocess.run(f"./{generator} < zrodlo2 > {test}", shell=True, timeout=10)
        subprocess.run(f"./{brut} < {test} > {testout}", shell=True, timeout=10)
        wynik = wykonaj(binary_code_name, test, args.maxtime)
        if wynik == "OK":
            ac += 1
        if wynik == "WA":
            wa += 1
        print(f"ac: {ac}, wa: {wa}, nr: {nr}")
        nr += 1


def run_tests_from_disk(args, binary_code_name, stn):
    print(bcolors.INFO + "Reading tests from the disk." + bcolors.ENDC)
    ile_testow = 0
    testy_z_wa = []
    testy_z_re = []
    katalog = args.testfolder or "."

    if not os.path.isdir(katalog):
        print(bcolors.FAIL + "Folder " + katalog + " doesn't exist" + bcolors.ENDC)
        sys.exit()

    prefix = args.otherprefix or stn

    for test in os.listdir(katalog):
        if fnmatch.fnmatch(test, prefix + '*.in'):
            wynik = wykonaj(binary_code_name, os.path.join(katalog, test), args.maxtime, args.checker, args.checkerbruteforce)
            if wynik == "WA":
                testy_z_wa.append(test)
            elif wynik == "RE":
                testy_z_re.append(test)
            ile_testow += 1

    ile_z_ok = ile_testow - len(testy_z_wa) - len(testy_z_re)
    print()
    if ile_testow > 0:
        print(bcolors.INFO + f"Passed {ile_z_ok}/{ile_testow} ~ {ile_z_ok * 100 // ile_testow}%" + bcolors.ENDC)
    if testy_z_wa:
        print(bcolors.FAIL + "WA on tests:")
        print(testy_z_wa)
        return "WA"
    if testy_z_re:
        print(bcolors.WARNING + "RE on tests:")
        print(testy_z_re, bcolors.ENDC)
        return "RE"
    return "OK"


def cleanup(result):
    print(bcolors.INFO + "Ending..." + bcolors.ENDC)
    if result == "OK":
        for f in [".temporary", ".temporary2", ".temporary3"]:
            if os.path.isfile(f):
                os.remove(f)


if __name__ == "__main__":
    main()
