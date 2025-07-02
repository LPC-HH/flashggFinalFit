#!/bin/bash
ulimit -s unlimited
set -e
cd /uscms_data/d3/mbarrial/fits-hgg/CMSSW_14_1_0_pre4/src
export SCRAM_ARCH=el9_amd64_gcc12
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval `scramv1 runtime -sh`
cd /uscms_data/d3/mbarrial/fits-hgg/CMSSW_14_1_0_pre4/src/flashggFinalFit/Datacard
export PYTHONPATH=$PYTHONPATH:/uscms_data/d3/mbarrial/fits-hgg/CMSSW_14_1_0_pre4/src/flashggFinalFit/tools:/uscms_data/d3/mbarrial/fits-hgg/CMSSW_14_1_0_pre4/src/flashggFinalFit/Datacard/tools

python3 /uscms_data/d3/mbarrial/fits-hgg/CMSSW_14_1_0_pre4/src/flashggFinalFit/Datacard/makeYields.py --cat cat2 --procs auto --ext tutorial --mass 125 --inputWSDirMap combined=/uscms_data/d3/mbarrial/higgsAnalysis/CMSSW_14_0_14/src/HmmAnalysis/root_io/tuples/split_tuples/ggH/ws_GG2H --sigModelWSDir ./Models/signal --sigModelExt packaged --bkgModelWSDir ./Models/background --bkgModelExt multipdf  --mergeYears --skipCOWCorr --systWeightScheme accEff
