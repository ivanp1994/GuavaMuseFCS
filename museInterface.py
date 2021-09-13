# -*- coding: utf-8 -*-
# pylint: disable=C0103
# pylint: disable=R1710
"""
@author = Ivan Pokrovac
pylint global evaluation = 10/10
"""
import tkinter as tk
from tkinter import filedialog
import pandas as pd

from .musefcsparser import parse, text_explanation
from .gating import GUIgating_outline as guigo
from .gui_enrichment import XYSelectorTopLevel
from .supplemental import ManualEntry, select_file
from .debris_exclusion import DebrisDataManager
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

        # this creates a new button that is placed in the frame of a given dataset
        # with enough leeway for new buttons
        # the button destroys the dataset completely
        delete_object = tk.Button(
            master=data_set.frame, text="Remove data", command=lambda: self.remove_data(data_set))
        delete_object.grid(row=0, column=6)


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

        master = mainclass.main  # master is tk.Tk root
        frame = tk.Frame(master=master)  # initializes frame
        self.main=mainclass
        self.frame = frame
        self.info = names
        self.data = merged_data
        self.debrisfree_data = None
        self.debris_top = None
        self.info_but = None
        
        # creates a button that promts exportation of data
        export_but = tk.Button(master=frame, text="Export",
                               command=self.export_data)
        export_but.grid(row=0, column=2,sticky="nsew")

        info_butt = tk.Button(master=frame, text="MERGED DATA",
                              command=self.info_prompt)
        self.info_but=info_butt
        info_butt.grid(row=0, column=0,sticky="nsew")

        gating_but = tk.Button(master=frame, text="GATING",
                               command=self.gating)        

        #gating_but = tk.Button(master=frame, text="GATING",
        #                       command=lambda: guigo(self.data))
        gating_but.grid(row=0, column=5,sticky="nsew")

        #enrichment_but = tk.Button(
         #   master=frame, text="ENRICHMENT", command=lambda: XYSelectorTopLevel(self.data))
        enrichment_but = tk.Button(
            master=frame, text="ENRICHMENT", command=self.enrichment)
        enrichment_but.grid(row=0, column=6,sticky="nsew")

        debrisexc_but = tk.Button(
            master=frame, text="Remove Debris", command=self.debris_removal)
        debrisexc_but.grid(row=0, column=7,sticky="nsew")
        # stores this frame in mainclass.frames list for better removal
        mainclass.frames.append(self)
        
        self.place() #<-places it on the grid
    
    def place(self):
        self.frame.grid(row=1, column=0)
        
    def debris_removal(self):
        """Starts debris removal procedure"""
        self.debris_top = DebrisDataManager(self.data)
        self.debris_top.master.protocol(
            "WM_DELETE_WINDOW", self.debris_removal_end)

    def debris_removal_end(self):
        """Ends debris removal procedure"""
        print("Debris removal ended")
        selected_data=self.debris_top.selected_data
        self.debris_top.master.destroy()
        if selected_data is None:
            return()
        names=list(dict.fromkeys(selected_data.Name))
        MDFSS = MDebrisFreeSS(self.main,names,merged_data=selected_data)
        MDFSS.place()

    
    def gating(self):
        guigo(self.data)
    
    def enrichment(self):
        XYSelectorTopLevel(self.data)
        

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

class MDebrisFreeSS(MDSS):
    def place(self):
        self.frame.grid(row=2,column=0)

    def __init__(self, mainclass, names, merged_data):
        super().__init__(mainclass, names, merged_data)
        self.info.insert(0,"Removed debris from following files")
        delete_object = tk.Button(master=self.frame, text="Remove data",
                                  command=lambda: self.frame.destroy())
        delete_object.grid(row=0, column=4,sticky="nsew")
        self.info_but["text"]="Debris Free Data"

def start_interface():
    """Starts"""
    app = Backbone()
    app.start()
