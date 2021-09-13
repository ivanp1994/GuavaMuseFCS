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

Additionally, another .FCS file is provided called "debris". This is a sample that has been visually inspected and contains no cells, only fragments of cells. This dataset will be very useful in [debris removal](#debris)


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

Initially, the *Number, Enrichment, & Depletion Menu* is empty. The top row of buttons changes the Biounit, the bottom row of buttons changes the Fraction displayed. Click on whatever you want to show that combination of Fraction and Biounit.


![NED menu 1](https://user-images.githubusercontent.com/84333373/132229853-9345a6c2-d2ce-497c-bbd1-4afd9087e3b7.PNG)

After selecting a graph.

![NED menu 2](https://user-images.githubusercontent.com/84333373/132229856-11e12c61-ae2e-4b22-be89-49166fa7b8bb.PNG)

Two graphs are displayed - a scatterplot of your X and Y values, and a normalized histogram of your X values to the right. Clicking on the either graph places one big vertical line. The textbox within the graph updates to tell you what percentage of dataset is to the right and what percentage of dataset is to the left. To the very right of the graphs is a reminder of your biounits and X values that are to be your threshold. Below the reminder, there are two buttons called **Replicate-based** and **Bootstrap-based**. These buttons calculate the NED - number, enrichment, and depletion of your procedure. The NED is calculated by the following formulaae :

1. Number - What percentage of events are to the right of your threshold line in the "PM" fraction
2. Enrichment - Ratio of percentage of events to the right of your threshold line in the "S" fraction, and percentage of events to the right of your threshold line in the "PM" fraction
3. Depletion - Ratio of percentage of events to the right of your threshold line in the "PM" fraction, and percentage of events to the right of your threshold line in the "M" fraction

All means and standard deviations are calculated through propagation of error for division.

The difference between **Replicate-based** and **Bootstrap-based** are in the ways resamples (to get means and standard deviations) are taken. Replicate-based presumes that user took multiple replicates of measurement, and calculated NED on that. Bootstrap-based pools all replicates of the same sample, and resamples a fixed percentage (40%) a fixed number of times (50). The idea is that you take quite a lot events when you do one flow cytometry measurement (upwards of 5000 samples!), and repeatedly resampling a high percentage of that measurement gets you close to sample estimates.

Clicking on either opens a new window to the right.

![ned result](https://user-images.githubusercontent.com/84333373/132231811-0d135bcd-841e-4918-ae7d-feadc258256b.PNG)

This window displays your results in a pandastable type of table. Right click on the table to export it. You can see that both our enrichment and depletion are relatively low. Is there a way to fix that?



## Debris removal <a name="debris"></a>

One of the problems in flow cytometry is existence of cellular debris - fragments of cells that are present in the uniform suspension. These fragments can be recorded by flow cytometry and be easily mistaken for cells - hence the precise terminology for one event recorded in flow cytometry is *event*, not cell. There are various ways to exclude debris, ranging from chemical treatments, through bioinformatic endeavors. The way presented here is the latter one. Note that Guava Muse also has option to exclude debris when events are collected. But if you didn't take advantage of Muse's debris exclusion feature, and instead recorded every event regardless of event size, the only choice for debris removal is through informatical methods.

Our method is latter, and it is based on the following idea. Guava Muse device is fundametally a cell counter, but like with every cell counter, it requires that the user has at least approximate idea of how much cells per microliter are in a sample - too concentrated or too diluted sample means that measurement will be imprecise (too concentrated sample might even clog the capillary of the device). Ideally, user has precounted his input sample with a hemocytometer and he knows how much cells will be in his input sample. The problem then is to determine a threshold to exclude cells, untill the number of cells is equal to the number of cells that the user knows is (more or less) true. 

By clicking on **Remove Debris** a window opens.

![debris intro](https://user-images.githubusercontent.com/84333373/132226947-bf8314af-63a9-4c42-b691-47a4620b9b15.PNG)

Clicking on **Select Input** opens a new window in which user can select the samples to undergo debris exclusion.

![debris select input](https://user-images.githubusercontent.com/84333373/132226951-eb71cebb-71fb-4f36-9d51-7c4047222f49.PNG)

Clicking on **Finalize** destroys the window. Now, user has to input X and Y values that will be used to plot a scatterplot. Clicking on **Select X&Y** opens a new window.

![debris select xy](https://user-images.githubusercontent.com/84333373/132226952-522d340c-45c9-41a9-9b42-c4304f047ddd.PNG)

Clicking on **Load** destroys the window. Now, user has to manually set a threshold for Y value. This threshold will apply to all biounits (see [Naming Scheme section](#naming)).

The top row of buttons changes the Biounit, the bottom row of buttons changes the Input Fraction displayed. Clicking on the graph sets a horizontal line and updates the graph to show what cell concentration is after placement. The bottom most row consists of a table in which the user can track the average number of cells per microliter, and the average Y value threshold. Additionally, one can use the Tab key to move the graphs along.

After setting thresholds, and double checking, all user has to do is exit the *Debris Exclusion* window.

Before setting threshold:

![debr_exc_new1](https://user-images.githubusercontent.com/84333373/132536485-6296880c-dc08-4eb4-909a-535342f00258.PNG)

After setting threshold:

![debr_exc_new2](https://user-images.githubusercontent.com/84333373/132536488-18b14325-51b2-41ec-9355-922dfa088480.PNG)

Now, all user has to do is exit the window, and a prompt will appear :

![debr_exc_new3](https://user-images.githubusercontent.com/84333373/132536489-452534cc-5604-4b12-a54c-0174adfb41a2.PNG)

In the prompt, user is reminded how much data they are removing. Pressing Yes removes all the debris. Pressing No aborts the entire procedure of debris removal. Pressing Cancel let's user continue tweaking debris exclusion.

![debris intro_after](https://user-images.githubusercontent.com/84333373/132226948-e3847e1a-85ae-4617-bd9b-99d43030e80f.PNG)

With our debris removed, we can revisit our [enrichment](#enrich) procedure :

![ned result 2](https://user-images.githubusercontent.com/84333373/132232666-55bed614-82dc-4be0-b47e-dea9c65d0665.PNG)

There's a slight, but not insignificant improvement to our enrichment, but not to our depletion. 




