#!/usr/bin/env python3
# TigerGui

import os
import platform
import random
import shutil
import subprocess
import time
from multiprocessing import Process
from tkinter import (BOTH, BOTTOM, DISABLED, E, END, EW, LEFT, NE, NS, NW,
                     NORMAL, RIGHT, S, SE, SW, TOP, W, X, Y, Button,
                     Checkbutton, Entry, Frame, Label, LabelFrame, Listbox,
                     Menu, Menubutton, Message, Misc, OptionMenu, PanedWindow,
                     Radiobutton, Scale, Scrollbar, Spinbox, Text, Tk,
                     Toplevel, ttk)
from tkinter import messagebox
from tkinter.filedialog import askdirectory, askopenfilename

from common import bcolors, wykonaj


class TigerGUI:
    def __init__(self, master):
        self.master = master
        master.title("TigerGUI")
        master.geometry("800x600")

        self.data = Data()
        self.create_widgets()

    def create_widgets(self):
        self.create_left_frame()
        self.create_right_frame()

    def create_left_frame(self):
        left_frame = ttk.Labelframe(self.master, text="Data")
        left_frame.pack(side=LEFT, fill=BOTH, expand=True)

        # Short Task Name
        stn_frame = ttk.Frame(left_frame)
        stn_frame.pack(fill=X, padx=5, pady=5)
        stn_label = ttk.Label(stn_frame, text="Short Task Name:")
        stn_label.pack(side=LEFT, padx=5)
        self.stn_var = StringVar()
        stn_entry = ttk.Entry(stn_frame, textvariable=self.stn_var)
        stn_entry.pack(fill=X, expand=True)
        stn_entry.bind("<Return>", self.on_stn_change)
        stn_button = ttk.Button(stn_frame, text="Set", command=self.on_stn_change)
        stn_button.pack(side=RIGHT)

        # Test Folder
        test_folder_frame = ttk.Frame(left_frame)
        test_folder_frame.pack(fill=X, padx=5, pady=5)
        test_folder_label = ttk.Label(test_folder_frame, text="Test Folder:")
        test_folder_label.pack(side=LEFT, padx=5)
        self.test_folder_var = StringVar(value="./")
        test_folder_entry = ttk.Entry(test_folder_frame, textvariable=self.test_folder_var, state=DISABLED)
        test_folder_entry.pack(fill=X, expand=True)
        test_folder_button = ttk.Button(test_folder_frame, text="...", command=self.select_test_folder)
        test_folder_button.pack(side=RIGHT)

        # Binary
        binary_frame = ttk.Frame(left_frame)
        binary_frame.pack(fill=X, padx=5, pady=5)
        binary_label = ttk.Label(binary_frame, text="Binary:")
        binary_label.pack(side=LEFT, padx=5)
        self.binary_var = StringVar()
        binary_entry = ttk.Entry(binary_frame, textvariable=self.binary_var, state=DISABLED)
        binary_entry.pack(fill=X, expand=True)
        binary_button = ttk.Button(binary_frame, text="...", command=self.select_binary)
        binary_button.pack(side=RIGHT)

        # Max Time
        max_time_frame = ttk.Frame(left_frame)
        max_time_frame.pack(fill=X, padx=5, pady=5)
        max_time_label = ttk.Label(max_time_frame, text="Max Time (s):")
        max_time_label.pack(side=LEFT, padx=5)
        self.max_time_var = StringVar(value="5")
        max_time_entry = ttk.Entry(max_time_frame, textvariable=self.max_time_var)
        max_time_entry.pack(fill=X, expand=True)

    def create_right_frame(self):
        right_frame = ttk.Labelframe(self.master, text="Results")
        right_frame.pack(side=RIGHT, fill=BOTH, expand=True)

        # Run buttons
        run_frame = ttk.Frame(right_frame)
        run_frame.pack(fill=X, padx=5, pady=5)
        run_button = ttk.Button(run_frame, text="Run Tests", command=self.run_tests)
        run_button.pack(side=LEFT, fill=X, expand=True)
        stop_button = ttk.Button(run_frame, text="Stop", command=self.stop_tests)
        stop_button.pack(side=RIGHT, fill=X, expand=True)

        # Results
        self.results_text = Text(right_frame, wrap="word", state=DISABLED)
        self.results_text.pack(fill=BOTH, expand=True, padx=5, pady=5)

    def on_stn_change(self, event=None):
        stn = self.stn_var.get()
        if stn:
            self.data.defaultInit(stn)
            self.test_folder_var.set(self.data.testFolder)
            self.binary_var.set(self.data.binaryCodeName)

    def select_test_folder(self):
        folder = askdirectory()
        if folder:
            self.data.testFolder = folder
            self.test_folder_var.set(folder)

    def select_binary(self):
        binary = askopenfilename()
        if binary:
            self.data.binaryCodeName = binary
            self.binary_var.set(binary)

    def run_tests(self):
        if not self.data.checkBasicData():
            return

        self.results_text.config(state=NORMAL)
        self.results_text.delete("1.0", END)
        self.results_text.config(state=DISABLED)

        self.continue_running = True
        self.process_tests()

    def stop_tests(self):
        self.continue_running = False

    def process_tests(self):
        if not self.continue_running:
            return

        tests = [f for f in os.listdir(self.data.testFolder) if f.endswith(".in")]
        total_tests = len(tests)
        passed_tests = 0

        for i, test_file in enumerate(tests):
            if not self.continue_running:
                break

            test_path = os.path.join(self.data.testFolder, test_file)
            result = wykonaj(
                self.data.binaryCodeName,
                test_path,
                float(self.max_time_var.get()),
            )

            self.results_text.config(state=NORMAL)
            self.results_text.insert(END, f"Test {i + 1}/{total_tests}: {test_file} - {result}\n")
            self.results_text.config(state=DISABLED)
            self.master.update_idletasks()

            if result == "OK":
                passed_tests += 1

        self.results_text.config(state=NORMAL)
        self.results_text.insert(END, f"\nPassed {passed_tests}/{total_tests} tests.")
        self.results_text.config(state=DISABLED)


class Data:
    def __init__(self):
        self.stn = ""
        self.binaryCodeName = ""
        self.testFolder = "./"
        self.workingFolder = "./"

    def defaultInit(self, stn):
        self.stn = stn
        self.binaryCodeName = os.path.join(self.workingFolder, stn)
        self.testFolder = self.workingFolder

    def checkBasicData(self):
        if not self.binaryCodeName:
            messagebox.showerror("Error", "Binary not specified.")
            return False
        if not os.path.isfile(self.binaryCodeName):
            messagebox.showerror("Error", "Binary does not exist.")
            return False
        return True


def main():
    root = Tk()
    gui = TigerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
