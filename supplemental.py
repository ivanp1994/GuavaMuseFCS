# -*- coding: utf-8 -*-
# pylint: disable=R0903
# pylint: disable=R0902
# pylint: disable=R1710
# pylint: disable=C0103
# pylint: disable=C0325
# pylint: disable=C0301
"""
@author = Ivan Pokrovac
pylint global evaluation = 9.94/10
"""
from tkinter import filedialog
import tkinter as tk
import numpy as np
from pandastable import Table
import pandas as pd


def select_file():
    """
    Creates a tkinter prompt for a .FCS file

    Returns file path
    """

    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=(
        ("fcs files", "*.fcs"), ("FCS files", "*.FCS"), ("All files", "*.*")))
    return(file_path)


def get_categorical(dataframe):
    """
    From a given dataframe, gets all categorical entries
    """
    categorical = dataframe.select_dtypes(exclude=[np.number])
    categorical.drop_duplicates(inplace=True)
    categorical.reset_index(inplace=True, drop=True)
    return(categorical)


def get_numerical(dataframe):
    """
    From a given dataframe, gets all numerical entries
    """
    numerical = dataframe.select_dtypes(include=[np.number])
    numerical.reset_index(inplace=True, drop=True)
    return(numerical)


class ModifiedOptionMenu():
    """
    self.variable ->variable of menu

    self.label    ->tk.Label

    self.optionmenu ->tk.Option menu


    """

    def place(self, r, c):
        """Places the menu on Row and Column"""
        self.label.grid(row=r, column=c, sticky="nsew")
        self.optionmenu.grid(row=r, column=c+1, sticky="nsew")

    def __init__(self, master, label, options, typevar):
        """
        Parameters
        ----------
        master : master for the button, a frame.
        label : string.
        options : list for choices.
        typevar : None, "bool", "int" if None then defaults to string

        Returns
        -------
        """
        label_ent = tk.Label(master=master, text=label,
                             anchor="w", relief="raised", bg="gainsboro")
        self.label = label_ent
        self.variable = tk.StringVar()
        if typevar == "bool":
            self.variable = tk.BooleanVar()
        if typevar == "int":
            self.variable = tk.IntVar()
        if typevar == "float":
            self.variable = tk.DoubleVar()

        self.variable.set(options[0])
        self.optionmenu = tk.OptionMenu(master, self.variable, *options)


class ModifiedSlider():
    """
    Just what it says
    """

    def place(self, r, c):
        """
        Places slider on specified row and column
        """
        self.label.grid(row=r, column=c, sticky="nsew")
        self.scale.grid(row=r, column=c+1, sticky="nsew")

    def __init__(self, master, label):
        """
        Document
        """
        variable = tk.DoubleVar()
        self.variable = variable
        self.master = master
        label_ent = tk.Label(master=master, text=label,
                             anchor="w", relief="raised", bg="gainsboro")
        self.label = label_ent
        scale = tk.Scale(master=master, from_=0.1, to=20,
                         variable=self.variable, orient="horizontal")
        self.variable.set(1)
        self.scale = scale


