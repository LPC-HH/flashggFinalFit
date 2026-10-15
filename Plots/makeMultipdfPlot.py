import os, sys
import re
from optparse import OptionParser
import ROOT
import pandas as pd
import numpy as np
import glob
import pickle
import math
import json
import csv
from collections import OrderedDict as od

from commonTools import *
from commonObjects import *

#CSVFILE="out_Yields.csv"

def calc_pull_metrics(hdata, hfit):

    pulls = []

    for ibin in range(1, hdata.GetNbinsX()+1):

        x = hdata.GetBinCenter(ibin)

        if (x > blindingRegion[0]) and (x < blindingRegion[1]):
            continue

        d = hdata.GetBinContent(ibin)
        e = hdata.GetBinError(ibin)

        if e <= 0:
            continue

        pdf_bin = hfit.FindBin(x)
        f = hfit.GetBinContent(pdf_bin)

        pulls.append((d-f)/e)

    pulls = np.asarray(pulls)

    if len(pulls) < 3:
        return None

    # -------------------
    # Durbin-Watson
    # -------------------

    dw = np.sum(np.diff(pulls)**2) / np.sum(pulls**2)

    # -------------------
    # neighbour product
    # -------------------

    prod = np.sum(pulls[:-1]*pulls[1:])

    # -------------------
    # lag1 correlation
    # -------------------

    r = np.corrcoef(pulls[:-1],pulls[1:])[0,1]

    return dw,prod,r
    
def calc_chi2(hdata, hfit, bname, n):#n: conversion factor from plotted contents to raw counts (1.0 for counts)

    chi2 = 0.
    nbin = 0

    for ibin in range(1, hdata.GetNbinsX()+1):

        x = hdata.GetBinCenter(ibin)

        # only sidebands
        inSB = ((SB1_low <= x <= SB1_high) or
                (SB2_low <= x <= SB2_high))

        if not inSB:
            continue

        # histograms hold raw event counts -> y is the observed number of events
        y = hdata.GetBinContent(ibin)/n

        pdf_bin = hfit.FindBin(x)
        f = hfit.GetBinContent(pdf_bin)/n

        #
        # Same asymmetric Poisson uncertainty as fTest.cpp
        #
        if y == 0:
            eyl = 0.0
            eyh = ROOT.Math.gamma_quantile_c(
                0.1586552539,
                1.0,
                1.0
            )
        else:
            eyl = y - ROOT.Math.gamma_quantile(
                0.1586552539,
                y,
                1.0
            )

            eyh = ROOT.Math.gamma_quantile_c(
                0.1586552539,
                y + 1.0,
                1.0
            ) - y

        sigma = eyl if (y > f) else eyh

        if sigma <= 0:
            continue

        pull = (y - f) / sigma

        chi2 += pull * pull
        nbin += 1

    # polynomial order = number of free parameters
    m = re.search(r'(\d+)$', bname)
    npar = int(m.group(1)) if m else 0

    ndof = nbin - npar

    if ndof <= 0:
        return None

    return chi2, ndof, chi2 / ndof
    
    
def get_options():
  parser = OptionParser()
  parser.add_option("--inputWSFile", dest="inputWSFile", default=None, help="Input multipdf RooWorkspace file")
  parser.add_option("--cat", dest="cat", default="RECO_0J_PTH_0_10_Tag0", help="Analysis category")
  parser.add_option("--unblind", dest="unblind", default=False, action="store_true", help="Unblind signal region")
  parser.add_option("--blindingRegion", dest="blindingRegion", default="123,127", help="Region in xvar to blind")
  parser.add_option("--doZeroes", dest="doZeroes", default=False, action="store_true", help="Add error of unity to zero bins to show on plot")
  parser.add_option("--ext", dest="ext", default='', help="Extension for saving")
  parser.add_option("--mass", dest="mass", default=125.38, help="Higgs mass")
  parser.add_option("--xvar", dest="xvar", default="CMS_hgg_mass,m_{#mu#mu},GeV", help="X-variable: name,title,units")
  parser.add_option("--nBins", dest="nBins", default=160, type='int', help=" 0.25 GeV per bin, Number of bins")
  parser.add_option("--pdfNBins", dest="pdfNBins", default=3200, type='int', help="Number of bins")
  parser.add_option("--translateCats", dest="translateCats", default=None, help="JSON to store cat translations")
  parser.add_option("--inputSignalWSFile", dest="inputSignalWSFile", default=None, help="Input wsig_13TeV RooWorkspace file. If not none this will add signal to plot")
  parser.add_option("--outCSV", dest="outCSV", default="out_yields.csv", help="Filename for the yields output CSV file")
  
  return parser.parse_args()
