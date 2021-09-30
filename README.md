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
Interface starts with just two buttons - **Add .FCS file** and **Merge Selected**:

![initial](https://user-images.githubusercontent.com/84333373/135472572-26107de6-1072-426f-a542-bd7ff028a061.PNG)

Clicking on **Add .FCS file** opens a prompt in which user can navigate to their .FCS file. Every file added is a unique structure, so there is no overwriting of original .FCS file(s). Here is how the window looks when two files are added.

![added](https://user-images.githubusercontent.com/84333373/135472567-eacfd456-db75-429e-a6b3-65c9fe5f3cd9.PNG)

Every structure has several components to it. First one is the label, displaying the name of the file (or it's unique ID). Second one is a Checkbox that can be toggled on and off. Third one is the **Delete** button - clicking it deletes the data from the interface (it doesn't delete the .FCS file). Followed by the delete button are two drop-down menus.

First one is called **Legendization** and it controls how user can rename their collected samples. Two options are available - **auto** (identically to text_explanation function above) and **manual** in which a new window prompt is created. For details, see section below.

![legendization](https://user-images.githubusercontent.com/84333373/135472573-7fa8bd80-df25-48e2-892c-db7eee169acb.png)

Second one is called **Command** and it lets user do stuff with data. In the main branch, available options are :
- **Export** - which exports the data as .csv or .xlsx. table
- **Draw** - prompts a creation of Draw Menu (for details see sections below)
- **Gate** - prompts a creation of a new window in which user can place "gates" in parts of their data and process them

Additional commands are found in gui_enrichment branch-
![command](https://user-images.githubusercontent.com/84333373/135472569-48307560-2714-4be4-80bd-c19000a04df9.png)

To process multiple datasets at the same time, user can click on **Merge Selected** which merges all files that are selected in a new structure. No original datasets are modified in this process.

![merged](https://user-images.githubusercontent.com/84333373/135472576-28d4130f-b49e-4ed2-8cb8-9e50bf79ae8c.PNG)

### Manually inputing sample names

The following prompt is opened:

![manualleg](https://user-images.githubusercontent.com/84333373/118641782-ddfc8700-b7da-11eb-9b99-f0bd80f839d8.PNG)

Under "Sample" column input the name of your sample. Under "Replicate" column, input the number of the replicate. If you didn't take repeated measurements of the same sample (shame on you!), just input 1 for every sample. 

You can use TAB to move sideways, and use ENTER to input information and change Sample name. If you input the same thing twice, the background will change to bright red. Inputting all samples and pressing ENTER, while there are no bright red labels, will finalize manual inputting.

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

Exiting the Gate Manager automatically adds a new structure to the main interface.

![gated](https://user-images.githubusercontent.com/84333373/135472570-833218bd-0738-499e-a2b8-7e1febe11502.PNG)

You can do whatever you can do with regular files - drawing, exporting, gating (again), etc.

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
