# -*- coding: utf-8 -*-
# pylint: disable=C0325
# pylint: disable=C0301
# pylint: disable=C0103
# pylint: disable=W0612
# pylint: disable=W0613
"""
Created on Wed Jun  9 12:16:59 2021
@author = Ivan Pokrovac
pylint global evaluation = 9.24/10
"""

import tkinter as tk
import seaborn as sns
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn.utils import resample
from pandastable import Table

# matplotlib.use("TkAgg")


from .supplemental import get_numerical, ModifiedOptionMenu


def create_bunit_frac(df):
    """


    Parameters
    ----------
    df : Pandas DataFrame that has a colon "Sample", entries in the colon
    "Sample" must be of the form "Fraction"-"Biounit"

    Returns
    -------
    Nothing, changes df to include Biounit and Fraction column

    """
    try:
        # checking if the already is a column Biounits
        biounits = df["Biounits"]
        fractions = df["Fraction"]
        return()
    except:
        pass
    samples = list(dict.fromkeys(df["Sample"]))

    biounits = [item[item.find("-")+1:] for item in samples]
    fractions = [item[:item.find("-")] for item in samples]

    d_fractions = dict(zip(samples, fractions))
    d_biounits = dict(zip(samples, biounits))
    df["Fraction"] = df["Sample"].map(d_fractions)
    df["Biounit"] = df["Sample"].map(d_biounits)
    df.reset_index(inplace=True, drop=True)
    return()


def barplot_ned(df):
    """
    Creates barplot representation of Number, Enrichment, Depletion
    """
    fig, axs = plt.subplots(3, sharex=True)
    fig.suptitle("Barplots of %Positive, Enrichment, and Depletion",
                 fontsize="x-large")
    n = df.loc[df["Type"] == "Number/%"]
    n.reset_index(inplace=True, drop=True)
    e = df.loc[df["Type"] == "Enrichment"]
    e.reset_index(inplace=True, drop=True)
    d = df.loc[df["Type"] == "Depletion"]
    d.reset_index(inplace=True, drop=True)

    # colors=plt.rcParams["axes.prop_cycle"].by_key()["color"]  ###THIS IS HOW I ENSURE COLOR CYCLING
    # ggplot colors
    # ['#E24A33', '#348ABD', '#988ED5', '#777777', '#FBC15E', '#8EBA42', '#FFB5B8']
    axs[0].set_ylabel("% Positive")
    axs[1].set_ylabel("Enrichment")
    axs[2].set_ylabel("Depletion")

    axs[0].bar(x=n["Biounit"], height=n["mean"], yerr=n["stdev"],
               capsize=5, error_kw={'markeredgewidth': 1}, color="#E24A33")
    axs[1].bar(x=e["Biounit"], height=e["mean"], yerr=e["stdev"],
               capsize=5, error_kw={'markeredgewidth': 1}, color='#348ABD')
    axs[2].bar(x=d["Biounit"], height=d["mean"], yerr=d["stdev"],
               capsize=5, error_kw={'markeredgewidth': 1}, color='#988ED5')
    return(fig)


def poe_DIV(mean1, mean2, stdev1, stdev2):
    """
    When variable Z is calculated by X/Y, this is the formula for
    error (standard deviation) of variable Z

    Parameters
    ----------
    mean1 : mean of first (X) variable.
    mean2 : mean of second (Y) variable.
    stdev1 : standard deviation of first (X) variable.
    stdev2 : standard deviation of second (Y) variable.

    Returns
    -------
    propagated error

    """
    mean = mean1/mean2
    a = stdev1/mean1
    b = stdev2/mean2
    a = a*a
    b = b*b
    e = (a+b)**0.5
    sd = mean*e
    return(sd)


