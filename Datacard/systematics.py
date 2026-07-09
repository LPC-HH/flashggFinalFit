# Python file to store systematics: for STXS analysis

# Comment out all nuisances that you do not want to include

# THEORY SYSTEMATICS:

# For type:constant
#  1) specify same value for all processes
#  2) define process map json in ./theory_uncertainties (add process names where necessary!)

# For type:factory
# Tier system: adds different uncertainties to dataframe
#   1) shape: absolute yield of process kept constant, shape effects i.e. calc migrations across cats
#   2) ishape: as (1) but absolute yield for proc x cat is allowed to vary
#   3) norm: absolute yield of production mode (s0) kept constant but migrations across sub-processes e.g. STXS bins.Same value in each category.
#   4) inorm: as (3) but absolute yield of production mode (s0) can vary
#   5) inc: variations in production mode (s0), same value for each subprocess in each category
# Relations: shape = ishape/inorm
#            norm  = inorm/inc
# Specify as list in dict: e.g. 'tiers'=['inc','inorm','norm','ishape','shape']

theory_systematics = [
    # Normalisation uncertainties: enter interpretations
    {
        "name": "BR_hmm",
        "title": "BR_hmm",
        "type": "constant",
        "prior": "lnN",
        "correlateAcrossYears": 1,
        "value": "0.983/1.0167",
    },
    {
        "name": "QCDscale_ggH",
        "title": "thu_QCDscale_ggH",
        "type": "constant",
        "prior": "lnN",
        "correlateAcrossYears": 1,
        "value": "theory_uncertainties/thu_ggh.json",
    },
    {
        "name": "pdf_Higgs_ggH",
        "title": "thu_pdf_Higgs_ggH",
        "type": "constant",
        "prior": "lnN",
        "correlateAcrossYears": 1,
        "value": "theory_uncertainties/thu_ggh.json",
    },
    {
        "name": "alphaS_ggH",
        "title": "alphaS_ggH",
        "type": "constant",
        "prior": "lnN",
        "correlateAcrossYears": 1,
        "value": "theory_uncertainties/thu_ggh.json",
    },
    {
        "name": "QCDscale_qqH",
        "title": "thu_QCDscale_qqH",
        "type": "constant",
        "prior": "lnN",
        "correlateAcrossYears": 1,
        "value": "theory_uncertainties/thu_qqh.json",
    },
    {
        "name": "pdf_Higgs_qqH",
        "title": "thu_pdf_Higgs_qqH",
        "type": "constant",
        "prior": "lnN",
        "correlateAcrossYears": 1,
        "value": "theory_uncertainties/thu_qqh.json",
    },
    {
        "name": "alphaS_qqH",
        "title": "alphaS_qqH",
        "type": "constant",
        "prior": "lnN",
        "correlateAcrossYears": 1,
        "value": "theory_uncertainties/thu_qqh.json",
    },
    # Shape uncertainties: enter direct XS measurements
    # Shape uncertainties: enter direct XS measurements
    # Scale weights grouping is defined in makeDatacard.py
    # For some reason, the name is saved only as `Scal`, not `Scale`, do not ask me why
    # Comment out the nominal weight here as it does not contain any `tiers`, so it would fail in `makeDatacard.py``
    # The scheme below is valid for v13, you need to explicitly check the nanoAOD documentation to validate your setup
    # {'name':'weight_LHEScal_0','title':'CMS_hgg_scaleWeight_0','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']},
    # {'name':'weight_LHEScal_1','title':'CMS_hgg_scaleWeight_1','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']},
    # {'name':'weight_LHEScal_2','title':'CMS_hgg_scaleWeight_2','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']}, #Unphysical
    # {'name':'weight_LHEScal_3','title':'CMS_hgg_scaleWeight_3','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']},
    # {'name':'weight_LHEScal_4','title':'CMS_hgg_scaleWeight_4','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']}, # nominal weight
    # {'name':'weight_LHEScal_5','title':'CMS_hgg_scaleWeight_5','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']},
    # {'name':'weight_LHEScal_6','title':'CMS_hgg_scaleWeight_6','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']}, #Unphysical
    # {'name':'weight_LHEScal_7','title':'CMS_hgg_scaleWeight_7','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']},
    # {'name':'weight_LHEScal_8','title':'CMS_hgg_scaleWeight_8','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']},
    # {'name':'weight_AlphaS','title':'CMS_hgg_AlphaS','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']},
    # {'name':'weight_PS_ISR','title':'CMS_hgg_PS_ISR','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']},
    # {'name':'weight_PS_FSR','title':'CMS_hgg_PS_FSR','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']}
]

# PDF weight
# for i in range(1,101): theory_systematics.append( {'name':'weight_LHEPd_%g'%i, 'title':'CMS_hgg_pdfWeight_%g'%i, 'type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']} )

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# EXPERIMENTAL SYSTEMATICS
# correlateAcrossYears = 0 : no correlation
# correlateAcrossYears = 1 : fully correlated
# correlateAcrossYears = -1 : partially correlated

