import os

# Paths and directory
cmsswbase__ = os.environ['CMSSW_BASE']
cwd__ = os.environ['CMSSW_BASE']+"/src/flashggFinalFit"
swd__ = "%s/Signal"%cwd__
bwd__ = "%s/Background"%cwd__
dwd__ = "%s/Datacard"%cwd__
fwd__ = "%s/Combine"%cwd__
pwd__ = "%s/Plots"%cwd__
twd__ = "%s/Trees2WS"%cwd__

# Centre of mass energy string
sqrts__ = "13TeV"

# Luminosity map in fb^-1: for using UL 2018
lumiMap = {
    '2016':36.33, 
    '2017':41.48, 
    '2018':59.83, 
<<<<<<< HEAD
    # 'combined':137.65, 
    # 'merged':137.65,
    '2022preEE':8.00,
    '2022postEE':26.70,
    'merged':170.97,
    #'combined':170.97,
    'combined':0.001,
=======
    'combined':58.927, 
    'merged':137.65,
    '2022preEE':8.00,
    '2022postEE':26.70,
    '2022': 7.9804,    #below added by Zhengliang
#    '2022': 34.652, #wrong, just a test
    '2022EE': 26.7,
    '2023': 17.794,
    '2023BPix': 9.451,
    '2022data': 34.652,
    '2023data': 24.275,
    'alldata': 58.927    
>>>>>>> 6b99263 (Add/update scripts and DYCore source)
}
# If using ReReco samples then switch to lumiMap below (missing data in 2018 EGamma data set)
#lumiMap = {'2016':36.33, '2017':41.48, '2018':59.35, 'combined':137.17, 'merged':137.17}
lumiScaleFactor = 1000 # Converting from pb to fb

# Constants
BR_W_lnu = 3.*10.86*0.01
BR_Z_ll = 3*3.3658*0.01
BR_Z_nunu = 20.00*0.01
BR_Z_qq = 69.91*0.01
BR_W_qq = 67.41*0.01

# Production modes and decay channel: for extract XS from combine
#productionModes = ['ggH','qqH','TTH','tHq','tHW','ggZH','WH','ZH','bbH', 'VBFH', 'WmH', 'WpH']

productionModes = ['ggH','qqH','ttH','tHq','tHW','ggZH','WH','ZH','bbH']
<<<<<<< HEAD
#decayMode = 'hgg'
decayMode = 'hmm'

# List of years
# years_to_process = ['2016','2017','2018','2022preEE','2022postEE']
years_to_process = ['combined']
=======
decayMode = 'hmm'

# List of years
#years_to_process = ['2016','2017','2018','2022preEE','2022postEE','2022','2022EE','2023','2023BPix']
years_to_process = ['2022', '2022EE', '2023', '2023BPix']
>>>>>>> 6b99263 (Add/update scripts and DYCore source)

# flashgg input WS objects
inputWSName__ = "tagsDumper/cms_hgg_13TeV"
inputNuisanceExtMap = {'scales':'','scalesCorr':'','smears':''}
# Signal output WS objects
outputWSName__ = "wsig"
outputWSObjectTitle__ = "hggpdfsmrel"
outputWSNuisanceTitle__ = "CMS_hgg_nuisance"
#outputNuisanceExtMap = {'scales':'%sscale'%sqrts__,'scalesCorr':'%sscaleCorr'%sqrts__,'smears':'%ssmear'%sqrts__,'scalesGlobal':'%sscale'%sqrts__}
outputNuisanceExtMap = {'scales':'','scalesCorr':'','smears':'','scalesGlobal':''}
# Bkg output WS objects
bkgWSName__ = "multipdf"
