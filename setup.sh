# Add tools dir to PYTHONPATH
eval `scramv1 runtime -sh`
export ROOT_IO=/uscms/home/christiw/nobackup/Hmm/CMSSW_14_0_14/src/HToMuMu/root_io_v3/

export PYTHONPATH=$PYTHONPATH:${CMSSW_BASE}/src/flashggFinalFit/tools