(opt,args) = get_options()

if opt.inputWSFile is not None:
  print((" --> Opening workspace: %s"%opt.inputWSFile))
  f = ROOT.TFile(opt.inputWSFile)
  w = f.Get("multipdf")

SB1_low, SB1_high = 110, 123 
SB2_low, SB2_high = 127, 150

yields = [] #FWHM, totalSig, totalBKG, BKGHWHM, SigHWHM

# Define blinding region
blindingRegion = [float(opt.blindingRegion.split(",")[0]),float(opt.blindingRegion.split(",")[1])]
# Define xvariable and categories
xvar = w.var(opt.xvar.split(",")[0])
weight = ROOT.RooRealVar("weight","weight",0)
xvar.SetTitle(opt.xvar.split(",")[1])
xvar.setPlotLabel(opt.xvar.split(",")[1])
xvar.setUnit(opt.xvar.split(",")[2])
xvar.setRange("SB1", SB1_low, SB1_high)
xvar.setRange("SB2", SB2_low, SB2_high)
xvar_arglist, xvar_argset = ROOT.RooArgList(xvar), ROOT.RooArgSet(xvar)

print("\n=== XVAR DEBUG ===")
print("Name:", xvar.GetName())
print("xmin =", xvar.getMin())
print("xmax =", xvar.getMax())
print("nbins =", xvar.getBins())
print("=================\n")

# Exact multipdf object and pdfindex
multipdf = w.pdf("CMS_hgg_%s_13TeV_bkgshape"%opt.cat)
pdfindex_bf = w.cat("pdfindex_%s_13TeV"%opt.cat).getIndex()
bpdf_bf_name = None
bpdfs = od()
for ipdf in range(multipdf.getNumPdfs()): 
  bpdfs[multipdf.getPdf(ipdf).GetName()] = w.pdf(multipdf.getPdf(ipdf).GetName())
  if ipdf == pdfindex_bf: bpdf_bf_name = multipdf.getPdf(ipdf).GetName()

print("=== Best fit pdf:", bpdf_bf_name, "===")
bpdf_bf = bpdfs[bpdf_bf_name]
bpdf_bf.getParameters(ROOT.RooArgSet(xvar)).Print("v")


print("\n=== FUNCTION VALUE DEBUG ===")

test_points = [110.125, 113.625, 140.125, 148.125]

for x in test_points:
    xvar.setVal(x)
    val = bpdf_bf.getVal(ROOT.RooArgSet(xvar))
    print(f"x = {x:.3f} -> pdf = {val:.10f}")

print("===========================\n")


# ---------------------------------------------------------------
# Normalization convention
# Everything drawn in this script is expressed as raw event counts
# in one data-sized bin (opt.nBins bins across the xvar range), so
# every histogram is directly comparable to the data points.
#   * a histogram made from a pdf stores (pdf value * bin width of
#     that histogram), so the factor binWidth/pdfBinWidth converts
#     it into the expected number of events in one data-sized bin
#     (= pdf value * binWidth).
#   * the data histogram is never rescaled: its contents are the
#     raw event counts and the kPoisson errors are then correct.
# ---------------------------------------------------------------
xvar_low, xvar_high = xvar.getMin(), xvar.getMax()
binWidth    = (xvar_high - xvar_low) / float(opt.nBins)     # width of a data bin
pdfBinWidth = (xvar_high - xvar_low) / float(opt.pdfNBins)  # width of a drawn pdf bin
pdfToDataBin = binWidth / pdfBinWidth                       # == opt.pdfNBins/opt.nBins
print("[INFO] data bin width = %s GeV | pdf bin width = %s GeV"%(binWidth,pdfBinWidth))

# Bkg yield of the best fit pdf as stored in the workspace (used for cross checks)
bkgshape_norm_ws = w.var("CMS_hgg_%s_13TeV_bkgshape_norm"%opt.cat).getVal()

hists = od()

d = w.data("roohist_data_mass_%s"%opt.cat)
# Raw event counts per bin - no scaling is ever applied to this histogram
hists['data'] = xvar.createHistogram("h_data", ROOT.RooFit.Binning(opt.nBins,xvar.getMin(),xvar.getMax()))
hists['data'].SetBinErrorOption(ROOT.TH1.kPoisson)

