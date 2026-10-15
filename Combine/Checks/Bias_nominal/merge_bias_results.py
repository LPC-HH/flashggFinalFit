#!/usr/bin/env python3

import ROOT as r
import glob
import os
import csv
import ast
import numpy as np


r.gROOT.SetBatch(True)


# ==========================
# Configuration
# ==========================

inputDir="BiasJobs"

outputDir="summary"

os.makedirs(outputDir,exist_ok=True)

plotDir=os.path.join(
    outputDir,
    "plots"
)

os.makedirs(plotDir,exist_ok=True)


outputCSV=os.path.join(
    outputDir,
    "bias_results_final.csv"
)


expectSignal=1.0


categories=[
    "ggHcat1",
    "ggHcat2",
    "ggHcat3",
    "ggHcat4",
    "ggHcat5",
    "ggHcat6",
    "VBFcat2",
    "VBFcat3",
    "VBFcat4",
    "VBFcat5",
    "VBFcat6",
]



# ==========================
# Read split CSV
# ==========================

def collect_csv(cat,pdf):

    pattern=(
        f"{inputDir}/{cat}/pdf{pdf}/split*/"
        "bias_*.csv"
    )

    return glob.glob(pattern)



def merge_csv_info(files):

    toy_function=None
    toy_index=None
    fit_method=None


    bestIndexCount={}
    bestFunctionCount={}


    for f in files:

        print("Reading csv:",f)


        with open(f) as fin:

            reader=csv.DictReader(fin)


            for row in reader:


                toy_function=row["toy_function"]

                toy_index=int(
                    row["toy_index"]
                )

                fit_method=row["fit_method"]



                index_dict=ast.literal_eval(
                    row["bestfit_index_counts"]
                )


                func_dict=ast.literal_eval(
                    row["bestfit_function_counts"]
                )


                for k,v in index_dict.items():

                    k=int(k)

                    bestIndexCount[k]=(
                        bestIndexCount.get(k,0)+v
                    )


                for k,v in func_dict.items():

                    bestFunctionCount[k]=(
                        bestFunctionCount.get(k,0)+v
                    )


    return (
        toy_function,
        toy_index,
        fit_method,
        bestIndexCount,
        bestFunctionCount
    )



# ==========================
# Read ROOT pull
# ==========================

def collect_root(cat,pdf):

    pattern=(
        f"{inputDir}/{cat}/pdf{pdf}/split*/"
        "BiasFits/*split*.root"
    )

    return glob.glob(pattern)



def calculate_pulls(files):

    pulls=[]
    filtered_pulls=[]

    rMin=-20.0
    rMax=20.0
    edgeTolerance=0.001

    for filename in files:

        print("\n================================")
        print("Reading root:",filename)
        print("================================")

        tf=r.TFile.Open(filename)

        if not tf or tf.IsZombie():
            print("  ERROR: cannot open file")
            continue

        tree=tf.Get("limit")

        if not tree:
            print("  ERROR: no limit tree")
            tf.Close()
            continue

        toys={}

        for i in range(tree.GetEntries()):

            tree.GetEntry(i)

            toy=int(tree.iToy)

            if toy not in toys:
                toys[toy]={}

            if tree.quantileExpected==-1:

                toys[toy]["bf"]=tree.r

            elif abs(tree.quantileExpected+0.32)<0.01:

                toys[toy]["lo"]=tree.r

            elif abs(tree.quantileExpected-0.32)<0.01:

                toys[toy]["hi"]=tree.r


        #
        # diagnostics
        #

        n_total=len(toys)

        n_bf=0
        n_lo=0
        n_hi=0
        n_complete=0
        n_bad_unc=0
        n_boundary=0
        n_good=0

        for toy,data in toys.items():

            if "bf" in data:
                n_bf += 1

            if "lo" in data:
                n_lo += 1

            if "hi" in data:
                n_hi += 1

            if not all(
                x in data for x in ["bf","lo","hi"]
            ):
                continue

            n_complete += 1

            unc=0.5*(data["hi"]-data["lo"])

            if unc<=0:
                n_bad_unc += 1
                continue

            pull=(data["bf"]-expectSignal)/unc

            pulls.append(pull)

            hitBoundary=False

            if data["bf"]+unc >= rMax-edgeTolerance:
                hitBoundary=True

            if data["bf"]-unc <= rMin+edgeTolerance:
                hitBoundary=True

            if hitBoundary:

                n_boundary += 1

            else:

                filtered_pulls.append(pull)
                n_good += 1


        print("  ROOT entries      :",tree.GetEntries())
        print("  unique iToy       :",n_total)
        print("  with bf           :",n_bf)
        print("  with lo           :",n_lo)
        print("  with hi           :",n_hi)
        print("  complete bf/lo/hi :",n_complete)
        print("  bad uncertainty   :",n_bad_unc)
        print("  boundary          :",n_boundary)
        print("  usable pull       :",n_good)

        tf.Close()

    return pulls, filtered_pulls



