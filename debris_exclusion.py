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

from .supplemental import get_numerical, ModifiedOptionMenu
from .gui_enrichment import create_bunit_frac


# USED


class InputReplicateFrame():
    def hide(self):
        self.frame.grid_forget()

    def place(self, r=1, c=0):
        self.frame.grid(row=r, column=c)

    def click_coordinate(self, event):
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


class RealDebrisTopLevel():

    def change_replicates_buttons(self, *args):
        curr_biounit = self.biounitVar.get()
        if self.curr_active != None:
            self.curr_active.grid_forget()

        self.curr_active = self.biounit_replicate_dic[curr_biounit]
        self.curr_active.grid(row=1, column=0, sticky="nw")

        s = self.data.loc[self.data.Biounit == curr_biounit]
        replicates = list(dict.fromkeys(s.Replicate))
        first = replicates[0]

        self.replicateVar.set(first)

    def change_graph_shown(self, *args):
        if self.curr_graph != None:
            self.curr_graph.hide()
        replicate_graph = self.replicate_graph_dic[self.replicateVar.get()]
        replicate_graph.place(r=5, c=0,)
        self.curr_graph = replicate_graph

    def get_info(self):

        _biounit_th = {}
        _biounit_num = {}

        for biounit in self.biounits:
            graphs = self.biounit_graph_dic[biounit]
            cell_th = [graph.cellsizethreshold for graph in graphs]
            cell_num = [graph.cellnumber *
                        graph.percentage_selected for graph in graphs]
            av_th = np.average(cell_th)
            av_num = np.average(cell_num)

            _biounit_th[biounit] = round(av_th, 4)
            _biounit_num[biounit] = round(av_num)
        # print(_biounit_num)
        # print(_biounit_th)
        return(_biounit_th, _biounit_num)

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

        pass

    def __init__(self, data, x="YEL-HLog", y="FSC-HLog"):
        self.master = tk.Toplevel()
        self.data = data
        self.biounitVar = tk.StringVar()
        self.replicateVar = tk.StringVar()
        self.curr_active = None
        self.curr_graph = None
        self._biounit_replicate_dic = {}  # <-for values
        self.biounit_replicate_dic = {}  # <-for a structure
        self.replicate_graph_dic = {}
        self.biounit_graph_dic = {}

        self.biounits = list(dict.fromkeys(data.Biounit))

        self.master.title("Debris Exclusion")
        biounit_frame = tk.Frame(master=self.master)
        biounit_frame.grid(row=0, column=0, sticky="nw")
        biounits = self.biounits
        plt.style.use("fivethirtyeight")

        i = 0
        for item in biounits:
            s = self.data.loc[self.data.Biounit == item]
            replicates = list(dict.fromkeys(s.Replicate))

            self._biounit_replicate_dic[item] = replicates
            bt = tk.Radiobutton(master=biounit_frame, indicatoron=0, width=20,
                                value=item, text=item, variable=self.biounitVar)
            bt.grid(row=0, column=i, sticky="nw")
            i = i+1

            self.biounit_replicate_dic[item] = tk.Frame(master=self.master)
            curr_frame = self.biounit_replicate_dic[item]
            j = 0
            supp = []
            for item2 in replicates:

                bt = tk.Radiobutton(master=curr_frame, indicatoron=0, width=20,
                                    value=item2, text=item2, variable=self.replicateVar)
                bt.grid(row=0, column=j, sticky="nw")

                one_graph = InputReplicateFrame(self.master, s, x, y, item2)
                self.replicate_graph_dic[item2] = one_graph
                supp.append(one_graph)
                j = j+1
            self.biounit_graph_dic[item] = supp

        # initialize tracing
        self.biounitVar.trace("w", self.change_replicates_buttons)
        self.replicateVar.trace("w", self.change_graph_shown)

        # initialize first selection - BIOUNIT
        self.biounitVar.set(biounits[0])
        first_frame = self.biounit_replicate_dic[biounits[0]]
        first_frame.grid(row=1, column=0, sticky="w")
        # initialize first selection - REPLICATE
        s = self.data.loc[self.data.Biounit == biounits[0]]
        replicates = list(dict.fromkeys(s.Replicate))
        first = replicates[0]
        self.replicateVar.set(first)

        # Place the graph
        current_graph_fr = self.replicate_graph_dic[first]
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
        infoseg = DebrisInformationSegment(
            self.master, self.biounits, self.get_info)

        # Connect changes to figure to changes in updatating DebrisInformationSegment
        input_frames = list(self.replicate_graph_dic.values())
        figures = [item.figure for item in input_frames]
        control_list = [figure.canvas.callbacks.connect(
            "button_press_event", infoseg.update) for figure in figures]


class DebrisInformationSegment():
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

        self.update()
        update_bt = tk.Button(
            master=self.frame, text="Update", command=self.update)
        #update_bt.grid(row=0, column=0, rowspan=3, sticky="nsew",)

    def update(self, *args):

        # Block for destroying
        for item in self.labels:
            item.destroy()
        self.labels = []

        _biounit_threshold, _biounit_cell, = self.retrieving_info()

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

            a.grid(row=0, column=pos, sticky="we")
            b.grid(row=1, column=pos, sticky="we")
            c.grid(row=2, column=pos, sticky="we")
            self.labels += [a, b, c]


