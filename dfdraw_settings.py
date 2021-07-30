# -*- coding: utf-8 -*-
# pylint: disable=C0325
# pylint: disable=C0103
# pylint: disable=W0231
# pylint: disable=C0301
# pylint: disable=R0902


"""
@author = Ivan Pokrovac
pylint global evaluation = 9.85/10
"""
import tkinter as tk
import numpy as np
from .supplemental import ModifiedOptionMenu, ModifiedSlider


class commonRelPlot():
    """
    Main class for settings of Relationship settings
    This class is the one from which all other classes inherit the most common elements
    All classes must start with "self.common_options()
    function and end with self.place_menus() function"
    """

    def __init__(self):
        """Just for documentation"""
        self.frame = None
        self.master = None
        self.numerical = None
        self.categorical = None
        # Options
        self.hueOption = None  # 1 #
        self.columnOption = None  # 2 #
        self.rowOption = None  # 3 #
        self.columnWrap = None  # 4 #
        self.legendOption = None  # 5 #
        self.styleOption = None  # 6 #
        self.markerOption = None  # 7 #
        self.optionMenus = None  # 8 #

    def common_yield(self):
        """
        Common yield returns dictionary called values that has following:
            HUE, COL, ROW, COL_WRAP
        """

        values = {"hue": self.hueOption.variable.get(),
                  "col": self.columnOption.variable.get(),
                  "row": self.rowOption.variable.get()}

        try:
            values["col_wrap"] = self.columnWrap.variable.get()
        except:
            values["col_wrap"] = None

        if values["col_wrap"] is not None and values["row"] != "None":
            values["col_wrap"] = None
            self.columnWrap.variable.set("None")

        return(values)

    def place_frame(self, r, c):
        """Places frame on R and C"""
        self.frame.grid(row=r, column=c)

    def place_menus(self):
        """Places menus"""
        n = 0
        for item in self.optionMenus:
            item.place(r=n, c=0)
            n = n+1

    def common_options(self, master, numerical, categorical):
        """Options common to all types of RelPlot"""
        self.frame = tk.Frame(master)
        self.master = master
        self.numerical = numerical
        self.categorical = categorical

        c_variables = list(categorical.columns)
        c_variables.insert(0, None)

        c_wraps = list(range(1, len(c_variables)))
        c_wraps.insert(0, None)

        # self.c_variables = c_variables  # categorical variables # do I use this for anything???

        hueOption = ModifiedOptionMenu(
            self.frame, label="HUE", options=c_variables, typevar=None)

        columnOption = ModifiedOptionMenu(
            self.frame, label="COLUMN", options=c_variables, typevar=None)

        rowOption = ModifiedOptionMenu(
            self.frame, label="ROW", options=c_variables, typevar=None)

        columnWrap = ModifiedOptionMenu(
            self.frame, label="COL-WRAP", options=c_wraps, typevar="int")

        legendOption = ModifiedOptionMenu(self.frame, label="LEGEND", options=[
                                          "auto", "brief", "full"], typevar=None)

        styleOption = ModifiedOptionMenu(
            self.frame, label="STYLE", options=c_variables, typevar=None)

        markerOption = ModifiedOptionMenu(self.frame, label="MARKER", options=[
                                          None, "True"], typevar=None)

        self.hueOption = hueOption  # 1#
        self.columnOption = columnOption  # 2#
        self.rowOption = rowOption  # 3#
        self.columnWrap = columnWrap  # 4#
        self.legendOption = legendOption  # 5#
        self.styleOption = styleOption  # 6#
        self.markerOption = markerOption  # 7#
        self.optionMenus = [self.hueOption, self.columnOption, self.rowOption, self.columnWrap,
                            self.legendOption, self.styleOption, self.markerOption]


class ScatterFrameSettings(commonRelPlot):
    """Scatterplot settings"""

    def yield_value_dictionary(self):
        """
        Yields selected settings in the form of dictionary
        """
        values = self.common_yield()
        values["legend"] = self.legendOption.variable.get()
        values["style"] = self.styleOption.variable.get()
        values["dotsize"] = self.dotSize.variable.get()

        # BLOCK TO TRANSFER marker FROM STR TO BOOL
        if self.markerOption.variable.get() == "True":
            values["marker"] = True
        else:
            values["marker"] = self.markerOption.variable.get()

        return(values)

    def __init__(self, master, numerical, categorical):
        self.common_options(master, numerical, categorical)
        dotSize = ModifiedSlider(self.frame, label="DOT SIZE")
        self.dotSize = dotSize
        self.optionMenus.append(self.dotSize)
        self.place_menus()


