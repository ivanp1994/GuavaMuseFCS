# -*- coding: utf-8 -*-
"""
Created on Mon Aug 23 15:51:15 2021

@author: ivanp
"""


import seaborn as sns
import numpy as np
import pandas as pd
import matplotlib
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import filedialog

from .supplemental import get_numerical, ModifiedOptionMenu
from .gui_enrichment import create_bunit_frac
from .musefcsparser import parse


# %% Manager - _BiounitDebrisDataStructure and DebrisDataManager

class _BiounitDebrisDataStructure():
    def __init__(self, master, Biounit, data):
        self.biounit = Biounit

        self.biounit_label = tk.Label(
            master=master, text=f"{Biounit=}", relief="ridge", bg="gainsboro")
        self.internal_bt = tk.Button(
            master=master, text="From internal", command=self.from_internal)
        self.external_bt = tk.Button(
            master=master, text="From external", command=self.from_external)
        self.info_label = tk.Label(
            master=master, text="", relief="ridge", bg="gainsboro")
        self.threshold_label = tk.Label(
            master=master, text="", relief="ridge", bg="gainsboro")

        self.data = data.loc[data.Biounit == Biounit]
        self.replicates = sorted(list(set(self.data.Replicate)))

        self.selection = None

    def place(self, row_pos):
        self.biounit_label.grid(row=row_pos, column=0, sticky="nsew")
        self.internal_bt.grid(row=row_pos, column=1, sticky="nsew")
        self.external_bt.grid(row=row_pos, column=2, sticky="nsew")
        self.info_label.grid(row=row_pos, column=3, sticky="nsew")
        self.threshold_label.grid(row=row_pos, column=4, sticky="nsew")

    def from_internal(self):
        """Select debris-graph by replicates within structure"""
        internal_prompt = tk.Toplevel()
        listbox = tk.Listbox(selectmode="multiple", master=internal_prompt)
        for i in range(len(self.replicates)):
            listbox.insert(i, self.replicates[i])
        listbox.pack()

        def finalize_internal(listbox, internal_prompt, structure):
            """Short small function to finalize internal selection"""
            indices = listbox.curselection()
            selection = [listbox.get(i) for i in indices]
            internal_prompt.destroy()
            if len(indices) == 0:
                return()
            structure.selection = selection
            structure.info_label["text"] = structure.selection

        internal_prompt.protocol("WM_DELETE_WINDOW", lambda: finalize_internal(
            listbox=listbox, internal_prompt=internal_prompt, structure=self))

    def from_external(self):
        """Provide external debris_path"""
        path = filedialog.askopenfilename(filetypes=(
            ("fcs files", "*.fcs"), ("FCS files", "*.FCS"), ("All files", "*.*")))
        if len(path) == 0:
            return()

        self.selection = path
        # display the short version of the path
        elements = path.split("/")
        while len(elements[-1]) == 0:
            elements.pop()
        short_version = elements[-1]
        self.info_label["text"] = short_version


