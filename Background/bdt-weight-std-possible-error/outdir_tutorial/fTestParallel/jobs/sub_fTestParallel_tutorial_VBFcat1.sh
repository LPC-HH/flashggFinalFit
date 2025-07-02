#!/bin/bash
ulimit -s unlimited
set -e
cd /uscms_data/d3/mbarrial/fits-hgg/CMSSW_14_1_0_pre4/src
export SCRAM_ARCH=el9_amd64_gcc12
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval `scramv1 runtime -sh`
cd /uscms_data/d3/mbarrial/fits-hgg/CMSSW_14_1_0_pre4/src/flashggFinalFit/Background
export PYTHONPATH=$PYTHONPATH:/uscms_data/d3/mbarrial/fits-hgg/CMSSW_14_1_0_pre4/src/flashggFinalFit/tools:/uscms_data/d3/mbarrial/fits-hgg/CMSSW_14_1_0_pre4/src/flashggFinalFit/Background/tools

/uscms_data/d3/mbarrial/fits-hgg/CMSSW_14_1_0_pre4/src/flashggFinalFit/Background/runBackgroundScripts.sh -i /uscms_data/d3/mbarrial/higgsAnalysis/CMSSW_14_0_14/src/HToMuMu/root_io/tuples/split_tuples/VBF/ws/allData_combined.root -p none -f VBFcat1 --ext tutorial --catOffset 0 --intLumi 170.97 --year all --batch local --queue espresso --sigFile none --isData --fTest
