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
                {'name':'BR_hmm','title':'BR_hmm','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':"1.012"},
                #{'name':'QCDscale_VH','title':'QCDscale_VH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_vh.json'}, # Note: VH had components accounted for in THU_qqH_*, set to 1 in json
                #{'name':'QCDscale_ggZH','title':'QCDscale_ggZH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggzh.json'}, # Note: ggZH lep components are accounted for in THU_ggZH i.e. this only covers the ggZH had component
                #{'name':'QCDscale_ttH','title':'QCDscale_ttH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_tth.json'},
                #{'name':'QCDscale_tHq','title':'QCDscale_tHq','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_thq.json'},
                #{'name':'QCDscale_tHW','title':'QCDscale_tHW','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_thw.json'},
                #{'name':'QCDscale_bbH','title':'QCDscale_bbH','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_bbh.json'},
                {'name':'Mu','title':'THU_ggH_Mu','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh.json'},
                {'name':'PT120','title':'THU_ggH_Pt120','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh.json'},
                {'name':'res','title':'THU_ggH_res','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_ggh.json'},
                {'name':'Jet01','title':'THU_VBF_Jet01','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh.json'},
                {'name':'Mjj120','title':'THU_VBF_Mjj120','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh.json'},
                {'name':'Mjj350','title':'THU_VBF_Mjj350','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh.json'},
                {'name':'Mjj60','title':'THU_VBF_Mjj60','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh.json'},
                {'name':'Mjj700','title':'THU_VBF_Mjj700','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh.json'},
                {'name':'PT25','title':'THU_VBF_Pt25','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':'theory_uncertainties/thu_qqh.json'},

                # Shape uncertainties: enter direct XS measurements
                # Shape uncertainties: enter direct XS measurements
                # Scale weights grouping is defined in makeDatacard.py
                # For some reason, the name is saved only as `Scal`, not `Scale`, do not ask me why
                # Comment out the nominal weight here as it does not contain any `tiers`, so it would fail in `makeDatacard.py``
                # The scheme below is valid for v13, you need to explicitly check the nanoAOD documentation to validate your setup
                #{'name':'weight_LHEScal_0','title':'CMS_hgg_scaleWeight_0','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']}, 
                #{'name':'weight_LHEScal_1','title':'CMS_hgg_scaleWeight_1','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']},
                #{'name':'weight_LHEScal_2','title':'CMS_hgg_scaleWeight_2','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']}, #Unphysical
                #{'name':'weight_LHEScal_3','title':'CMS_hgg_scaleWeight_3','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']},
                #{'name':'weight_LHEScal_4','title':'CMS_hgg_scaleWeight_4','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']}, # nominal weight
                #{'name':'weight_LHEScal_5','title':'CMS_hgg_scaleWeight_5','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']}, 
                #{'name':'weight_LHEScal_6','title':'CMS_hgg_scaleWeight_6','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']}, #Unphysical
                #{'name':'weight_LHEScal_7','title':'CMS_hgg_scaleWeight_7','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']},
                #{'name':'weight_LHEScal_8','title':'CMS_hgg_scaleWeight_8','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']},
                #{'name':'weight_AlphaS','title':'CMS_hgg_AlphaS','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']},
                #{'name':'weight_PS_ISR','title':'CMS_hgg_PS_ISR','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']},
                #{'name':'weight_PS_FSR','title':'CMS_hgg_PS_FSR','type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']}

              ]

# PDF weight
#for i in range(1,101): theory_systematics.append( {'name':'weight_LHEPd_%g'%i, 'title':'CMS_hgg_pdfWeight_%g'%i, 'type':'factory','prior':'lnN','correlateAcrossYears':1,'tiers':['shape']} )

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# EXPERIMENTAL SYSTEMATICS
# correlateAcrossYears = 0 : no correlation
# correlateAcrossYears = 1 : fully correlated
# correlateAcrossYears = -1 : partially correlated