class DebrisDataManager():

    def __init__(self, data):

        self.data = data.copy()
        self.selected_data = None  # <-data after debris is removed
        self.biounits = None
        self.x = None
        self.y = None
        # <- {biounit:biounitstruc} where {biounit=Str} and {biounitstruc=_BiounitDebrisDataStructure}
        self.biounit_biounitstruc_dic = {}
        # <- {biounit:debrisdata} where {biounit=Str} and {debrisdata=pd.DataFrame}
        self.biounit_debrisdataset_dic = {}
        self.listbox = None  # <-in case of internal
        self.debristoplevel_struct = None  # <- DebrisToplevel object
        self.end_it_all_button = None  # <- Button that concludes debris removal session
        self.master = tk.Toplevel()
        
        self.master.title("Debris Removal Manager")

        if not hasattr(self.data, "Biounit"):
            try:
                create_bunit_frac(self.data)
            except ValueError:
                _faulty_samples = [item for item in list(
                    set(data.Sample)) if "-" not in item]
                raise ValueError(
                    f'The following samples do not have "-": \n {_faulty_samples}')
        self.biounits = sorted(list(set(self.data.Biounit)))

        xy_options = list(get_numerical(self.data).columns)
        x_menu = ModifiedOptionMenu(
            master=self.master, label="X= ", options=xy_options, typevar=None)
        y_menu = ModifiedOptionMenu(
            master=self.master, label="Y= ", options=xy_options, typevar=None)
        self.x = x_menu.variable
        self.y = y_menu.variable

        # remove from full function
        self.x.set("YEL-HLog")
        self.y.set("FSC-HLog")

        x_menu.place(0, 0)
        y_menu.place(1, 0)

        tk.Label(master=self.master, text="Biounit Label and Command menu",
                 bg="gainsboro", relief="groove").grid(row=2, column=0, columnspan=3, sticky="nsew")
        tk.Label(master=self.master, text="Path/Input selection",
                 bg="gainsboro", relief="groove").grid(row=2, column=3, sticky="nsew")
        tk.Label(master=self.master, text="Threshold",
                 bg="gainsboro", relief="groove").grid(row=2, column=4, sticky="nsew")
        row_pos = 3
        for biounit in self.biounits:
            self.biounit_biounitstruc_dic[biounit] = _BiounitDebrisDataStructure(
                self.master, biounit, self.data)
            self.biounit_biounitstruc_dic[biounit].place(row_pos)
            row_pos += 1

        tk.Button(master=self.master, text="Enter Debris Removal Window",
                  command=self.enter_debris_removal).grid(row=row_pos, column=0, columnspan=3, sticky="nsew")
        self.end_it_all_button = tk.Button(master=self.master, text="Conclude the Debris Removal Session").grid(
            row=row_pos, column=3, columnspan=2, sticky="nsew")

    def biounit_threshold_update(self, bt_dic):
        """updates biounitstructure threshold label"""
        for biounit in bt_dic.keys():
            datastructure = self.biounit_biounitstruc_dic[biounit]
            threshold = bt_dic[biounit]
            threshold = round(threshold, 3)
            datastructure.threshold_label["text"] = threshold

    def enter_debris_removal(self):
        """short function for entering debris removal"""
        print("entered debris removal")
        biounit_structure = self.biounit_biounitstruc_dic
        for biounit in biounit_structure.keys():
            structure = biounit_structure[biounit]
            selection = structure.selection
            # this print right here so I can skip some steps in constructing

            if type(selection) == list:
                debris_dataset = self.data.loc[self.data.Biounit == biounit]
                debris_dataset = debris_dataset.loc[debris_dataset.Replicate.isin(
                    selection)]
            elif type(selection) == str:
                debris_dataset = parse(selection)
            else:
                raise ValueError(f"Not selected for {biounit}")
            self.biounit_debrisdataset_dic[biounit] = debris_dataset

        self.debristoplevel_struct = DebrisToplevel(
            self.biounit_debrisdataset_dic, x=self.x.get(), y=self.y.get())
        self.debristoplevel_struct.master.protocol(
            "WM_DELETE_WINDOW", self.prompt_to_end)

    def prompt_to_end(self):
        """Double checks if everything is done - if YES then initializes selected_data to not be none"""

        print("entered prompt to end")
        t, n, p = self.debristoplevel_struct.get_info()
        y_column = self.y.get()
        biounits = list(t.keys())
        lis = []
        for biounit in biounits:
            s = self.data.loc[self.data.Biounit == biounit]
            ss = s.loc[s[y_column] > t[biounit]]
            lis.append(ss)
        selected_data = pd.concat(lis)
        selected_data.reset_index(inplace=True, drop=True)

        per_removed = 100 - len(selected_data)/len(self.data)*100

        box = tk.messagebox.askyesnocancel(
            title="Finish removal?", message=f"This will remove approximately {per_removed:.2f} % of data. \n Proceed? ")

        # if YES -> debris-free data passed as selected data
        # if NO  -> original data passed as selected data

        if box == True:
            self.selected_data = selected_data
            self.debristoplevel_struct.master.destroy()
            self.biounit_threshold_update(t)
            #self.info_label["text"] = "Debris Removed"

        elif box == False:
            self.debristoplevel_struct.master.destroy()
            #self.info_label["text"] = "Debris Not Removed"
        else:
            pass

        def bind_concluding_debris_button(self, func):
            """func -> the function bound to the button"""
            pass