def figure_plots(df, x="YEL-HLog", y="FSC-HLog"):
    """
    Make multiple figures based on Fraction column

    Return: Dictionary of Figures
    """
    fractions = list(dict.fromkeys(df["Fraction"]))
    dictionary_figures = {}

    for item in fractions:
        data = df.loc[df["Fraction"] == item]

        figure = Figure((10, 5))
        scat = figure.add_subplot(121)
        dist = figure.add_subplot(122)

        sns.scatterplot(data=data, x=x, y=y, ax=scat, s=1)
        sns.histplot(data=data, x=x, ax=dist)

        # scat.set_aspect(1)
        # dist.set_aspect(0.01)

        dictionary_figures[item] = figure

    return(dictionary_figures)

# CLASSES


class Fraction_Frames():
    """
    A frame under control of BiounitFrame
    Can be one of four - "INP","PM","S","M"
    Every frame has its canvas and figure
    and on this canvas and figure you can click to create a
    red vertical line
    """

    def change_value(self, d):
        """
        Changes value of the vertical X line
        """
        self.t = self.t+d
        self.t = round(self.t, 5)
        self.entry.delete(0, "end")
        display = str(self.t)
        if len(display) > 5:
            display = display[:5]
        self.entry.insert(0, display)

        for line in self.lines:
            line.set_xdata(self.t)
        for value in self.dictionary_canvas.values():
            value.draw()
        self.textbox_update()

    def get_entry(self, add):
        """
        Gets the X value of the vertical X line
        add is here just in case Enter is pressed (tkinter Event)
        """

        can = self.entry.get()
        # fixing difference between Euro and USA spelling (e.g. 12.0 vs 12,0)
        if "," in can:
            can = can.replace(",", ".")
        try:
            can = float(can)
            self.t = can
            for line in self.lines:
                line.set_xdata(self.t)
            self.canvas.draw()
        except:
            self.entry.delete(0, "end")
            self.entry.insert(0, str(self.t))

        for value in self.dictionary_canvas.values():
            value.draw()
        self.textbox_update()

    def textbox_create(self):
        """
        Creates a textbox to display in the frame
        """

        props = dict(boxstyle="round", facecolor="wheat", alpha=0.9)
        self.fraction_textboxes = {}
        df = self.df
        for fraction in self.dictionary_figures.keys():
            data = df.loc[df["Fraction"] == fraction]
            series = data[self.x]

            left = np.count_nonzero(series > self.t)/len(series)*100
            left = round(left, 2)

            right = 100-left
            right = round(right, 2)

            display = "Left:   "+str(left)+"%"+"\n"+"Right: "+str(right)+"%"

            figure = self.dictionary_figures[fraction]
            axes = figure.get_axes()

            text0 = axes[0].text(0.70, 0.90, display,
                                 transform=axes[0].transAxes, bbox=props)
            text1 = axes[1].text(0.70, 0.90, display,
                                 transform=axes[1].transAxes, bbox=props)

            self.fraction_textboxes[fraction] = (text0, text1)

    def textbox_update(self):
        """
        Updates textbox
        """
        df = self.df
        for fraction in self.dictionary_figures.keys():

            data = df.loc[df["Fraction"] == fraction]
            series = data[self.x]

            left = np.count_nonzero(series > self.t)/len(series)*100
            left = round(left, 2)

            right = 100-left
            right = round(right, 2)

            display = "Left:   "+str(left)+"%"+"\n"+"Right: "+str(right)+"%"

            textboxes = self.fraction_textboxes[fraction]
            textboxes[0].set_text(display)
            textboxes[1].set_text(display)

    def show_fraction(self, *args):
        """
        Shows graphs of selected fraction
        """

        self.cur_active.pack_forget()
        fr = self.fraction_var.get()
        canvas = self.dictionary_canvas[fr]
        figure = self.dictionary_figures[fr]
        widget = canvas.get_tk_widget()
        widget.pack()

        f = figure.canvas.callbacks.connect(
            'button_press_event', self.click_coordinate)

        self.cur_active = widget

    def click_coordinate(self, event):
        """
        When user clicks on the graph, places a horizontal line where the user clicked
        """
        x = event.xdata
        self.entry.delete(0, "end")
        self.entry.insert(0, str(x)[:5])
        self.get_entry(None)

    def __init__(self, master, df, x="YEL-HLog", y="FSC-HLog"):
        """
        Initializes the fraction frame
        """
        self.df = df
        self.x = x
        frame = tk.Frame(master)
        self.fractionframe = frame

        canvasframe = tk.Frame(master)
        self.canvasframe = canvasframe

        # <-FRACTION : FIGURE dictionary
        dictionary_figures = figure_plots(df, x, y)
        dictionary_canvas = {}  # <-FRACTION : CANVAS dictionary
        self.dictionary_figures = dictionary_figures
        self.dictionary_canvas = dictionary_canvas

        for key in dictionary_figures.keys():
            dictionary_canvas[key] = FigureCanvasTkAgg(
                dictionary_figures[key], master=canvasframe)
        # Fraction Variable that controls what Fraction is shown

        fraction_var = tk.StringVar()
        self.fraction_var = fraction_var
        self.fraction_var.set(list(dictionary_figures.keys())[0])
        # initalizes first variable
        fr = self.fraction_var.get()
        # places the first canvas
        canvas = self.dictionary_canvas[fr]
        widget = canvas.get_tk_widget()
        widget.pack()
        self.cur_active = widget
        # connects the figure to clicking of the canvas
        figure = self.dictionary_figures[fr]
        f = figure.canvas.callbacks.connect(
            'button_press_event', self.click_coordinate)
        # starts tracing the variable so different fractions can be shown
        self.fraction_var.trace("w", self.show_fraction)

        i = 0
        for item in dictionary_figures.keys():
            bt = tk.Radiobutton(master=frame, indicatoron=0, width=5,
                                value=item, text=item, variable=self.fraction_var)
            bt.grid(row=0, column=i, sticky="nw")
            i = i+1

        t = 0.5
        self.t = t
        self.lines = []

        axes = []
        figures = list(dictionary_figures.values())
        for figure in figures:
            for ax in figure.axes:
                axes.append(ax)

        colors = matplotlib.rcParams["axes.prop_cycle"].by_key()["color"]
        self.axes = axes
        for ax in self.axes:
            line = ax.axvline(x=t, linewidth=1, color=colors[2])
            self.lines.append(line)

        self.textbox_create()

        control = tk.Frame(master)
        self.controlframe = control
        entry = tk.Entry(master=control)
        entry.bind("<Return>", self.get_entry)
        entry.insert(0, str(t))
        entry.grid(row=0, column=3)
        self.entry = entry

        button_dec = tk.Button(master=control, text="<<",
                               command=lambda: self.change_value(-0.1))
        button_dec.grid(row=0, column=1)

        button_decs = tk.Button(master=control, text="<",
                                command=lambda: self.change_value(-0.01))
        button_decs.grid(row=0, column=2)

        button_inc = tk.Button(master=control, text=">>",
                               command=lambda: self.change_value(0.1))
        button_inc.grid(row=0, column=5)

        button_incs = tk.Button(master=control, text=">",
                                command=lambda: self.change_value(0.01))
        button_incs.grid(row=0, column=4)

    def place(self, row, column=0):
        """
        Shows the frame
        """
        self.fractionframe.grid(row=row, column=column, sticky="nw")
        self.canvasframe.grid(row=row+1, column=column)
        self.controlframe.grid(row=row+2, column=column)

    def hide(self):
        """
        Hides the frame
        """
        self.fractionframe.grid_forget()
        self.canvasframe.grid_forget()
        self.controlframe.grid_forget()