experimental_systematics = [
                {'name':'lumi_13p6TeV_2022','title':'lumi_13p6TeV_2022','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':"1.014"},
                {'name':'lumi_13p6TeV_2022EE','title':'lumi_13p6TeV_2022EE','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':"1.014"},
                {'name':'lumi_13p6TeV_2023','title':'lumi_13p6TeV_2023','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':"1.014"},
                {'name':'lumi_13p6TeV_2023BPix','title':'lumi_13p6TeV_2023BPix','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':"1.014"},
                {'name':'lumi_13p6TeV_2024','title':'lumi_13p6TeV_2024','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':"1.014"},
                {'name':'lumi_13p6TeV_2025','title':'lumi_13p6TeV_2025','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':"1.014"},
                {'name':'CMS_muon_trigger_eff','title':'CMS_muon_trigger_eff','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':"0.994/1.006"},
                {'name':'CMS_muon_eff','title':'CMS_muon_eff','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':"-2", 'valueByCat': {'ggHcat1': '0.998/1.002', 'ggHcat2': '0.996/1.004','ggHcat3': '0.994/1.004', 'ggHcat4': '0.998/1.002','ggHcat5': '0.996/1.006','VBFcat1': '0.998/1.002', 'VBFcat2': '0.996/1.004','VBFcat3': '0.994/1.004', 'VBFcat4': '0.998/1.002','VBFcat5': '0.996/1.006'}},
                {'name':'CMS_pileup_2022','title':'CMS_pileup_2022','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':"1.001/0.999"},
                {'name':'CMS_pileup_2022EE','title':'CMS_pileup_2022EE','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':"1.001/0.999"},
                {'name':'CMS_pileup_2023','title':'CMS_pileup_2023','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':"1.001/0.999"},
                {'name':'CMS_pileup_2023BPix','title':'CMS_pileup_2023BPix','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':"1.001/0.999"},
                {'name':'CMS_pileup_2024','title':'CMS_pileup_2024','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':"1.001/0.999"},
                {'name':'CMS_pileup_2025','title':'CMS_pileup_2025','type':'constant','prior':'lnN','correlateAcrossYears':1,'value':"1.001/0.999"},

                #{'name':'weight_Pileup','title':'CMS_hgg_PileupWeight','type':'factory','prior':'lnN','correlateAcrossYears':1},
                #{'name':'weight_TriggerSF','title':'CMS_hgg_TriggerWeight','type':'factory','prior':'lnN','correlateAcrossYears':1},
                #{'name':'weight_ElectronVetoSF','title':'CMS_hgg_ElectronVetoSF','type':'factory','prior':'lnN','correlateAcrossYears':1},
                #{'name':'weight_PreselSF','title':'CMS_hgg_PreselSF','type':'factory','prior':'lnN','correlateAcrossYears':1},
                #{'name':'weight_SF_photon_ID','title':'CMS_hgg_phoIdMva','type':'factory','prior':'lnN','correlateAcrossYears':1},
                #{'name':'energyErrShift','title':'CMS_hgg_SigmaEOverEShift','type':'factory','prior':'lnN','correlateAcrossYears':1}
              ]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Shape nuisances: effect encoded in signal model
# mode = (other,scalesGlobal,scales,scalesCorr,smears): match the definition in the signal models

signal_shape_systematics = [
                #{'name':'deltafracright','title':'deltafracright','type':'signal_shape','mode':'other','mean':'0.0','sigma':'0.02'},
                #{'name':'Scale','title':'Scale','type':'signal_shape','mode':'scales','mean':'0.0','sigma':'1.0'},
                #{'name':'Smearing','title':'Smearing','type':'signal_shape','mode':'smears','mean':'0.0','sigma':'1.0'},
                #{'name':'NonLinearity','title':'NonLinearity','type':'signal_shape','mode':'scalesGlobal','mean':'0.0','sigma':'0.002'},
                #{'name':'Geant4','title':'Geant4','type':'signal_shape','mode':'scalesGlobal','mean':'0.0','sigma':'0.0005'}
              ]
