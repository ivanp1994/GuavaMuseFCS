# -*- coding: utf-8 -*-
# pylint: disable=C0325
# pylint: disable=C0301
# pylint: disable=C0103
# pylint: disable=W0612
# pylint: disable=W0613
"""
Created on Tue Aug 31 12:32:18 2021
Added initial t setting as percentile of X column of INP Fraction

Added redundancy when data doesnt have Biounit or Fraction column
@author: ivanp
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
from sklearn.mixture import GaussianMixture as GMM
from pandastable import Table
from .supplemental import get_numerical, ModifiedOptionMenu
import scipy.stats as stats

# %%FUNCTIONS


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
    samples = list(dict.fromkeys(df["Sample"]))
    for item in samples:
        if "-" not in item:
            raise ValueError(f'Sample {item} is does not have "-" in it')
    biounits = [item[item.find("-")+1:] for item in samples]
    fractions = [item[:item.find("-")] for item in samples]

    d_fractions = dict(zip(samples, fractions))
    d_biounits = dict(zip(samples, biounits))
    df["Fraction"] = df["Sample"].map(d_fractions)
    df["Biounit"] = df["Sample"].map(d_biounits)
    df.reset_index(inplace=True, drop=True)
    return()


def replicate_measurement(data, x, bt_dictionary) -> dict:
    """
    Measures from replicates of a fraction of a given biounit


    Parameters
    ----------
    data : dataframe with biounit and fraction columns.
    x : column name.
    bt_dictionary : biounit to threshold dictionary.

    Returns
    -------
    Dictionary of the form:
        {
        BIOUNIT_1 : {Fraction_1 : percentage_above_threshold_in_fraction_1,
                     Fraction_2 : percentage_above_threshold_in_fraction_2},
        BIOUNIT_2:  {Fraction_1 : percentage_above_threshold_in_fraction_1,
                     Fraction_2 : percentage_above_threshold_in_fraction_2},

        }

    """
    biounits = list(bt_dictionary.keys())
    fractions = list(set(data.Fraction))
    biounit_fraction = {}
    for biounit in biounits:
        threshold = bt_dictionary[biounit]
        subset_bunit = data.loc[data.Biounit == biounit]
        fraction_measurement = {}
        for fraction in fractions:
            subset_fraction = subset_bunit.loc[subset_bunit.Fraction == fraction]
            replicates = list(set(subset_fraction.Replicate))
            measurements = []
            for replicate in replicates:
                subset_replicate = subset_fraction.loc[subset_fraction.Replicate == replicate]
                series = subset_replicate[x]
                above = np.count_nonzero(series > threshold)
                percentage = above/len(series)*100
                measurements.append(percentage)
                # print(f"{biounit=},{threshold=},{fraction=},{replicate=},{percentage=}")
            fraction_measurement[fraction] = measurements
        biounit_fraction[biounit] = fraction_measurement
    return(biounit_fraction)


def bootstrap_measurement(data, x, bt_dictionary, n_iters=500, per_sample=0.40):
    """
    Bootstraps (resamples) {per_sample} from a given fraction of a given biounit {n_iters} times to return measurement

    Parameters
    ----------
    data : dataframe with biounit and fraction columns.
    x : column name.
    bt_dictionary : biounit to threshold dictionary.
    n_iters : number of resamples
    per_sample : what percentage of sample to resample

    Returns
    -------
    Dictionary of the form:
        {
        BIOUNIT_1 : {Fraction_1 : percentage_above_threshold_in_fraction_1,
                     Fraction_2 : percentage_above_threshold_in_fraction_2},
        BIOUNIT_2:  {Fraction_1 : percentage_above_threshold_in_fraction_1,
                     Fraction_2 : percentage_above_threshold_in_fraction_2},
        }

    """

    def internal_bootstrap(series, threshold, n_iters, per_sample):
        """Quick resample and storage in a list {measurements}"""
        measurements = []
        sample_size = int(per_sample*len(series))
        for i in range(n_iters):
            resampled = resample(series, n_samples=sample_size, replace=False)
            above = np.count_nonzero(resampled > threshold)
            percentage = above/len(resampled)*100
            measurements.append(percentage)
        return(measurements)

    biounits = list(bt_dictionary.keys())
    fractions = list(set(data.Fraction))
    biounit_fraction = {}
    for biounit in biounits:
        threshold = bt_dictionary[biounit]
        subset_bunit = data.loc[data.Biounit == biounit]
        fraction_measurement = {}
        for fraction in fractions:
            subset_fraction = subset_bunit.loc[subset_bunit.Fraction == fraction]
            series = subset_fraction[x]
            fraction_measurement[fraction] = internal_bootstrap(
                series, threshold, n_iters, per_sample)
        biounit_fraction[biounit] = fraction_measurement
    return(biounit_fraction)


def poe_DIV_meanstd(series1, series2) -> tuple:
    """
    Propagation of error when dependent variable is calculated
    through division of elements of series1 over series2

    Order matters
    Parameters
    ----------
    series1 : first numpy array.
    series2 : second numpy array.

    Returns
    -------
    Tuple of ("mean","standard deviation")
    Values are floats rounded to 3, converted to strings for easier display
    """

    mean1 = np.mean(series1)
    mean2 = np.mean(series2)
    stdev1 = np.std(series1)
    stdev2 = np.std(series2)

    mean1 = np.mean(series1)
    mean2 = np.mean(series2)
    stdev1 = np.std(series1)
    stdev2 = np.std(series2)

    mean = mean1/mean2
    a = stdev1/mean1
    b = stdev2/mean2
    a = a*a
    b = b*b
    e = (a+b)**0.5
    sd = mean*e

    mean = str(round(mean, 3))
    sd = str(round(sd, 3))
    return(mean, sd)


def NED_calculation(provided_dictionary) -> pd.DataFrame:
    """
    NED = Number, Enrichment, Depletion


    Parameters
    ----------
    provided_dictionary : dictionary that functions "replicate_measurement" or "bootstrap_measurement" provide

    Returns
    -------
    Pandas DataFrame to display
    """
    biounits = list(provided_dictionary.keys())
    biounit_dictionary = {}
    for biounit in biounits:
        ned_dic = {}
        fraction_measure_dic = provided_dictionary[biounit]
        pm = np.array(fraction_measure_dic["PM"])
        ss = np.array(fraction_measure_dic["S"])
        mg = np.array(fraction_measure_dic["M"])

        number = (str(round(np.mean(pm), 3)), str(round(np.std(pm), 3)))
        enrichment = poe_DIV_meanstd(ss, pm)
        depletion = poe_DIV_meanstd(pm, mg)

        n_dis = " ± ".join(number)
        e_dis = " ± ".join(enrichment)
        d_dis = " ± ".join(depletion)

        ned_dic["Number"] = n_dis
        ned_dic["Enrichment"] = e_dis
        ned_dic["Depletion"] = d_dis
        biounit_dictionary[biounit] = ned_dic
    final_result = pd.DataFrame.from_dict(biounit_dictionary).T
    final_result.reset_index(inplace=True)

    return(final_result)


def get_appropriate_array(data, t, x):
    """GMM doesnt play nice for pandas series"""
    data = data.loc[data[x] > t]
    pandas_series = np.array(data.loc[data.Fraction == "S"][x])
    numpy_array = pandas_series.reshape(-1, 1)
    return(numpy_array)


def threshold_gainer(data, x, tolerance=0.001):
    """
    Write a big docu here, I'll forget
    Selecting only S fraction, and do a GMM
    Truncate ~3 stdevs until convergence
        this means that mean-3stdev is selected as threshold
        and everything below that threshold is removed
        and then do another GMM fitting
    Repeat until there is convergence:
        convergence is defined when ratio of old threshold and new threshold is
        within 1+- tolerance

    Returns a threshold
    Anything above that is considered to be potential sgonia

    Parameters
    ----------
    data : pandas dataframe.
    tolerance : TYPE, optional
        DESCRIPTION. The default is 0.001.
    x : column in data. The default is "YEL-HLog".

    Returns
    -------
    None.

    """

    def gaussian_mixture_workflow(data, t, x):
        """short function for getting univar KDE params"""
        gm = GMM(1)
        chi_array = get_appropriate_array(data, t, x)
        gm.fit(chi_array)
        mean = float(gm.means_)
        stdev = float(gm.covariances_)**0.5
        threshold = mean-2.5*stdev
        return(threshold)

    old_t = gaussian_mixture_workflow(data, 0, x)
    while True:
        new_t = gaussian_mixture_workflow(data, old_t, x)
        ratio = new_t/old_t
        if ratio < 1 + tolerance and ratio > 1 - tolerance:
            break
        old_t = new_t
    return(new_t)


# %% END OF FUNCTIONs


class BiounitsFrame():
    """
    Internal class for EnrichmentTopLevel
    Houses buttons to select {biounit} and {fraction} to display

    Method yield_btdictionary allows extraction of {biounit} : {threshold}
    """

    def __init__(self, master, data, x, y):
        self.data = data.copy()
        self.biounits = []
        self.biounit_fractionframe_dic = {}
        self.biounit_kdesgoniaframe_dic = {}
        self.biounit_selected = tk.StringVar()
        self.fraction_selected = tk.StringVar()
        self.canvas_frame = None
        self.kde_sgonia_frame = None
        #  Block to extract information about Biounit and Fractions
        if not hasattr(data, "Biounit"):
            create_bunit_frac(self.data)
        self.biounits = list(dict.fromkeys(self.data.Biounit))

        #  Frames for buttons and frame for canvas
        bt_biounit_frame = tk.Frame(master)  # <- Biounit
        bt_biounit_frame.pack(anchor="w")

        bt_fraction_frame = tk.Frame(master)  # <- Fraction
        bt_fraction_frame.pack(anchor="w")

        canvas_frame = tk.Frame(master)      # <- Canvas/Graphs
        self.canvas_frame = canvas_frame
        canvas_frame.pack()

        # <-Holding normalized S gonia frame (to be added)
        kde_sgonia_frame = tk.Frame(master)
        self.kde_sgonia_frame = kde_sgonia_frame
        kde_sgonia_frame.pack()

        #  Radiobuttons for both variables / Creation of FractionsFrame structure
        for biounit in self.biounits:
            fractions = self.data.loc[self.data.Biounit == biounit]["Fraction"]
            fractions = list(set(fractions))
            fractions.sort()
            if len(fractions) != 4:
                self.biounits.remove(biounit)
                continue

            # finding the initial threshold as 99th percentile of X column in INP Fraction
            biounit_data = self.data.loc[self.data.Biounit == biounit]
            input_data = biounit_data.loc[data.Fraction == "INP"]
            input_series = input_data[x]
            initial_t = np.percentile(input_series, 99)

            # create radiobuttons to control Biounit
            rb = tk.Radiobutton(master=bt_biounit_frame, indicatoron=0, width=20,
                                value=biounit, text=biounit, variable=self.biounit_selected)
            rb.pack(anchor="w", side="right")

            # creating a FractionsFrame #it's just created, not packed
            fractionsframe = FractionsFrame(frame=canvas_frame,
                                            data=self.data.loc[self.data.Biounit == biounit],
                                            fractions=fractions,
                                            x=x, y=y, initial_t=initial_t
                                            )
            self.biounit_fractionframe_dic[biounit] = fractionsframe
            # creating a SgoniaFrame
            sgoniaframe = SgoniaFrame(kde_sgonia_frame,
                                      data=self.data.loc[self.data.Biounit == biounit],
                                      x=x, initial_t=initial_t)
            self.biounit_kdesgoniaframe_dic[biounit] = sgoniaframe

        fractions = list(set(self.data.Fraction))
        fractions.sort()
        for fraction in fractions:
            rb = tk.Radiobutton(master=bt_fraction_frame, indicatoron=0, width=5,
                                value=fraction, text=fraction, variable=self.fraction_selected)
            rb.pack(anchor="w", side="left")
        #  Tracing variables/Setting initial
        self.fraction_selected.set(fractions[0])
        self.biounit_selected.set(self.biounits[0])

        self.biounit_selected.trace("w", self.show_graph)
        self.fraction_selected.trace("w", self.show_graph)

    def show_graph(self, *args):
        """Show selected graph"""
        # get what was selected
        selected_biounit = self.biounit_selected.get()
        selected_fraction = self.fraction_selected.get()

        # forget everything not shown
        self.forget_all_graphs()

        # select a widget to be shown ->scatter and hist
        sel_fram = self.biounit_fractionframe_dic[selected_biounit]
        sel_fram.show_fraction(selected_fraction)

        # select a widget to be shown ->kde sgonia
        sel_kdeframe = self.biounit_kdesgoniaframe_dic[selected_biounit]
        sel_kdeframe.pack()

    def forget_all_graphs(self):
        """Forget all displayed graphs"""
        fractionframes = list(self.biounit_fractionframe_dic.values())
        widgets = []
        for item in fractionframes:
            widgets += list(item.fraction_widget_dic.values())

        # to be added later
        sgoniaframes = list(self.biounit_kdesgoniaframe_dic.values())
        widgets2 = [item.widget for item in sgoniaframes]
        widgets = widgets+widgets2

        for widget in widgets:
            widget.pack_forget()

    def yield_btdictionary(self):
        """
        Returns a dictionary of the form {Biounit:Threshold}
        """
        dic = {}
        for biounit in self.biounits:
            sel_fram = self.biounit_fractionframe_dic[biounit]
            thresh = sel_fram.t
            dic[biounit] = thresh
        return(dic)


class FractionsFrame():
    """
    Internal class for EnrichmentTopLevel
    Has no buttons

    Each pair of {biounit}{fraction} has its own canvas in which two graphs
    are displayed - scatterplot of (x,y) and histogram (x) with density

    Each graph is clickable, and clicking the graph changes the placement of
    vertical line that functions as a divisor
    """

    def __init__(self, frame, data, fractions, x, y, initial_t):

        self.data = data
        self.x = x
        self.t = initial_t

        self.fraction_figure_dic = {}
        self.fraction_canvas_dic = {}
        self.fraction_widget_dic = {}
        self.fraction_textboxes = {}
        self.lines = []
        #  "private" variables
        axes = []
        props = dict(boxstyle="round", facecolor="wheat", alpha=0.9)
        # Create all figures/textboxs/update trackers
        for fraction in fractions:
            # %% Create all figures
            subset = data.loc[data.Fraction == fraction]
            figure = Figure((10, 5))

            sc = figure.add_subplot(121)
            ds = figure.add_subplot(122)

            sns.scatterplot(data=subset, x=x, y=y, ax=sc, s=1)
            sns.histplot(data=subset, x=x, ax=ds, stat="density")

            canvas = FigureCanvasTkAgg(figure, master=frame)
            widget = canvas.get_tk_widget()
            figure.subplots_adjust(bottom=0.200)

            # %% Create a textbox
            series = subset[x]
            left = np.count_nonzero(series < self.t)/len(series)*100
            left = round(left, 2)
            right = 100 - left
            right = round(right, 2)
            display = "Left:   "+str(left)+"%"+"\n"+"Right: "+str(right)+"%"
            textbox_1 = sc.text(0.70, 0.90, display,
                                transform=sc.transAxes, bbox=props)
            textbox_2 = ds.text(0.70, 0.90, display,
                                transform=ds.transAxes, bbox=props)

            # %% Update all dictionaries and lists
            self.fraction_figure_dic[fraction] = figure
            self.fraction_canvas_dic[fraction] = canvas
            self.fraction_widget_dic[fraction] = widget
            axes += [sc, ds]
            self.fraction_textboxes[fraction] = (textbox_1, textbox_2)
        # %% Finished creating
        # Create initial line(s) with default threshold of 1
        colors = matplotlib.rcParams["axes.prop_cycle"].by_key()["color"]
        self.lines = [ax.axvline(
            x=self.t, linewidth=3, color=colors[2]) for ax in axes]
        # Connect controling lines
        control_list = [figure.canvas.callbacks.connect(
            "button_press_event", self.replace_line) for figure in list(self.fraction_figure_dic.values())]

    def show_fraction(self, fraction):
        """
        Show the fraction
        This function must be called after widgets are forgot or graphs will be constantly shown
        """
        widget = self.fraction_widget_dic[fraction]
        widget.pack()

    def replace_line(self, event):
        """Manager for clicking the graph"""
        if event.inaxes is None:
            return()
        self.t = event.xdata
        _private = [line.set_xdata(self.t) for line in self.lines]
        self.update_textboxes()
        self.redraw_canvases()

    def redraw_canvases(self):
        """Redraw of all canvases to update changes in the line positioning"""
        canvases = list(self.fraction_canvas_dic.values())
        for canvas in canvases:
            canvas.draw()

    def update_textboxes(self):
        """Updating textboxes that show left to right"""
        for fraction in self.fraction_textboxes:
            subset = self.data.loc[self.data["Fraction"] == fraction]
            series = subset[self.x]
            left = np.count_nonzero(series < self.t)/len(series)*100
            left = round(left, 2)
            right = 100-left
            right = round(right, 2)
            display = "Left:   "+str(left)+"%"+"\n"+"Right: "+str(right)+"%"

            textboxes = self.fraction_textboxes[fraction]
            textboxes[0].set_text(display)
            textboxes[1].set_text(display)


class InformationFrame():
    """
    Internal class for EnrichmentTopLevel
    It's just used to display {biounit}:{threshold} '
    """

    def __init__(self, master, bt_dictionary):
        self.master = master
        self.biounit_label_dic = {}

        for biounit in bt_dictionary.keys():
            label = tk.Label(master=self.master, text="", relief="raised")
            label.pack(anchor="w", expand=True, fill="both")
            self.biounit_label_dic[biounit] = label

        self.update(bt_dictionary)

    def update(self, bt_dictionary):
        """Update the info frame"""
        for bunit in bt_dictionary.keys():
            threshold = round(bt_dictionary[bunit], 3)
            display = f"{bunit} : {threshold}"
            label = self.biounit_label_dic[bunit]
            label["text"] = display


class SgoniaFrame():
    """
    Internal class for EnrichmentTopLevel
    Has no buttons

    This Frame houses a univariate Gaussian of "S" Fraction for X column
    The S fraction is first processed by "theshold_gainer" function that removes
    smaller, left peak from dataset

    Then Normal distribution is drawn, and enrichment_threshold is plotted as a part
    of the Normal distribution
    """

    def __init__(self, frame, data, x, initial_t):
        self.data = data
        self.x = x
        self.t = initial_t
        self.figure = Figure((10, 5))
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=frame)
        self.widget = self.canvas.get_tk_widget()
        self.mean = None
        self.stdev = None

        # beautifying ax a bit
        biounit = list(set(self.data.Biounit))[0]
        self.ax.set_title(
            f"Univariate Gaussian density plot for S fraction of {biounit}")
        self.ax.set_xlabel(x)
        self.figure.subplots_adjust(bottom=0.150)

        # do the GMM stuff
        sgonia_t = threshold_gainer(self.data, self.x)
        # threshold_gainer is a function for estimating GMM of Sgonia
        sgonia_df = self.data.loc[self.data.Fraction == "S"]
        sgonia = sgonia_df.loc[sgonia_df[x] > sgonia_t]
        chi_array = get_appropriate_array(sgonia, 0, x)

        # estimate the Sgonial GMM
        gm = GMM(1)
        gm.fit(chi_array)
        self.mean = float(gm.means_)
        self.stdev = float(gm.covariances_)**0.5
        # plotting
        mean = self.mean
        stdev = self.stdev

        # <-this will plot entire curve
        x = np.linspace(mean - 3*stdev, mean + 3*stdev, 100)
        # <-represents a part until enrichment_t
        px = np.arange(mean-3*stdev, self.t, self.t/100)
        # <- normal distribution by estimated parameters
        iq = stats.norm(mean, stdev)
        # <- Integral of -INF to self.t of GMM
        uncertain_perc = round(100*iq.cdf(self.t), 2)

        self.ax.plot(x, stats.norm.pdf(x, mean, stdev))  # <- plot a curve
        # fill between and add text
        # <- this will be stored in ax.collections
        self.ax.fill_between(px, iq.pdf(px), color="purple")
        props = dict(boxstyle="round", facecolor="wheat", alpha=0.9)
        display = f"The purple part is {uncertain_perc} %"
        self.ax.text(0.70, 0.90, display, transform=self.ax.transAxes,
                     bbox=props)  # <- this will be stored in ax.texts

    def update_kdesgonia_plot(self, new_t):
        """updates kdesgonia plot for a new threshold"""
        ax = self.ax
        mean = self.mean
        stdev = self.stdev

        ax.collections.pop()  # <-this removes prior fill

        # <-represents a part until enrichment_t
        px = np.arange(mean-3*stdev, new_t, new_t/100)
        iq = stats.norm(mean, stdev)
        # <- this will be stored in ax.collections
        ax.fill_between(px, iq.pdf(px), color="purple")

        uncertain_perc = round(100*iq.cdf(new_t), 2)
        display = f"The purple part is {uncertain_perc} %"
        ax.texts[0].set_text(display)
        self.canvas.draw()

    def pack(self):
        """forget it, its china town"""
        self.widget.pack()


class EnrichmentTopLevel():
    """TopLevel that houses all Enrichment structures"""

    def __init__(self, data, x="YEL-HLog", y="FSC-HLog"):

        # plt.style.use("ggplot")
        # plt.style.use("tableau-colorblind10")
        plt.style.use("fivethirtyeight")  # <-This one proved the best
        # plt.style.use("seaborn-darkgrid")

        self.master = tk.Toplevel()
        self.x = x
        self.data = data

        self.biounits_structure = None  # <-BiounitsFrame class
        self.information_structure = None  # <-InformationFrame class
        self.bt_dictionary = {}  # <-{Biounit : Threshold}
        self.backend_result = None  # <- displaying result of NED calculation

        self.master.title("Number, Enrichment, & Depletion Menu")

        # Fixing lack of "Biounit" and "Fraction" column
        if not hasattr(self.data, "Biounit"):
            try:
                create_bunit_frac(self.data)
            except ValueError:
                _faulty_samples = [item for item in list(
                    set(data.Sample)) if "-" not in item]
                raise ValueError(
                    f'The following samples do not have "-": \n {_faulty_samples}')

        # Create a BiounitFrame -> stores Graphs
        biounits_frame = tk.Frame(master=self.master)
        biounits_frame.pack(side="left", anchor="nw")
        self.biounits_structure = BiounitsFrame(biounits_frame, data, x, y)
        self.bt_dictionary = self.biounits_structure.yield_btdictionary()

        # Create InformationFrame -> displays dictionary
        info_fr = tk.Frame(master=self.master)
        info_fr.pack(side="left", anchor="n")
        tk.Label(master=info_fr, text="").pack(
            anchor="w", expand=True, fill="both")
        tk.Label(master=info_fr, text="").pack(
            anchor="w", expand=True, fill="both")
        tk.Label(master=info_fr, text="").pack(
            anchor="w", expand=True, fill="both")
        self.information_structure = InformationFrame(
            info_fr, self.bt_dictionary)

        # Connect Biounit/Fraction variables to updating bt_dictionary
        self.biounits_structure.fraction_selected.trace(
            "w", self.update_btdictionary)
        self.biounits_structure.biounit_selected.trace(
            "w", self.update_btdictionary)
        # but I really want to connect update to click
        # to do that I need to extract! all figures first
        figures = []
        biounits = self.biounits_structure.biounits
        for biounit in biounits:
            frfrstr = self.biounits_structure.biounit_fractionframe_dic[biounit]
            figs = list(frfrstr.fraction_figure_dic.values())
            figures += figs
        control_list = [figure.canvas.callbacks.connect(
            "button_press_event", self.update_btdictionary) for figure in figures]
        # Adding option for backend

        tk.Button(master=info_fr, text="Replicate-based", width=20,
                  command=self.replicate_backend).pack()
        tk.Button(master=info_fr, text="Bootstrap-based", width=20,
                  command=self.bootstrap_backend).pack()

    def update_btdictionary(self, *args):
        """updates the {biounit}:{threshold} dictionary"""
        self.bt_dictionary = self.biounits_structure.yield_btdictionary()
        # updating information presentation
        self.information_structure.update(self.bt_dictionary)
        # updating kde plot
        # {biounit : Sgoniaframe}
        _dic = self.biounits_structure.biounit_kdesgoniaframe_dic
        for biounit in self.bt_dictionary.keys():
            new_t = self.bt_dictionary[biounit]
            sgoniaframe = _dic[biounit]
            sgoniaframe.update_kdesgonia_plot(new_t)

    def replicate_backend(self):
        """calculations according to repeated measurements"""
        x = self.x
        data = self.data
        bt_dictionary = self.bt_dictionary
        dictionary = replicate_measurement(data, x, bt_dictionary)
        dataframe = NED_calculation(dictionary)

        if self.backend_result is None:
            self.create_backend_display(dataframe)
        else:
            self.update_backend_display(dataframe)

    def bootstrap_backend(self):
        """calculations according to bootstrapped measurements"""
        x = self.x
        data = self.data
        bt_dictionary = self.bt_dictionary
        dictionary = bootstrap_measurement(data, x, bt_dictionary)
        dataframe = NED_calculation(dictionary)

        if self.backend_result is None:
            self.create_backend_display(dataframe)
        else:
            self.update_backend_display(dataframe)

    def create_backend_display(self, dataframe):
        """Create backend display"""
        backendres_fr = tk.Frame(master=self.master)
        backendres_fr.pack(side="right", anchor="nw", fill="x", expand=True)
        self.backend_result = Table(parent=backendres_fr, dataframe=dataframe)
        self.backend_result.show()

    def update_backend_display(self, dataframe):
        """Update backend display"""
        self.backend_result.model.df = dataframe
        self.backend_result.redraw()


class XYSelectorTopLevel():
    """Tkinter toplevel here just to select X and Y variable"""

    def select_xy(self):
        """Finalizes X Y selection and self-destructs"""
        x = self.x.get()
        y = self.y.get()
        data = self.data
        create_bunit_frac(data)
        self.master.destroy()
        EnrichmentTopLevel(data, x, y)

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
