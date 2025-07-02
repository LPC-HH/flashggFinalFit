#!/bin/bash
ulimit -s unlimited
set -e
cd /uscms_data/d3/mbarrial/fits-hgg/CMSSW_14_1_0_pre4/src
export SCRAM_ARCH=el9_amd64_gcc12
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval `scramv1 runtime -sh`
cd /uscms_data/d3/mbarrial/fits-hgg/CMSSW_14_1_0_pre4/src/flashggFinalFit/Signal
export PYTHONPATH=$PYTHONPATH:/uscms_data/d3/mbarrial/fits-hgg/CMSSW_14_1_0_pre4/src/flashggFinalFit/tools:/uscms_data/d3/mbarrial/fits-hgg/CMSSW_14_1_0_pre4/src/flashggFinalFit/Signal/tools

python3 /uscms_data/d3/mbarrial/fits-hgg/CMSSW_14_1_0_pre4/src/flashggFinalFit/Signal/scripts/fTest.py --cat cat2 --procs GG2H --ext tutorial_combined --inputWSDir /uscms_data/d3/mbarrial/higgsAnalysis/CMSSW_14_0_14/src/HmmAnalysis/root_io/tuples/split_tuples/ggH/ws_GG2H --doPlots
