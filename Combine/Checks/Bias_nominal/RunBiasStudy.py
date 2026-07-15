#!/usr/bin/env python
import os
import csv

from biasUtils import *

from optparse import OptionParser
parser = OptionParser()
parser.add_option("-d","--datacard",default="Datacard.root")
parser.add_option("-w","--workspace",default="w")
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

(opts,args) = parser.parse_args()
#print()
if opts.nToys>opts.split and not opts.nToys%opts.split==0: raise RuntimeError('The number of toys %g needs to be smaller than or divisible by the split number %g'%(opts.nToys, opts.split))


import ROOT as r
r.gROOT.SetBatch(True)
r.gStyle.SetOptStat(2211)

ws = r.TFile(opts.datacard).Get(opts.workspace)

pdfs = rooArgSetToList(ws.allPdfs())
multipdfName = None
for pdf in pdfs:
    if pdf.InheritsFrom("RooMultiPdf"):
        if multipdfName is not None: raiseMultiError() 
        multipdfName = pdf.GetName()
        print('Conduct bias study for multipdf called %s'%multipdfName)

multipdf = ws.pdf(multipdfName)
#print(multipdf)

varlist = rooArgSetToList(ws.allCats())
indexName = None
for var in varlist:
    if var.GetName().startswith('pdfindex'):
        if indexName is not None: raiseMultiError()
        indexName = var.GetName()
        print('Found index called %s'%indexName)
print()

from collections import OrderedDict as od
indexNameMap = od()
for ipdf in range(multipdf.getNumPdfs()):
    if opts.selectFunction is not None:
        if not multipdf.getPdf(ipdf).GetName().count(opts.selectFunction): continue
    indexNameMap[ipdf] = multipdf.getPdf(ipdf).GetName()