# %% Toplevel - DebrisToplevel, DebrisToplevel_GraphStruct, DebrisToplevel_InfoStruct

class DebrisToplevel():

    def __init__(self, biounit_debrisdataset_dic, x="YEL-HLog", y="FSC-HLog"):

        self.master = tk.Toplevel()

        self.biounitVar = tk.StringVar()
        self.replicateVar = tk.StringVar()
        self.curr_active = None
        self.curr_graph = None

        # <-{biounit:replicate} where {biounit=Str} and {replicate=Str}
        self._biounit_replicate_dic = {}
        # <-{biounit:replicate} where {biounit=Str} amd {replicate=tk.Frame}
        self.biounit_replicate_dic = {}
        self.biounitreplicate_graph_dic = {}
        self.biounit_graph_dic = {}

        self.biounits = list(biounit_debrisdataset_dic.keys())

        self.master.title("Debris Exclusion")
        biounit_frame = tk.Frame(master=self.master)
        biounit_frame.grid(row=0, column=0, sticky="nw")
        biounits = self.biounits
        plt.style.use("fivethirtyeight")

        i = 0
        for biounit in biounits:
            biounit_dataset = biounit_debrisdataset_dic[biounit]
            # print(biounit)
            try:
                replicates = list(dict.fromkeys(biounit_dataset.Replicate))
            except AttributeError:
                biounit_dataset["Replicate"] = biounit_dataset.Sample
                replicates = list(dict.fromkeys(biounit_dataset.Sample))
            self._biounit_replicate_dic[biounit] = replicates

            bt = tk.Radiobutton(master=biounit_frame, indicatoron=0, width=20,
                                value=biounit, text=biounit, variable=self.biounitVar)
            bt.grid(row=0, column=i, sticky="nw")
            i = i+1
            self.biounit_replicate_dic[biounit] = tk.Frame(master=self.master)
            curr_frame = self.biounit_replicate_dic[biounit]

            j = 0
            graph_list = []  # <-list for storing all graphs belonging to biounit
            for replicate in replicates:

                bt = tk.Radiobutton(master=curr_frame, indicatoron=0, width=20,
                                    value=replicate, text=replicate, variable=self.replicateVar)
                bt.grid(row=0, column=j, sticky="nw")

                one_graph = DebrisToplevel_GraphStruct(
                    self.master, biounit_dataset, x, y, replicate)

                self.biounitreplicate_graph_dic[biounit+replicate] = one_graph
                graph_list.append(one_graph)
                j = j+1
            self.biounit_graph_dic[biounit] = graph_list

        # initialize tracing
        self.biounitVar.trace("w", self.change_replicates_buttons)
        self.replicateVar.trace("w", self.change_graph_shown)

        # initialize first selection - BIOUNIT
        first_biounit = biounits[0]
        self.biounitVar.set(first_biounit)
        first_frame = self.biounit_replicate_dic[first_biounit]
        first_frame.grid(row=1, column=0, sticky="w")

        # initialize first selection - REPLICATE
        first_replicates = self._biounit_replicate_dic[first_biounit]
        first_replicate = first_replicates[0]
        self.replicateVar.set(first_replicate)

        # Place the graph
        first_combination = first_biounit+first_replicate
        current_graph_fr = self.biounitreplicate_graph_dic[first_combination]
        current_graph_fr.place(r=5, c=0)
        # create current active for tracking purpose
        self.curr_active = first_frame  # ->Current frame for Replicate buttons
        self.curr_graph = current_graph_fr

        # I want right-click to change graph/biounit
        self.master.bind("<Tab>", self.select_next)

        # I need an information segment
        # [Biounit] [...] [...] [...] ...
        # [Cells]   [...] [...] [...] ...
        # [Threshold] [...] [...] [...] ...
        """
        _biounit_cell = {}
        for biounit in biounits:
            s = self.data.loc[self.data.Biounit == biounit]
            cells = np.array(list(dict.fromkeys(s["Cell Number"])))
            average = round(np.average(cells))
            _biounit_cell[biounit] = average
        """
        infoseg = DebrisToplevel_InfoStruct(
            self.master, self.biounits, self.get_info)

        # Connect changes to figure to changes in updatating DebrisToplevel_InfoStruct
        input_frames = list(self.biounitreplicate_graph_dic.values())
        figures = [item.figure for item in input_frames]
        control_list = [figure.canvas.callbacks.connect(
            "button_press_event", infoseg.update) for figure in figures]

    def change_replicates_buttons(self, *args):

        curr_biounit = self.biounitVar.get()
        if self.curr_active != None:
            self.curr_active.grid_forget()

        self.curr_active = self.biounit_replicate_dic[curr_biounit]
        self.curr_active.grid(row=1, column=0, sticky="nw")
        replicates = self._biounit_replicate_dic[curr_biounit]
        first = replicates[0]
        self.replicateVar.set(first)

    def change_graph_shown(self, *args):

        if self.curr_graph != None:
            self.curr_graph.hide()
        combination = self.biounitVar.get()+self.replicateVar.get()
        replicate_graph = self.biounitreplicate_graph_dic[combination]
        replicate_graph.place(r=5, c=0,)
        self.curr_graph = replicate_graph

    def get_info(self):

        _biounit_th = {}
        _biounit_num = {}
        _biounit_per = {}

        for biounit in self.biounits:
            graphs = self.biounit_graph_dic[biounit]
            cell_th = [graph.cellsizethreshold for graph in graphs]
            cell_num = [graph.cellnumber *
                        graph.percentage_selected for graph in graphs]
            perc_selec = [graph.percentage_selected*100 for graph in graphs]
            av_th = np.average(cell_th)
            av_num = np.average(cell_num)
            av_perc = np.average(perc_selec)
            # print(f"{biounit=},{av_th=}")

            _biounit_th[biounit] = round(av_th, 4)
            _biounit_num[biounit] = round(av_num)
            _biounit_per[biounit] = round(av_perc, 2)
        # print(_biounit_num)
        # print(_biounit_th)
        # print(f"{_biounit_th=},{_biounit_num=},{_biounit_per=}")
        return(_biounit_th, _biounit_num, _biounit_per)

    def select_next(self, event):
        """Selects the next replicate
        OR if there is no replicate, selects the next biounit"""

        curr_biounit = self.biounitVar.get()
        curr_replicate = self.replicateVar.get()

        replicate_list = self._biounit_replicate_dic[curr_biounit]
        index_of_current = replicate_list.index(curr_replicate)
        try:
            next_replicate = replicate_list[index_of_current+1]
            self.replicateVar.set(next_replicate)
        except IndexError:
            # if there is no next in replicates
            # select the next from biounits
            index_of_current = self.biounits.index(curr_biounit)
            try:
                next_biounit = self.biounits[index_of_current+1]
            except IndexError:
                # if there is no next biounit, circle back to the first one
                next_biounit = self.biounits[0]
            default_replicate = self._biounit_replicate_dic[curr_biounit][0]
            self.replicateVar.set(default_replicate)
            self.biounitVar.set(next_biounit)