# ==========================
# Main
# ==========================

results=[]



for cat in categories:


    catPlotDir=os.path.join(
        plotDir,
        cat
    )

    os.makedirs(
        catPlotDir,
        exist_ok=True
    )


    pdfDirs=glob.glob(
        f"{inputDir}/{cat}/pdf*"
    )


    for pdfDir in pdfDirs:


        name=os.path.basename(pdfDir)


        if not name[3:].isdigit():
            continue


        pdf=int(name[3:])


        print("\n================")
        print(cat,"PDF",pdf)



        csvFiles=collect_csv(
            cat,
            pdf
        )


        if len(csvFiles)==0:
            continue



        (
            toy_function,
            toy_index,
            fit_method,
            bestIndexCount,
            bestFunctionCount
        )=merge_csv_info(csvFiles)



        rootFiles=collect_root(
            cat,
            pdf
        )


        pulls, filtered_pulls=calculate_pulls(
            rootFiles
        )


        print(
            "Number of pulls:",
            len(pulls)
        )


        if len(pulls)==0:
            continue



        # histogram

        hist=r.TH1F(
            f"{cat}_{pdf}",
            f"{cat} {toy_function};Pull;Entries",
            160,
            -8,
            8
        )


        hist_filtered=r.TH1F(
            f"{cat}_{pdf}_filtered",
            f"{cat} {toy_function};Pull;Entries",
            160,
            -8,
            8
        )


        for p in pulls:
            hist.Fill(p)


        for p in filtered_pulls:
            hist_filtered.Fill(p)



        median=np.median(pulls)
        
        if len(filtered_pulls)>0:
            filtered_median=np.median(filtered_pulls)
        else:
            filtered_median=np.nan


        bias_pull=np.nan
        bias_err=np.nan
        sigma=np.nan
        sigma_err=np.nan
        chi2=np.nan
        valid=0



        if len(pulls)>=5:

            result=hist.Fit(
                "gaus",
                "SQ0"
            )


            func=hist.GetFunction(
                "gaus"
            )


            if func and int(result)==0:


                bias_pull=func.GetParameter(1)

                bias_err=func.GetParError(1)

                sigma=func.GetParameter(2)

                sigma_err=func.GetParError(2)

                chi2=func.GetChisquare()

                valid=1



        # plot

        # plot

        c=r.TCanvas(
            f"c_{cat}_{pdf}",
            "",
            800,
            600
        )


        hist.SetLineColor(r.kBlue)
        hist.SetLineWidth(2)


        hist_filtered.SetLineColor(r.kRed)
        hist_filtered.SetLineWidth(2)



        hist.Draw("hist")


        hist_filtered.Draw(
            "hist same"
        )


        legend=r.TLegend(
            0.65,
            0.75,
            0.88,
            0.88
        )


        legend.AddEntry(
            hist,
            "All toys",
            "l"
        )


        legend.AddEntry(
            hist_filtered,
            "Filtered toys",
            "l"
        )


        legend.Draw()

        c.SaveAs(
            os.path.join(
                catPlotDir,
                f"pdf{pdf}_pull.png"
            )
        )



        results.append(
            {

            "category":cat,

            "toy_function":toy_function,

            "toy_index":toy_index,

            "fit_method":fit_method,


            "bestfit_index_counts":
                str(bestIndexCount),


            "bestfit_function_counts":
                str(bestFunctionCount),


            "n_toys":
                len(pulls),


            "bias_pull":
                bias_pull,


            "bias_pull_median":
                median,


            "filtered_pull_median":
                filtered_median,


            "filtered_event_count":
                len(filtered_pulls),


            "bias_pull_err":
                bias_err,


            "fit_sigma":
                sigma,


            "fit_sigma_err":
                sigma_err,


            "fit_chi2":
                chi2,


            "fit_valid":
                valid

            }
        )



# ==========================
# Write CSV
# ==========================


fields=[

"category",

"toy_function",
"toy_index",

"fit_method",

"bestfit_index_counts",
"bestfit_function_counts",

"n_toys",

"bias_pull",
"bias_pull_median",
"filtered_pull_median",
"filtered_event_count",
"bias_pull_err",

"fit_sigma",
"fit_sigma_err",

"fit_chi2",

"fit_valid"

]


with open(outputCSV,"w",newline="") as f:


    writer=csv.DictWriter(
        f,
        fieldnames=fields
    )

    writer.writeheader()

    writer.writerows(results)



print("\nDone")
print(outputCSV)