class Biounit_Frames():
    """
    This Frame houses Biounits as defined in github.doc
    Every Biounit Frame has 4 corresponding Fraction Frames
        "INP","PM","M","S"
    Every Biounit Frame also *controls* which Fraction Frame is currently shown
    """

    def show_unit(self, *args):
        """
        Controls what Fraction is show
        """
        self.cur_active.hide()
        self.explframe.destroy()
        biounit = self.biounit_var.get()
        fraction_frame = self.biounit_fractionfr[biounit]
        fraction_frame.place(row=1)
        self.cur_active = fraction_frame

        for item in self.biounit_fractionfr.values():
            for canvas in item.dictionary_canvas.values():
                canvas.draw()
        self.explframe = BTFrame(self.master, self.biounit_fractionfr)
        self.explframe.place(2, 1)
        self.toplevelmaster.add_load_btbutton()

    def __init__(self,  master, enrichmenttoplevel, data, x="YEL-HLog", y="FSC-HLog"):
        """
        Initializes the frame
        """
        self.master = master
        self.toplevelmaster=enrichmenttoplevel
        plt.style.use("ggplot")
        # blue blue red
        matplotlib.rcParams['axes.prop_cycle'] = matplotlib.cycler(
            color=["#348ABD", "#348ABD", "#E24A33", "green"])

        biounits = list(dict.fromkeys(data["Biounit"]))

        biounit_fractionfr = {}
        self.biounit_fractionfr = biounit_fractionfr
        for biounit in biounits:
            df = data.loc[data["Biounit"] == biounit]
            biounit_fractionfr[biounit] = Fraction_Frames(master, df, x, y)

        self.biounitframe = tk.Frame(master)
        self.biounitframe.grid(row=0, column=0, sticky="nw")
        self.biounit_var = tk.StringVar()

        # Initializes the first showing
        self.biounit_var.set(biounits[0])
        biounit = self.biounit_var.get()
        fraction_frame = self.biounit_fractionfr[biounit]
        fraction_frame.place(row=1)
        self.cur_active = fraction_frame

        self.explframe = BTFrame(self.master, self.biounit_fractionfr)
        self.explframe.place(2, 1)
        # Starts the biounit tracing
        self.biounit_var.trace("w", self.show_unit)

        i = 0
        for item in biounits:
            bt = tk.Radiobutton(master=self.biounitframe, indicatoron=0,
                                width=10, value=item, text=item, variable=self.biounit_var)
            bt.grid(row=2, column=i, sticky="nw")
            i = i+1


