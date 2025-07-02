#!/bin/bash
ulimit -s unlimited
set -e
cd /uscms_data/d3/mbarrial/fits-hgg/CMSSW_14_1_0_pre4/src
export SCRAM_ARCH=el9_amd64_gcc12
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval `scramv1 runtime -sh`
cd /uscms_data/d3/mbarrial/fits-hgg/CMSSW_14_1_0_pre4/src/flashggFinalFit/Signal
export PYTHONPATH=$PYTHONPATH:/uscms_data/d3/mbarrial/fits-hgg/CMSSW_14_1_0_pre4/src/flashggFinalFit/tools:/uscms_data/d3/mbarrial/fits-hgg/CMSSW_14_1_0_pre4/src/flashggFinalFit/Signal/tools

python3 /uscms_data/d3/mbarrial/fits-hgg/CMSSW_14_1_0_pre4/src/flashggFinalFit/Signal/scripts/signalFit.py --inputWSDir /uscms_data/d3/mbarrial/higgsAnalysis/CMSSW_14_0_14/src/HToMuMu/root_io/tuples/split_tuples/VBF/ws_VBF --ext tutorial_combined --proc VBF --cat VBFcat4 --year combined --analysis tutorial --massPoints 125 --scales 'Scale' --scalesCorr '' --scalesGlobal '' --smears 'Smearing' --doPlots --useDCB --skipVertexScenarioSplit --skipSystematics --massPoints 125 --skipBeamspotReweigh