class LineFrameSettings(commonRelPlot):
    """Lineplot settings"""

    def yield_value_dictionary(self):
        """
        Yields selected settings in the form of dictionary
        """
        values = self.common_yield()
        values["legend"] = self.legendOption.variable.get()
        values["style"] = self.styleOption.variable.get()
        # BLOCK TO TRANSFER marker FROM STR TO BOOL
        if self.markerOption.variable.get() == "True":
            values["marker"] = True
        else:
            values["marker"] = self.markerOption.variable.get()
        values["dashes"] = self.dashesOption.variable.get()
        # BLOCK TO CONVERT CONFIDENCE INTERVAL TO INT, IF POSSIBLE
        try:
            confin = int(self.ciOption.variable.get())
        except:
            confin = self.ciOption.variable.get()
        values["ci"] = confin
        values["estimator"] = self.estimatorOption.variable.get()
        estimator_dic = {None: None,
                         "mean": np.mean,
                         "sum": np.sum,
                         "min": np.min,
                         "max": np.max,
                         "median": np.median}
        if values["estimator"] is not None:
            values["estimator"] = estimator_dic[values["estimator"]]
        return(values)

    def __init__(self, master, numerical, categorical):
        self.common_options(master, numerical, categorical)
        estOptions = [None, "mean", "sum", "min", "max", "median"]
        # ESTIMATOR OPTIONS UPDATE ACCORDING TO
        estimatorOption = ModifiedOptionMenu(
            self.frame, label="ESTIMATOR", options=estOptions, typevar=None)
        self.estimatorOption = estimatorOption
        self.optionMenus.append(self.estimatorOption)

        dashesOption = ModifiedOptionMenu(self.frame, label="DASHES", options=[
                                          False, True], typevar="bool")
        self.dashesOption = dashesOption
        self.optionMenus.append(self.dashesOption)

        ciOption = ModifiedOptionMenu(self.frame, label="CONF.INTERVAL", options=[
                                      None, "sd", "95", "68", "34"], typevar=None)
        self.ciOption = ciOption
        self.ciOption.variable.set("95")
        self.optionMenus.append(self.ciOption)

        self.place_menus()
### RELPLOT SETTINGS ###

### DISPLOT SETTINGS ###


class commonDisPlot():
    """
    Main class for settings of Displot settings

    This class is the one from which all other classes inherit the most common elements

    All classes must start with "self.common_options() function
    and end with self.place_menus() function"
    """

    def __init__(self):
        """Just for documentation"""
        self.frame = None
        self.master = None
        self.numerical = None
        self.categorical = None
        # Options
        self.hueOption = None  # 1 #
        self.columnOption = None  # 2 #
        self.rowOption = None  # 3 #
        self.columnWrap = None  # 4 #
        self.legendOption = None  # 5 #
        self.cumulativeOption = None  # 6 #
        self.optionMenus = None  # 7 #

    def common_yield(self):
        """
        Common yield returns dictionary called values that has following:
            HUE, COL, ROW, COL_WRAP
        """
        values = {"hue": self.hueOption.variable.get(),
                  "col": self.columnOption.variable.get(),
                  "row": self.rowOption.variable.get()}
        try:
            values["col_wrap"] = self.columnWrap.variable.get()
        except:
            values["col_wrap"] = None
        if values["col_wrap"] is not None and values["row"] != "None":
            values["col_wrap"] = None
            self.columnWrap.variable.set("None")

        values["legend"] = self.legendOption.variable.get()
        values["cumulative"] = self.cumulativeOption.variable.get()

        return(values)

    def place_frame(self, r, c):
        """ Places frame on R and C """
        self.frame.grid(row=r, column=c)

    def place_menus(self):
        """ Places menus"""
        n = 0
        for item in self.optionMenus:
            item.place(r=n, c=0)
            n = n+1

    def common_options(self, master, numerical, categorical):
        """Options common to all types of DisPlot"""
        self.frame = tk.Frame(master)
        self.master = master
        self.numerical = numerical
        self.categorical = categorical

        c_variables = list(categorical.columns)
        c_variables.insert(0, None)

        c_wraps = list(range(1, len(c_variables)))
        c_wraps.insert(0, None)

        # self.c_variables = c_variables  # categorical variables

        hueOption = ModifiedOptionMenu(
            self.frame, label="HUE", options=c_variables, typevar=None)

        columnOption = ModifiedOptionMenu(
            self.frame, label="COLUMN", options=c_variables, typevar=None)

        rowOption = ModifiedOptionMenu(
            self.frame, label="ROW", options=c_variables, typevar=None)

        columnWrap = ModifiedOptionMenu(
            self.frame, label="COL-WRAP", options=c_wraps, typevar="int")

        legendOption = ModifiedOptionMenu(self.frame, label="LEGEND", options=[
                                          True, False], typevar="bool")

        cumulativeOption = ModifiedOptionMenu(self.frame, "CUMULATIVE", options=[
                                              False, True], typevar="bool")

        self.hueOption = hueOption  # 1#
        self.columnOption = columnOption  # 2#
        self.rowOption = rowOption  # 3#
        self.columnWrap = columnWrap  # 4#
        self.legendOption = legendOption  # 5#
        self.cumulativeOption = cumulativeOption  # 6#

        self.optionMenus = [self.hueOption, self.columnOption, self.rowOption, self.columnWrap,
                            self.legendOption, self.cumulativeOption]