class BTFrame():
    """
    Frame for holding information about biounits and thresholds
    """

    def place(self, r, c):
        """Places the frame"""
        self.btframe.grid(row=r, column=c, sticky="n")

    def destroy(self):
        """Destroys the frame"""
        self.btframe.destroy()

    def __init__(self, master, biounit_fractionfr):
        """Initializes the frame"""
        bt_dic = {}  # <-BIOUNIT:THRESHOLD
        for item in biounit_fractionfr.keys():
            frframe = biounit_fractionfr[item]
            t = frframe.t
            bt_dic[item] = t
        self.btframe = tk.Frame(master=master)
        tk.Label(master=self.btframe, text="BIOUNIT", bg="gainsboro",
                 relief="raised").grid(row=0, column=0)
        tk.Label(master=self.btframe, text="THRESHOLD",
                 bg="gainsboro", relief="raised").grid(row=0, column=1)
        for i in range(len(bt_dic.keys())):
            b = list(bt_dic.keys())[i]
            t = bt_dic[b]
            tk.Label(master=self.btframe, text=b, bg="white", borderwidth=2,
                     relief="ridge").grid(row=i+1, column=0, sticky="nsew")
            tk.Label(master=self.btframe, text=t, bg="white", borderwidth=2,
                     relief="ridge").grid(row=i+1, column=1, sticky="nsew")

        self.finalpos = i+2


