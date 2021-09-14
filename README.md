# Enrichment and Debris Removal branch

Enrichment branch is functionally the same as main branch, but there are additional features implemented. Additional features are:
1. Calculating enrichment of a procedure
2. Informatically excluding cellular debris

Enrichment branch is relatively rigid (as opposed to main branch) in what it can take as input. This rigidity manifests itself in naming scheme of recorded samples.
Additionally, if one wants to exclude debris, a .CSV file that accompanies .FCS file is required. 

To start the branch, do everything from main (use ```start_interface()``` function). Load your dataset, name it, and then merge it. You will get a new window:

![mainlevelintro](https://user-images.githubusercontent.com/84333373/132229057-5dab658f-ab4a-40e4-bb32-8ca4597c95bc.PNG)

Clicking on **ENRICHMENT** leads to [enrichment window](#enrich) while clicking on **Debris Removal** leads to [debris removal window](#debris)

## Naming scheme <a name="naming"></a>

Naming scheme must start with one of the four values - INP, M, PM, S each representing one Fraction. For more details on what those Fractions represent, check out [Enrichment procedure header](#enrich). Biounits go after a fraction, separated by "-" sign, and they can be named whatever you want. 

Correct examples :

INP-BiounitA
INP-BiounitB
PM-BiounitC

Incorrect examples :

inP:BiounitA
inp:BiounitA
INP:BiounitA

## Example dataset provided

Example given here is an uniform suspension of testicular cells of a mouse. Each mouse is considered one separate biounit. 
Uniform suspension of testicular cells consists of many different cell types - including spermatogonia, spermatides, Leydig cells, spermatozoa, etc.
Spermatogonia express c-kit receptor, and they are subsequently marked with phycoerythryn (PE) marked antibody (PE-antibody). Magnetic nanobeads that recognize PE are then added to the mixture, and suspension is subjected to
[magnetically activated cell sorting](https://en.wikipedia.org/wiki/Magnetic-activated_cell_sorting) that results in fraction enriched for spermatogonia, and fraction depleted of spermatogonia.

The procedure results in four fractions per mouse. Additionally, PE can be detected through GuavaMuse through YEL parameter. The problem is that all cells demonstrate some level of yellow flourescence in
a phenomenon called "[autoflourescence](https://en.wikipedia.org/wiki/Autofluorescence)". To differentiate spermatogonia from autoflorescent cells, PE-unmarked fraction ("INP") must be recorded to calibrate GuavaMuse sample collecting.
PE-marked fraction ("PM") will then be recorded and if marking is successful - there will be a population of cells to the right of YEL-HLog parameter corresponding to PE-marked spermatogonia. Next, spermatogonia are magnetically separated into a fraction enriched for spermatogonia ("S)
and fraction depleted of spermatogonia ("M").

Our dataset consists of 2 mouse - one which has been subjected to a mild experiment, and one that served as a control to that experiment. Each mouse has 4 fractions, to the total number of 8 different samples. Additionally, every sample has been 3 three times in quick succession on Guava Muse, to a total of 24 Guava Muse "samples".

Additionally, another .FCS file is provided called "debris". This is a sample that has been visually inspected and contains no cells, only fragments of cells. This dataset will be very useful in [debris removal](#debris).


## Enrichment procedure <a name="enrich"></a>

The purpose of the enrichment branch is to quantify and visualize percentage of cells positive for certain condition and enrichment of those cells after a certain operation.
Enrichment branch makes use of **"Biounit"** - which is a unit defined by some biological criteria (e.g. a mouse or cell type), and **"Fraction"** which is one part of "marking and enriching" operation.

Procedure goes roughly like this:

- Uniform cell suspension containing various different cells is achieved - "INP" fraction
- Certain cells within are marked in a way that GuavaMuse can detect - "PM" fraction
- Certain procedure is done on marked cell suspension that results in the increase of the proportion of those marked cells - "S" fraction
- (Optional) Certain procedure is done on marked cell suspension that results in the decrease of the proportion of those marked cells - "M" fraction

Each of those 4 stages is a different fraction of the same biounit. Allowed fraction names are "INP", "PM", "S", and "M". To enter Enrichment Menu, click on **Enrichment**.

A familiar menu opens up :

![debris select xy](https://user-images.githubusercontent.com/84333373/132226952-522d340c-45c9-41a9-9b42-c4304f047ddd.PNG)

Select your X and Y values, then click **Load**

Initially, the *Number, Enrichment, & Depletion Menu* consists of three rows of buttons - Command buttons, Biounit buttons, and Fraction buttons.
Biounit buttons change the Biounit, Fraction buttons change the Fraction, and Command buttons execute following comands.

Initially, no graph is present. 

![1](https://user-images.githubusercontent.com/84333373/133249143-d1eba9aa-af12-4eb8-be2d-b4cc9a2edd5e.PNG)

But clicking on any element in Biounit/Fraction buttons shows two plots for that combination. To the left is a scatterplot of Y versus X, and to the right is a normalized histogram of X values.

![2](https://user-images.githubusercontent.com/84333373/133249146-f7da9ce9-e8b8-4c5e-a7a6-ff5d6683968e.PNG)

Clicking within the boundaries of any graph places a vertical line with x coordinate where you clicked. This is the threshold line and it is used for further calculations. There is a box with text in both graphs, showing what percentage of the dataset is to the left, what percentage of the dataset is to the right, and the X coordinate of the line. Clicking on **Set Box visibility** toggles this box on and off.

![box invisi](https://user-images.githubusercontent.com/84333373/133249147-d3622ea3-e4a0-4e89-9ddd-62d3e5e733e1.PNG)

Clicking on either **Replicate-based** or **Bootstrap-based** calculates the following things:

1. Number - What percentage of events are to the right of your threshold line in the "PM" fraction
2. Enrichment - Ratio of percentage of events to the right of your threshold line in the "S" fraction, and percentage of events to the right of your threshold line in the "PM" fraction
3. Depletion - Ratio of percentage of events to the right of your threshold line in the "PM" fraction, and percentage of events to the right of your threshold line in the "M" fraction

All means and standard deviations are calculated through propagation of error for division.

The difference between **Replicate-based** and **Bootstrap-based** are in the ways resamples (to get means and standard deviations) are taken. Replicate-based presumes that user took multiple replicates of measurement, and calculated NED on that. Bootstrap-based pools all replicates of the same sample, and resamples a fixed percentage (40%) a fixed number of times (50). The idea is that you take quite a lot events when you do one flow cytometry measurement (upwards of 5000 samples!), and repeatedly resampling a high percentage of that measurement gets you close to sample estimates.

Clicking on either opens a new window to the right.

![after operation](https://user-images.githubusercontent.com/84333373/133250055-7820569c-f387-436c-b3c0-2623ddb69d7a.PNG)

This window displays your results in a pandastable type of table. Right click on the table to export it. You can see that both our enrichment and depletion are relatively low. Is there a way to fix that?



## Debris removal <a name="debris"></a>

One of the problems in flow cytometry is existence of cellular debris - fragments of cells that are present in the uniform suspension. These fragments can be recorded by flow cytometry and be easily mistaken for cells - hence the precise terminology for one event recorded in flow cytometry is *event*, not cell. There are various ways to exclude debris, ranging from chemical treatments, through bioinformatic endeavors. The way presented here is the latter one. Note that Guava Muse also has option to exclude debris when events are collected. But if you didn't take advantage of Muse's debris exclusion feature, and instead recorded every event regardless of event size, the only choice for debris removal is through informatical methods.

Our method is latter, and it is based on the following idea. Guava Muse device is fundametally a cell counter, but like with every cell counter, it requires that the user has at least approximate idea of how much cells per microliter are in a sample - too concentrated or too diluted sample means that measurement will be imprecise (too concentrated sample might even clog the capillary of the device). Ideally, user has precounted his input sample with a hemocytometer and he knows how much cells will be in his input sample. The problem then is to determine a threshold to exclude cells, untill the number of cells is equal to the number of cells that the user knows is (more or less) true. 

One other option is to record a sample that the user *knows* has no cells, but contains cell fragments, and setting a debris exclusion threshold according to that sample. Both options are present.

By clicking on **Remove Debris** a window opens.

![debrmanag](https://user-images.githubusercontent.com/84333373/133114324-12c55c3f-1142-4040-93d3-28ac5633b51f.PNG)

The X and Y will be axes of a scatterplot used to pick out debris. Usually, Y is something that represents cell size, such as forward scatter height.

In the *Biounit Label and Command menu* you can see your Biounits (Control and Experiment), and next to them are two buttons - **From internal** and **From external**. 

Clicking on **From internal** opens a prompt in which you can select what Replicates will you use for your debris removal. 
Clicking on **From external** opens a prompt in which you can navigate to a .FCS file you will use your debris removal. We have provided debris.FCS in the sample datasets.

Selecting either option will update the *Path/Input selection* for each biounit. We have chosen to navigate to the same debris.FCS file provided.

![debrmanag2](https://user-images.githubusercontent.com/84333373/133115716-5fa0c000-04b8-4246-9d08-fed6b33bf2b1.PNG)

Clicking on **Enter Debris Removal Window** opens a new window.  

![debriexc](https://user-images.githubusercontent.com/84333373/133115925-1f8d0ab4-06ce-4088-b315-d487f2b7c4df.PNG)

The window contains scatterplot a of selected X and Y values. Clicking on the scatterplot within its boundaries places a horizontal line. Only events above this horizontal line are considered cells, and the textbox within the scatterplot is updated to reflect the number of cells above the horizontal line. Every biounit is unique, even when the debris file is the same, and therefore a whole total of biounits * debris replicates scatterplots are possible. You can switch to the next scatterplot by using Tab key, or by clicking buttons in the upper two rows.

Since this is a dataset in which we haven't seen any cells, our threshold will be relatively high, and the amount of our "cells" will be relatively low. 2 percent of dataset remains, reflecting the possibility that in a suspension of 100 cellular fragments, there are at least 2 passing cells. 

![debriexc2](https://user-images.githubusercontent.com/84333373/133116844-31147de8-75d1-423e-b48a-475513a094e1.PNG)

Finish the debris removal by exiting the *Debris Exclusion* window. A prompt will appear asking the user for confirmation. Click Yes to finalize the procedure. Click No to abort the debris removal procedure, and click Cancel to return to the procedure. After clicking Yes, *Debris Removal Manager* is updated to reflect selected thresholds. 

Exiting *Debris Removal Manager* updates the *GuavaMuse Parser* window with a new dataset.

![main](https://user-images.githubusercontent.com/84333373/133117838-fd82f6f4-9631-463d-967a-ff300ec16392.PNG)
![debrmang3](https://user-images.githubusercontent.com/84333373/133117841-98eac3c9-50d3-41af-88f5-72d4cdb303e4.PNG)

Clicking on **Debris Free Data** you can see all .FCS files you loaded. You can manage this dataset just like any other dataset - export it, delete it, gate it, calculate enrichment, remove debris (again), etc. 

Revising our [enrichment](#enrich) procedure we can see significant improvements :

![enr](https://user-images.githubusercontent.com/84333373/133118594-21ed13de-3939-4245-86fc-b468a6fe3fc1.PNG)

First thing we can note is that the elipsoid population from S fraction is removed - this likely represented cell fragments with their c-kit receptor intact. Another thing to note is that while enrichment has improved, our depletion stayed the same - and  this likely reflects reality better.

![after debris](https://user-images.githubusercontent.com/84333373/133250638-b610afbc-84bc-4562-8986-ca6754e6c683.PNG)

Branch **experiment** contains additional procedures and graphs. For more information, check it out!







