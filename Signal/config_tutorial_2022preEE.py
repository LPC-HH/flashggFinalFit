# Config file: options for signal fitting

_year = '2023BPix'

signalScriptCfg = {
  
  # Setup
  'inputWSDir':'/home/zguo/Finalfit/CMSSW_14_1_0_pre4/src/flashggFinalFit/wkspace_store/%s/signal_%s'%(_year, _year), 
  'procs':'auto', # if auto: inferred automatically from filenames
  'cats':'auto', # if auto: inferred automatically from (0) workspace
  'ext':'tutorial_%s'%_year,
  'analysis':'tutorial', # To specify which replacement dataset mapping (defined in ./python/replacementMap.py)
  'year':'%s'%_year, # Use 'combined' if merging all years: not recommended
  'massPoints':'125',

  #Photon shape systematics  
  'scales':'Scale', # separate nuisance per year
  'scalesCorr':'', # correlated across years
  'scalesGlobal':'', # affect all processes equally, correlated across years
  'smears':'Smearing', # separate nuisance per year

  # Job submission options
#  'batch':'condor', # ['condor','SGE','IC','local']
#  'queue':'espresso',
  
  'batch':'local',
  'queue':'espresso',
  'systematics':'skipSystematics',

}
 