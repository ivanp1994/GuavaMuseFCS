# -*- coding: utf-8 -*-
# pylint: disable=C0103
# pylint: disable=C0301
# pylint: disable = R1710
"""
@author = Ivan Pokrovac
pylint global evaluation = 9.68/10
"""

import tkinter as tk
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import numpy as np


from .dfdraw_settings import ScatterFrameSettings, LineFrameSettings, HistogramFrameSettings, KDEFrameSettings, ECDFFrameSettings, BoxSwarmFrameSettings, StripFrameSettings, ViolinFrameSettings, BoxenFrameSettings, BarFrameSettings, PointFrameSettings
from .dfdraw_settings import Typeframe, Varframe

from .supplemental import ModifiedOptionMenu, DataDrawSelector, get_categorical, get_numerical


def draw_dist(kind, data, x, y, values):
    """
    Function for drawing distance plots - hist,kde,ecdf
    Difference between univariate and bivariate versions exist:
        BiVariate hist doesn't have "element" and "multiple" attribute'
        BiVariate kde has "levels", UniVariate kde has "multiple" and "common_grid"
    ECDF cannot have Y as variable

    """
    if kind == "hist":
        if y is None:  # Y isn't a variable - UniVariate histogram
            sns.displot(data=data, x=x, kind=kind, hue=values["hue"], col=values["col"],
                        col_wrap=values["col_wrap"], legend=values["legend"], cumulative=values["cumulative"],
                        bins=values["bins"], stat=values["stat"], multiple=values["multiple"],
                        discrete=values["discrete"],
                        element=values["element"])
        else:  # Y is a variable - BiVariate histogram
            sns.displot(data=data, x=x, y=y, kind=kind, hue=values["hue"], col=values["col"],
                        col_wrap=values["col_wrap"], legend=values["legend"], cumulative=values["cumulative"],
                        bins=values["bins"], stat=values["stat"],
                        discrete=values["discrete"])
    if kind == "kde":
        if y is None:  # Y isn't a variable - UniVariate density plot
            sns.displot(data=data, x=x, y=y, kind=kind, hue=values["hue"], col=values["col"], col_wrap=values["col_wrap"],
                        legend=values["legend"], row=values["row"], cumulative=values["cumulative"],
                        bw_method=values["bw_method"], bw_adjust=values["bw_adjust"], common_norm=values["common_norm"],
                        multiple=values["multiple"], common_grid=values["common_grid"])
        else:  # Y is a variable - BiVariate Density plot
            sns.displot(data=data, x=x, y=y, kind=kind, hue=values["hue"], col=values["col"], col_wrap=values["col_wrap"],
                        legend=values["legend"], row=values["row"], cumulative=values["cumulative"],
                        bw_method=values["bw_method"], bw_adjust=values["bw_adjust"], common_norm=values["common_norm"],
                        levels=values["levels"])
    if kind == "ecdf":
        sns.displot(data=data, x=x, kind=kind, hue=values["hue"], col=values["col"], col_wrap=values["col_wrap"],
                    legend=values["legend"], row=values["row"],
                    stat=values["stat"], complementary=values["complementary"])


def draw_rel(kind, data, x, y, values):
    """
    Function for drawing relationship plots - scatter and line
    Cannot have y as None
    """
    if kind == "scatter":
        sns.relplot(data=data, x=x, y=y, kind=kind, hue=values["hue"], col=values["col"], col_wrap=values["col_wrap"],
                    legend=values["legend"], row=values["row"], style=values["style"], marker=values["marker"],
                    s=values["dotsize"])
    if kind == "line":
        sns.relplot(data=data, x=x, y=y, kind=kind, hue=values["hue"], col=values["col"], col_wrap=values["col_wrap"],
                    legend=values["legend"], row=values["row"], style=values["style"], marker=values["marker"],
                    dashes=values["dashes"], ci=values["ci"], estimator=values["estimator"])


