#!/usr/bin/env python
import os
import csv
import numpy as np

from biasUtils import *

from optparse import OptionParser
parser = OptionParser()
parser.add_option(
    "-d","--toyDatacard",
    default="Datacard_toy.root"
)

parser.add_option(
    "-w","--fitDatacard",
    default="Datacard_fit.root"
)

parser.add_option(
    "--toyWorkspace",
    default="w"
)

parser.add_option(
    "--fitWorkspace",
    default="w"
)
parser.add_option("-t","--toys",action="store_true", default=False)
parser.add_option("-n","--nToys",default=1000,type="int")
parser.add_option("-f","--fits",action="store_true", default=False)
parser.add_option("-p","--plots",action="store_true", default=False)
parser.add_option("-e","--expectSignal",default=1.,type="float")
parser.add_option("-m","--mH",default=125.,type="float")
parser.add_option("-c","--combineOptions",default="")
parser.add_option("-s","--seed",default=-1,type="int")
parser.add_option("--dryRun",action="store_true", default=False)
parser.add_option("--poi",default="r")
parser.add_option("--split",default=500,type="int")
parser.add_option("--selectFunction",default=None)
parser.add_option("--gaussianFit",action="store_true", default=False)
parser.add_option("-b", "--BDTCategory", default="")
parser.add_option("--generateCSV",action="store_true", default=False)
parser.add_option("--outCSV", dest="outCSV", default="bias_results.csv", help="Filename for the yields output CSV file")
parser.add_option("--statOnly", action="store_true", default=False, help="Freeze CMS_hmm_peak/sigma signal-shape parameters in toy and fit workspaces")

(opts,args) = parser.parse_args()
#print()
if opts.nToys>opts.split and not opts.nToys%opts.split==0: raise RuntimeError('The number of toys %g needs to be smaller than or divisible by the split number %g'%(opts.nToys, opts.split))


import ROOT as r
r.gROOT.SetBatch(True)
r.gStyle.SetOptStat(2211)

toyWS = r.TFile(opts.toyDatacard).Get(opts.toyWorkspace)

fitWS = r.TFile(opts.fitDatacard).Get(opts.fitWorkspace)

toyPdfs = rooArgSetToList(toyWS.allPdfs())

toyMultipdfName = None

for pdf in toyPdfs:
    if pdf.InheritsFrom("RooMultiPdf"):
        if toyMultipdfName is not None:
            raiseMultiError()

        toyMultipdfName = pdf.GetName()

        print(
            "Toy multipdf:",
            toyMultipdfName
        )


toyMultipdf = toyWS.pdf(toyMultipdfName)

fitPdfs = rooArgSetToList(fitWS.allPdfs())

fitMultipdfName = None

for pdf in fitPdfs:

    if pdf.InheritsFrom("RooMultiPdf"):

        if fitMultipdfName is not None:
            raiseMultiError()

        fitMultipdfName = pdf.GetName()

        print(
            "Fit multipdf:",
            fitMultipdfName
        )


fitMultipdf = fitWS.pdf(fitMultipdfName)
#print(multipdf)

toyIndexName=None

for var in rooArgSetToList(toyWS.allCats()):

    if var.GetName().startswith("pdfindex"):

        toyIndexName=var.GetName()

        print(
            "Toy index:",
            toyIndexName
        )

        break
        
fitIndexName=None

for var in rooArgSetToList(fitWS.allCats()):

    if var.GetName().startswith("pdfindex"):

        fitIndexName=var.GetName()

        print(
            "Fit index:",
            fitIndexName
        )

        break

from collections import OrderedDict as od
toyIndexNameMap = od()

for ipdf in range(toyMultipdf.getNumPdfs()):

    if opts.selectFunction is not None:

        if not toyMultipdf.getPdf(ipdf).GetName().count(opts.selectFunction):
            continue


    toyIndexNameMap[ipdf] = toyMultipdf.getPdf(ipdf).GetName()

fitIndexNameMap = od()

for ipdf in range(fitMultipdf.getNumPdfs()):

    fitIndexNameMap[ipdf] = fitMultipdf.getPdf(ipdf).GetName()    

# --statOnly: freeze the new signal-shape parameters (CMS_hmm_peak/sigma_*)
# in both the toy-generating and the fitting workspace.
def signal_shape_vars(ws):
    names = []
    for v in rooArgSetToList(ws.allVars()):
        n = v.GetName()
        if n.endswith("_%s"%opts.BDTCategory) and (n.startswith("CMS_hmm_peak_") or n.startswith("CMS_hmm_sigma_")):
            names.append(n)
    return names

toyStatVars = signal_shape_vars(toyWS) if opts.statOnly else []
fitStatVars = signal_shape_vars(fitWS) if opts.statOnly else []
if opts.statOnly:
    print("statOnly toy signal-shape vars:", toyStatVars)
    print("statOnly fit signal-shape vars:", fitStatVars)

