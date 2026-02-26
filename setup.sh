# Add tools dir to PYTHONPATH
eval `scramv1 runtime -sh`
export ROOT_IO=/uscms/home/esledge/nobackup/CMSSW_14_0_14/src/HToMuMu/root_io/

export PYTHONPATH=$PYTHONPATH:${CMSSW_BASE}/src/flashggFinalFit/tools