class HistogramFrameSettings(commonDisPlot):
    """Histogram settings"""

    def yield_value_dictionary(self):
        """
        Yields selected settings in the form of dictionary
        """
        values = self.common_yield()
        values["bins"] = self.binsOption.variable.get()
        values["stat"] = self.statOption.variable.get()
        values["element"] = self.elementOption.variable.get()
        values["multiple"] = self.multipleOption.variable.get()
        values["discrete"] = self.discreteOption.variable.get()
        return(values)

    def __init__(self, master, numerical, categorical):
        self.common_options(master, numerical, categorical)

        binOpt = ["auto", "fd", "doane", "scott",
                  "stone", "rice", "sturges", "sqrt"]
        binsOption = ModifiedOptionMenu(
            self.frame, "BINS", options=binOpt, typevar=None)
        self.binsOption = binsOption
        self.optionMenus.append(binsOption)

        stopt = ["count", "frequency", "density", "probability"]
        statOption = ModifiedOptionMenu(
            self.frame, "STAT", options=stopt, typevar=None)
        self.statOption = statOption
        self.optionMenus.append(statOption)

        elopt = ["bars", "step", "poly"]
        elementOption = ModifiedOptionMenu(
            self.frame, "ELEMENT", options=elopt, typevar=None)
        self.elementOption = elementOption
        self.optionMenus.append(elementOption)

        mulopt = ["layer", "dodge", "stack", "fill"]
        multipleOption = ModifiedOptionMenu(
            self.frame, "MULTIPLE", options=mulopt, typevar=None)
        self.multipleOption = multipleOption
        self.optionMenus.append(multipleOption)

        discreteOption = ModifiedOptionMenu(self.frame, "DISCRETE", options=[
                                            False, True], typevar="bool")
        self.discreteOption = discreteOption
        self.optionMenus.append(discreteOption)

        self.place_menus()


class KDEFrameSettings(commonDisPlot):
    """Kernel Density Estimator (density) plot settings"""

    def yield_value_dictionary(self):
        """
        Yields selected settings in the form of dictionary
        """
        values = self.common_yield()
        values["multiple"] = self.multipleOption.variable.get()
        values["bw_method"] = self.bwmethodOption.variable.get()
        values["bw_adjust"] = self.bwadjustOption.variable.get()
        values["levels"] = self.levelsOption.variable.get()
        values["common_norm"] = self.commonnormOption.variable.get()
        values["common_grid"] = self.commongridOption.variable.get()

        return(values)

    def __init__(self, master, numerical, categorical):
        self.common_options(master, numerical, categorical)

        multipleOption = ModifiedOptionMenu(self.frame, "MULTIPLE", options=[
                                            "layer", "stack", "fill"], typevar=None)
        self.multipleOption = multipleOption
        self.optionMenus.append(multipleOption)

        bwmethodOption = ModifiedOptionMenu(self.frame, label="BW Method", options=[
                                            "scott", "silverman"], typevar=None)
        self.bwmethodOption = bwmethodOption
        self.optionMenus.append(bwmethodOption)

        bwadjopt = [0.1, 0.25, 0.5, 0.75, 1, 2, 4, 10, 20, 40, 80, 100]
        bwadjustOption = ModifiedOptionMenu(
            self.frame, label="BW Adjust", options=bwadjopt, typevar="float")
        bwadjustOption.variable.set(1)
        self.bwadjustOption = bwadjustOption
        self.optionMenus.append(bwadjustOption)

        levelsOption = ModifiedOptionMenu(
            self.frame, label="Levels", options=range(1, 20), typevar="int")
        levelsOption.variable.set(10)
        self.levelsOption = levelsOption
        self.optionMenus.append(levelsOption)

        commonnormOption = ModifiedOptionMenu(
            self.frame, label="JOINT NORMALIZATION", options=[True, False], typevar="bool")
        self.commonnormOption = commonnormOption
        self.optionMenus.append(commonnormOption)

        commongridOption = ModifiedOptionMenu(self.frame, label="JOINT GRID", options=[
                                              True, False], typevar="bool")
        self.commongridOption = commongridOption
        self.optionMenus.append(commongridOption)

        self.place_menus()