if opt.unblind: d.fillHistogram(hists['data'],xvar_arglist)
else: d.reduce("%s<%f|%s>%f"%(xvar.GetName(),blindingRegion[0],xvar.GetName(),blindingRegion[1])).fillHistogram(hists['data'],xvar_arglist)

data_sb_integral = 0
for ibin in range(1, hists['data'].GetNbinsX()+1):
    bcenter = hists['data'].GetBinCenter(ibin)
    if (bcenter >= SB1_low and bcenter <= SB1_high) or (bcenter >= SB2_low and bcenter <= SB2_high):
        data_sb_integral += hists['data'].GetBinContent(ibin)

print("\n\n\n\n")
print("data_sb_integral:", data_sb_integral)
print("\n\n\n\n")

for bname, bpdf in list(bpdfs.items()):
  hists[bname] = bpdf.createHistogram("h_%s"%bname,xvar,ROOT.RooFit.Binning(opt.pdfNBins,xvar.getMin(),xvar.getMax()))
  # Match the pdf shape to the data in the sidebands: the pdf is unit
  # normalized, so the total number of expected events is data_sb_integral/pdf_sb_integral
  pdf_sb_integral = bpdf.createIntegral(ROOT.RooArgSet(xvar),ROOT.RooFit.NormSet(xvar),ROOT.RooFit.Range("SB1,SB2")).getVal()
  scale = data_sb_integral / pdf_sb_integral
  # pdf curve (fine binning): expected events in one data-sized bin
  hists[bname].Scale(scale*pdfToDataBin)

  if bname == bpdf_bf_name:
    # Same envelope binned as the data (used for pulls, chi2 and the ratio pads).
    # Its bins already have the data width, so only the sideband matching is needed.
    hists["%s_nBins"%bname] = bpdf.createHistogram("h_%s_nBins"%bname,xvar,ROOT.RooFit.Binning(opt.nBins,xvar.getMin(),xvar.getMax()))
    hists["%s_nBins"%bname].Scale(scale)

#Scale pdf histograms to match data
# All histograms are now in raw event counts per data-sized bin:
#   data         -> untouched raw counts
#   bkg envelope -> expected events, matched to the data sidebands
#   signal       -> expected events, scaled by its physical yield
# so no additional bin-width scaling must be applied here.

# Extract data histogram



if opt.doZeroes:
  for ibin in range(1,hists['data'].GetNbinsX()+1):
    bcenter = hists['data'].GetBinCenter(ibin)
    # Skip blinded region
    if( not opt.unblind )&(bcenter > blindingRegion[0])&(bcenter < blindingRegion[1]): continue
    if hists['data'].GetBinContent(ibin)==0.:
      hists['data'].SetBinError(ibin,1)
      
metrics = {}

for bname, bpdf in bpdfs.items():

    hfit = hists["%s_nBins"%bname] \
           if ("%s_nBins"%bname) in hists \
           else hists[bname]

    pullMetric = calc_pull_metrics(
        hists['data'],
        hfit
    )

    chi2Metric = calc_chi2(
        hists['data'],
        hfit,
        bname,
        1.0
    )

    metrics[bname] = (
        pullMetric,
        chi2Metric
    )    


'''
bin1 = hists['data'].FindBin(122)
bin2 = hists['data'].FindBin(128)
axis = hists['data'].GetXaxis()
nbins = hists['data'].GetNbinsX()
centers = [axis.GetBinCenter(i) for i in range(1, nbins+1)]
values = np.array([hists['data'].GetBinContent(i) for i in range(1, nbins+1)])
print(values)
#npHistData = np.array(hists['data'])

s = np.sum(values[bin1:bin2])
n = hists['data'].Integral(bin1, bin2)
print(centers)
print(f"-------------- Bin 1: {bin1} | Bin 2: {bin2} --------------")
print(f"-------------- Data Number in HWHM: {n} {s} --------------")'''
# Create ratio histograms
hists_ratio = od()
for bname in bpdfs:
  hists_ratio[bname] = hists[bname]-hists[bpdf_bf_name]

hists_ratio['data'] = hists['data'].Clone()
hists_ratio['data'].Reset()
for ibin in range(1,hists['data'].GetNbinsX()+1):
  bcenter = hists['data'].GetBinCenter(ibin)
  if(not opt.unblind)&(bcenter>blindingRegion[0])&(bcenter<blindingRegion[1]): continue
  bval, berr = hists['data'].GetBinContent(ibin), hists['data'].GetBinError(ibin)
  bkgval = hists["%s_nBins"%bpdf_bf_name].GetBinContent(ibin)
  #print(f"-------------- BKG val in bin: {bkgval} {ibin} --------------")
  hists_ratio['data'].SetBinContent(ibin,bval-bkgval)
  hists_ratio['data'].SetBinError(ibin,berr)

