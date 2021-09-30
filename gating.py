# -*- coding: utf-8 -*-
# pylint: disable=R0903
# pylint: disable=R0902
# pylint: disable=R1710
# pylint: disable=C0103
# pylint: disable=C0325
# pylint: disable=C0301
"""
@author: Ivan Pokrovac
pylint global evaluation = 9.83/10
"""

import tkinter as tk
from tkinter import filedialog

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import PolygonSelector
from matplotlib.path import Path


from .supplemental import get_categorical, get_numerical, ModifiedOptionMenu, DataDrawSelector

###FUNCTIONS I NEED###


def data_figure(data, x="YEL-HLog", y="FSC-HLog"):
    """
    Draws a scatterplot on ax, returns figure object of matplotlib Figure class

    Parameters
    ----------
    data : pandas Dataframe.
    x : name of column in data to be drawn on X axis. The default is "YEL-HLog".
    y : name of column in data to be drawn on Y axis. The default is "FSC-HLog".

    Returns
    -------
    Figure

    """
    fig = Figure(figsize=(10, 10))
    ax = fig.add_subplot(111)
    sns.scatterplot(data=data, x=x, y=y, ax=ax, s=1)
    return(fig)


def gate_events(verts, data, x, y):
    """
    From a Gate class, returns all events that are within the gate, as well as
    counts what percentage are within the event, what percentage are outside the event

    THIS DOES NOT MODIFY ORIGINAL DATA

    Parameters
    ----------
    verts : Vertices of a polygon gate.
    data : DataFrame.
    x : Name of column that is x axis of scatterplot
    y : Name of column that is y axis of scatterplot

    Returns
    -------
    Gated events,
    Number of events in the gate
    Number of events outside the gate

    """
    path = Path(verts)
    # I need to add a new discrimininant
    # SELECT ONLY X AND Y COLUMNS

    temp = data[[x, y]]
    # <-Array of True/False same len as the data set
    contains = path.contains_points(temp)

    within = contains.sum()  # Number of True
    without = len(contains) - within  # Number of False

    p_within = round(within/len(contains)*100, 3)
    p_without = round(without/len(contains)*100, 3)

    plc = data.copy()
    plc.insert(0, "gated", contains)

    gated = plc.loc[plc["gated"] == True]
    gated.reset_index(inplace=True, drop=True)
    return(gated, p_within, p_without)


class Gate():
    """
    Gate selector class, only used to get vertices of a polygon by user input
    """

    def onselect(self, event):
        """Stores selected verts and disconnects poly"""
        self.verts = event
        self.poly.disconnect_events()

    def __init__(self, data, ax):
        """
        Parameters
        ----------
        data : dataframe
        ax : matplotlib Axes class
        Returns
        -------
        """
        self.data = data
        self.ax = ax
        self.verts = None
        self.poly = PolygonSelector(ax, self.onselect)


class GateInfo():
    """
    This class is used to actually construct a gate,
    assign it name, color, and relevant statistics, as well as capture all
    events within this gate

    This class is also used to manipulate the gated data,
    such as remove the gates, and export the data
    """

    def __init__(self, gate, name, color, within, without, gated_events, master, topclass):
        """
        Initializes gate

        """
        self.gate = gate
        self.color = color
        self.within = within
        self.without = without
        self.gated_events = gated_events
        self.topclass = topclass
        self.frame = tk.Frame(master)

        self.name_entry = tk.Entry(self.frame)
        self.name_entry.insert(0, name)

        within = tk.Label(text="Within %: " +
                          str(self.within), master=self.frame)
        without = tk.Label(text="Outside %: " +
                           str(self.without), master=self.frame)

        self.name_entry.grid(row=0, column=0)
        within.grid(row=0, column=2)
        without.grid(row=0, column=3)

        remove_gate_bt = tk.Button(
            master=self.frame, text="Remove", command=self.remove_gate)
        remove_gate_bt.grid(row=0, column=4)

        # adding color
        fig = Figure(figsize=(0.5, 0.5))
        ax = fig.add_subplot(111)

        # need to remove the ticks and splines
        # fig.patch.set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.get_xaxis().set_ticks([])
        ax.get_yaxis().set_ticks([])

        ax.set_facecolor(color)

        canvas = FigureCanvasTkAgg(fig, master=self.frame)
        canvas.get_tk_widget().grid(row=0, column=1)
        canvas.draw()

    def __str__(self):
        """
        Prints out name of the gate, followed by percentage of data within and outside the gate
        """
        p1 = self.name_entry.get()+"\n"
        p2 = "Within  the Gate: "+str(self.within)+"%\n"
        p3 = "Outside the Gate: "+str(self.without)+"%\n"
        r = p1+p2+p3
        return(r)

    def remove_gate(self):
        """Removes the Gate"""

        complete_removal = self.topclass.remove_gate  # tying the to the main function
        gate = self.gate
        complete_removal(gate)


