# Impacts

Impacts documentation to come here. 

# Bias studies

Here we provide a script to perform a simple bias study. 

## Inputs

The only pre-requisite is a workspace with a single category, 
and therefore a single multipdf (the object that controls the envelope method) 
and a single pdf index corresponding to the choice of functional form.

To create this, it's simple to use the existing combineCards functionality, for example:
```
combineCards.py Datacard.txt --ic cat_name > Datacard_cat_name.txt
```

This creates a .txt datacard with only categories matching the reg exp `cat_name` included. 
Be careful: you will probably have to manually delete some pdfindex lines at the bottom; 
the script does not know that these correspond to the analysis categories, 
and therefore will leave them all in (you only want the one corresponding to the category you are studying). 

Once that is done, you can run your usual `text2workspace` command to generate the `-d, --datacard` input for this script. 

## Usage

The script is split into three different stages:
 * `-t, --toys`:  throw and save a total of `-n,--nToys` toys for each of the candidate functions included in the envelope
 * `-f, --fits`:  fit each of those toys and extract the uncertainty
 * `-p, --plots`: plot the pull distribution of the resulting fits

You can then inspect the output plots and hope to see an approximately gaussian shape with zero mean and unit width.
Normally, provided that the absolute value of the mean is less than 0.14, this is considered satisfactory. 

The three steps can be run in one go, but it's probably safer to run them one-by-one. 
Here is an example:

```
python3 RunBiasStudy.py -d Datacard_mu_ggH_cat0.root -t -b ${cat}
python3 RunBiasStudy.py -d Datacard_mu_ggH_cat0.root -b ${cat} -f -c "--setParameterRanges r=-5,5 --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints" 
python3 RunBiasStudy.py -d Datacard_mu_ggH_cat0.root -b ${cat} -p --gaussianFit
```
The options for the second step are passed to combine; these are recommended to get the fit to converge. 
The additional option on the plotting is fairly self-explanatory; it adds a gaussian fit to the output plot.

Intead of running step-by-step, you can run the entire bias test at once with the run_Bias_nominal.sh script. For this script to run properly, the datacards by category need to have already been created in  ../../Datacard_tutorial_${cat}_mu_inclusive.root. In the bash script, the categories are looped over which may also need to be adjusted if the categorization has changed.

```
bash run_Bias_nominal.sh
```

## More options

There are various things one can tweak for these studies. 
Here is a list of the common options: 
 * `-n,--nToys`: the default number of toys is 1000 per function, but can be lowered or raised. 
 * `-e,--expectSignal`: the injected signal strength is 1 by default, but zero can also be checked, or higher values for searches. 
 * `-s,--seed`: the default value of -1 finds a random seed; you can fix this for reproducility if you prefer.
 * `--poi`: if your parameter of interest is called something other than `r`, say so here.
 * `--split`: default number of toys to be thrown or fits to be performed in one go. Set to 500 but may need to be lowered for memory reasons if you have a more complicated fit. 
 * `--selectFunction`: you can specify a string here to only select certain functions for these studies (e.g. `bern` to match all Bernstein polynomials, `exp1` to match just the first-order exponential).

## Plotting
After the bias study is run, to generate the bias study plots, run
```
python3 plotBiasResults.py -c <outputCSVname>.csv
```

## new bias fit
1.Remember to `make` and `make clean` in the bkg dir to make the changes to bkg work
2.Use `bash preparefiles.sh` to prepare the input workspace for the bias fit, notice this will also change the workspace in `Combine` dir
3.Use `python3 create_condor_jobs.py` to create the condor config, this is for the condor on ustc cluster, please change to your own setting, the CMSSW is not needed to be upload to condor.
4.Submit the created condor config
5.`python3 merge_bias_results.py` to get the merged results