if opts.toys:
    print("\nCreating toys")
    if not os.path.isdir('BiasToys'): os.system('mkdir -p BiasToys')
    os.system('rm -f BiasToys/*.root')
    toyCmdBase = 'combine -m %.4f -d %s -M GenerateOnly --expectSignal %.4f -s %g --saveToys'%(opts.mH, opts.datacard, opts.expectSignal, opts.seed)
    #print("Base toy command:")
    #print(toyCmdBase)
    #print()
    #quit()
    for ipdf,pdfName in indexNameMap.items():
        name = shortName(pdfName)
        print("Creating toys for: " + name)
        if opts.nToys > opts.split:
            for isplit in range(opts.nToys//opts.split):
                toyCmd = toyCmdBase + ' -t %g -n _%s_split%g --setParameters %s=%g,r=1 --freezeParameters %s'%(opts.split, name, isplit, indexName, ipdf, indexName)
                print("Run toy command:")
                #print(toyCmd + "\n")
                run(toyCmd, dry=opts.dryRun)
                os.system('mv higgsCombine_%s* %s'%(name, toyName(name,opts.BDTCategory,split=isplit)))
        else: 
            toyCmd = toyCmdBase + ' -t %g -n _%s --setParameters %s=%g,r=1 --freezeParameters %s'%(opts.nToys, name, indexName, ipdf, indexName)
            print("Run toy command:")
            #print(toyCmd + "\n")
            run(toyCmd, dry=opts.dryRun)
            os.system('mv higgsCombine_%s* %s'%(name, toyName(name, opts.BDTCategory)))
            
print()

if opts.fits:
    if not os.path.isdir('BiasFits'): os.system('mkdir -p BiasFits')
    os.system('rm -f BiasFits/*.root')
    fitCmdBase = 'combine -m %.4f -d %s -M MultiDimFit -P %s --algo singles %s --robustFit 1'%(opts.mH, opts.datacard, opts.poi, opts.combineOptions)
    #print("Base fits command:")
    #print(fitCmdBase)
    #quit()
    for ipdf,pdfName in indexNameMap.items():
        name = shortName(pdfName)
        print("Fitting for toy: " + name)
        for fitipdf, fitpdfName in indexNameMap.items():
            fitFxnName = shortName(fitpdfName)
            print("Fitting toy: " + name + " wth pdf model: " + fitFxnName)
            if opts.nToys > opts.split:
                for isplit in range(opts.nToys//opts.split):
                    fitCmd = fitCmdBase + ' -t %g -n _%s_split%g --toysFile=%s --setParameters %s=%g --freezeParameters MH,%s'%(opts.split, name + "toy_" + fitFxnName + "fit", isplit, toyName(name,opts.BDTCategory, split=isplit), indexName, fitipdf, indexName)
                    print("Run fits command:")
                    run(fitCmd, dry=opts.dryRun)
                    os.system('mv higgsCombine_%s* %s'%(name, fitName(name,fitFxnName, opts.BDTCategory, split=isplit)))
                run('hadd %s BiasFits/*%s*%s*split*%s*.root'%(fitName(name, fitFxnName, opts.BDTCategory), opts.BDTCategory, name, fitFxnName), dry=opts.dryRun)
            else:
                fitCmd = fitCmdBase + ' -t %g -n _%s --toysFile=%s --setParameters %s=%g,r=1 --freezeParameters MH,%s'%(opts.nToys, name + "toy_" + fitFxnName + "fit", toyName(name, opts.BDTCategory), indexName, fitipdf, indexName)
                print("Run fits command:")
                #print(fitCmd + "\n")
                #quit()
                run(fitCmd, dry=opts.dryRun)
                #print('mv higgsCombine_%s* %s'%(name, fitName(name, fitFxnName)))
                os.system('mv higgsCombine_%s* %s'%(name, fitName(name, fitFxnName, opts.BDTCategory)))

if opts.plots:
    import numpy as np

    if not os.path.isdir('BiasPlots'):
        os.system('mkdir -p BiasPlots')

    os.system('rm -f BiasPlots/*.root')

    for ipdf,pdfName in indexNameMap.items():

        name = shortName(pdfName)

        for fitipdf, fitpdfName in indexNameMap.items():

            fitFxnName = shortName(fitpdfName)

            tfile = r.TFile(fitName(name, fitFxnName, opts.BDTCategory))

            if not tfile or tfile.IsZombie():
                print("Missing/bad fit file:",
                      fitName(name, fitFxnName, opts.BDTCategory))
                continue

            tree = tfile.Get("limit")

            if not tree:
                print("No limit tree in:",
                      fitName(name, fitFxnName, opts.BDTCategory))
                continue

            print(name,
                  fitFxnName,
                  "entries =",
                  tree.GetEntries())

            if tree.GetEntries() == 0:
                print("No fit entries:",
                      fitName(name, fitFxnName, opts.BDTCategory))
                continue

            pullHist = r.TH1F(
                'pullsForTruth_%s_%s'%(name,fitFxnName),
                '%s pull distribution using %s to fit %s toys'
                %(opts.BDTCategory,fitFxnName,name),
                160,
                -8.,
                8.
            )

            pullHist.GetXaxis().SetTitle('Pull')
            pullHist.GetYaxis().SetTitle('Entries')

            pull_values = []

            for itoy in range(opts.nToys):

                tree.GetEntry(3*itoy)

                if getattr(tree,'quantileExpected') != -1:
                    raiseFailError(itoy,True)
                    continue

                bf = getattr(tree,'r')

                tree.GetEntry(3*itoy+1)

                if not abs(getattr(tree,'quantileExpected')-(-0.32)) < 0.001:
                    raiseFailError(itoy,True)
                    continue

                lo = getattr(tree,'r')

                tree.GetEntry(3*itoy+2)

                if not abs(getattr(tree,'quantileExpected')-(0.32)) < 0.001:
                    raiseFailError(itoy,True)
                    continue

                hi = getattr(tree,'r')

                diff = bf - opts.expectSignal
                unc  = 0.5*(hi-lo)

                if unc > 0.:

                    pull = diff/unc

                    pullHist.Fill(pull)
                    pull_values.append(pull)

            # -----------------------------
            # Median pull (NEW bias metric)
            # -----------------------------

            if len(pull_values) > 0:
                median_pull = float(np.median(pull_values))
            else:
                median_pull = float("nan")

            print(
                "[BIAS] category=%s toy=%s fit=%s median_pull=%.5f"
                %(opts.BDTCategory,
                  name,
                  fitFxnName,
                  median_pull)
            )

            canv = r.TCanvas(
                "c_%s_%s"%(name,fitFxnName),
                "",
                800,
                600
            )

            pullHist.Draw()

            # median line
            medianLine = r.TLine(
                median_pull,
                0,
                median_pull,
                pullHist.GetMaximum()
            )

            medianLine.SetLineColor(r.kRed)
            medianLine.SetLineWidth(3)
            medianLine.Draw("same")

            label = r.TLatex()
            label.SetNDC()
            label.SetTextSize(0.04)

            label.DrawLatex(
                0.58,
                0.85,
                "Median = %.3f"%median_pull
            )

            # ------------------------------------
            # Gaussian fit (diagnostic information)
            # ------------------------------------

            gaus_mean = float("nan")
            gaus_mean_err = float("nan")

            fit_sigma = float("nan")
            fit_sigma_err = float("nan")

            fit_chi2 = float("nan")
            fit_valid = 0

            if opts.gaussianFit:

                r.gStyle.SetOptFit(111)

                fit_result = pullHist.Fit("gaus","SQ")

                fit = pullHist.GetFunction("gaus")

                fit_status = int(fit_result)

                if fit and fit_status == 0:

                    gaus_mean = fit.GetParameter(1)
                    gaus_mean_err = fit.GetParError(1)

                    fit_sigma = fit.GetParameter(2)
                    fit_sigma_err = fit.GetParError(2)

                    fit_chi2 = fit.GetChisquare()

                    fit_valid = 1

                    print(
                        "[GAUS] mean=%.5f +/- %.5f sigma=%.5f +/- %.5f"
                        %(gaus_mean,
                          gaus_mean_err,
                          fit_sigma,
                          fit_sigma_err)
                    )

                else:

                    print(
                        "WARNING: Gaussian fit failed for %s %s %s"
                        %(name,
                          fitFxnName,
                          opts.BDTCategory)
                    )

            canv.SaveAs(
                '%s.pdf'
                %plotName(name,
                          fitFxnName,
                          opts.BDTCategory)
            )

            canv.SaveAs(
                '%s.png'
                %plotName(name,
                          fitFxnName,
                          opts.BDTCategory)
            )

            # ------------------------
            # CSV output
            # ------------------------

            if opts.generateCSV:

                fields = [
                    "category",
                    "toy_function",
                    "fit_function",
                    "n_toys",

                    "bias_pull",      # median pull
                    "gaus_mean",
                    "gaus_mean_err",

                    "fit_sigma",
                    "fit_sigma_err",
                    "fit_chi2",
                    "fit_valid"
                ]

                csv_exists = os.path.isfile(opts.outCSV)

                with open(opts.outCSV,
                          mode='a',
                          newline='') as f:

                    writer = csv.DictWriter(
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

                        "fit_function":
                            fitFxnName,

                        "n_toys":
                            opts.nToys,

                        # MEDIAN PULL = BIAS
                        "bias_pull":
                            median_pull,

                        "gaus_mean":
                            gaus_mean,

                        "gaus_mean_err":
                            gaus_mean_err,

                        "fit_sigma":
                            fit_sigma,

                        "fit_sigma_err":
                            fit_sigma_err,

                        "fit_chi2":
                            fit_chi2,

                        "fit_valid":
                            fit_valid
                    })

            tfile.Close()