class ECDFFrameSettings(commonDisPlot):
    """Empirical Cumulative Density Function plot settings"""

    def yield_value_dictionary(self):
        """
        Yields selected settings in the form of dictionary
        """
        values = self.common_yield()
        values["stat"] = self.statOption.variable.get()
        values["complementary"] = self.compOption.variable.get()
        return(values)

    def __init__(self, master, numerical, categorical):
        self.common_options(master, numerical, categorical)

        statOption = ModifiedOptionMenu(self.frame, label="STAT", options=[
                                        "proportion", "count"], typevar=None)
        self.statOption = statOption
        self.optionMenus.append(statOption)

        compOption = ModifiedOptionMenu(self.frame, label="COMPLEMENTARY", options=[
                                        False, True], typevar="bool")
        self.compOption = compOption
        self.optionMenus.append(compOption)

        self.optionMenus.remove(self.cumulativeOption)  # why is this here
        self.place_menus()

### DISPLOT SETTINGS ###
# CATPLOT SETTINGS ###3


class commonCatPlot():
    """
    Main class for settings of Catplot settings

    This class is the one from which all other classes inherit the most common elements

    All classes must start with "self.common_options() function and end with self.place_menus() function"
    """

    def __init__(self):
        """Just for documentation"""
        self.frame = None
        self.master = None
        self.numerical = None
        self.categorical = None
        # Options
        self.hueOption = None  # 1 #
        self.columnOption = None  # 2 #
        self.rowOption = None  # 3 #
        self.columnWrap = None  # 4 #
        self.legendOption = None  # 5 #
        self.optionMenus = None  # 6 #

    def common_yield(self):
        """
        Common yield returns dictionary called values that has following:
            HUE, COL, ROW, COL_WRAP
        """
        values = {"hue": self.hueOption.variable.get(),
                  "col": self.columnOption.variable.get(),
                  "row": self.rowOption.variable.get(),
                  "legend": self.legendOption.variable.get()}
        try:
            values["col_wrap"] = self.columnWrap.variable.get()
        except:
            values["col_wrap"] = None
        if values["col_wrap"] is not None and values["row"] != "None":
            values["col_wrap"] = None
            self.columnWrap.variable.set("None")
        return(values)

    def place_frame(self, r, c):
        """ Places frame on R and C """
        self.frame.grid(row=r, column=c)

    def place_menus(self):
        """Places menus"""
        n = 0
        for item in self.optionMenus:
            item.place(r=n, c=0)
            n = n+1

    def common_options(self, master, numerical, categorical):
        """Options common to all types of CatPlot"""
        self.frame = tk.Frame(master)
        self.master = master
        self.numerical = numerical
        self.categorical = categorical

        c_variables = list(categorical.columns)
        c_variables.insert(0, None)

        c_wraps = list(range(1, len(c_variables)))
        c_wraps.insert(0, None)

        hueOption = ModifiedOptionMenu(
            self.frame, label="HUE", options=c_variables, typevar=None)

        columnOption = ModifiedOptionMenu(
            self.frame, label="COLUMN", options=c_variables, typevar=None)

        rowOption = ModifiedOptionMenu(
            self.frame, label="ROW", options=c_variables, typevar=None)

        columnWrap = ModifiedOptionMenu(
            self.frame, label="COL-WRAP", options=c_wraps, typevar="int")

        legendOption = ModifiedOptionMenu(self.frame, label="LEGEND", options=[
                                          True, False], typevar="bool")

        self.hueOption = hueOption  # 1#
        self.columnOption = columnOption  # 2#
        self.rowOption = rowOption  # 3#
        self.columnWrap = columnWrap  # 4#
        self.legendOption = legendOption  # 5#

        self.optionMenus = [self.hueOption, self.columnOption, self.rowOption, self.columnWrap,
                            self.legendOption]


