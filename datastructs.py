# -*- coding: utf-8 -*-
#  pylint: disable=C0103

"""
@author = Ivan Pokrovac
pylint global evaluation = 10/10
"""
import tkinter as tk
from tkinter import filedialog

from .musefcsparser import parse, text_explanation
from .gating import GUIgating_outline as guigo
from .supplemental import ManualEntry


class DSS():
    """
    This is one data set structure. It consists of a tkinter Frame structure
    (attribute self.frame), of museobject structure (attribute self.object),
    and the name of the file (attribute self.name).
    """

    def place(self, n):
        """
        Places the structure on tkinter frame. N is the number of currently loaded
        data_set structures and it suitably places new structure  in Nth row.

        Parameters
        ----------
        n : Number of currently loaded data_set structures

        Returns
        -------
        None.

        """
        self.frame.grid(row=n, column=0)

    def export_data(self):
        """
        Exports the dataframe to a given directory

        Two formats are available : .XLSX and .CSV

        Returns
        -------
        None.

        """

        data = self.data
        directory = filedialog.asksaveasfilename(title="Save all data from dataset", filetypes=[(
            "Excel files", "*.xlsx"), ("Comma Separated Values", "*.csv")], defaultextension=".csv")
        ext = directory[-4:]
        if ext == "xlsx":
            data.to_excel(directory)
        if ext == ".csv":
            data.to_csv(directory)

    def automatic_legendry(self):
        """
        See "text_explanation"
        """
        data = text_explanation(self.path)
        self.data = data

    def __init__(self, main, path):
        """
        This is one data set structure. It consists of a tkinter Frame structure
        (attribute self.frame), of museobject structure (attribute self.object),
        and the name of the file (attribute self.name).

        Parameters
        ----------
        main : tkinter root frame (tk.Tk())
        path : .FCS file

        Returns
        -------
        Creates the above structure. It does not place it on the tkinter main.

        """

        frame = tk.Frame(master=main)  # initializes frame
        self.frame = frame
        self.path = path

        museobject = parse(path, "obj")  # creates muse object
        self.data = museobject.data

        # makes tkinter label to show name of loaded object
        self.name = path.split("/")[-1]
        label = tk.Label(master=frame, text=self.name)
        self.label = label
        label.grid(row=0, column=0)

        # creates a button that prompts automatic legendization
        auto_legendry = tk.Button(
            master=frame, text="Automatic Legend", command=self.automatic_legendry)
        auto_legendry.grid(row=0, column=1)

        # creates a button that prompts manual legendization through creation of manual_entry object
        manual_legendry = tk.Button(
            master=frame, text="Manual Legend", command=lambda: ManualEntry(museobject))
        manual_legendry.grid(row=0, column=2)

        # creates a button that promts exportation of data
        export_but = tk.Button(master=frame, text="Export",
                               command=self.export_data)
        export_but.grid(row=0, column=3)

###
###


class MDSS():
    """
    Creates a merged_data_set structure that consists of all data frame loaded
    Dataframes must either all be legendized, or no dataframe must be legendized
    It inherits from data_set_structure, and makes use of export_data function
    """

    def info_prompt(self):
        """
        Makes info prompt box where all data that were loaded and merged show

        Returns
        -------

        """

        prompt = tk.Toplevel()
        n = 1
        tk.Label(master=prompt, text="LOADED DATA").grid(row=0, column=0)
        for item in self.info:
            tk.Label(master=prompt, text=item).grid(row=n, column=0)
            n = n+1

    def __init__(self, mainclass, names, merged_data):
        """
        Creates a merged_data_set structure that consists of all data frame loaded
        Dataframes must either all be legendized, or no dataframe must be legendized
        It inherits from data_set_structure, and makes use of export_data function


        Parameters
        ----------
        main : main_app class of which tkinter root (tk.Tk()) is the .main attribute

        names : list of names of all datasets.

        merged_data : pandas dataframe with all the loaded data.

        Returns
        -------
        None.

        """

        main = mainclass.main  # main is tk.Tk root
        frame = tk.Frame(master=main)  # initializes frame
        self.frame = frame
        self.info = names
        self.data = merged_data
        frame.grid(row=1, column=0)
        # creates a button that promts exportation of data
        export_but = tk.Button(master=frame, text="Export",
                               command=self.export_data)
        export_but.grid(row=0, column=2)

        info_butt = tk.Button(master=frame, text="MERGED DATA",
                              command=self.info_prompt)
        info_butt.grid(row=0, column=0)

        gating_but = tk.Button(master=frame, text="GATING",
                               command=lambda: guigo(self.data))
        gating_but.grid(row=0, column=5)

        # stores this frame in mainclass.frames list for better removal
        mainclass.frames.append(self)

    def export_data(self):
        """
        Exports the dataframe to a given directory

        Two formats are available : .XLSX and .CSV

        Returns
        -------
        None.

        """

        data = self.data
        directory = filedialog.asksaveasfilename(title="Save all data from dataset", filetypes=[(
            "Excel files", "*.xlsx"), ("Comma Separated Values", "*.csv")], defaultextension=".csv")
        ext = directory[-4:]
        if ext == "xlsx":
            data.to_excel(directory)
        if ext == ".csv":
            data.to_csv(directory)
###
###
