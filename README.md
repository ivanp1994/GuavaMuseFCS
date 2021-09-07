# GuavaMuseFCS-Main branch
This repository houses code for several things:
1. Read  [.FCS](https://en.wikipedia.org/wiki/Flow_Cytometry_Standard) files provided [Guava Muse Cell Analyzer](https://www.luminexcorp.com/muse-cell-analyzer/)
2. Provide Graphical User Interface for interacting with said data
3. Provide Graphical User Interface for drawing said data
4. Provide Graphical User Interface for drawing any dataframe using [seaborn](https://seaborn.pydata.org/) library

Additionally, the branch "gui_enrichment" has several more precise applications

## Parsing Guava Muse .FCS data

### Requirements

Requirements can be found in requirements.txt file provided, and to install them simply run:

```pip install -r requirements.txt```

None of the requirements are that unsual - the bulk of modules used are tkinter, matplotlib, seaborn, pandas, and numpy. Some lesser known modules are pandastable and sklearn. Likewise, there is no specific version of any module required, and I believe this repository is relatively future-proofed.

### Intro
The primary way to parse Guava Muse .FCS data is by using `parse` function which takes a *path* to your .FCS file and outputs

1. data in the form of pandas DataFrame (`parse(path,"data")`)
2. tuple of meta information and data in the form of pandas DataFrame (`parse(path,"full")`)
3. or a python object that can be inspected (`parse(path,"obj")`)

depending on the additional argument provided.
Examples:

```
from GuavaMuseFCS import parse

data=parse(path)`
meta,data=parse(path,"full")
python_object=parse(path,"obj")

```

If user does not want to type in the full path, function `select_file` is provided that opens a file browser to a path:

```
from GuavaMuseFCS import select_file()
path=select_file()
data=parse(path)
```

### Renaming Samples from a text file
Sometimes, naming samples directly from the Guava Muse Cell Analyzer is unwieldy, so default names (eg. "Sample-001, Sample-002"...) are left as default Sample names. There is an option to rename samples directly from **Graphical User Interface** provided in this repository, or from a similarly named .txt file. In order to rename samples from the text file, text file must

1. Be the same name as .FCS file (minus the extension) - eg. ("samples_recorded_02092021.CCY.FCS" and "samples_recorded_02092021.CCY.txt") 
2. Have the same number of lines as there are samples - eg. if there are 20 samples in the above .FCS file, the accompanying text file must have 20 lines

Order of lines in the text matters!

Finally, it is customary to take multiple measurements of the same sample. In this case, we make a distinction between a "Sample" and a "Replicate" - Sample is biologically distinct (e.g. in different Eppendorf tubes) while Replicate is just multiple measurements of the same Sample. If you're not taking repeated measurements (well, shame on you!), feel free to ignore this.

To rename sample directly, function `text_explanation` is used, and it takes a path to your .FCS file.

Example:

```
from GuavaMuseFCS import text_explanation
data_with_legend=text_explanation(path)
```
### Guava Muse .FCS data
By default, data from flow cytometry holds following columns:

1. 'Sample', 
2. 'FSC-HLin',
3. 'FSC-W',
4. 'YEL-HLin',
5. 'YEL-W',
6. 'RED-HLin',
7. 'RED-W',
8. 'Time',
9. 'FSC-HLog', 
10. 'YEL-HLog',
11. 'RED-HLog

Additional column 'Name' is added to the dataset corresponding to the name of the .FCS file, and depending on user manipulation, columns 'Sample' and 'Replicate'

FSC refers to Forward Scatter (correlating to size of the event). RED and YEL refer to red and yellow flourescence. HLin refers to linear measurement of height of signal, while HLog refers to logarithmic (base 10) transformation of HLin. W refers to width of the signal.

Different modules call these same columns differently - eg. a Cell Cycle module that is based on Propidium Iodide (red flourescence dye) will call RED-HLin "DNA content". The function `parse` "unifies" the data names. 

## Graphical User Interface
### Starting GUI

Function start_interface, well, starts the interface

```
from GuavaMuseFCS import start_interface
start_interface()
```
Interface is a tkinter object that houses three buttons:

1. Add File
2. Merge Files
3. Draw Menu

### Adding Files
**Add File** opens a prompt to add a file. This is how the interface looks when several files are added:

![first one](https://user-images.githubusercontent.com/84333373/131835689-c57d13e1-7e5f-4056-a20a-e1ed540fa51e.PNG)

Additional buttons appear for each file. These buttons are:

1. Automatic Legend
2. Manual Legend
3. Export 
4. Remove data

Clicking on **Remove data** removes the data. Clicking on **Export data** creates a prompt to export data in either .XLSX or .CSV format. Exporting as .XLSX might take some time. Clicking on **Automatic Legend** is functionally identical to `text_explanation` function as it renames from text file. Clicking on **Manual Legend** creates a prompt to manually input names for every sample.

### Manually inputing sample names

The following prompt is opened:

![manualleg](https://user-images.githubusercontent.com/84333373/118641782-ddfc8700-b7da-11eb-9b99-f0bd80f839d8.PNG)

Under "Sample" column input the name of your sample. Under "Replicate" column, input the number of the replicate. If you didn't take repeated measurements of the same sample (shame on you!), just input 1 for every sample. 

You can use TAB to move sideways, and use ENTER to input information and change Sample name. If you input the same thing twice, the background will change to bright red. Inputting all samples and pressing ENTER, while there are no bright red labels, will finalize manual inputting.

### Merging files

Clicking on **Merge** files collates the files in one super data set. Merge can only be achieved when number of columns are equal (so you either need to legendize all the datasets, or none of the datasets).

Merging files changes the interface like this:

![gating](https://user-images.githubusercontent.com/84333373/123617428-84d73880-d807-11eb-9641-5bd8640efaf3.PNG)

Additional buttons appear for the great merge. These buttons are:

1. MERGED DATA
2. Export
3. Remove data
4. GATING

Clicking on **MERGED DATA** gives you a prompt of all data you merged in this file. Clicking on **Export** and **Remove data** is self explanatory, and clicking on **GATING** opens a *Gating Menu*.

Finally, clicking on **Draw Menu** opens the drawing menu.

### Gating Menu

First, "Select the Data for Gating" prompt is opened. 

![gating_adding](https://user-images.githubusercontent.com/84333373/123617699-cf58b500-d807-11eb-8bf9-5d6e4ab88f4e.PNG)

Select what data you want to add, and then click **Add to selected**. Click **Switch View** to inspect selected data. Select the data you don't want to gate, then click **Remove from Selected**. Finally, once you're sure with your choice, click **Finalize**. 

A prompt to select X and Y values for resulting scatter plot will open.

![xyselector](https://user-images.githubusercontent.com/84333373/121691343-3156b200-cac7-11eb-9054-79d99cec177a.PNG)

Select your X and Y values and then click **Load**. The XY prompt will close, but "Select the Data for Gating" will remain open. Finally, "Gating Menu" prompt will open.

![gating_gate1](https://user-images.githubusercontent.com/84333373/123618673-b6043880-d808-11eb-9226-7aeac9627cea.PNG)

Gating Menu contains X Y scatterplot of your selected data, and several buttons below. Buttons are:

1. Initiate Gate
2. Complete Gate
3. Apply Gates to Data

Clicking on **Initiate Gate** will let you put "points" on the scatterplot. Points will be vertices of a polygon and completing the polygon completes one Gate, and enables you to add another gate by clicking on **Initiate Gate**.

Gate placed:

![gating_gate2](https://user-images.githubusercontent.com/84333373/123619042-109d9480-d809-11eb-8921-94327023dca3.PNG)

Clicking **Complete Gates** finalizes all gates and provides you with information about the gates - what percentage of events is in the Gate or outside the Gate.

Gates finalized:

![gating_gate3](https://user-images.githubusercontent.com/84333373/123619390-6a9e5a00-d809-11eb-84a5-15a9670ceaa8.PNG)

You can rename the Gates if you want. 
Finally, clicking on **Apply Gates to Data** lets you export the dataset with additional columns. These additional columns represent gates, and have either True or False, representing if an event is in the gate or not.

### Draw Menu

If you clicked **Draw Menu**, following prompt appeared:

![drawframe](https://user-images.githubusercontent.com/84333373/119473955-f8d77a00-bd4b-11eb-97f5-569f6372026f.PNG)

Clicking on **SELECT DATA** lets you select what data will you draw by pulling up Select Data prompt:

![gating_adding](https://user-images.githubusercontent.com/84333373/123617699-cf58b500-d807-11eb-8bf9-5d6e4ab88f4e.PNG)

Select what data you want to draw, and then click **Add to selected**. Click **Switch View** to inspect selected data. Select the data you don't want to draw, then click **Remove from Selected**. Finally, once you're sure with your choice, click **Finalize**. 

Changing **STYLE** changes the style of a graph.

Changing **TYPE** changes the type of the graph. Current types are:

1. Distribution plot
2. Relationship plot
3. Categorical plot

Changing **KIND** changes the kind of a graph. Every type has it's own corresponding set of "kinds". For example, Distribution plot has "hist" for histogram, "kde" for kernel density estimate, "ecdf" for empirical cumulative density function. Additionally, to the far right of the graph, there are type-and-kind specific options for plotting. 

I recommend checking out seaborn's documentation and tutorials for further information.

Finally, clicking **DRAW** draws the graph according to your specifications.

## Standalone Draw Menu

If you want to draw other pandas DataFrames other than the ones from .FCS files, you can do that too. For example, seaborn module has lots of datasets.

```
import seaborn as sns
data=sns.load_dataset("penguins")
```
We now loaded a dataset about penguins. Start Drawing interface with the following code:
```
from GuavaMuseFCS import DrawTopLevel
app=DrawTopLevel(None,data)
app.start()
```