def draw_cat(kind, data, x, y, values):
    """
    Function for drawing categorical plots:
        box, swarm, strip, violin, boxen, bar, point

    """

    if kind in ("box", "swarm"):
        sns.catplot(data=data, x=x, y=y, kind=kind, hue=values["hue"], row=values["row"], col=values["col"],
                    col_wrap=values["col_wrap"], legend=values["legend"])
    elif kind == "strip":
        sns.catplot(data=data, x=x, y=y, kind=kind, hue=values["hue"], row=values["row"], col=values["col"],
                    col_wrap=values["col_wrap"], legend=values["legend"],
                    jitter=values["jitter"])
    elif kind == "violin":
        sns.catplot(data=data, x=x, y=y, kind=kind, hue=values["hue"], row=values["row"], col=values["col"],
                    col_wrap=values["col_wrap"], legend=values["legend"],
                    bw=values["bw"], scale=values["scale"], inner=values["inner"])

    elif kind == "boxen":
        sns.catplot(data=data, x=x, y=y, kind=kind, hue=values["hue"], row=values["row"], col=values["col"],
                    col_wrap=values["col_wrap"], legend=values["legend"],
                    k_depth=values["k_depth"], scale=values["scale"],
                    outlier_prop=values["outlier_prop"], trust_alpha=values["trust_alpha"])
    elif kind == "bar":
        sns.catplot(data=data, x=x, y=y, kind=kind, hue=values["hue"], row=values["row"], col=values["col"],
                    col_wrap=values["col_wrap"], legend=values["legend"],
                    dashes=values["dashes"], ci=values["ci"], estimator=values["estimator"])
    else: #kind = "point"
        sns.catplot(data=data, x=x, y=y, kind=kind, hue=values["hue"], row=values["row"], col=values["col"],
                    col_wrap=values["col_wrap"], legend=values["legend"],
                    dashes=values["dashes"], ci=values["ci"], estimator=values["estimator"],
                    join=values["join"])