class GatingMainWindow():
    """
    Outline of
    """

    def gate_initiate(self):
        """
        Initiates one Gate
        """
        ax = self.figure.get_axes()[0]
        data = self.data
        gate = Gate(data, ax)

        self.gates.append(gate)

        # need to get rid of duplicates

    def gates_complete(self,):
        """
        Finalizes all gates
        """

        # block that destroyes all widgets in infoframe to make refreshing work
        for widget in self.infoframe.winfo_children():
            widget.destroy()

        # This block isn't necessary'
        # try:
            # for widget in self.infoframe.winfo_children():
            # widget.destroy()
        # except:
            # pass

        self.redraw_canvas()  # get rid of all the vertices
        data = self.data
        x_val = self.x
        y_val = self.y

        i = 0
        colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
        ax = self.figure.get_axes()[0]
        self.gatesinfo = []
        self.gate_gateinfo_dic = {}  # <-gate to gateinfo class dictionary
        for gate in self.gates:
            color = colors[i]  # set a color
            i = i+1
            name = "Gate No."+str(i)  # set a name

            verts = gate.verts  # draw the gate
            x = [item[0] for item in verts]
            y = [item[1] for item in verts]
            ax.fill(x, y, color, alpha=0.5)

            gated, within, without = gate_events(verts, data, x_val, y_val)
            gateinfo = GateInfo(gate, name, color, within,
                                without, gated, self.infoframe, self)

            self.gate_gateinfo_dic[gate] = gateinfo
            self.gatesinfo.append(gateinfo)

        self.canvas.draw()
        self.gates_info_place()

    def gates_info_place(self):
        """
        Places GatesInfo on the tkinter frame
        Adds button to remove said gate
        """

        for item in self.gatesinfo:
            item.frame.pack(anchor="w")

    def remove_gate(self, gate):
        """
        Removes the gate

        Parameters
        ----------
        gate : The object of Gate class to be destroyed

        Returns
        -------
        None.

        """

        self.gates.remove(gate)  # <-remove from the list
        # dunno if this is necessary
        gateinfo = self.gate_gateinfo_dic[gate]  # <-get a gateinfo object
        self.gatesinfo.remove(gateinfo)  # <-remove a gateinfo object
        self.gate_gateinfo_dic.pop(gate)  # <-remove dictionary

        # I need to destroy gateinfo frame
        self.gatesinfo = []  # empty out gates info
        for widget in self.infoframe.winfo_children():
            widget.destroy()

        # redraw the canvas
        self.redraw_canvas()
        # apply gates
        self.gates_complete()

    def redraw_canvas(self):
        """Redraws canvas"""
        self.canvas.get_tk_widget().destroy()

        # shifts old figures
        # I ALWAYS NEED TO RECREATE THE FIGURE. ALWAYS.

        self.figure = data_figure(self.data, self.x, self.y)

        # new canvas
        canvas = FigureCanvasTkAgg(self.figure, master=self.canvasframe)
        widget = canvas.get_tk_widget()
        widget.grid(row=0, column=0)
        self.canvas = canvas
        self.canvas.draw()

    def apply_gates(self):
        """Applies the gates - saves the dataset in .CVS or .XLSX"""
        if len(self.gates) == 0:  # terminate if there is no gates
            return()

        # HERE I NEED TO ADD A DISCRIMINATOR
        # data as what is drawn on the plot
        # is just a segment of full data with only x and y values
        # as opposed to full data
        data = self.data  # <-FULL DATA

        x = self.x
        y = self.y
        dataframe = data[[x, y]]
        d = {}
        for gate in self.gates:
            verts = gate.verts
            path = Path(verts)
            # Additional code to make it robust for the future
            contains = path.contains_points(dataframe)

            # This block necessary for naming
            gateinfo = self.gate_gateinfo_dic[gate]
            name_entry = gateinfo.name_entry
            name = name_entry.get()

            d[name] = contains
        d = pd.DataFrame.from_dict(data=d)  # robustnes

        rezult = pd.concat([data, d], axis=1)  # change data for fuller data
        self.gated_data = rezult
        box = filedialog.messagebox.askyesno(
            title="Export Data", message="Export Data")
        if box:

            directory = filedialog.asksaveasfilename(title="Save all data from dataset", filetypes=[(
                "Excel files", "*.xlsx"), ("Comma Separated Values", "*.csv")], defaultextension=".csv")
            ext = directory[-4:]
            if ext == "xlsx":
                rezult.to_excel(directory)
            if ext == ".csv":
                rezult.to_csv(directory)

    def __init__(self, data, x, y):
        self.master = tk.Tk()
        self.master.title("Gating Menu")
        self.data = data
        self.data.reset_index(inplace=True, drop=True)
        self.canvasframe = tk.Frame(self.master)  # <-CANVAS FRAME
        self.canvasframe.grid(row=0, column=0)
        self.x = x
        self.y = y
        self.gate_gateinfo_dic = None
        self.gated_data = None
        figure = data_figure(data, self.x, self.y)  # creates a figure
        canvas = FigureCanvasTkAgg(
            figure, master=self.canvasframe)  # creates a canvas
        plt.style.use("fivethirtyeight")
        # I NEED TO CREATE A DEEP COPY OF A FIGURE
        self.figure = figure
        self.canvas = canvas
        self.gates = []  # <-All Gate classes stored in one list
        self.gatesinfo = []  # <-All GateInfo stored in one list
        widget = canvas.get_tk_widget()
        widget.grid(row=0, column=0)
        canvas.draw()  # draws canvas

        self.controlframe = tk.Frame(self.master)  # <-CONTROL FRAME
        self.controlframe.grid(row=1, column=0)

        enter_selection_bt = tk.Button(
            master=self.controlframe, command=self.gate_initiate, text="Initiate Gate")
        enter_selection_bt.grid(row=1, column=0)

        gate_complete_bt = tk.Button(
            master=self.controlframe, command=self.gates_complete, text="Complete Gates")
        gate_complete_bt.grid(row=1, column=1)

        apply_gates_bt = tk.Button(
            master=self.controlframe, command=self.apply_gates, text="Apply Gates to Data")
        apply_gates_bt.grid(row=1, column=2)

        self.infoframe = tk.Frame(self.master)
        self.infoframe.grid(row=2, column=0)