if opt.inputSignalWSFile is not None: 
  doSignal = True
  cat = opt.cat
  fsig = ROOT.TFile(opt.inputSignalWSFile)
  wsig = fsig.Get("wsig_13TeV")
  wsig.var("MH").setVal(float(opt.mass))

  # Extract norms
  norms = od()
  spdfs = od()        # fine binning, for drawing
  spdfs_nBins = od()  # data binning, for yields and window integrals
  signal_norm_total = 0.
  for year in years_to_process:
    allNorms = wsig.allFunctions().selectByName("*%s*normThisLumi"%year)
    for normObj in rooiter(allNorms):
      # Set integrated lumi
      wsig.var("IntLumi").setVal(lumiMap[year]*lumiScaleFactor)
      proc = normObj.GetName().split("hggpdfsmrel_")[-1].split("_%s_"%year)[0]
      k  =  "%s__%s"%(proc,year)
      _id = "%s_%s_%s_%s"%(proc,year,cat,sqrts__)
      norms[k] = wsig.function("%s_%s_normThisLumi"%(outputWSObjectTitle__,_id))

      # Expected number of signal events for this process in this category
      yield_norm = norms[k].getVal()
      signal_norm_total += yield_norm

      pdf = wsig.pdf("%s_%s"%(outputWSObjectTitle__,_id))
      # Drawn curve: the pdf is unit normalized, so scaling by the yield
      # and by binWidth/pdfBinWidth gives the expected events in one data-sized bin
      spdfs[_id] = pdf.createHistogram("h_pdf_%s"%_id,xvar,ROOT.RooFit.Binning(opt.pdfNBins))
      spdfs[_id].Scale(yield_norm*pdfToDataBin)
      # Data-binned version: contents are already in data-sized bins
      spdfs_nBins[_id] = pdf.createHistogram("h_pdf_nBins_%s"%_id,xvar,ROOT.RooFit.Binning(opt.nBins))
      spdfs_nBins[_id].Scale(yield_norm)

  # Sum pdf histograms
  for _id, p in list(spdfs.items()):
    if 'spdf' not in hists:
      hists['spdf'] = p.Clone("h_spdf")
      hists['spdf'].Reset()
    hists['spdf'] += p

  for _id, p in list(spdfs_nBins.items()):
    if 'spdf_nBins' not in hists:
      hists['spdf_nBins'] = p.Clone("h_spdf_nBins")
      hists['spdf_nBins'].Reset()
    hists['spdf_nBins'] += p

  # No further scaling: the signal histograms are already in event counts
  print("[INFO] total signal yield from norms = %.4f"%signal_norm_total)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Plotting
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(True)

cat = opt.cat

def Translate(name, ndict):
    return ndict[name] if name in ndict else name
def LoadTranslations(jsonfilename):
    with open(jsonfilename) as jsonfile:
        return json.load(jsonfile)
translateCats = {} if opt.translateCats is None else LoadTranslations(opt.translateCats)

blindingRegion = [float(opt.blindingRegion.split(",")[0]),float(opt.blindingRegion.split(",")[1])]

canv = ROOT.TCanvas("canv_%s"%cat,"canv_%s"%cat,700,1000)
pad1 = ROOT.TPad("pad1_%s"%cat,"pad1_%s"%cat,0,0.45,1,1.00)
pad1.SetTickx()
pad1.SetTicky()
pad1.SetBottomMargin(0.18)
pad1.SetLeftMargin(0.12)
pad1.Draw()
pad2 = ROOT.TPad("pad2_%s"%cat,"pad2_%s"%cat,0,0.22,1,0.45)
pad2.SetTickx()
pad2.SetTicky()
pad2.SetTopMargin(0.03)
pad2.SetBottomMargin(0.25)
pad2.SetLeftMargin(0.12)
pad2.Draw()
pad3 = ROOT.TPad("pad3_%s"%cat,"pad3_%s"%cat,0,0.00,1,0.22)
pad3.SetTickx()
pad3.SetTicky()
pad3.SetTopMargin(0.03)
pad3.SetBottomMargin(0.30)
pad3.SetLeftMargin(0.12)
pad3.Draw()
padSizeRatio = 0.65/0.45

