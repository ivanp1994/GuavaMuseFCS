# Experimental

This branch is identical to **gui_enrichment** with one tiny difference in the enrichment procedure.

After finishing debris removal and entering enrichment calculation, the *Number, Enrichment, & Depletion Menu* is a bit different.

![experimental_1](https://user-images.githubusercontent.com/84333373/133120401-019d49d3-6d3f-4a8d-9aa5-975868f7d876.PNG)

Right below the scatterplot and histogram, there is a new graph titled **Univariate Gaussian density plot for S fraction of {biounit}**.

This graph is a normal distribution of S fraction of its respective Biounit. The enrichment threshold, controlled by a yellow line on either scatterplot or histogram, is marked on this new plot, and the CDF of that threshold with respect to normal distribution is calculated and displayed in the textbox as **The purple part is {CDF}**. The part under the graph is colored purple.

The rational behind this branch is following. It's almost impossible to enrich/purify with a procedure with 100% purity. So we will always have some leftover cells. This can be seen in histogram that has one giant peak to the right (in our experimental dataset, this would be spermatogonial cells) and one smaller peak to the left (representing other autoflourescent cells). Likewise, the right peak's left tail is heavier that it's right tail, and it is entirely possible that the heavyness of it's left tail is due to overlap of right peak's left tail and left peak's right tail.

In order to effectively remove the left peak's interference, we iteratively apply [gaussian mixture model](https://en.wikipedia.org/wiki/Mixture_model) through sklearn's mixture library. The algorithm is following

1. Apply univariate gaussian mixture model on our S fraction's X value - yielding mean and standard deviation.
2. Set a threshold to be equal mean - 2.5 standard deviations. 
3. Remove data that has X value below the threshold.
4. Repeat procedure.

The procedure repeats until the ratio of new and old threshold is within (0.999,1.001).

The idea is that we can "purify" the targeted fraction (spermatogonia in our case) from a relatively high purity -dont have strength update later