toyStatSet = "".join(",%s=0"%n for n in toyStatVars)
toyStatFreeze = (","+",".join(toyStatVars)) if toyStatVars else ""
fitStatSet = "".join(",%s=0"%n for n in fitStatVars)
fitStatFreeze = (","+",".join(fitStatVars)) if fitStatVars else ""

if opts.toys:
    print("\nCreating toys")
    if not os.path.isdir('BiasToys'): os.system('mkdir -p BiasToys')
    os.system('rm -f BiasToys/*.root')
    toyCmdBase = 'combine -m %.4f -d %s -M GenerateOnly --expectSignal %.4f -s %g --saveToys'%(opts.mH, opts.toyDatacard, opts.expectSignal, opts.seed)
    #print("Base toy command:")
    #print(toyCmdBase)
    #print()
    #quit()
    for ipdf,pdfName in toyIndexNameMap.items():
        name = shortName(pdfName)
        print("Creating toys for: " + name)
        if opts.nToys > opts.split:
            for isplit in range(opts.nToys//opts.split):
                toyCmd = toyCmdBase + ' -t %g -n _%s_split%g --setParameters %s=%g,r=1%s --freezeParameters %s%s'%(opts.split, name, isplit, toyIndexName, ipdf, toyStatSet, toyIndexName, toyStatFreeze)
                print("Run toy command:")
                #print(toyCmd + "\n")
                run(toyCmd, dry=opts.dryRun)
                os.system('mv higgsCombine_%s* %s'%(name, toyName(name,opts.BDTCategory,split=isplit)))
        else: 
            toyCmd = toyCmdBase + ' -t %g -n _%s --setParameters %s=%g,r=1%s --freezeParameters %s%s'%(opts.nToys, name, toyIndexName, ipdf, toyStatSet, toyIndexName, toyStatFreeze)
            print("Run toy command:")
            #print(toyCmd + "\n")
            run(toyCmd, dry=opts.dryRun)
            os.system('mv higgsCombine_%s* %s'%(name, toyName(name, opts.BDTCategory)))
            
print()

if opts.fits:

    if not os.path.isdir('BiasFits'):
        os.system('mkdir -p BiasFits')

    os.system('rm -f BiasFits/*.root')


    fitCmdBase = (
        'combine '
        '-m %.4f '
        '-d %s '
        '-M MultiDimFit '
        '-P %s '
        '--algo singles '
        '--robustFit 1 '
        '--cminFallbackAlgo Minuit2,Migrad,0:0.1 '
        '--cminFallbackAlgo Minuit2,Simplex,0:0.5 '
        '--saveSpecifiedIndex %s '
        '%s'
        %
        (
            opts.mH,
            opts.fitDatacard,
            opts.poi,
            fitIndexName,
            opts.combineOptions
        )
    )


    for ipdf,pdfName in toyIndexNameMap.items():

        name = shortName(pdfName)

        print(
            "Discrete profiling fit for toy:",
            name
        )


        if opts.nToys > opts.split:


            for isplit in range(opts.nToys//opts.split):


                fitCmd = (
                    fitCmdBase
                    +
                    ' -t %g '
                    '-n _%s_split%d '
                    '--toysFile=%s '
                    '--setParameters r=1%s '
                    '--freezeParameters MH%s'
                    %
                    (
                        opts.split,
                        name,
                        isplit,
                        toyName(
                            name,
                            opts.BDTCategory,
                            split=isplit
                        ),
                        fitStatSet,
                        fitStatFreeze
                    )
                )


                print(fitCmd)

                run(
                    fitCmd,
                    dry=opts.dryRun
                )


                os.system(
                    'mv higgsCombine_%s* %s'
                    %
                    (
                        name,
                        fitName(
                            name,
                            "discrete",
                            opts.BDTCategory,
                            split=isplit
                        )
                    )
                )


            run(
                'hadd %s BiasFits/*%s*split*.root'
                %
                (
                    fitName(
                        name,
                        "discrete",
                        opts.BDTCategory
                    ),
                    name
                ),

                dry=opts.dryRun
            )


        else:


            fitCmd = (
                fitCmdBase
                +
                ' -t %g '
                '-n _%s '
                '--toysFile=%s '
                '--setParameters r=1%s '
                '--freezeParameters MH%s'
                %
                (
                    opts.nToys,
                    name,
                    toyName(
                        name,
                        opts.BDTCategory
                    ),
                    fitStatSet,
                    fitStatFreeze
                )
            )


            print(fitCmd)


            run(
                fitCmd,
                dry=opts.dryRun
            )


            os.system(
                'mv higgsCombine_%s* %s'
                %
                (
                    name,
                    fitName(
                        name,
                        "discrete",
                        opts.BDTCategory
                    )
                )
            )

if opts.plots:

    if not os.path.isdir('BiasPlots'):
        os.system('mkdir -p BiasPlots')


    for ipdf,pdfName in toyIndexNameMap.items():

        name = shortName(pdfName)


        fitFile = fitName(
            name,
            "discrete",
            opts.BDTCategory
        )


        tfile = r.TFile(fitFile)


        if not tfile or tfile.IsZombie():

            print(
                "Missing fit file:",
                fitFile
            )

            continue


        tree = tfile.Get("limit")


        if not tree:

            print(
                "Missing limit tree:",
                fitFile
            )

            continue


        print(
            name,
            "entries =",
            tree.GetEntries()
        )


        #
        # store best-fit pdf statistics
        #
        bestIndexCount = {}
        bestFunctionCount = {}


        #
        # initialize all possible pdfs
        #
        for idx,func in fitIndexNameMap.items():

            bestIndexCount[idx] = 0

            bestFunctionCount[
                shortName(func)
            ] = 0



        pullHist = r.TH1F(
            "pullsForTruth_%s"%name,
            "Discrete profiling pull %s"%name,
            160,
            -8,
            8
        )


        pullHist.GetXaxis().SetTitle("Pull")
        pullHist.GetYaxis().SetTitle("Entries")

        pull_values = []

        for itoy in range(opts.nToys):


            #
            # best fit entry
            #
            tree.GetEntry(3*itoy)


            if tree.quantileExpected != -1:
                continue


            bf = tree.r


            #
            # get best-fit pdf index
            #
            if hasattr(tree, fitIndexName):

                best_index = int(
                    getattr(tree, fitIndexName)
                )


                if best_index in bestIndexCount:

                    bestIndexCount[best_index] += 1


                    best_func = shortName(
                        fitIndexNameMap[best_index]
                    )


                    bestFunctionCount[best_func] += 1


            #
            # lower uncertainty
            #
            tree.GetEntry(3*itoy+1)


            if abs(tree.quantileExpected+0.32)>0.001:
                continue


            lo = tree.r



            #
            # upper uncertainty
            #
            tree.GetEntry(3*itoy+2)


            if abs(tree.quantileExpected-0.32)>0.001:
                continue


            hi = tree.r



            unc = 0.5*(hi-lo)


            if unc>0:

                pull = (bf-opts.expectSignal)/unc

                pullHist.Fill(pull)

                pull_values.append(pull)



        canv=r.TCanvas()

        pullHist.Draw()



        #
        # Gaussian fit
        #
        if opts.gaussianFit:


            r.gStyle.SetOptFit(111)


            result=pullHist.Fit(
                "gaus",
                "S"
            )


            fit=pullHist.GetFunction("gaus")


            if fit and int(result)==0:

                bias_pull=fit.GetParameter(1)

                bias_pull_err=fit.GetParError(1)

                fit_sigma=fit.GetParameter(2)

                fit_sigma_err=fit.GetParError(2)

                fit_chi2=fit.GetChisquare()

                fit_valid=1


            else:

                bias_pull=float("nan")
                bias_pull_err=float("nan")
                fit_sigma=float("nan")
                fit_sigma_err=float("nan")
                fit_chi2=float("nan")
                fit_valid=0



            canv.SaveAs(
                "%s.pdf"
                %
                plotName(
                    name,
                    "discrete",
                    opts.BDTCategory
                )
            )
            
            
        if len(pull_values) > 0:
            bias_pull_median = np.median(pull_values)
        else:
            bias_pull_median = float("nan")


        #
        # CSV output
        #
        if opts.generateCSV:


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
                "bias_pull_err",

                "fit_sigma",
                "fit_sigma_err",

                "fit_chi2",

                "fit_valid"

            ]


            csv_exists=os.path.isfile(opts.outCSV)



            with open(
                opts.outCSV,
                "a",
                newline=""
            ) as f:


                writer=csv.DictWriter(
                    f,
                    fieldnames=fields
                )


                if not csv_exists:
                    writer.writeheader()



                writer.writerow({

                    "category":
                        opts.BDTCategory,


                    "toy_function":
                        name,


                    "toy_index":
                        ipdf,


                    "fit_method":
                        "discrete",


                    #
                    # save dictionary directly
                    #
                    "bestfit_index_counts":
                        str(bestIndexCount),


                    "bestfit_function_counts":
                        str(bestFunctionCount),


                    "n_toys":
                        opts.nToys,


                    "bias_pull":
                        bias_pull,
                        
                    "bias_pull_median":
                        bias_pull_median,

                    "bias_pull_err":
                        bias_pull_err,


                    "fit_sigma":
                        fit_sigma,


                    "fit_sigma_err":
                        fit_sigma_err,


                    "fit_chi2":
                        fit_chi2,


                    "fit_valid":
                        fit_valid

                })