# Axis options 
ROOT.TGaxis.SetMaxDigits(4)
ROOT.TGaxis.SetExponentOffset(-0.05,0.00,"y")

# Nominal plot
pad1.cd()
h_axes = hists['data'].Clone()
h_axes.Reset()
h_axes.SetMaximum((hists['data'].GetMaximum()+hists['data'].GetBinError(hists['data'].GetMaximumBin()))*1.3)
h_axes.SetMinimum(0.)
h_axes.SetTitle("")
h_axes.GetXaxis().SetTitle("")
h_axes.GetXaxis().SetLabelSize(0)
h_axes.GetYaxis().SetTitleSize(0.05)
h_axes.GetYaxis().SetTitle("Events / %s GeV"%binWidth)
h_axes.GetYaxis().SetTitleOffset(1.1)
h_axes.GetYaxis().SetLabelSize(0.035)
h_axes.GetYaxis().SetLabelOffset(0.007)
h_axes.Draw()

leg0 = ROOT.TLegend(0.18,0.67,0.48,0.77)
leg0.SetFillStyle(0)
leg0.SetLineColor(0)
leg0.SetTextSize(0.025)
leg0.SetNColumns(2)
leg0.AddEntry(hists['data'],"#scale[1.5]{Data}","ep")
if doSignal: leg0.AddEntry(hists['spdf'],"#scale[1.5]{S model}","fl")
leg0.Draw("Same")


leg = ROOT.TLegend(0.58,0.4,0.86,0.86)
leg.SetFillStyle(0)
leg.SetLineColor(0)
leg.SetTextSize(0.025)
#leg.AddEntry(hists['data'],"#scale[1.5]{Data}","ep")
#if doSignal: leg.AddEntry(hists['spdf'],"#scale[1.5]{S model}","fl")
#leg.AddEntry(0,"","")
for bname in bpdfs: 
  if "dytbern" in bname: fname = "#bf{DY Theory core with Bernstein}"
  elif "dytcheb" in bname: fname = "#bf{DY Theory core with Chebychev}"
  elif "dytpow" in bname: fname = "#bf{DY Theory core with exp(Powerlaw)}"
  elif "dytlau" in bname: fname = "#bf{DY Theory core with Laurent}"
  elif "dytBbern" in bname: fname = "#bf{DY Theory Bern core with Bernstein}"
  elif "dytBcheb" in bname: fname = "#bf{DY Theory Bern core with Chebychev}"
  elif "dytBpow" in bname: fname = "#bf{DY Theory Bern core with exp(Powerlaw)}"
  elif "dytBlau" in bname: fname = "#bf{DY Theory Bern core with Laurent}"
  elif "dytEcheb" in bname: fname = "#bf{DY Theory Exp core with Chebychev}"
  elif "dytEpow" in bname: fname = "#bf{DY Theory Exp core with exp(Powerlaw)}"
  elif "dytElau" in bname: fname = "#bf{DY Theory Exp core with Laurent}"
  elif "dytPcheb" in bname: fname = "#bf{DY Theory Pow core with Chebychev}"
  elif "dytPpow" in bname: fname = "#bf{DY Theory Pow core with exp(Powerlaw)}"
  elif "dytPlau" in bname: fname = "#bf{DY Theory Pow core with Laurent}"
  elif "dytFcheb" in bname: fname = "#bf{DY Theory Fewz core with Chebychev}"
  elif "dytFpow" in bname: fname = "#bf{DY Theory Fewz core with exp(Powerlaw)}"
  elif "dytFlau" in bname: fname = "#bf{DY Theory Fewz core with Laurent}"
  elif "bwzexp" in bname: fname = "#bf{bwz x exp}"
  elif "bwzgam" in bname: fname = "#bf{bwzgamma}"
  elif "2exp" in bname: fname = "#bf{weighted sum of 3 and 2 order exp}"
  elif "2pow" in bname: fname = "#bf{weighted sum of 3 and 2 order pow}"
  elif "bern" in bname: fname = "#bf{Bernstein polynomial}"
  elif "exp" in bname: fname = "#bf{Sum of exponentials}"
  elif "pow" in bname: fname = "#bf{Sum of power law functions}"
  elif "lau" in bname: fname = "#bf{Laurent series}"
  elif "mBW" in bname: fname = "#bf{modified Breit Wigner funciton}"
  elif "dyt" in bname: fname = "#bf{DY Theory core with empirical function}"
  else: fname = "Unknown function"
  pullMetric, chi2Metric = metrics[bname]

  dw, prod, r = pullMetric

  if chi2Metric is None:
      metricStr = "DW %.2f  S %.1f"%(dw,prod)
      print("\n\n\n\n\nnone chi2metric\n\n\n\n")
  else:
      chi2, ndof, chi2ndof = chi2Metric
      metricStr = "DW %.2f  S %.1f  #chi^{2}/ndf %.2f"%(dw,prod,chi2ndof)
  if bname == bpdf_bf_name: lstr = "#splitline{%s}{%s  Order %s (Best fit)}"%(fname,metricStr,bname[-1])
  else: lstr = "#splitline{%s}{%s  Order %s}"%(fname,metricStr,bname[-1])
  leg.AddEntry(hists[bname],lstr,"l")