class DebrisToplevel_GraphStruct():

    def __init__(self, master, data, x, y, replicate):
        self.frame = tk.Frame(master=master)
        self.canvas = None
        self.figure = Figure((10, 10))
        self.cellnumber = None
        self.percentage_selected = 1
        self.textbox = None
        self.line = None
        self.data = None
        self.y = y
        self.cellsizethreshold = 0

        u_data = data.loc[data.Replicate == replicate]
        self.data = u_data
        self.cellnumber = u_data["Cell Number"].iloc[0]

        # draw a figure
        colors = matplotlib.rcParams["axes.prop_cycle"].by_key()["color"]
        scat = self.figure.add_subplot(111)
        sns.scatterplot(data=u_data, x=x, y=y, ax=scat, s=1)

        # draw an initial line
        self.line = scat.axhline(0, linewidth=3, color=colors[2])

        # create a texbox
        display = self.cellnumber*self.percentage_selected
        display = str(display)+" Cells per Microliter"
        props = dict(boxstyle="round", facecolor="wheat", alpha=0.9)
        self.textbox = scat.text(
            0.75, 0.95, display, transform=scat.transAxes, bbox=props)

        # place it on canvas
        canvas = FigureCanvasTkAgg(self.figure, master=self.frame)
        widget = canvas.get_tk_widget()
        widget.grid(row=1, column=0)
        self.canvas = canvas
        # connect clickage!
        f = self.figure.canvas.callbacks.connect(
            'button_press_event', self.click_coordinate)

    def hide(self):
        self.frame.grid_forget()

    def place(self, r=1, c=0):
        self.frame.grid(row=r, column=c)

    def click_coordinate(self, event):
        if event.inaxes is None:
            return()
        y_coord = event.ydata

        self.cellsizethreshold = y_coord
        self.line.set_ydata(y_coord)
        data = self.data
        y = self.y
        series = data[y]
        above = np.count_nonzero(series > y_coord)
        percentage = above/len(series)
        self.percentage_selected = percentage

        display = self.cellnumber*self.percentage_selected
        display = round(display)

        display = str(display)+" Cells per Microliter"
        self.textbox.set_text(display)

        self.canvas.draw()