class DataDrawSelector():
    """
    self.master    ->tkinter master for frame storage
    self.label     ->tk.Label for what is shown
    self.all_data  -> all categorical data (pd.DF)
    self.all_table -> all categorical data (pandastable Table)
    self.all_frame -> frame in which all_table is shown

    self.selected  ->all categorical data that are selected during the run
    self.selected_table ->selected data (pandastable Table)
    self.selected_frame ->frame in which selected_table is shown

    self.button_frame  ->frame for buttons
    """

    def select_add(self):
        """
        Select from ALL DATA what to add

        """

        selected = self.all_table.getSelectedRows()  # gets selected data
        self.selected = pd.concat([self.selected, selected]).drop_duplicates(
        ).reset_index(drop=True)  # merges it into attribute
        selected_frame = tk.Frame(master=self.master)
        self.selected_frame = selected_frame
        # DO NOT PUT SELECTED FRAME ON GRID
        selected_table = Table(parent=selected_frame,
                               dataframe=self.selected, enable_menus=False)
        self.selected_table = selected_table

    def select_remove(self):
        """
        Select from SELECTED DATA what to remove

        """

        if self.shown == "ALL":
            return()
        to_remove = self.selected_table.getSelectedRows()  # what is to be removed

        self.selected = pd.concat([self.selected, to_remove]).drop_duplicates(
            keep=False)  # this drops duplicates, removing cells joint to both dataframes
        # .model.df is the dataframe in which table is stored, so just change it when needed
        self.selected_table.model.df = self.selected
        self.selected_table.redraw()  # redrawing the table

    def switch_view(self):
        """
        Switches the frame between ALL DATA and SELECTED DATA

        """

        if self.shown == "ALL":
            self.all_frame.grid_forget()
            self.selected_frame.grid(column=0, row=1)
            self.selected_table.show()
            self.shown = "SELECTED"
            self.label["text"] = self.shown
        else:
            # .remove table destroys!!! not hides the original frame
            self.selected_frame.grid_forget()
            self.all_frame.grid(column=0, row=1)
            self.all_table.show()
            self.shown = "ALL"
            self.label["text"] = self.shown

    def __init__(self, master, categorical):
        self.master = master  # tk master level, tk.Tk() or tk.Toplevel()
        self.selected = None  # data that are selected to be drawn
        self.selected_frame = None  # currently selected frame
        self.selected_table = None
        self.all_data = categorical  # all categorical data

        # frame in which all categorical data are placed
        all_frame = tk.Frame(master=master)
        self.all_frame = all_frame
        all_frame.grid(column=0, row=1)
        # pandastable structure showing what is to be selected
        all_table = Table(parent=all_frame,
                          dataframe=self.all_data, enable_menus=False)
        self.all_table = all_table
        all_table.show()
        self.shown = "ALL"

        # frame in which buttons are shown
        frame_button = tk.Frame(master=master)
        frame_button.grid(column=0, row=0, sticky="w")
        self.button_frame = frame_button
        # label to show what data is currently shown
        label = tk.Label(master=frame_button, text=self.shown)
        label.grid(row=0, column=0, sticky="nsew")
        self.label = label

        tk.Button(master=frame_button, text="Add to Selected", command=self.select_add).grid(
            row=0, column=1, sticky="nsw")  # button to select data

        tk.Button(master=frame_button, text="Switch View", bg="gainsboro", command=self.switch_view).grid(
            row=0, column=2, sticky="nsw")  # switching between ALL DATA (to select) and SELECTED DATA (to remove)

        tk.Button(master=frame_button, text="Remove from Selected", command=self.select_remove).grid(
            row=0, column=3, sticky="nsw")  # button to remove from selected data


