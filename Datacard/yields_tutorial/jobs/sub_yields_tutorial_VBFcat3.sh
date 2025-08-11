#!/bin/bash
ulimit -s unlimited
set -e
cd /afs/cern.ch/user/y/yulou/CMSSW_14_1_0_pre4/src
export SCRAM_ARCH=el9_amd64_gcc12
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval `scramv1 runtime -sh`
cd /afs/cern.ch/user/y/yulou/CMSSW_14_1_0_pre4/src/flashggFinalFit/Datacard
export PYTHONPATH=$PYTHONPATH:/afs/cern.ch/user/y/yulou/CMSSW_14_1_0_pre4/src/flashggFinalFit/tools:/afs/cern.ch/user/y/yulou/CMSSW_14_1_0_pre4/src/flashggFinalFit/Datacard/tools

python3 /afs/cern.ch/user/y/yulou/CMSSW_14_1_0_pre4/src/flashggFinalFit/Datacard/makeYields.py --cat VBFcat3 --procs auto --ext tutorial --mass 125 --inputWSDirMap combined=/eos/home-y/yulou/Fnal-hmm/root_io/tuples/split_tuples/VBF/ws_VBF --sigModelWSDir ./Models/signal --sigModelExt packaged --bkgModelWSDir ./Models/background --bkgModelExt multipdf  --mergeYears --skipCOWCorr --systWeightScheme accEff