if doSignal:
  hists['spdf'].SetLineWidth(2)
  hists['spdf'].SetLineColor(9)
  hists['spdf'].SetFillColor(38)
  hists['spdf'].SetFillStyle(3001)
  hists['spdf'].GetXaxis().SetRangeUser(blindingRegion[0],blindingRegion[1])
  lowBin = hists['spdf'].FindFirstBinAbove(0.5*hists['spdf'].GetMaximum())
  highBin = hists['spdf'].FindLastBinAbove(0.5*hists['spdf'].GetMaximum())
  fwhm_low = hists['spdf'].GetBinCenter(lowBin)
  fwhm_high = hists['spdf'].GetBinCenter(highBin)
  fwhmText = ROOT.TLatex()
  fwhmText.SetTextFont(42)
  fwhmText.SetTextAlign(11)
  fwhmText.SetNDC()
  fwhmText.SetTextSize(0.03)
  fwhmText.DrawLatex(0.17,0.25,"FWHM = %1.2f GeV"%(fwhm_high-fwhm_low))
  print(f'-------------- FWHM_low: {fwhm_low} | FWHM_high: {fwhm_high} --------------')

  # Yields: every histogram holds raw event counts per data-sized bin, so a plain
  # Integral() (sum of the bin contents) directly gives the number of events.
  # The "_nBins" histograms never had SetRangeUser applied, so they integrate
  # over the full xvar range.
  hsig = hists['spdf_nBins']
  hbkg = hists["%s_nBins"%bpdf_bf_name]

  fwhm_lowBin = hbkg.FindBin(fwhm_low)
  fwhm_highBin = hbkg.FindBin(fwhm_high)

  signal_yield_total = hsig.Integral()
  signal_yieldFWHM = hsig.Integral(fwhm_lowBin, fwhm_highBin)
  bkg_yield_total = hbkg.Integral()
  bkg_yieldFWHM = hbkg.Integral(fwhm_lowBin, fwhm_highBin)
  print("[CHECK] bkg yield: sideband matched = %.2f | workspace bkgshape norm = %.2f"%(bkg_yield_total,bkgshape_norm_ws))
  print("[CHECK] signal yield: hist integral = %.4f | sum of norms = %.4f"%(signal_yield_total,signal_norm_total))
  print(f'-------------- Signal Yield Total: {signal_yield_total} | Signal Yield FHWM: {signal_yieldFWHM} --------------\n-------------- Bkg Yield Total: {bkg_yield_total} | Bkg Yield FWHM: {bkg_yieldFWHM} --------------')
  hists['spdf'].Draw("Hist same cf")
yieldText = ROOT.TLatex()
yieldText.SetTextFont(42)
yieldText.SetTextAlign(11)
yieldText.SetNDC()
yieldText.SetTextSize(0.03)
yieldText.DrawLatex(0.17,0.65,"S = %.2f | S_FWHM = %.2f "%(signal_yield_total, signal_yieldFWHM))
yieldText.DrawLatex(0.17,0.6,"B = %.2f | B_FWHM = %.2f "%(bkg_yield_total, bkg_yieldFWHM))
yields = {'Category': Translate(cat,translateCats),'FWHM': (fwhm_high-fwhm_low), 'Total Sig': signal_yield_total, 'Total Bkg': bkg_yield_total, 'Sig FWHM': signal_yieldFWHM, 'Bkg FWHM': bkg_yieldFWHM}
colourOptions=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]

bnames = list(bpdfs.keys())

fit_bnames  = []
test_bnames = []