class DrawTopLevel():
    """
    self.myself      ->tk.Toplevel()
    self.categorical ->categorical part of dataframe
    self.numerical   ->numerical part of dataframe
    self.draw_selector  ->  object of draw_select class in which .selected data is stored
                            selected data is just subset of .categorical

    self.selected_categorical ->selected subset of .categorical from draw_select class
    self.settings ->current settings frame
    """

    def start(self):
        """Starts DrawTopLevel"""
        if hasattr(self, "root"):
            self.root.mainloop()

    def categorical_shift(self, *args):
        """
        Shifts what is shown in Varframe according to thte Type of graph
        """
        varframe = self.varframe
        tyype = self.typeframe.type_var.get()
        if tyype == "Categorical":
            varframe.categorical_shift(True)
        else:
            varframe.categorical_shift(False)

    def finish_selection(self):
        """
        Finalizes the selection for data
        First by selecting what categorical data is selected from
        self.draw_selector (DataDrawSelector)
        and then by selecting that data
        """
        self.selected_categorical = self.draw_selector.selected
        df = self.dataframe
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
        self.selected_data = selected_df

    def choose_data(self):
        """
        Creates a new window for choosing data
        Calls the "finish selection" function (the above one)
        """

        select_toplevel = tk.Toplevel(master=self.myself)
        draw_select_obj = DataDrawSelector(select_toplevel, self.categorical)
        self.draw_selector = draw_select_obj
        tk.Button(master=self.draw_selector.button_frame, text="FINALIZE",
                  command=self.finish_selection).grid(row=0, column=4, sticky="nsw")

    def kind_settings(self, *args):
        """
        Depending on the kind of graph, selects what settings can apply
        """

        kind = self.typeframe.kind_var.get()
        #kind ="scatter" or "line"
        dictionary = {"scatter": ScatterFrameSettings(self.myself, self.numerical, self.categorical),
                      "line": LineFrameSettings(self.myself, self.numerical, self.categorical),
                      "hist": HistogramFrameSettings(self.myself, self.numerical, self.categorical),
                      "kde": KDEFrameSettings(self.myself, self.numerical, self.categorical),
                      "ecdf": ECDFFrameSettings(self.myself, self.numerical, self.categorical),
                      "box": BoxSwarmFrameSettings(self.myself, self.numerical, self.categorical),
                      "strip": StripFrameSettings(self.myself, self.numerical, self.categorical),
                      "swarm": BoxSwarmFrameSettings(self.myself, self.numerical, self.categorical),
                      "violin": ViolinFrameSettings(self.myself, self.numerical, self.categorical),
                      "boxen": BoxenFrameSettings(self.myself, self.numerical, self.categorical),
                      "bar": BarFrameSettings(self.myself, self.numerical, self.categorical),
                      "point": PointFrameSettings(self.myself, self.numerical, self.categorical), }
        # BLOCK TO REMOVE PREVIOUS FRAME
        try:
            master = self.myself
            slaves = master.grid_slaves(row=0, column=4)
            for item in slaves:
                item.grid_forget()
        except:
            pass

        settings = dictionary[kind]
        settings.place_frame(r=0, c=4)
        self.settings = settings

    def retrieve_settings(self):
        """
        This retrieves settings
        Fixes inconsistencies
        And calls draw function
        """
        matplotlib.use("TkAgg")
        settings = self.settings
        values = settings.yield_value_dictionary()

        try:  # this tries if there is estimator in values
            item = values["estimator"]
            if item == "median":  # if estimator is median then it links numpy function
                values["estimator"] = np.median
        except:
            pass

        # solving None, True, False being passed as strings
        for item in values.keys():
            value = values[item]
            if value == "None":
                values[item] = None
            if value == "True":
                values[item] = True
            if value == "False":
                values[item] = False

        # solving ECDF only being univariate
        if self.y.get() is not None and self.kind.get() == "ecdf":
            self.y.set(None)

        # solving for lunacy of having relplot and no Y variable
        if self.y.get() == "None" and self.type.get() == "Relationship":
            raise ValueError("No Y variable for Relationship plot")


        # extracting information - x, y, kind, type, data
        x = self.x.get()
        y = self.y.get()
        if y == "None":
            y = None
        kind = self.kind.get()
        type_graph = self.type.get()
        data = self.selected_data

        if type_graph == "Distribution":
            draw_dist(kind, data, x, y, values)

        if type_graph == "Relationship":
            draw_rel(kind, data, x, y, values)

        if type_graph == "Categorical":
            draw_cat(kind,data,x,y,values)

    def __init__(self, master, dataframe):
        categorical = get_categorical(dataframe)
        numerical = get_numerical(dataframe)
        if master is None:  # adding standalone option
            drawframe = tk.Tk()
        else:
            drawframe = tk.Toplevel()
        self.dataframe = dataframe
        drawframe.title("Draw Menu")
        self.myself = drawframe  # this is tk.Toplevel()
        if isinstance(self.myself, tk.Tk):
            self.root = self.myself  # adding redundancy
        self.categorical = categorical
        self.numerical = numerical
        self.selected_data = dataframe
        self.draw_selector = None
        self.selected_categorical = None

        button_frame = tk.Frame(master=drawframe)
        button_frame.grid(row=0, column=0, sticky="nsew")

        tk.Button(master=button_frame, text="SELECT DATA",
                  command=self.choose_data).grid(row=0, column=0, sticky="nsew")
        tk.Button(master=button_frame, text="DRAW", command=self.retrieve_settings).grid(
            row=2, column=0, sticky="nsew")

        matplotstyle = ModifiedOptionMenu(
            button_frame, "STYLE", list(plt.style.available), None)
        matplotstyle.variable.set("seaborn")
        plt.style.use(matplotstyle.variable.get())
        matplotstyle.variable.trace(
            "w", lambda a, b, c: plt.style.use(matplotstyle.variable.get()))
        matplotstyle.place(0, 3)

        typeframe = Typeframe(drawframe)
        typeframe.place(r=0, c=1)
        self.typeframe = typeframe

        varframe = Varframe(drawframe, numerical, categorical)
        varframe.place(r=0, c=2)
        self.varframe = varframe

        self.x = self.varframe.first
        self.y = self.varframe.second
        self.type = self.typeframe.type_var
        self.kind = self.typeframe.kind_var

        type_transitory = typeframe.type_var  # controls what KIND will be shown
        type_transitory.trace("w", self.categorical_shift)

        kind_for_settings = typeframe.kind_var
        kind_for_settings.trace("w", self.kind_settings)

        # first instatiation of kind settings
        self.kind_settings(None, None, None)