class DebrisToplevel_InfoStruct():

    def __init__(self, master, biounits, update_function):
        self.frame = tk.Frame(master=master)
        self.labels = []
        self.biounits = biounits
        self.retrieving_info = update_function

        self.frame.grid(row=3, column=0, sticky="w")
        tk.Label(master=self.frame, text="Biounit", relief="raised",
                 bg="gainsboro").grid(row=0, column=1, sticky="we")
        tk.Label(master=self.frame, text="Cells", relief="raised",
                 bg="gainsboro").grid(row=1, column=1, sticky="we")
        tk.Label(master=self.frame, text="Threshold", relief="raised",
                 bg="gainsboro").grid(row=2, column=1, sticky="we")
        tk.Label(master=self.frame, text="Percentage Remaining", relief="raised",
                 bg="gainsboro").grid(row=3, column=1, sticky="we")

        self.update()
        update_bt = tk.Button(
            master=self.frame, text="Update", command=self.update)
        #update_bt.grid(row=0, column=0, rowspan=3, sticky="nsew",)

    def update(self, *args):

        # Block for destroying
        for item in self.labels:
            item.destroy()
        self.labels = []

        _biounit_threshold, _biounit_cell, _biounit_per = self.retrieving_info()

        # Block for updating
        for i in range(len(self.biounits)):
            biounit = self.biounits[i]
            pos = i+2

            a = tk.Label(master=self.frame, text=biounit, relief="raised",
                         width=10)
            b = tk.Label(master=self.frame,
                         text=_biounit_cell[biounit], relief="raised", width=10)

            c = tk.Label(master=self.frame, text=_biounit_threshold[biounit], relief="raised",
                         width=10)
            d = tk.Label(master=self.frame,
                         text=_biounit_per[biounit], relief="raised", width=10)

            a.grid(row=0, column=pos, sticky="we")
            b.grid(row=1, column=pos, sticky="we")
            c.grid(row=2, column=pos, sticky="we")
            d.grid(row=3, column=pos, sticky="we")
            self.labels += [a, b, c, d]