for bname in bnames:

    # -----------------------------
    # test functions
    # -----------------------------
    if ("bwzexp" in bname) or \
       ("bwzgam" in bname) or \
       (("bern" in bname) and ("dytbern" not in bname) and ("dytBbern" not in bname)) or \
       ("2pow" in bname) or \
       ("2exp" in bname) or \
       ("mBW" in bname):
        test_bnames.append(bname)

    # -----------------------------
    # fit functions
    # -----------------------------
    else:
        fit_bnames.append(bname)
        
# -----------------------------
# Draw fit functions
# -----------------------------
for bidx, bname in enumerate(fit_bnames):

    hists[bname].SetLineWidth(3)
    hists[bname].SetLineStyle(1)
    hists[bname].SetLineColor(colourOptions[bidx])

    hists[bname].Draw("HIST L same")

# -----------------------------
# Draw test functions
# -----------------------------
for bidx, bname in enumerate(test_bnames):

    hists[bname].SetLineWidth(1)
    hists[bname].SetLineStyle(4)      # dashed
    hists[bname].SetLineColor(colourOptions[bidx])

    hists[bname].Draw("HIST L same")
    
hists['data'].SetMarkerStyle(20)
hists['data'].SetMarkerColor(1)
hists['data'].SetLineColor(1)
hists['data'].Draw("Same PE")

leg.Draw("Same")

# --- Draw SB boundaries ---
line_SB1 = ROOT.TLine(SB1_high, h_axes.GetMinimum(), SB1_high, h_axes.GetMaximum())
line_SB2 = ROOT.TLine(SB2_low, h_axes.GetMinimum(), SB2_low, h_axes.GetMaximum())

for l in [line_SB1, line_SB2]:
    l.SetLineStyle(2)   # dashed
    l.SetLineWidth(2)
    l.SetLineColor(ROOT.kBlack)
    l.Draw("same")


# Add TLatex to plot
lat0 = ROOT.TLatex()
lat0.SetTextFont(42)
lat0.SetTextAlign(11)
lat0.SetNDC()
lat0.SetTextSize(0.06)
#lat0.DrawLatex(0.12,0.92,"#bf{CMS} #it{Preliminary}")
#lat0.DrawLatex(0.12,0.92,"#bf{CMS}")
lat0.DrawLatex(0.18,0.80,"#scale[0.75]{%s}"%Translate(cat,translateCats))

lat1 = ROOT.TLatex()
lat1.SetTextFont(42)
lat1.SetTextAlign(31)
lat1.SetNDC()
lat1.SetTextSize(0.06)
#lat1.DrawLatex(0.9,0.92,"137 fb^{-1} (13 TeV)")

pad2.cd()
h_axes_ratio = hists_ratio['data'].Clone()
h_axes_ratio.Reset()
h_axes_ratio.SetMaximum((hists_ratio['data'].GetMaximum()+hists_ratio['data'].GetBinError(hists_ratio['data'].GetMaximumBin()))*1.5)
h_axes_ratio.SetMinimum((hists_ratio['data'].GetMinimum()-hists_ratio['data'].GetBinError(hists_ratio['data'].GetMinimumBin()))*1.3)
#h_axes_ratio.SetMaximum(1030)
#h_axes_ratio.SetMinimum(-1050)
h_axes_ratio.SetTitle("")
h_axes_ratio.GetXaxis().SetTitleSize(0.05*padSizeRatio)
h_axes_ratio.GetXaxis().SetLabelSize(0.035*padSizeRatio)
h_axes_ratio.GetXaxis().SetLabelOffset(0.007)
h_axes_ratio.GetXaxis().SetTickLength(0.03*padSizeRatio)
h_axes_ratio.GetYaxis().SetLabelSize(0.035*padSizeRatio)
h_axes_ratio.GetYaxis().SetLabelOffset(0.007)
h_axes_ratio.GetYaxis().SetTitle("")
h_axes_ratio.Draw()

if doSignal:
  hsr = hists['spdf'].Clone()
  hsr.SetLineWidth(2)
  hsr.SetLineColor(9)
  hsr.SetFillColor(38)
  hsr.SetFillStyle(3001)
  hsr.GetXaxis().SetRangeUser(blindingRegion[0],blindingRegion[1])
  hsr.Draw("Hist same cf")

# -----------------------------
# Draw fit functions
# -----------------------------
for bidx, bname in enumerate(fit_bnames):

    hists_ratio[bname].SetLineWidth(3)
    hists_ratio[bname].SetLineStyle(1)
    hists_ratio[bname].SetLineColor(colourOptions[bidx])

    hists_ratio[bname].Draw("HIST L same")