class Replicate_Backend():
    """
    This class contains functions to calculate N,E,D
    from Replicates at the end
    """

    # deleted percentil between x and threshold dic
    def above_threshold(self, df, x, threshold_dic):
        """
            Parameters
            ----------
            df : DataFrame that has columns "Biounit" and "Fractions"
                Valid types of "Fraction" values are "INP","PM","S","M"
            x : numerical column in df on which percentile will be calculated.
            percentil : int.
            threshold_dic : A dictionary of the type {"Biounit":value} where value dictates threshold

            Returns
            -------
            Dictionary of the type:
                "Biounit" : {dic1}
            When {dic1} is the dictonary of the type:
                {"Fraction":[list]}
            And [list] contains percentage of

        """

        biounits = list(dict.fromkeys(df["Biounit"]))
        fractions = ["INP", "PM", "S", "M"]
        maindics = {}
        for unit in biounits:
            value = threshold_dic[unit]
            dic = {}
            for fraction in fractions:
                sample = fraction+"-"+unit
                select = df.loc[df["Sample"] == sample]
                replicates = list(dict.fromkeys(select["Replicate"]))
                aboves = []
                for replicate in replicates:
                    select = df.loc[df["Replicate"] == replicate]
                    #print("biounit: ",unit, " fraction: ",fraction, " replicate: ",replicate)
                    series = select[x]
                    above = np.count_nonzero(series > value)
                    # aboves.append(above)
                    percentage = above/len(series)*100
                    aboves.append(percentage)
                dic[fraction] = np.array(aboves)
            maindics[unit] = dic
        return(maindics)

    def reformat_dic(self, above_threshold):
        """
        This reformats dictionary gotten through "above_threshold" function into a dataframe
        """
        f = []
        for item1 in above_threshold.keys():
            level1 = above_threshold[item1]
            for item2 in level1.keys():
                series = level1[item2]
                mean = np.mean(series)
                stdev = np.std(series)
                lis = [item1, item2, mean, stdev]
                f.append(lis)
        f = pd.DataFrame(f)
        f.columns = ["Biounit", "Fraction", "mean", "stdev"]
        return(f)

    def reformat_dataframe(self, fdf):
        """
        This reformats dataframe gotten through "reformat_dic" function into a new dataframe congrued for plotting

        Parameters
        ----------
        fdf : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        biounits = list(dict.fromkeys(fdf["Biounit"]))
        final = []
        for item in biounits:
            selected = fdf.loc[fdf["Biounit"] == item]

            number_m = float(
                selected.loc[selected["Fraction"] == "PM"]["mean"])
            number_sd = float(
                selected.loc[selected["Fraction"] == "PM"]["stdev"])

            s_m = float(selected.loc[selected["Fraction"] == "S"]["mean"])
            s_sd = float(selected.loc[selected["Fraction"] == "S"]["stdev"])
            m_m = float(selected.loc[selected["Fraction"] == "M"]["mean"])
            m_sd = float(selected.loc[selected["Fraction"] == "M"]["stdev"])

            # ENRICHMENT and DEPLETION FORMULAE
            #   ENRICHMENT = S / PM
            #   DEPLETION = PM / M
            enrichment_mean = s_m/number_m
            depletion_mean = number_m/m_m

            enrichment_std = poe_DIV(s_m, number_m, s_sd, number_sd)
            depletion_std = poe_DIV(number_m, m_m, number_sd, m_sd)

            part1 = [item, "Number/%", number_m, number_sd]
            part2 = [item, "Enrichment", enrichment_mean, enrichment_std]
            part3 = [item, "Depletion", depletion_mean, depletion_std]
            total = [part1, part2, part3]
            total = pd.DataFrame(total)
            total.columns = ["Biounit", "Type", "mean", "stdev"]

            final.append(total)
        final = pd.concat(final)
        return(final)

    def __init__(self, df, x, bt_dic):  # <-bt_dic - BIOUNIT THRESHOLD DIC
        """
        Initalizes the backend
        """
        create_bunit_frac(df)
        above_threshold = self.above_threshold(df, x, bt_dic)
        f = self.reformat_dic(above_threshold)
        result = self.reformat_dataframe(f)
        result.reset_index(inplace=True, drop=True)
        self.result = result


class Bootstrap_Backend():
    """
    This class contains functions to calculate N,E,D
    from Bootstraped at the end
    """

    def percentage_above(self, series, value):
        """
        Returns the percentage of data that are above given value
        """
        above = np.count_nonzero(series > value)
        percentage = above/len(series)*100
        return(percentage)

    def bootstrap(self, series, value, x,):
        """
        Bootstraps the series provided
        """
        iterations = self.iterations
        samplesize = self.samplesize
        per_samplesize = samplesize/100
        sample_size = int(len(series)*per_samplesize)
        percentages = []
        for i in range(iterations):
            resampled = resample(series, n_samples=sample_size, replace=False)
            per = self.percentage_above(resampled, value)
            percentages.append(per)
        percentages = np.array(percentages)
        return(percentages)

    def bootstrapping_amounts(self, data, x, bt_dic):
        """
        From given dataframe that has columns "Sample" with values in form of
        INP-X, S-X, PM-X where INP signifies input (unmarked cells), S signifies enriched cells,
        and PM signifies marked but un-enriched cells, and a given percentil data, returns
        bootstraped percentages of enriched cells (definition is given in functions "bootstrap" and "percentage_above")
        in the form of dictionary in the form of : BIOUNIT : [booted_input, booted_marked, booted_enriched,booted_depleted]
            where booted_* are pandas series of length 10000.

        Parameters
        ----------
        data : Pandas DataFrame with a column of "YEL-HLog" and "Sample". Sample column must have values in the form of:
            INP-X, S-X, PM-X where INP signifies input (unmarked cells), S signifies enriched cells,
        and PM signifies marked but un-enriched cells, AND X signifies "Biounit" (biological sample from which fractions are recorded)

        percentil : value to be passed to "bootstrap" and "percentage_above" functions.

        Returns
        -------
        Dictionary in the form of:
            BIOUNIT : [booted_input, booted_marked, booted_enriched]
            where booted_* are pandas series of length 10000.

        """

        ###BLOCK FOR CREATING BIOUNITS###
        create_bunit_frac(data)
        biounits = list(dict.fromkeys(data["Biounit"]))

        # SELECT BIOUNITS
        # THIS DICTIONARY IS OF THE FORM biounit: [boot_input,boot_pm,boot_sgonia] where boots are series
        biounit_dic = {}

        for biounit in biounits:
            select = data.loc[data["Biounit"] == biounit]

            # selecting partial dataframe
            only_input = select.loc[select["Fraction"] == "INP"]
            only_rich = select.loc[select["Fraction"] == "S"]
            only_dep = select.loc[select["Fraction"] == "M"]
            only_pm = select.loc[select["Fraction"] == "PM"]

            # selecting only X
            only_input = only_input[x]
            only_rich = only_rich[x]
            only_dep = only_dep[x]
            only_pm = only_pm[x]

            value = bt_dic[biounit]
            boot_inp = self.bootstrap(only_input, value, x)
            boot_rich = self.bootstrap(only_rich, value, x)
            boot_dep = self.bootstrap(only_dep, value, x)
            boot_pm = self.bootstrap(only_pm, value, x)

            biounit_dic[biounit] = [boot_inp, boot_pm, boot_rich, boot_dep]

        return(biounit_dic)

    def full_bootstraped_frame(self, biounit_dic):
        """
        Rewraps dictionary into a pandas dataframe

        """
        final = []
        for item in biounit_dic.keys():
            values = biounit_dic[item]
            inp = values[0]
            pm = values[1]
            s = values[2]
            m = values[3]

            # NUMBER
            number_m = pm.mean()
            number_sd = pm.std()
            part1 = [item, "Number/%", number_m, number_sd]

            # ENRICHMENT and DEPLETION FORMULAE
            #   ENRICHMENT = S / PM
            #   DEPLETION = PM / M
            # MEANS
            enrichment_mean = s.mean()/number_m
            depletion_mean = number_m/m.mean()
            # ERRORs
            enrichment_std = poe_DIV(s.mean(), pm.mean(), s.std(), pm.std())
            depletion_std = poe_DIV(pm.mean(), m.mean(), pm.std(), m.std())
            #print("s: ", s.std()," m: ",m.std()," pm:",pm.std())
            #print("enrich ",enrichment_std, " depletion ",depletion_std)

            part2 = [item, "Enrichment", enrichment_mean, enrichment_std]
            part3 = [item, "Depletion", depletion_mean, depletion_std]
            total = [part1, part2, part3]
            total = pd.DataFrame(total)
            total.columns = ["Biounit", "Type", "mean", "stdev"]
            final.append(total)

        final = pd.concat(final)
        final.reset_index(inplace=True, drop=True)
        return(final)

    def __init__(self, df, x, bt_dic, iterations, samplesize):  # <-bt_dic - BIOUNIT THRESHOLD DIC
        """Initializes the backend"""
        self.iterations = iterations
        self.samplesize = samplesize
        biounit_dic = self.bootstrapping_amounts(df, x, bt_dic)
        result = self.full_bootstraped_frame(biounit_dic)
        self.result = result


class EnrichmentToplevel():
    """
    Enrichment toplevel
    This toplevel contains several features:
        BioUnitFrames (each BUF has 4 Fraction Frames under it)
        Control Frame - which houses buttons to calculate our N,E,D
        Table Frame - which houses Table report of N,E,D
        Graph Frame - Which houses visualization of N, E, D

    """

    def load_btdata(self):
        """Creates a bt_dic -> dictionary of Biounit to Threshold"""
        bfe_part = self.bfe
        biounit_fractionfr = bfe_part.biounit_fractionfr
        bt_dic = {}  # <-BIOUNIT:THRESHOLD
        for item in biounit_fractionfr.keys():
            frframe = biounit_fractionfr[item]
            t = frframe.t
            bt_dic[item] = t
        self.bt_dic = bt_dic

    def calculate(self):
        """Calculates N,E,D and creates reports"""
        # BLOCK THAT CREATES FRAME IF ITS NOT CREATED
        try:
            self.tableframe
            self.graphframe
        except:
            self.tableframe = tk.Frame(self.master)
            self.tableframe.grid(row=2, column=3, sticky="n")
            self.graphframe = tk.Frame(self.master)
            self.graphframe.grid(row=4, column=0, sticky="n")
        # BLOCK THAT CHECKS FOR ITERATIONS
        iterations = self.iterations_entry.get()
        try:
            iterations = int(iterations)  # if integer, proceed
            if iterations < 1:  # checks that its a positive number
                self.calc.set("REPLICATE")
                self.iterations_entry.delete(0, "end")
        except:  # if not integer, modify - set to replicate and delete entry
            self.calc.set("REPLICATE")
            self.iterations_entry.delete(0, "end")
        # BLOCK THAT CHECKS FOR SAMPLESIZE PERCENTAGE
        samplesize = self.samplesize_entry.get()
        try:
            if "," in samplesize:
                samplesize = samplesize.replace(",", ".")
            samplesize = float(samplesize)
            if samplesize < 1 or samplesize >= 100:  # value from 0 to 99.9...
                print("out of bounds")
                self.calc.set("REPLICATE")
                self.samplesize_entry.delete(0, "end")
        except:
            self.calc.set("REPLICATE")
            self.samplesize_entry.delete(0, "end")

        # BLOCK THAT PASSES RELEVANT VARIABLES
        df = self.df
        x = self.x
        bt_dic = self.bt_dic

        # command={"REPLICATE":Replicate_Backend(df,x,bt_dic),"BOOTSTRAP":Bootstrap_Backend(df,x,bt_dic,iterations,samplesize)}
        # backend=command[self.calc.get()]

        if self.calc.get() == "REPLICATE":
            backend = Replicate_Backend(df, x, bt_dic)
        else:
            backend = Bootstrap_Backend(df, x, bt_dic, iterations, samplesize)

        # CREATE REPORT AND VISUALIZATION
        result = backend.result
        table_widget = Table(parent=self.tableframe,
                             dataframe=result, editable=False)
        table_widget.show()

        bcanvas = FigureCanvasTkAgg(
            barplot_ned(result), master=self.graphframe)
        bcanvas.draw()
        bcanvas.get_tk_widget().grid(row=0, column=0)
    def add_load_btbutton(self):
        
        bfe_part=self.bfe
        exp = bfe_part.explframe
        pos = exp.finalpos  # <-FINAL ROW POSITION OF TKINTER STUCT
        expframe = exp.btframe  # <-TKINTER STRUCT

        load_bt = tk.Button(master=expframe, bg="gainsboro",
                            text="LOAD", command=self.load_btdata)
        load_bt.grid(row=pos, column=0, columnspan=2, sticky="nsew")
        
    
    def __init__(self, df, x="YEL-HLog", y="FSC-HLog"):
        """Calls the TopLevel"""
        master = tk.Toplevel()
        master.title("Number, Enrichment, & Depletion Menu")
        self.df = df
        self.x = x
        self.master = master
        self.bt_dic = None  # Will later have biounit:threshold dictionary
        bfe_part = Biounit_Frames(self.master, self, df, x, y)  # <-BIOUNIT FRAME
        self.bfe = bfe_part  # <-HAS BIOUNIT, FRACTION, EXPLANATION frame
        exp = bfe_part.explframe
        pos = exp.finalpos  # <-FINAL ROW POSITION OF TKINTER STUCT
        expframe = exp.btframe  # <-TKINTER STRUCT

        load_bt = tk.Button(master=expframe, bg="gainsboro",
                            text="LOAD", command=self.load_btdata)
        load_bt.grid(row=pos, column=0, columnspan=2, sticky="nsew")

        controlframe = tk.Frame(master=master)
        # <-controling frame that has options for Calculation
        self.controlframe = controlframe
        # <-In line with Canvas frame
        controlframe.grid(row=2, column=2, sticky="n")

        self.calc = tk.StringVar()  # <-StringVar for the type of calculation

        tk.Label(master=self.controlframe, width=18, text="OPTION",
                 bg="gainsboro", relief="raised").grid(row=0, column=0)
        tk.Radiobutton(master=self.controlframe, indicatoron=0, width=18, value="REPLICATE",
                       text="REPLICATE", variable=self.calc).grid(row=1, column=0)
        tk.Radiobutton(master=self.controlframe, indicatoron=0, width=18, value="BOOTSTRAP",
                       text="BOOTSTRAP", variable=self.calc).grid(row=2, column=0)
        tk.Button(master=self.controlframe, bg="powder blue", width=18, text="CALCULATE",
                  command=self.calculate).grid(row=8, column=0)

        tk.Label(master=self.controlframe, width=14, text="ITERATIONS",
                 bg="gainsboro", relief="raised").grid(row=4, column=0)
        self.iterations_entry = tk.Entry(
            master=self.controlframe, width=14, justify="center")
        self.iterations_entry.grid(row=5, column=0)
        tk.Label(master=self.controlframe, width=14, text="SAMPLE SIZE/%",
                 bg="gainsboro", relief="raised").grid(row=6, column=0)
        self.samplesize_entry = tk.Entry(
            master=self.controlframe, width=14, justify="center")
        self.samplesize_entry.grid(row=7, column=0)


class XYSelectorTopLevel():
    """Tkinter toplevel here just to select X and Y variable"""

    def select_xy(self):
        """Finalizes X Y selection and self-destructs"""
        x = self.x.get()
        y = self.y.get()
        data = self.data
        create_bunit_frac(data)
        EnrichmentToplevel(data, x, y)

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
        tk.Button(master=self.master, text="LOAD", command=self.select_xy).grid(
            row=0, column=2, rowspan=2, sticky="nsew")
