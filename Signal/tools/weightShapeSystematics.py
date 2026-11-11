"""Fit binwise LHE QCD envelopes/PDF quadrature and morph PDF parameters.

The final rate is deliberately independent of these nuisances. Input variations
are rescaled to the nominal sum of weights before using the existing fitter.
"""

import glob
import json
import math
import os
from collections import OrderedDict

import ROOT
import numpy as np
import uproot
from commonObjects import inputWSName__, outputWSNuisanceTitle__, sqrts__, swd__
from commonTools import procToData
from simultaneousFit import SimultaneousFit
from plottingTools import plotPdfComponents


def fit_weight_shapes(opt, nominal, fit_proc, fit_cat, xvar, mh, mh_low, mh_high):
    xvar.setBins(opt.nBins)
    # Hold all RooFit dependencies alive until FinalModel has been saved.
    objects = []
    variations = {}
    report = {"fit_proc": fit_proc, "fit_cat": fit_cat, "fit_error_type": "SumW2", "parameters": {}}
    scale_indices = [0, 1, 3, 4, 5, 7, 8]
    branches = ['weight_LHEScal_%g'%i for i in scale_indices]
    branches += ['weight_LHEPd_%g'%i for i in range(103)]
    shape_datasets = {
        source: {direction: OrderedDict() for direction in ('up', 'down')}
        for source in ('qcd', 'pdf')
    }
    for mass in opt.massPoints.split(','):
        paths = glob.glob('%s/output*M%s*%s.root'%(opt.inputWSDir,mass,fit_proc))
        if len(paths) != 1:
            raise RuntimeError('Expected one input workspace for %s M%s: %s'%(fit_proc,mass,paths))
        data_name = '%s_%s_%s_%s'%(procToData(fit_proc.split('_')[0]),mass,sqrts__,fit_cat)

        # Use exactly the nominal fit binning before combining LHE variations.
        prefix = '%s_%s_%s_%s'%(opt.proc,opt.cat,opt.year,mass)
        histograms = {}
        for branch in ['nominal'] + branches:
            name = '%s_%s'%(prefix,branch)
            histograms[branch] = ROOT.TH1D(name,name,opt.nBins,xvar.getMin(),xvar.getMax())
            histograms[branch].SetDirectory(0)
            histograms[branch].Sumw2()
        with uproot.open(paths[0]) as handle:
            tree_path = '%s/%s_lhe'%(inputWSName__.rsplit('/',1)[0],data_name)
            if tree_path not in handle:
                raise RuntimeError('Missing %s in %s; rebuild tuple workspaces'%(tree_path,paths[0]))
            tree = handle[tree_path]
            for branch in [opt.xvar,'weight'] + branches:
                if branch not in tree:
                    raise RuntimeError('Missing %s in %s'%(branch,tree_path))
            for chunk in tree.iterate([opt.xvar,'weight']+branches,library='np',step_size='10 MB'):
                values = np.ascontiguousarray(chunk[opt.xvar],dtype='float64')
                weights = np.ascontiguousarray(chunk['weight'],dtype='float64')
                if not np.all(np.isfinite(values)) or not np.all(np.isfinite(weights)):
                    raise RuntimeError('Non-finite nominal event in %s'%data_name)
                histograms['nominal'].FillN(len(values),values,weights)
                for branch in branches:
                    varied_weights = np.ascontiguousarray(weights*chunk[branch],dtype='float64')
                    if not np.all(np.isfinite(varied_weights)):
                        raise RuntimeError('Non-finite %s in %s'%(branch,data_name))
                    histograms[branch].FillN(len(values),values,varied_weights)

        central = histograms['nominal']
        reference = histograms['weight_LHEScal_4']
        varied_hists = {}
        for source in ('qcd', 'pdf'):
            varied_hists[source] = {}
            for direction in ('up', 'down'):
                name = '%s_%s_%s'%(prefix,source,direction)
                varied_hists[source][direction] = central.Clone(name)
                varied_hists[source][direction].SetDirectory(0)
        for b in range(1,central.GetNbinsX()+1):
            content = central.GetBinContent(b)
            scale4 = reference.GetBinContent(b)
            # Match the supplied QCD prescription, including central in envelope.
            if scale4 > 0:
                scales = [histograms['weight_LHEScal_%g'%i].GetBinContent(b) for i in scale_indices]
                varied_hists['qcd']['up'].SetBinContent(b,content*max(scales)/scale4)
                varied_hists['qcd']['down'].SetBinContent(b,content*min(scales)/scale4)
            delta = math.sqrt(sum(
                (histograms['weight_LHEPd_%g'%i].GetBinContent(b)-content)**2
                for i in range(103)))
            varied_hists['pdf']['up'].SetBinContent(b,content+delta)
            varied_hists['pdf']['down'].SetBinContent(b,content-delta)

        target = nominal.datasetForFit[mass].sumEntries()
        for source in ('qcd', 'pdf'):
            for direction in ('up', 'down'):
                hist = varied_hists[source][direction]
                # Retain nominal bin errors, as in the supplied Clone/SetBinContent
                # prescription. These do not include uncertainty on the envelope.
                for b in range(1,hist.GetNbinsX()+1):
                    if 110 <= hist.GetBinCenter(b) <= 140:
                        if hist.GetBinContent(b) != 0 and hist.GetBinError(b) <= 0:
                            raise RuntimeError('Missing statistical error for %s %s bin %g in %s'%(source,direction,b,data_name))
                if hist.Integral() <= 0 or target <= 0:
                    raise RuntimeError('Non-positive %s %s integral in %s'%(source,direction,data_name))
                hist.Scale(target/hist.Integral())
                name = hist.GetName() + '_data'
                varied = ROOT.RooDataHist(name,name,ROOT.RooArgList(xvar),hist)
                shape_datasets[source][direction][mass] = varied
                objects.extend([hist,varied])
        objects.extend(histograms.values())

    for source in ('qcd', 'pdf'):
        variations[source] = {}
        for direction in ("up", "down"):
            datasets = shape_datasets[source][direction]
            fit = SimultaneousFit(
                "%s_%s" % (source, direction),
                opt.proc,
                opt.cat,
                datasets,
                xvar.Clone(),
                mh,
                mh_low,
                mh_high,
                opt.massPoints,
                opt.nBins,
                opt.MHPolyOrder,
                opt.minimizerMethod,
                opt.minimizerTolerance,
            )
            if opt.useDCB:
                fit.buildDCBplusGaussian()
            else:
                fit.buildNGaussians(nominal.nGaussians)
            # Start every variation from the nominal best fit.
            for key, variable in fit.Vars.items():
                if key in nominal.Vars:
                    variable.setVal(nominal.Vars[key].getVal())
            fit.runFit(isSystematic=True)
            if not fit.FitResult.success or not math.isfinite(float(fit.FitResult.fun)):
                raise RuntimeError(
                    "Failed %s %s shape fit: %s"
                    % (source, direction, fit.FitResult.message)
                )
            for index, value in enumerate(fit.FitResult.x):
                fit.FitParameters[index].setVal(float(value))
            if opt.doPlots:
                plot_dir = '%s/outdir_%s/signalFit/Plots'%(swd__,opt.ext)
                os.makedirs(plot_dir,exist_ok=True)
                plotPdfComponents(fit,_outdir=plot_dir,
                                  _extension='%s_%s_%s_'%(source,direction,opt.year),
                                  _proc=opt.proc,_cat=opt.cat)
            fit.buildSplines()
            variations[source][direction] = fit
            objects.append(fit)

    nuisances = {}
    for source in variations:
        name = "%s_%s_shape" % (outputWSNuisanceTitle__, source)
        nuisances[source] = ROOT.RooRealVar(name, name, 0.0, -5.0, 5.0)
        nuisances[source].setConstant(True)
        objects.append(nuisances[source])

    # Replace all fitted shape splines, including tails and mixture fractions.
    # Positive parameters use log interpolation; fractions use logit interpolation.
    # dm is an additive mass offset. All reproduce nominal/Up/Down at 0/+1/-1.
    for key, central in list(nominal.Splines.items()):
        name = "%s_%s_%s_%s" % (key, opt.proc, opt.year, opt.cat)
        central.SetName(name + "_nominal")
        args = ROOT.RooArgList(central)
        is_fraction = key.startswith("frac")
        is_offset = key.startswith("dm")
        transform = (
            (lambda x: "log((%s)/(1-(%s)))" % (x, x))
            if is_fraction
            else ((lambda x: x) if is_offset else (lambda x: "log(%s)" % x))
        )
        expression = transform("@0")
        report["parameters"][key] = {}
        for source, fits in variations.items():
            position = args.getSize()
            args.add(nuisances[source])
            for direction in ("up", "down"):
                spline = fits[direction].Splines[key]
                spline.SetName(name + "_%s_%s" % (source, direction))
                args.add(spline)
            theta, up, down = ["@%d" % (position + i) for i in range(3)]
            expression += "+TMath::Max(%s,0.)*(%s-%s)+TMath::Max(-%s,0.)*(%s-%s)" % (
                theta,
                transform(up),
                transform("@0"),
                theta,
                transform(down),
                transform("@0"),
            )
            report["parameters"][key][source] = {}
            for mass in opt.massPoints.split(","):
                mh.setVal(float(mass))
                values = [
                    central.getVal(),
                    fits["up"].Splines[key].getVal(),
                    fits["down"].Splines[key].getVal(),
                ]
                if any(not math.isfinite(v) for v in values) or (
                    not is_offset
                    and any(v <= 0 or (is_fraction and v >= 1) for v in values)
                ):
                    raise RuntimeError(
                        "Invalid interpolation endpoints for %s %s M%s: %s"
                        % (key, source, mass, values)
                    )
                report["parameters"][key][source][mass] = dict(
                    zip(("nominal", "up", "down"), values)
                )
        if is_fraction:
            expression = "1./(1.+exp(-(%s)))" % expression
        elif not is_offset:
            expression = "exp(%s)" % expression
        morphed = ROOT.RooFormulaVar(name, name, expression, args)
        for mass in opt.massPoints.split(","):
            mh.setVal(float(mass))
            for source, fits in variations.items():
                for theta, endpoint in (
                    (0.0, central),
                    (1.0, fits["up"].Splines[key]),
                    (-1.0, fits["down"].Splines[key]),
                ):
                    nuisances[source].setVal(theta)
                    if not math.isclose(
                        morphed.getVal(),
                        endpoint.getVal(),
                        rel_tol=1.0e-7,
                        abs_tol=1.0e-9,
                    ):
                        raise RuntimeError(
                            "Interpolation endpoint mismatch for %s %s" % (key, source)
                        )
                nuisances[source].setVal(0.0)
        nominal.Splines[key] = morphed
        objects.extend([central, args, morphed])
    mh.setVal(125.0)
    directory = "%s/outdir_%s/signalFit/shapeSystematics" % (swd__, opt.ext)
    os.makedirs(directory, exist_ok=True)
    with open(
        "%s/%s_%s_%s.json" % (directory, opt.proc, opt.year, opt.cat), "w"
    ) as output:
        json.dump(report, output, indent=2, sort_keys=True)
    return objects