class InputSelector():

    def finalize(self, *args):
        indices = self.listbox.curselection()
        selected = [self.listbox.get(i) for i in indices]
        print(selected)
        selected_data = self.data.loc[self.data["Replicate"].isin(selected)]
        XYSelectorTopLevel(selected_data)
        self.master.destroy()

    def bind_finalization(self, func):
        self.finalize_bt.bind("<Button-1>", func)

    def __init__(self, data):
        self.master = tk.Toplevel()
        self.master.title("Selecting inputs")
        self.data = data
        # self.master.geometry("100x300")
        samples = list(dict.fromkeys(data.Replicate))
        samples.sort()
        self.listbox = tk.Listbox(selectmode="multiple", master=self.master)
        for i in range(len(samples)):
            self.listbox.insert(i, samples[i])
        self.listbox.grid(row=1, column=0, sticky="nsew")
        tk.Label(master=self.master, text="Select").grid(
            row=0, column=0, sticky="nsew")
        self.finalize_bt = tk.Button(master=self.master, text="FINALIZE")
        self.finalize_bt.grid(row=2, column=0, sticky="nsew")


class XYSelectorTopLevel():
    """Tkinter toplevel here just to select X and Y variable"""

    def bind_finalization(self, func):
        self.finalize_bt.bind("<Button-1>", func)

    def __init__(self, data):
        """Initializes the selector"""
        master = tk.Toplevel()
        self.master = master
        self.master.title("X & Y")
        self.data = data
        num = get_numerical(data)
        columns = list(num.columns)
        x = ModifiedOptionMenu(self.master, "X=", columns, None)
        x.place(0, 0)
        self.x = x.variable
        y = ModifiedOptionMenu(self.master, "Y=", columns, None)
        y.place(1, 0)
        self.y = y.variable
        self.finalize_bt = tk.Button(master=self.master, text="LOAD",)
        self.finalize_bt.grid(row=0, column=2, rowspan=2, sticky="nsew")
##


class DebrisDataManager():

    def finalize_inputselector(self, *args):
        inputselector = self.input_selector
        indices = inputselector.listbox.curselection()
        self.inputs = [inputselector.listbox.get(i) for i in indices]
        inputselector.master.destroy()
        print(self.inputs)

    def finalize_xyselector(self, *args):
        xy_selector = self.xy_selector
        self.x = xy_selector.x.get()
        self.y = xy_selector.y.get()
        xy_selector.master.destroy()
        print(self.x, self.y)

    def start_input_selection(self):
        data = self.data
        self.input_selector = InputSelector(data)
        self.input_selector.bind_finalization(self.finalize_inputselector)

    def start_xy_selection(self):
        data = self.data
        self.xy_selector = XYSelectorTopLevel(data)
        self.xy_selector.bind_finalization(self.finalize_xyselector)

    def start_debris_excl(self):
        if len(self.inputs) == 0:
            return()
        self.input_data = self.data.loc[self.data.Replicate.isin(self.inputs)]
        self.debris_info = RealDebrisTopLevel(self.input_data)
        self.debris_info.master.protocol(
            "WM_DELETE_WINDOW", self.prompt_to_end)
        #self.debris_info.master.protocol("WM_DELETE_WINDOW", self.end_debri)

    def prompt_to_end(self):
        t, n = self.debris_info.get_info()
        biounits = list(t.keys())
        lis = []
        for biounit in biounits:
            s = self.data.loc[self.data.Biounit == biounit]
            ss = s.loc[s[self.y] > t[biounit]]
            lis.append(ss)
        selected_data = pd.concat(lis)
        selected_data.reset_index(inplace=True, drop=True)

        per_removed = 100 - len(selected_data)/len(self.data)*100

        box = tk.messagebox.askyesnocancel(
            title="Finish removal?", message=f"This will remove approximately {per_removed:.2f} % of data. \n Proceed? ")

        # if YES -> debris-free data passed as selected data
        # if NO  -> original data passed as selected data
        #

        if box == True:
            self.selected_data = selected_data
            self.info_label["text"] = "Debris Removed"
            self.debris_info.master.destroy()
        elif box == False:
            self.selected_data = self.data
            self.info_label["text"] = "Debris Not Removed"
            self.debris_info.master.destroy()
        else:
            self.info_label["text"] = ""

    def __init__(self, data):

        self.master = tk.Toplevel()
        self.data = data
        self.inputs = []
        self.input_data = None
        self.selected_data = None
        self.x = None
        self.y = None
        self.debris_info = None
        self.input_selector = None
        self.xy_selector = None
        self.master.title("Debris Data Manager")
        self.info_label = tk.Label(master=self.master, text="")

        create_bunit_frac(self.data)
        tk.Button(master=self.master, text="Select Input", command=self.start_input_selection).pack(
            anchor="nw", expand=True, fill="both")
        tk.Button(master=self.master, text="Select X&Y", command=self.start_xy_selection).pack(
            anchor="nw", expand=True, fill="both")
        tk.Button(master=self.master, text="Exclude Debris", command=self.start_debris_excl).pack(
            anchor="nw", expand=True, fill="both")
        self.info_label.pack()