class BoxSwarmFrameSettings(commonCatPlot):
    """Boxplot settings"""

    def yield_value_dictionary(self):
        """
        Yields selected settings in the form of dictionary
        """
        values = self.common_yield()
        return(values)

    def __init__(self, master, numerical, categorical):
        self.common_options(master, numerical, categorical)
        self.place_menus()


class StripFrameSettings(commonCatPlot):
    """Strip plot settings"""

    def yield_value_dictionary(self):
        """
        Yields selected settings in the form of dictionary
        """
        values = self.common_yield()
        values["jitter"] = self.jitterOption.variable.get()
        return(values)

    def __init__(self, master, numerical, categorical):
        self.common_options(master, numerical, categorical)

        jitterOption = ModifiedOptionMenu(self.frame, label="JITTER", options=[
                                          False, True], typevar="bool")
        self.jitterOption = jitterOption
        self.optionMenus.append(jitterOption)

        self.place_menus()


class ViolinFrameSettings(commonCatPlot):
    """Violin plot settings"""

    def yield_value_dictionary(self):
        """
        Yields selected settings in the form of dictionary
        """
        values = self.common_yield()
        values["bw"] = self.bwmethodOption.variable.get()
        values["scale"] = self.scaleOption.variable.get()
        values["inner"] = self.innerOption.variable.get()
        return(values)

    def __init__(self, master, numerical, categorical):
        self.common_options(master, numerical, categorical)

        bwmethodOption = ModifiedOptionMenu(self.frame, label="BW Method", options=[
                                            "scott", "silverman"], typevar=None)
        self.bwmethodOption = bwmethodOption
        self.optionMenus.append(bwmethodOption)

        scaleOption = ModifiedOptionMenu(self.frame, label="SCALE", options=[
                                         "area", "count", "width"], typevar=None)
        self.scaleOption = scaleOption
        self.optionMenus.append(scaleOption)

        innerOption = ModifiedOptionMenu(self.frame, label="INNER", options=[
                                         "box", "quartile", "point", "stick", None], typevar=None)
        self.innerOption = innerOption
        self.optionMenus.append(innerOption)

        self.place_menus()


class BoxenFrameSettings(commonCatPlot):
    """Boxen plot settings"""

    def yield_value_dictionary(self):
        """
        Yields selected settings in the form of dictionary
        """
        values = self.common_yield()

        values["scale"] = self.scaleOption.variable.get()
        values["k_depth"] = self.kdepthOption.variable.get()
        values["outlier_prop"] = self.outlierpropOption.variable.get()
        values["trust_alpha"] = self.trustalphaOption.variable.get()
        return(values)

    def __init__(self, master, numerical, categorical):
        self.common_options(master, numerical, categorical)

        kdepthOption = ModifiedOptionMenu(self.frame, label="K DEPTH", options=[
                                          "tukey", "proportion", "trustworthy", "full"], typevar=None)
        self.kdepthOption = kdepthOption
        self.optionMenus.append(kdepthOption)

        scaleOption = ModifiedOptionMenu(self.frame, label="SCALE", options=[
                                         "exponential", "linear", "area"], typevar=None)
        self.scaleOption = scaleOption
        self.optionMenus.append(scaleOption)

        ranges = [x/100 for x in range(5, 100, 5)]
        ranges.append(0.99)

        outlierpropOption = ModifiedOptionMenu(
            self.frame, label="OUTLIER PROP", options=ranges, typevar="float")
        self.outlierpropOption = outlierpropOption
        self.optionMenus.append(outlierpropOption)

        trustalphaOption = ModifiedOptionMenu(
            self.frame, label="CONFIDENCE LEVEL", options=ranges, typevar="float")
        trustalphaOption.variable.set(0.95)
        self.trustalphaOption = trustalphaOption
        self.optionMenus.append(trustalphaOption)

        self.place_menus()