class GatingDataManager():
    def __init__(self, data):
        self.data = data
        self.master = tk.Toplevel()
        self.categorical = get_categorical(data)
        self.selected_categorical = None
        self.object_in_session = None
        self.gated_data = None
        self.x = None
        self.y = None

        tk.Button(master=self.master, text="Select Data", command=self.categorical_data_selection).grid(
            row=0, column=0, columnspan=2, sticky="nsew")
        xy_options = list(get_numerical(self.data).columns)
        x_menu = ModifiedOptionMenu(
            master=self.master, label="X= ", options=xy_options, typevar=None)
        y_menu = ModifiedOptionMenu(
            master=self.master, label="Y= ", options=xy_options, typevar=None)
        self.x = x_menu.variable
        self.y = y_menu.variable

        self.x.set("YEL-HLog")
        self.y.set("FSC-HLog")
        x_menu.place(1, 0)
        y_menu.place(2, 0)
        tk.Button(master=self.master, text="Enter Gating", command=self.enter_gating).grid(
            row=3, column=0, columnspan=2, sticky="nsew")

    def categorical_data_selection(self):
        select = tk.Toplevel()
        select.title("Select the Data for Gating")
        self.object_in_session = DataDrawSelector(select, self.categorical)
        tk.Button(master=self.object_in_session.button_frame, text="FINALIZE",
                  command=lambda: self.finish_categorical_data_selection(select)).grid(row=0, column=4, sticky="nsw")

    def finish_categorical_data_selection(self, select_toplevel):
        self.selected_categorical = self.object_in_session.selected

        self.object_in_session = None
        select_toplevel.destroy()
        df = self.data
        selected_c = self.selected_categorical
        columns_c = list(selected_c.columns)
        d = {}
        for column in columns_c:
            selected = selected_c[column]
            selected = list(set(selected))
            df_s = df.loc[df[column].isin(selected)]
            d[column] = len(df_s)
        minimal = min(d, key=d.get)
        selected_column = minimal
        selected_rows = selected_c[minimal]
        selected_df = df.loc[df[selected_column].isin(selected_rows)]
        self.selected_categorical = selected_df

    def enter_gating(self):
        if self.selected_categorical is None:
            data = self.data
        else:
            data = self.selected_categorical
        x = self.x.get()
        y = self.y.get()
        self.object_in_session = GatingMainWindow(data, x, y)
        self.object_in_session.master.protocol(
            "WM_DELETE_WINDOW", self.finish_gating)

    def finish_gating(self):

        self.gated_data = self.object_in_session.gated_data
        self.object_in_session.master.destroy()
        self.object_in_session = None
