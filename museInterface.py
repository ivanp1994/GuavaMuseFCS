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
from .gating import GatingDataManager
from .supplemental import select_file, ModifiedOptionMenu
from .dfdrawer import DrawTopLevel


def start_interface():
    """Starts tkinter interface"""
    app = ParserInterface()
    app.master.mainloop()


class ParserInterface():
    """Wrap around tkinter Tk, holding datasets, etc"""
    grid_row = 0

    def __init__(self):
        self.master = tk.Tk()
        self.paths = []
        self.datastructs = []
        self.command_frame = tk.Frame(master=self.master)
        self.data_frame = tk.Frame(master=self.master)
        self.master.title("Guava Muse FCS parser and drawer")

        def quit_me():
            """quick ironing out of tkinter imperfection"""
            self.master.quit()
            self.master.destroy()
        self.master.protocol("WM_DELETE_WINDOW", quit_me)

        self.command_frame.grid(row=0, column=0)
        self.data_frame.grid(row=1, column=0)

        tk.Button(master=self.command_frame, command=self.add_path, text="Add .FCS file",
                  ).pack(side="left", anchor="nw",)
        tk.Button(master=self.command_frame, command=self.merge, text="Merge Selected",
                  ).pack(side="left", anchor="nw",)

    def add_path(self):
        """Add one FCS"""

        path = select_file()
        if path != "" and path not in self.paths:
            self.paths.append(path)
            self.datastructs.append(DataStructure(self, path))

    def merge(self):
        """Merge Datasets"""
        selected = [item for item in self.datastructs if item.selectedVar.get()]
        if len(selected) > 1:
            paths = [item.path for item in selected]
            data = [item.data for item in selected]
            data = pd.concat(data, axis=0, ignore_index=True)
            self.datastructs.append(ModifiedDataStructure(
                self, path=paths, data=data, what="merge"))


class DataStructure():
    """Basic datastructure with commands"""
    pathCounter = 0  # used to differentiate paths excised from this DataStructure

    def __init__(self, ParserInterfaceInst, path, **kwargs):
        # frame within a frame
        self.master = ParserInterfaceInst.data_frame
        self.path = path
        self.data = None
        self.parserinterfaceinst = ParserInterfaceInst
        self.legendization_option = None
        self.operation_option = None
        # what object is in session, here to hold Gate and Debris
        self.object_in_session = None
        self.label = tk.Label(master=self.master, text="",
                              bg="gainsboro", width=30)
        self.selectedVar = tk.BooleanVar()  # used for selecting
        self.type = "loaded"

        if "data" not in kwargs:
            self.data = parse(path)
        else:
            self.data = kwargs["data"]

        if isinstance(path, str):
            self.label["text"] = path.split("/")[-1]

        # grid handling
        row = ParserInterfaceInst.grid_row
        ParserInterfaceInst.grid_row = row + 1

        self.label.grid(row=row, column=0)

        tk.Checkbutton(master=self.master, variable=self.selectedVar,
                       command=lambda: self.selectedVar.set(
                           not self.selectedVar.get())).grid(row=row, column=1)

        tk.Button(master=self.master, text="Delete",
                  command=self.delete_data).grid(row=row, column=2)

        legendry_menu = ModifiedOptionMenu(master=self.master, label="Legendization",
                                           options=["---", "auto", "manual"],
                                           typevar=None)
        legendry_menu.variable.trace("w", self.handle_legendization)
        self.legendization_option = legendry_menu.variable

        command_menu = ModifiedOptionMenu(master=self.master, label="Command",
                                          options=["---", "Export",
                                                   "Gate", "Draw"],
                                          typevar=None)
        command_menu.variable.trace("w", self.handle_commands)
        self.command_option = command_menu.variable

        legendry_menu.place(r=row, c=3)  # next is 5
        command_menu.place(r=row, c=5)

    def handle_legendization(self, *args):
        """Handles legendization"""
        legendization_dictionary = {
            "auto": self.automatic_leg,
            "manual": self.manual_leg
        }
        value = self.legendization_option.get()
        if value != "---":
            command = legendization_dictionary[value]
            command()

    def handle_commands(self, *args):
        """Handles commands"""
        command_dictionary = {"Export": self.export_data,
                              "Draw": self.draw,
                              "Gate": self.gate
                              }
        value = self.command_option.get()
        if value != "---":
            print(value)
            command = command_dictionary[value]
            command()

    def delete_data(self):
        """Delete data"""
        self.parserinterfaceinst.paths.remove(self.path)
        self.parserinterfaceinst.datastructs.remove(self)
        self.master.destroy()

    def export_data(self):
        """Export the data where, in what format"""
        directory = filedialog.asksaveasfilename(title="Save all data from dataset", filetypes=[(
            "Excel files", "*.xlsx"), ("Comma Separated Values", "*.csv")], defaultextension=".csv")
        if directory[-4:] == "xlsx":
            self.data.to_excel(directory)
        if directory[-4:] == ".csv":
            self.data.to_csv(directory)

    def automatic_leg(self):
        """Automatic legendization acc. to .TXT file"""
        self.data = text_explanation(self.path)

    def manual_leg(self):
        """Manual legendization"""
        ManualEntry(self.data)

    def draw(self):
        """General Drawer"""
        DrawTopLevel("Not None", self.data)

    def gate(self):
        """Start gating procedure"""
        self.object_in_session = GatingDataManager(self.data)
        self.object_in_session.master.protocol(
            "WM_DELETE_WINDOW", self.gate_end)

    def gate_end(self):
        """End gating procedure"""
        selected_data = self.object_in_session.gated_data
        self.object_in_session.master.destroy()
        self.object_in_session = None
        if selected_data is None:
            return()
        gated_path = f"<ID={DataStructure.pathCounter}>"+self.path
        print("Ended Gate")
        DataStructure.pathCounter += 1
        self.parserinterfaceinst.datastructs.append(ModifiedDataStructure(
            self.parserinterfaceinst, path=gated_path, data=selected_data, what="gate"))


