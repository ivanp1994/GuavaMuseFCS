# -*- coding: utf-8 -*-
# pylint: disable=C0103
# pylint: disable=R1710
"""
@author = Ivan Pokrovac
pylint global evaluation = 10/10
"""
import tkinter as tk
import pandas as pd

from .datastructs import DSS, MDSS
from .supplemental import select_file
from .dfdrawer import DrawTopLevel


class Backbone():
    """
    Some documentation here
    """

    # MERGING DATA BLOCK : BEGINNING
    def merge_data(self):
        """
        Merges all data in one big structure, removing everything else in the process
        Creates merged_data_set_structure that is similar to data_set_structure
        and places it on main app,

        No further data can be added unless RESET is run

        Returns
        -------
        None.
        """

        # I want to check that every dataframe has exact number of columns
        # because I want data to be a tight fit around themselves
        # dataframes that were legendized have one column more

        # all loaded data in form of pandas.DataFrame
        datas = [item.data for item in self.frames]

        # number of columns in everydata set
        # if there is more than 1, that means
        #  there are dataframes with diff num of columns
        col_len = [len(item.columns) for item in datas]
        col_len = set(col_len)  # removing duplicates
        if len(col_len) != 1:
            return()

        # main = self.main  # self is the entire main_app class, self.main is the tkinter root

        names = [item.name for item in self.frames]  # names of all merged data
        merged_data = pd.concat(datas)  # concatenates dataframes

        # self.frames is a list in which all data_strucs are contained
        # this makes sure that this list empties
        # need to use while to make sure that len of self.frames is 0
        while len(self.frames) > 0:  # this definitely makes sure that data is removed
            self.remove_data(self.frames[0])

        self.file_row = 1  # sets file row to 1
        # THIS IS HOW MERGED_DATA IS STORED
        self.merged_data = MDSS(self, names, merged_data)
        # this creates a new button that is placed in the frame of a given dataset
        # with enough leeway for new buttons
        # the button destroys the dataset completely
        delete_object = tk.Button(master=self.merged_data.frame, text="Remove data",
                                  command=lambda: self.remove_data(self.merged_data))
        delete_object.grid(row=0, column=4)


# MERGING DATA BLOCK : END
# ADD & REMOVE DATA BLOCK : BEGINNING

    def remove_data(self, frame):
        """
        Removes data_set_structure

        Parameters
        ----------
        frame : data_set_structure that is to be removed

        Returns
        -------
        None.

        """
        #print("all loaded: ", self.paths)
        self.frames.remove(frame)
        # data_set_str has additional path which is stored in mainapp (self)
        if isinstance(frame, DSS):
            self.paths.remove(frame.path)  # removes from list of paths
        frame.frame.destroy()  # destroys tkinter object

    def add_data(self):
        """
        Adds data. Data is added in the form of data_set_structure which is a class
        initialized with variables main (tkinter tk.Tk()) and path (where .FCS file is)

        Data_set_structure is stored in self.frames and self.loaded_data attributes

        Returns
        -------

        """

        main = self.main  # self is the entire main_app class, self.main is the tkinter root
        path = select_file()  # function for opening path
        if path in self.paths:
            return()  # checking for duplicates, if found, stops the function
        self.paths.append(path)
        data_set = DSS(main, path)  # creates new data_set
        # selects where to place it
        data_set.place(self.file_row)
        self.file_row = self.file_row+1  # shifting the entire row 1 bottom

        self.frames.append(data_set)
        # storing the entire frame object

        #this creates a new button that is placed in the frame of a given dataset
        #with enough leeway for new buttons
        # the button destroys the dataset completely
        delete_object = tk.Button(
            master=data_set.frame, text="Remove data", command=lambda: self.remove_data(data_set))
        delete_object.grid(row=0, column=6)


# ADD & REMOVE DATA BLOCK : END


#####

    def start(self):
        """Starts the GUI"""
        self.main.mainloop()

    def __init__(self):
        """
        This creates the main_app structure.
        Attributes are:

        self.main (tk.Tk() element of tkinter, or "root")


        self.paths which is a list of all paths to .FCS files

        self.frames which is a list that contains data_set_structures defined in the above class

        self.file_row which modifies where a new data structure will be placed

        Returns
        -------
        None.

        """

        main = tk.Tk()
        main.title("GuavaMuse Parser")
        self.main = main
        self.file_row = 1
        self.paths = []
        self.frames = []  # list of frames, frames being frame.class not tkinter Frame
        self.merged_data = None
        button_dictionary = {}  # in this dictionary, buttons will be stored

        def quit_me():
            main.quit()
            main.destroy()
        main.protocol("WM_DELETE_WINDOW", quit_me)

        # this frame stores all the buttons
        button_frame = tk.Frame(master=main)
        # this button prompts addition of a new .FCS file
        open_file = tk.Button(master=button_frame, text="Add File",
                              bg="gainsboro", command=self.add_data)
        open_file.grid(row=0, column=0)
        # this button prompts all files to be merged in one superfile
        merge_files = tk.Button(master=button_frame, text="Merge Files",
                                bg="gainsboro", command=self.merge_data)
        merge_files.grid(row=0, column=1)

        button_dictionary["ADD"] = open_file
        button_dictionary["MERGE"] = merge_files

        self.button_dictionary = button_dictionary

        button_frame.grid(row=0, column=0)
        tk.Button(master=button_frame, text="Draw Menu", bg="gainsboro",
                  command=lambda: DrawTopLevel(self.main,
                                               self.merged_data.data)).grid(row=0, column=3)


def start_interface():
    """Starts"""
    app = Backbone()
    app.start()