class BarFrameSettings(commonCatPlot):
    """Barplot settings"""

    def yield_value_dictionary(self):
        """
        Yields selected settings in the form of dictionary
        """
        values = self.common_yield()
        values["dashes"] = self.dashesOption.variable.get()
        # BLOCK TO CONVERT CONFIDENCE INTERVAL TO INT, IF POSSIBLE
        try:
            confin = int(self.ciOption.variable.get())
        except:
            confin = self.ciOption.variable.get()

        values["ci"] = confin
        values["estimator"] = self.estimatorOption.variable.get()
        estimator_dic = {None: None,
                         "mean": np.mean,
                         "sum": np.sum,
                         "min": np.min,
                         "max": np.max,
                         "median": np.median}

        values["estimator"] = estimator_dic[values["estimator"]]
        return(values)

    def __init__(self, master, numerical, categorical):
        self.common_options(master, numerical, categorical)

        estimatorOption = ModifiedOptionMenu(self.frame, label="ESTIMATOR", options=[
                                             "mean", "sum", "min", "max", "median"], typevar=None)  # ESTIMATOR OPTIONS UPDATE ACCORDING TO
        self.estimatorOption = estimatorOption
        self.optionMenus.append(self.estimatorOption)

        dashesOption = ModifiedOptionMenu(self.frame, label="DASHES", options=[
                                          False, True], typevar="bool")
        self.dashesOption = dashesOption
        self.optionMenus.append(self.dashesOption)

        ciOption = ModifiedOptionMenu(self.frame, label="CONF.INTERVAL", options=[
                                      None, "sd", "95", "68", "34"], typevar=None)
        self.ciOption = ciOption
        self.ciOption.variable.set("95")
        self.optionMenus.append(self.ciOption)

        self.place_menus()


class PointFrameSettings(commonCatPlot):
    """Pointplot settings"""

    def yield_value_dictionary(self):
        """
        Yields selected settings in the form of dictionary
        """
        values = self.common_yield()
        values["dashes"] = self.dashesOption.variable.get()
        # BLOCK TO CONVERT CONFIDENCE INTERVAL TO INT, IF POSSIBLE
        try:
            confin = int(self.ciOption.variable.get())
        except:
            confin = self.ciOption.variable.get()
        values["ci"] = confin
        values["join"] = self.joinOption.variable.get()
        values["estimator"] = self.estimatorOption.variable.get()
        estimator_dic = {None: None,
                         "mean": np.mean,
                         "sum": np.sum,
                         "min": np.min,
                         "max": np.max,
                         "median": np.median}

        values["estimator"] = estimator_dic[values["estimator"]]
        return(values)

    def __init__(self, master, numerical, categorical):
        self.common_options(master, numerical, categorical)

        estimatorOption = ModifiedOptionMenu(self.frame, label="ESTIMATOR", options=[
                                             "mean", "sum", "min", "max", "median"], typevar=None)  # ESTIMATOR OPTIONS UPDATE ACCORDING TO
        self.estimatorOption = estimatorOption
        self.optionMenus.append(self.estimatorOption)

        dashesOption = ModifiedOptionMenu(self.frame, label="DASHES", options=[
                                          False, True], typevar="bool")
        self.dashesOption = dashesOption
        self.optionMenus.append(self.dashesOption)

        ciOption = ModifiedOptionMenu(self.frame, label="CONF.INTERVAL", options=[
                                      None, "sd", "95", "68", "34"], typevar=None)
        self.ciOption = ciOption
        self.ciOption.variable.set("95")
        self.optionMenus.append(self.ciOption)

        joinOption = ModifiedOptionMenu(self.frame, label="JOIN", options=[
                                        True, False], typevar="bool")
        self.joinOption = joinOption
        self.optionMenus.append(joinOption)
        self.place_menus()