class ModifiedDataStructure(DataStructure):
    """A bit advanced, not really necessary, just wanted to test inheritance"""
    colordic = {"debris": "mint cream",
                "gate": "alice blue", "merge": "gainsboro"}

    def __init__(self, ParserInterfaceInst, path, **kwargs):
        super().__init__(ParserInterfaceInst, path, **kwargs)
        # _x=re.findall("<ID=[0-9]+>",self.path)[0]
        # original_path=(self.path[len(_x):])
        self.label["bg"] = ModifiedDataStructure.colordic[kwargs["what"]]
        self.type = kwargs["what"]
        if self.type != "merge":
            self.data.Name = f"{self.type} from "+self.data.Name
        else:
            self.label["text"] = "Merged Data"

    def automatic_leg(self):
        print("Pointless for this dataset")


class ManualEntry():
    """A Tkinter wrapped window for manual legendization of samples"""

    def __init__(self, data):
        """
        This prompts the creation of a tkinter window in which user can input
        Sample and Replicate entries
        (e.g. Sample_001 being "treated:1", Sample_002 being "treated:2", etc)
        for a given dataset. Dataset that is given is contained in museobj parameter,
        which contains
        attributes .data (the total dataset) and .samples
        which is a list of string naming every sample
        in the given dataset

        Main is just a tkinter.Root that manual minimizes (not implemented yet)

        Parameters
        ----------
        main : tkinter.Root window.
        museobj : pandas DataFrame that has "Sample" column.

        Returns
        -------
        Modifies museobj parameter to include legendization ("Sample" and "Replicate" columns)

        """

        # initial conditions

        self.master = tk.Toplevel()
        self.data = data
        self.legend_dictionary = None
        self.label_entries = []
        self.sample_entries = []
        self.replicate_entries = []

        self.master.title("Legendize manually")

        try:
            samples_to_replace = self.data.Replicate
        except AttributeError:
            samples_to_replace = self.data.Sample

        samples_to_replace = sorted(list(set(samples_to_replace)))
        n = len(samples_to_replace)

        # setting up labels
        tk.Label(text="Current name", master=self.master, relief="raised",
                 bg="gainsboro").grid(row=0, column=0, sticky="nsew")
        tk.Label(text="Enter sample", master=self.master, relief="raised",
                 bg="gainsboro").grid(row=0, column=1, sticky="nsew")
        tk.Label(text="Enter number", master=self.master, relief="raised",
                 bg="gainsboro").grid(row=0, column=2, sticky="nsew")

        # setting up the windows'0, 1 and 2 column
        for i in range(n):
            # labels
            label = tk.Label(
                master=self.master, text=samples_to_replace[i], relief="raised",
                bg="gainsboro", pady=5)

            label.grid(row=i+1, column=0, sticky="nsew")
            self.label_entries.append(label)

            # samples
            samp = tk.Entry(master=self.master)
            samp.grid(column=1, row=i+1, sticky="nsw")
            samp.bind("<Return>", self.enter_info)
            self.sample_entries.append(samp)

            # replicate numbers
            repl = tk.Entry(master=self.master)
            repl.grid(column=2, row=i+1, sticky="nsw")
            repl.bind("<Return>", self.enter_info)
            self.replicate_entries.append(repl)

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

        labels = self.label_entries
        samples = self.sample_entries
        replicates = self.replicate_entries
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

        # dictionary of the type {"Sample_001":"user_input_1:user_input_2}
        dictionary = self.legend_dictionary

        keys = list(dictionary.values())  # these values will be new keys
        values = [x[:x.find(":")] for x in keys]
        # this is dictionary from replicate to sample
        second_dictionary = dict(zip(keys, values))

        # the following is necessary if one wants to update their legend
        # if there is no "Replicate" column, "Samples" column is first mapped using
        # legendized dictionary (of type {"Sample_001":"user_input_1:user_input_2})
        # that column is switched to "Replicate" column
        # "Sample" column is then changed to include everything
        # before ":" delimited usually "user_input_1"

        # if there is "Replicate" column, "Sample" column is changed to be equal to
        #"Replicate" column mapped using dictionary (type:{"Sample_001":"user_input_1:user_input_2})

        try:
            self.data["Sample"] = self.data["Replicate"].map(dictionary)
            self.data["Replicate"] = self.data["Sample"]
            self.data["Sample"] = self.data["Sample"].map(second_dictionary)
        except KeyError:
            self.data["Sample"] = self.data["Sample"].map(dictionary)
            self.data["Replicate"] = self.data["Sample"]
            self.data["Sample"] = self.data["Sample"].map(second_dictionary)
