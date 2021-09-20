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
