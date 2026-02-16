# Input config file for running trees2ws

trees2wsCfg = {

  # Name of RooDirectory storing input tree
  'inputTreeDir':'',

  # Variables to be added to dataframe: use wildcard * for common strings
<<<<<<< HEAD
  # 'mainVars':["CMS_hgg_mass","weight","dZ","weight_*"], # Var for the nominal RooDataSets
  # 'dataVars':["CMS_hgg_mass","weight"], # Vars to be added for data
  'mainVars':["CMS_hgg_mass","weight"], # Var for the nominal RooDataSets
  'dataVars':["CMS_hgg_mass"], # Vars to be added for data
=======
  'mainVars':["dimuon_mass","weight","dZ","weight_*"], # Var for the nominal RooDataSets
  'dataVars':["dimuon_mass","weight"], # Vars to be added for data
>>>>>>> 6b99263 (Add/update scripts and DYCore source)
  'stxsVar':'',
  'systematicsVars':["dimuon_mass","weight"], # Variables to add to sytematic RooDataHists
  'theoryWeightContainers':{},

  # List of systematics: use string YEAR for year-dependent systematics
  # 'systematics':["Scale","Smearing"],
  'systematics':[],

  # Analysis categories: python list of cats or use 'auto' to extract from input tree
  'cats':'auto'

}
