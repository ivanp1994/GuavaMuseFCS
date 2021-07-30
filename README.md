# GuavaMuseFCS parsing/ pandasDataFrame GUI plotter
Parsing data from [GuavaMuse cytometer](https://www.luminexcorp.com/muse-cell-analyzer/)'s exported .FCS file and drawing said data or any other pandas DataFrame structure 

## Simplest parsing
Simplest parsing involves Python (numpy and pandas package needed):
```
from . import parse
meta,data=parse(path)
```
**Meta** is a dictionary structure containing all meta-information (samples, data, user, etc.) while **data** is pandas DataFrame with actual measurements.
Columns of **data** are all parameters that GuavaMuse cytometer records, with an added column "Sample" and "Name".

Total columns of **data** are:
- Name
- Sample
- FSC-HLin
- FSC-HLog
- YEL-HLin
- YEL-HLog
- RED-HLin
- RED-HLog
- TIME
- FSC-W
- RED-W
- YEL-W

Name is the name of the .FCS file, Sample contains all datasets recorded. FSC corresponds to cell size, YEL corresponds to yellow flourescence (for example, flourescence of phycoerythrin), RED corresponds to red flourescence (for example, flourescence of propidium iodide).
HLog is [hyperlog](https://pubmed.ncbi.nlm.nih.gov/15700280/) transformation of HLin version. W is supposed to be parameter for Width (encoding the duration of the signal, as opposed to height of the signal) enabling doublet detection.

Normally, the channel name depends on the module used. For example, Cell Cycle module (extension .CCY.FCS) will explicitly call "RED-HLin" DNA Content, while a Ki67 module (extension .Ki67.FCS) will explicitly call "YEL-HLog" Ki67 positive. The channel names are unified so that different modules still have the same channel names.

If navigating to the path is difficult, a tkinter GUI interface is provided in the form of select_file function
```
from . import parse
from . import select_file
path=select_file()
meta,data=parse(path)
```
The select_file function will open an OpenFile prompt which is then parsed using parse function

## Option for legendization

Additional feature is added in the form of **text_explanation** function. GuavaMuse, by default, encodes each measurement in the format of "Sample-XXX" where XXX a number (e.g. Sample-001). Since using touchscreen/mouse+touchscreen on cytometer is rather unwieldy, said formatting persists in the .FCS file. However **text_explanation** function takes a path to .FCS file, and takes a path to .TXT file of the same name, and replaces Sample-XXX with user inputted name. 

The .TXT file must the number of lines equal to the number of samples recorded in .FCS file and in the same folder as the .FCS file.

Text file example:

![text file example](https://user-images.githubusercontent.com/84333373/118640838-b8bb4900-b7d9-11eb-9ee2-4736fd6d1dcb.PNG)

Data before and after **text_explanation** :

![databefore_dataafter](https://user-images.githubusercontent.com/84333373/118641363-5a429a80-b7da-11eb-92bd-d2b6d121badd.PNG)


In the above example, text file has 12 lines, each corresponding to each of 12 samples in the corresponding .FCS file. Since repeated measurements of the same sample is desired, example .FCS file consists of 3 replicate measurements of 4 samples (total 12). 

**Text_explanation** function also inserts one new column titled **Replicate** that corresponds to repeated measurement of sample sample. 

## Advanced parsing with tkinter GUI

Additional features are provided in the form of a Graphic User Interface.  [pandasTable package](https://pandastable.readthedocs.io/en/latest/pandastable.html) is needed.

GUI is started by

```
from . import start_interface
start_interface()
```

**start_interface()** starts a [tkinter .mainloop](https://www.educba.com/tkinter-mainloop/) that doesn't end until user ends the window.

Interface looks like this:

![initial](https://user-images.githubusercontent.com/84333373/118638099-c7543100-b7d6-11eb-940b-327e2655334b.PNG)

- **Add** file opens a prompt for adding a .FCS file. 

- **Merge** file merges all files into one file (necessary to enter Draw Menu)

- **D R A W** enters the Draw Menu (more on that later)

After a couple of files are added, interface looks like this:

![added files](https://user-images.githubusercontent.com/84333373/118638856-8dcff580-b7d7-11eb-8690-8ea19a3908e1.PNG)

- **Automatic Legend** - legendizes the dataset according to **text_explanation** function
- **Manual Legend** - prompts manual legendization
- **Export Data** - exports the data to .CSV or .XSLX file
- **Remove Data** - deletes the data set

Manual legendization : 

![manualleg](https://user-images.githubusercontent.com/84333373/118641782-ddfc8700-b7da-11eb-9b99-f0bd80f839d8.PNG)

Once either all samples or none samples are legendized, press **"Merge Files"** and **"D R A W"** to enter DrawFrame

# Gating and Drawing

After pressing **Merge Files** the interface looks like this:

![gating](https://user-images.githubusercontent.com/84333373/123617428-84d73880-d807-11eb-9641-5bd8640efaf3.PNG)

Pressing **D R A W** enters Draw Menu (#Drawing Dataframe section), and pressing **Gating** enables gating (#Gating section)

# Gating

Pressing Gating first prompts the Menu in which the user can select data upon which Gating procedure will be performed. The *"Select Data for Gating"* looks like this:

![gating_adding](https://user-images.githubusercontent.com/84333373/123617699-cf58b500-d807-11eb-8bf9-5d6e4ab88f4e.PNG)

Pressing **Add to Selected** adds the row to selected data. Pressing **Switch View** switches between all available data and selected data. Pressing **Remove from Selected** removes the selected row from selected data. Finally, pressing **Finalize** enters the next phase of gating - creating a scatterplot. The "Select Data for Gating" menu persists, so multiple gating sessions can be done. First a prompt is created in which the user can select X and Y variables:

![gating_crsc](https://user-images.githubusercontent.com/84333373/123618330-6160bd80-d808-11eb-8b2c-9f27ac442b6e.PNG)
 
Pressing **Load** enters the next phase of gating - gating upon the scatterplot. Which looks like this:

![gating_gate1](https://user-images.githubusercontent.com/84333373/123618673-b6043880-d808-11eb-9226-7aeac9627cea.PNG)

Pressing **Initiate Gate** enables the user to click on the scatterplot and create a series of points. Those points will then form vertices of a polygon which will act as a gate. Complete the polygon to create one gate. Below is an example of one gate.

![gating_gate2](https://user-images.githubusercontent.com/84333373/123619042-109d9480-d809-11eb-8921-94327023dca3.PNG)

Pressing **Complete Gates** finalizes the gating procedure. In the example below, we created one more gate and pressed Complete Gates.

![gating_gate3](https://user-images.githubusercontent.com/84333373/123619390-6a9e5a00-d809-11eb-84a5-15a9670ceaa8.PNG)

Scatterplot is now changed to include Gates (colored and transparent polygones) on the scatterplot, and gates summaries below the the buttons. Gate summary includes a name of a gate (can be changed by clicking and retyping), color of the gate, and statistics such as what percentage of data are within the gate and outside the gate. In the example provided, Gate No.2 is orange colored, and 13.853% of all data are within this Gate. Pressing Remove, deletes the gate from the scatterplot and the gate summary.

Finally, pressing **Apply Gates to Data** exports the data in the form of .CSV or .XLSX file. Data also contains columns named for Gates with values True/False if the datapoint is found in the gate or not. 

# Drawing Dataframe

Draw Menu looks like this:

![drawframe](https://user-images.githubusercontent.com/84333373/119473955-f8d77a00-bd4b-11eb-97f5-569f6372026f.PNG)

- **Select Data** button prompts selecting what parts of dataframe will be drawn (default is all)
- **Draw** draws the graph
- **Style** changes the [matplotlib stylesheets](https://matplotlib.org/stable/gallery/style_sheets/style_sheets_reference.html)

The Type and Kind settings dictate what kind of plot will be drawn, the full list is here:

- Distribution
  - hist - [Histogram plot](https://seaborn.pydata.org/generated/seaborn.histplot.html)
  - ecdf - [Empirical Cumulative Distribution Function plot](https://seaborn.pydata.org/generated/seaborn.ecdfplot.html#seaborn.ecdfplot)
  - kde - [Kernel Density Estimate/Density plot](https://seaborn.pydata.org/generated/seaborn.kdeplot.html#seaborn.kdeplot)
- Relationship
  - scatter - [Scatter plot](https://seaborn.pydata.org/generated/seaborn.scatterplot.html?highlight=scatter%20plot#seaborn.scatterplot)
  - line - [Line plot](https://seaborn.pydata.org/generated/seaborn.lineplot.html#seaborn.lineplot)
- Categorical
  - strip - [Strip plot](https://seaborn.pydata.org/generated/seaborn.stripplot.html?highlight=stripplot)
  - swarm - [Swarm plot](https://seaborn.pydata.org/generated/seaborn.swarmplot.html?highlight=swarm#seaborn.swarmplot)
  - box - [Box plot](https://seaborn.pydata.org/generated/seaborn.boxplot.html?highlight=box#seaborn.boxplot)
  - boxen - [Boxen plot](https://seaborn.pydata.org/generated/seaborn.boxenplot.html?highlight=box#seaborn.boxenplot)
  - violin - [Violin plot](https://seaborn.pydata.org/generated/seaborn.violinplot.html?highlight=violin#seaborn.violinplot)
  - point - [Point plot](https://seaborn.pydata.org/generated/seaborn.pointplot.html?highlight=point#seaborn.pointplot)
  - bar - [Bar plot](https://seaborn.pydata.org/generated/seaborn.barplot.html?highlight=barplot#seaborn.barplot)

Variables X and Y dictate what will be drawn on X and Y axis.

Additional settings are placed to the right variables, and I recommend going to above links to see what setting does what. For example, for Distribution plot of Histogram kind, bins defines how bins are created - seaborn offers options "fd","doane","sturges" etc. See seaborn's documentation for this.

# Using Draw Menu GUI to draw other dataframes

dfdrawer can be used to draw other datasets. For example:

```
import seaborn as sns
data=sns.load_datasets("fmri")
```

Seaborn module comes with various sample datasets, in the above example, we loaded "fmri" dataset

To call dataframe drawer without anything else use:

```
from . import DrawTopLevel
v=DrawTopLevel(master=None,dataframe=data)
v.myself.mainloop()
```
DrawTopLevel is a class that is called with two variables, master and dataframe. Master denotes tkinter Toplevel (tk.Toplevel()) or root (tk.Tk()), so DrawTopLevel can be plugged in any tkinter style interface. If master is called with None, then DrawTopLevel stands alone. .myself is the attribute of DrawTopLevel denoting tkinter root or Toplevel (depending on master) object, and if master is none, .myself needs to be started with .mainloop() method. 