experimental_systematics = [
    {
        "name": "lumi_combined",
        "title": "CMS_lumi",
        "type": "constant",
        "prior": "lnN",
        "correlateAcrossYears": 1,
        "value": "1.03",
    },
    {
        "name": "pileup",
        "title": "CMS_pileup",
        "type": "constant",
        "prior": "lnN",
        "correlateAcrossYears": 1,
        "value": "-2",
        "valueByCat": {
            "ggHcat1": "1.0155/0.9846",
            "ggHcat2": "1.0042/0.9951",
            "ggHcat3": "1.0057/0.9955",
            "ggHcat4": "1.0126/0.9868",
            "ggHcat5": "1.0119/0.9881",
            "VBFcat1": "1.0162/0.9861",
            "VBFcat2": "1.0081/0.9922",
            "VBFcat3": "1.0073/0.9907",
            "VBFcat4": "0.9987/1.0010",
            "VBFcat5": "0.9546/1.0497",
        },
    },
    {
        "name": "mu_trig_eff",
        "title": "CMS_mu_trig_eff",
        "type": "constant",
        "prior": "lnN",
        "correlateAcrossYears": 1,
        "value": "-2",
        "valueByCat": {
            "ggHcat1": "0.9986/1.0014",
            "ggHcat2": "0.9990/1.0010",
            "ggHcat3": "0.9992/1.0008",
            "ggHcat4": "0.9993/1.0007",
            "ggHcat5": "0.9992/1.0008",
            "VBFcat1": "0.9986/1.0014",
            "VBFcat2": "0.9987/1.0013",
            "VBFcat3": "0.9988/1.0012",
            "VBFcat4": "0.9989/1.0011",
            "VBFcat5": "0.9993/1.0007",
        },
    },
    {
        "name": "mu_ID_eff",
        "title": "CMS_mu_ID_eff",
        "type": "constant",
        "prior": "lnN",
        "correlateAcrossYears": 1,
        "value": "-2",
        "valueByCat": {
            "ggHcat1": "0.9988/1.0013",
            "ggHcat2": "0.9990/1.0010",
            "ggHcat3": "0.9992/1.0008",
            "ggHcat4": "0.9993/1.0007",
            "ggHcat5": "0.9993/1.0007",
            "VBFcat1": "0.9987/1.0013",
            "VBFcat2": "0.9988/1.0012",
            "VBFcat3": "0.9988/1.0012",
            "VBFcat4": "0.9989/1.0011",
            "VBFcat5": "0.9991/1.0009",
        },
    },
    {
        "name": "mu_ISO_eff",
        "title": "CMS_mu_ISO_eff",
        "type": "constant",
        "prior": "lnN",
        "correlateAcrossYears": 1,
        "value": "-2",
        "valueByCat": {
            "ggHcat1": "0.9974/1.0026",
            "ggHcat2": "0.9979/1.0021",
            "ggHcat3": "0.9984/1.0016",
            "ggHcat4": "0.9986/1.0014",
            "ggHcat5": "0.9987/1.0013",
            "VBFcat1": "0.9972/1.0028",
            "VBFcat2": "0.9973/1.0027",
            "VBFcat3": "0.9975/1.0026",
            "VBFcat4": "0.9977/1.0023",
            "VBFcat5": "0.9982/1.0018",
        },
    },
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Shape nuisances: effect encoded in signal model
# mode = (other,scalesGlobal,scales,scalesCorr,smears): match the definition in the signal models

signal_shape_systematics = [
    {
        "name": "peak_ggH_ggHcat1",
        "title": "peak_ggH_ggHcat1",
        "type": "signal_shape",
        "mode": "other",
        "mean": "0.0",
        "sigma": "0.001",
        "cats": ["ggHcat1"],
    },
    {
        "name": "peak_ggH_ggHcat2",
        "title": "peak_ggH_ggHcat2",
        "type": "signal_shape",
        "mode": "other",
        "mean": "0.0",
        "sigma": "0.001",
        "cats": ["ggHcat2"],
    },
    {
        "name": "peak_ggH_ggHcat3",
        "title": "peak_ggH_ggHcat3",
        "type": "signal_shape",
        "mode": "other",
        "mean": "0.0",
        "sigma": "0.001",
        "cats": ["ggHcat3"],
    },
    {
        "name": "peak_ggH_ggHcat4",
        "title": "peak_ggH_ggHcat4",
        "type": "signal_shape",
        "mode": "other",
        "mean": "0.0",
        "sigma": "0.001",
        "cats": ["ggHcat4"],
    },
    {
        "name": "peak_ggH_ggHcat5",
        "title": "peak_ggH_ggHcat5",
        "type": "signal_shape",
        "mode": "other",
        "mean": "0.0",
        "sigma": "0.001",
        "cats": ["ggHcat5"],
    },
    {
        "name": "sigma_ggH_ggHcat1",
        "title": "sigma_ggH_ggHcat1",
        "type": "signal_shape",
        "mode": "other",
        "mean": "0.0",
        "sigma": "0.1",
        "cats": ["ggHcat1"],
    },
    {
        "name": "sigma_ggH_ggHcat2",
        "title": "sigma_ggH_ggHcat2",
        "type": "signal_shape",
        "mode": "other",
        "mean": "0.0",
        "sigma": "0.1",
        "cats": ["ggHcat2"],
    },
    {
        "name": "sigma_ggH_ggHcat3",
        "title": "sigma_ggH_ggHcat3",
        "type": "signal_shape",
        "mode": "other",
        "mean": "0.0",
        "sigma": "0.1",
        "cats": ["ggHcat3"],
    },
    {
        "name": "sigma_ggH_ggHcat4",
        "title": "sigma_ggH_ggHcat4",
        "type": "signal_shape",
        "mode": "other",
        "mean": "0.0",
        "sigma": "0.1",
        "cats": ["ggHcat4"],
    },
    {
        "name": "sigma_ggH_ggHcat5",
        "title": "sigma_ggH_ggHcat5",
        "type": "signal_shape",
        "mode": "other",
        "mean": "0.0",
        "sigma": "0.1",
        "cats": ["ggHcat5"],
    },
]
