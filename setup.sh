# Add tools dir to PYTHONPATH
eval `scramv1 runtime -sh`
export ROOT_IO=/home/zguo/HmmCombine/ntuples_v2d4d2_elise/

export PYTHONPATH=$PYTHONPATH:${CMSSW_BASE}/src/flashggFinalFit/tools