class ManualEntry():
    """A Tkinter wrapped window for manual legendization of samples"""
    def legendize(self):
        """
        This function works on self.object parameter of class manual_entry

        Manual entry class mainly consists of self.manual which is tkinter window
        and self.object which is muse_creator_fcs object.

        Self.object itself has attributes .data and .samples
        This function modifies the muse object to include .data, .samples, and .replicate
        attributes, as well as inserting new column titled "Replicate" into .data attribute

        Parameters
        ----------
        a : muse_creator_fcs object. It has attributes .data which is a pandas DataFrame
        structure that is modified

        Returns
        -------
        Modifies pandas DataFrame (a.data) attribute to include Sample and Replicate

        """
        print("legendize occured")
        museobject = self.object
        # dictionary of the type {"Sample_001":"user_input_1:user_input_2}
        dictionary = self.legend_dictionary

        after = museobject

        keys = list(dictionary.values())  # these values will be new keys
        values = [x[:x.find(":")] for x in keys]
        # this is dictionary from replicate to sample
        second_dictionary = dict(zip(keys, values))

        after.replicates = keys  # updating replicates
        after.samples = list(dict.fromkeys(values))  # updating samples

        # the following is necessary if one wants to update their legend
        # if there is no "Replicate" column, "Samples" column is first mapped using
        # legendized dictionary (of type {"Sample_001":"user_input_1:user_input_2})
        # that column is switched to "Replicate" column
        # "Sample" column is then changed to include everything before ":" delimited
        # usually "user_input_1"

        # if there is "Replicate" column, "Sample" column is changed to be equal to
        # "Replicate" column mapped using dictionary (type:{"Sample_001":"user_input_1:user_input_2})

        try:
            after.data["Sample"] = after.data["Replicate"].map(dictionary)
            after.data["Replicate"] = after.data["Sample"]
            after.data["Sample"] = after.data["Sample"].map(second_dictionary)
        except KeyError:
            after.data["Sample"] = after.data["Sample"].map(dictionary)
            after.data["Replicate"] = after.data["Sample"]
            after.data["Sample"] = after.data["Sample"].map(second_dictionary)

    def enter_info(self, event):
        """
        This is a function that is called when user presses "Enter" in any of
        the given Entry fields

        Two parameters are passed, which is a (class manual) or the self attribute
        and b which is tkinter.Event class, b is not used.

        Class manual contains self.labels, which is a collection of tkinter labels
        whose displayed "text" is accessed by ["text"] suffix

        Class manual contains self.samples and self.replicates which are a collection
        of tkinter entries whose given value is accessed by .get() method

        This function checks that user inputed something in every Entry field,
        checks that Sample+Replicate are not duplicated (e.g, that Sample:01 is not written twice),
        and then prompts legendization through manual.legendize() (a.legendize()) function

        Parameters
        ----------
        self : Self, or manual class
        event : Tkinter event class

        Returns
        -------
        None.

        """

        print(event)
        labels = self.labels
        samples = self.samples
        replicates = self.replicates
        # the size of lists
        n = len(labels)
        # the original labels
        original_text = [label["text"] for label in labels]
        storage = []  # this list makes sure that there are no duplicates
        for i in range(n):
            sam = samples[i]
            rep = replicates[i]
            sam_val = sam.get()
            rep_val = rep.get()
            if len(sam_val) > 0 and len(rep_val) > 0:
                text = sam_val+":"+rep_val
                label = labels[i]
                label["text"] = text
                if text in storage:
                    label["bg"] = "red"
                    duplicate = True  # Boolean that prevents duplicate entry
                else:
                    label["bg"] = "white"
                    storage.append(text)
                    duplicate = False  # Boolean that prevents duplicate entry

        # checking that everything is entered
        check1 = [len(x.get()) for x in samples]
        # checking that everything is entered
        check2 = [len(x.get()) for x in samples]

        if 0 not in check1 and 0 not in check2 and duplicate is False:
            new_labels = [label["text"] for label in labels]
            dictionary = dict(zip(original_text, new_labels))

            # IMPORTANT! DICTIONARY FROM WHICH LEGEND IS MADE
            self.legend_dictionary = dictionary
            self.legendize()  # legendization function

    def __init__(self, museobj):
        """
        This prompts the creation of a tkinter window in which user can input
        Sample and Replicate entries (e.g. Sample_001 being "treated:1", Sample_002 being "treated:2", etc)
        for a given dataset. Dataset that is given is contained in museobj parameter, which contains
        attributes .data (the total dataset) and .samples which is a list of string naming every sample
        in the given dataset

        Main is just a tkinter.Root that manual minimizes (not implemented yet)

        Parameters
        ----------
        main : tkinter.Root window.
        museobj : Given dataset parsed using "muse_fcs_creator" class from a selected .FCS file.

        Returns
        -------
        Modifies museobj parameter to include legendization ("Sample" and "Replicate" columns)

        """
        enter_info = self.enter_info  # function from manual_entry class is reframed to fit into __init__ fun

        # initial conditions
        manual = tk.Toplevel()
        self.manual = manual
        self.object = museobj
        self.legend_dictionary = None
        manual.title("Legendize manually")

        try:
            samples_to_replace = museobj.replicates
            n = len(samples_to_replace)
        except AttributeError:
            samples_to_replace = museobj.samples
            n = len(samples_to_replace)

        label_entries = []
        sample_entries = []
        replicate_entries = []

        # setting up labels
        tk.Label(text="Current name", master=manual, relief="raised",
                 bg="gainsboro").grid(row=0, column=0, sticky="nsew")
        tk.Label(text="Enter sample", master=manual, relief="raised",
                 bg="gainsboro").grid(row=0, column=1, sticky="nsew")
        tk.Label(text="Enter number", master=manual, relief="raised",
                 bg="gainsboro").grid(row=0, column=2, sticky="nsew")

        # setting up the windows'0, 1 and 2 column
        for i in range(n):
            # labels
            label = tk.Label(
                master=manual, text=samples_to_replace[i], relief="raised", bg="gainsboro", pady=5)
            label.grid(row=i+1, column=0, sticky="nsew")
            label_entries.append(label)

            # samples
            samp = tk.Entry(master=manual)
            samp.grid(column=1, row=i+1, sticky="nsw")
            samp.bind("<Return>", enter_info)
            sample_entries.append(samp)

            # replicate numbers
            repl = tk.Entry(master=manual)
            repl.grid(column=2, row=i+1, sticky="nsw")
            repl.bind("<Return>", enter_info)
            replicate_entries.append(repl)

        self.labels = label_entries
        self.samples = sample_entries
        self.replicates = replicate_entries
