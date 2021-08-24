# GuavaMuseFCS-Enrichment branch

Enrichment branch is functionally the same as main branch, but there are additional features implemented in the form of quantifying both number and enrichment percentage of cells after some operation.
Enrichment branch is relatively rigid (as opposed to main branch) in what it can take as input. This rigidity manifests itself in naming scheme of recorded samples.

The purpose of the enrichment branch is to quantify and visualize percentage of cells positive for certain condition and enrichment of those cells after a certain operation.
Enrichment branch makes use of **"Biounit"** - which is a unit defined by some biological criteria (e.g. a mouse or cell type), and **"Fraction"** which is one part of "marking and enriching" operation.

Procedure goes roughly like this:

- Uniform cell suspension containing various different cells is achieved - "INP" fraction
- Certain cells within are marked in a way that GuavaMuse can detect - "PM" fraction
- Certain procedure is done on marked cell suspension that results in the increase of the proportion of those marked cells - "S" fraction
- (Optional) Certain procedure is done on marked cell suspension that results in the decrease of the proportion of those marked cells - "M" fraction

Each of those 4 stages is a different fraction of the same biounit. Allowed fraction names are "INP", "PM", "S", and "M".

# Example on MACS for mouse spermatogonia

Example given here is an uniform suspension of testicular cells of a mouse. Each mouse is considered one separate biounit. 
Uniform suspension of testicular cells consists of many different cell types - including spermatogonia, spermatides, Leydig cells, spermatozoa, etc.
Spermatogonia express c-kit receptor, and they are subsequently marked with phycoerythryn (PE) marked antibody (PE-antibody). Magnetic nanobeads that recognize PE are then added to the mixture, and suspension is subjected to
[magnetically activated cell sorting](https://en.wikipedia.org/wiki/Magnetic-activated_cell_sorting) that results in fraction enriched for spermatogonia, and fraction depleted of spermatogonia.

The procedure results in four fractions per mouse. Additionally, PE can be detected through GuavaMuse through YEL parameter. The problem is that all cells demonstrate some level of yellow flourescence in
a phenomenon called "[autoflourescence](https://en.wikipedia.org/wiki/Autofluorescence)". To differentiate spermatogonia from autoflorescent cells, PE-unmarked fraction ("INP") must be recorded to calibrate GuavaMuse sample collecting.
PE-marked fraction ("PM") will then be recorded and if marking is successful - there will be a population of cells to the right of YEL-HLog parameter corresponding to PE-marked spermatogonia. Next, spermatogonia are magnetically separated into a fraction enriched for spermatogonia ("S)
and fraction depleted of spermatogonia ("M"). Example histogram is given below:

![mouse example](https://user-images.githubusercontent.com/84333373/118981191-606f7d00-b97a-11eb-91cd-78b5faac00ed.png)

Histogram for biounit (mouse) "C_1" and various fractions. Fractions are sorted from least amount of PE-positive cells to most amount of PE-positive cells ("INP","M","PM","S").



Enrichment branch is initialized the same as main branch through:

```
from museInterface import start_interface
start_interface()
```
This results in standard interface, same as one in main:

![initial](https://user-images.githubusercontent.com/84333373/118638099-c7543100-b7d6-11eb-940b-327e2655334b.PNG)

After adding one or more files, in order for the next part to work, user must legendize samples to a compliant form. 

Compliant form of samples must be of the form "Fraction"-"Biounit". Example is given here:

![text file example](https://user-images.githubusercontent.com/84333373/118640838-b8bb4900-b7d9-11eb-9ee2-4736fd6d1dcb.PNG)

After legendization and merging datafiles, the interface looks like this:

![initial](https://user-images.githubusercontent.com/84333373/121691256-17b56a80-cac7-11eb-8516-5a9b7db698a6.PNG)

The difference is in the option for Enrichment.


# Enrichment

Clicking Enrichment opens a new window

![xyselector](https://user-images.githubusercontent.com/84333373/121691343-3156b200-cac7-11eb-9054-79d99cec177a.PNG)

- X Value
This is a name of numeric column on which enrichment procedure is measured. In our example of mouse spermatogonia, X Value would be YEL-HLog

- Y Value
This is a name of numeric column that will be the Y axis of the scatterplot

Clicking Load opens a new window

![ned_menu](https://user-images.githubusercontent.com/84333373/121691524-6105ba00-cac7-11eb-8eb4-a5bb0d0d7d7d.PNG)

The upper row contains biounits. The row below contains fractions.
Clicking on the buttons switches from biounit to biounit, or from fraction to fraction, changing the display of the scatterplot and histogram plot.

## Display

Two plots are displayed, right below rows containing fractions. One is scatterplot, and the other is histogram plot. 
On both plots are two red lines, intersecting at a set X value. This X value will be called **threshold**. Clicking on the buttons below the plots changes the position of the two red lines and the threshold. 
The current X value of red lines is displayed in the middle of the buttons. It's also possible to change the coordinate, and the threshold value, by typing in a valid value (integer or float, both x.x and x,x format are accepted). Clicking on the graph also sets the red line where you clicked.

Changing the position of the red lines changes the textbox in the upper right corner of the graphs. Textbox displays what percentage of the data is to the left and to the right of the red lines at any given time. 

To the right of graphs is a table detailing threshold of all biounits. After all thresholds are set adequately, the display looks like this.

![ned_menu_after](https://user-images.githubusercontent.com/84333373/121692871-d32ace80-cac8-11eb-9f3f-10d0ace6bed4.PNG)

Clicking "Load" enables calculation of number, enrichment, and depletion.

## Enrichment calculation

What will be calculated next is the percentage of *X Values* **above** the threshold in other fractions.

- **%Number** will be equal to the percentage of "PM" fraction that is above the threshold
- **Enrichment** is calculated as a ratio of percentage of "S" fraction above the calculated percentile value, and percentage of "PM" fraction above that same value
- **Depletion** is calculated as a ratio of percentage of "PM" fraction above the calculated percentile value, and percentage of "M" fraction above that same value

Standard deviation for the latter two is calculated through [*propagation of error/uncertainty*](https://en.wikipedia.org/wiki/Propagation_of_uncertainty#Resistance_measurement)

There are two main options to calculate means and standard deviations.

### Replicate

If technical replicates of biounits and fraction were taken - one biounit/fraction measured multiple times on Guava Muse cytometer, clicking on Replicate, and then Calculate gives the following graph:

![ned_menu_repllicate](https://user-images.githubusercontent.com/84333373/121696637-8cd76e80-cacc-11eb-9da5-43dcad4bc3f0.PNG)

There is a tabular representation of results to the right, and graphical representation of tabular results below. 

### Bootstrap

Bootstrap option works by pooling all technical replicates (or not, if there are no technical replicate), then "resampling" from that pool a number of times. 
For example, if the pool were (1,2,5,6,7), and sampling 3 values from that pool 2 times would yield (1,2,5) or (2,5,7). The number of times a "resample" will happen is dicated by **Iterations** and it can only be a positive integer. The size or a "resampled" sample is dictated by **Sample Size%** and it can be any number between 1 and 100. Be warned, for extreme values, e.g. 10000 iterations, the procedure will take some time. The result will be given same as for the *Replicate* option. 

![ned_menu_bootstrap](https://user-images.githubusercontent.com/84333373/121697838-be046e80-cacd-11eb-9739-4a518a9314bb.PNG)