# -----------------------------
# Draw test functions
# -----------------------------
for bidx, bname in enumerate(test_bnames):

    hists_ratio[bname].SetLineWidth(1)
    hists_ratio[bname].SetLineStyle(4)
    hists_ratio[bname].SetLineColor(colourOptions[bidx])

    hists_ratio[bname].Draw("HIST L same")
    
hists_ratio['data'].SetMarkerStyle(20)
hists_ratio['data'].SetMarkerColor(1)
hists_ratio['data'].SetLineColor(1)
hists_ratio['data'].Draw("Same PE")

# Add TLatex to ratio plot
lat2 = ROOT.TLatex()
lat2.SetTextFont(42)
lat2.SetTextAlign(33)
lat2.SetNDC(1)
lat2.SetTextSize(0.045*padSizeRatio)
lat2.DrawLatex(0.87,0.91,"Best fit B function subtracted")

pad3.cd()
h_axes_ratio_zoom = hists_ratio['data'].Clone()
h_axes_ratio_zoom.Reset()
sigMax = hists['spdf'].GetMaximum()

h_axes_ratio_zoom.SetMaximum( 1.5*sigMax )
h_axes_ratio_zoom.SetMinimum(-1.5*sigMax )
#h_axes_ratio.SetMaximum(1030)
#h_axes_ratio.SetMinimum(-1050)
h_axes_ratio_zoom.SetTitle("")
h_axes_ratio_zoom.GetXaxis().SetTitleSize(0.05*padSizeRatio)
h_axes_ratio_zoom.GetXaxis().SetLabelSize(0.035*padSizeRatio)
h_axes_ratio_zoom.GetXaxis().SetLabelOffset(0.007)
h_axes_ratio_zoom.GetXaxis().SetTickLength(0.03*padSizeRatio)
h_axes_ratio_zoom.GetYaxis().SetLabelSize(0.035*padSizeRatio)
h_axes_ratio_zoom.GetYaxis().SetLabelOffset(0.007)
h_axes_ratio_zoom.GetYaxis().SetTitle("")
h_axes_ratio_zoom.Draw()

if doSignal:
  hsr2 = hists['spdf'].Clone()
  hsr2.SetLineWidth(2)
  hsr2.SetLineColor(9)
  hsr2.SetFillColor(38)
  hsr2.SetFillStyle(3001)
  hsr2.GetXaxis().SetRangeUser(blindingRegion[0],blindingRegion[1])
  hsr2.Draw("Hist same cf")

# -----------------------------
# Draw fit functions
# -----------------------------
for bidx, bname in enumerate(fit_bnames):

    hists_ratio[bname].SetLineWidth(3)
    hists_ratio[bname].SetLineStyle(1)
    hists_ratio[bname].SetLineColor(colourOptions[bidx])

    hists_ratio[bname].Draw("HIST L same")

# -----------------------------
# Draw test functions
# -----------------------------
for bidx, bname in enumerate(test_bnames):

    hists_ratio[bname].SetLineWidth(1)
    hists_ratio[bname].SetLineStyle(4)
    hists_ratio[bname].SetLineColor(colourOptions[bidx])

    hists_ratio[bname].Draw("HIST L same")
    
hists_ratio['data'].SetMarkerStyle(20)
hists_ratio['data'].SetMarkerColor(1)
hists_ratio['data'].SetLineColor(1)
hists_ratio['data'].Draw("Same PE")

# Add TLatex to ratio plot
lat3 = ROOT.TLatex()
lat3.SetTextFont(42)
lat3.SetTextAlign(33)
lat3.SetNDC(1)
lat3.SetTextSize(0.045*padSizeRatio)
lat3.DrawLatex(0.87,0.91,"Best fit B function subtracted")

canv.Update()

ext_str = f"_{opt.ext}" if opt.ext != "" else ""
if not os.path.isdir(f"plots{ext_str}"):
  os.system(f"mkdir -p plots{ext_str}")
canv.SaveAs(f"plots{ext_str}/multipdf_plot_%s.pdf"%(cat))
canv.SaveAs(f"plots{ext_str}/multipdf_plot_%s.png"%(cat))

csv_exists = os.path.isfile(opt.outCSV)

with open(opt.outCSV, mode='a', newline='') as f:
  writer = csv.DictWriter(f, fieldnames=yields.keys())

  if not csv_exists:
    writer.writeheader()
  writer.writerow(yields)