class Typeframe():
    """
    self.frame -> tkinter Frame to place on a master using .place method
    self.type_kind_dic  -> dictionary of type to kind
    self.type_var  ->tkinter StringVar (use .get() to get python string) FOR TYPE (rel,cat,dis)
    self.kind_var  ->tkinter StringVar (use .get() to get python string) FOR KIND
    self.type_menu ->tkinter OptionsMenu (use ["menu"] to access)
    self.kind_menu ->tkinter OptionsMenu (use ["menu"] to access)

    """

    def place(self, r, c):
        """
        Places Typeframe (self.frame) on a grid to row "r" and column "c"
        """
        self.frame.grid(row=r, column=c, sticky="nsew")

    def updatekind(self, *args):
        """
        Kind menu is dependent on type menu, and updates kind menu to match type menu
        """
        tyype = self.type_var.get()
        kinds = self.type_kind_dic[tyype]

        kind_menu = self.kind_menu["menu"]
        kind_menu.delete(0, "end")

        self.kind_var.set(kinds[0])
        for kind in kinds:
            kind_menu.add_command(
                label=kind, command=lambda kynd=kind: self.kind_var.set(kynd))

    def __init__(self, master):
        self.frame = tk.Frame(master=master)
        dictionary = {"Categorical": ["strip", "swarm", "box", "violin", "boxen", "point", "bar"],
                      "Distribution": ["hist", "kde", "ecdf"],
                      "Relationship": ["scatter", "line"]}
        self.type_kind_dic = dictionary

        types = list(dictionary.keys())
        type_var = tk.StringVar(name="type_variable")
        type_var.set(types[1])
        self.type_var = type_var

        kind_var = tk.StringVar(name="kind_variable")
        kind_var.set(dictionary[types[1]][0])
        self.kind_var = kind_var

        typeOptions = tk.OptionMenu(self.frame, self.type_var, *types)
        typeOptions.grid(row=0, column=1, sticky="nsew")
        tk.Label(master=self.frame, text="TYPE", bg="gainsboro",
                 relief="raised").grid(row=0, column=0, sticky="nsew")
        self.type_menu = typeOptions

        kindOptions = tk.OptionMenu(
            self.frame, self.kind_var, *dictionary[type_var.get()])
        # kindOptions=tk.OptionMenu(self.frame,self.kind_var,"")
        kindOptions.grid(row=1, column=1, sticky="nsew")
        tk.Label(master=self.frame, text="KIND", bg="gainsboro",
                 relief="raised").grid(row=1, column=0, sticky="nsew")
        self.kind_menu = kindOptions

        self.type_var.trace("w", self.updatekind)


class Varframe():
    """
    self.frame       ->
    self.c_variables ->
    self.f_variables ->
    self.s_variables ->

    self.first      ->
    self.second     ->
    self.first_menu ->
    self.second_menu->
    """

    def categorical_shift(self, direction):
        """
        Shifts what is first variable.
        If direction is True, it is directed in the categorical data
        where first variable must be from Categorical ((column list))

        If direction is False, it is directed in the numerical data
        where first variable must be from Numerical (column list)

        """
        self.first_menu["menu"].delete(0, "end")
        if direction:
            for x in self.c_variables:
                self.first_menu["menu"].add_command(
                    label=x, command=lambda xx=x: self.first.set(xx))
            self.first.set(self.c_variables[0])

        else:
            for x in self.f_variables:
                self.first_menu["menu"].add_command(
                    label=x, command=lambda xx=x: self.first.set(xx))
            self.first.set(self.f_variables[0])

    def place(self, r, c):
        """Places the frame"""
        self.frame.grid(row=r, column=c, sticky="nsew")

    def __init__(self, master, numerical, categorical):
        self.frame = tk.Frame(master)

        c_variables = list(categorical.columns)+list(numerical.columns)
        f_variables = list(numerical.columns)
        s_variables = list(numerical.columns)
        s_variables.insert(0, None)
        self.c_variables = c_variables
        self.f_variables = f_variables
        self.s_variables = s_variables

        first_var = tk.StringVar(name="first_variable")
        first_var.set(f_variables[0])
        self.first = first_var

        second_var = tk.StringVar(name="second_variable")
        second_var.set(s_variables[0])
        self.second = second_var

        firstOptions = tk.OptionMenu(self.frame, self.first, *f_variables)
        tk.Label(master=self.frame, text="X=", bg="gainsboro",
                 relief="raised").grid(row=0, column=0, sticky="nsew")
        firstOptions.grid(row=0, column=1, sticky="nsew")
        self.first_menu = firstOptions

        secondOptions = tk.OptionMenu(self.frame, self.second, *s_variables)
        tk.Label(master=self.frame, text="Y=", bg="gainsboro",
                 relief="raised").grid(row=1, column=0, sticky="nsew")
        secondOptions.grid(row=1, column=1, sticky="nsew")
        self.second_menu = secondOptions
