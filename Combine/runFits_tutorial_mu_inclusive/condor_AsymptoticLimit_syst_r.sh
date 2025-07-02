#!/bin/sh
ulimit -s unlimited
set -e
cd /uscms_data/d3/mbarrial/fits-hgg/CMSSW_14_1_0_pre4/src
export SCRAM_ARCH=el9_amd64_gcc12
source /cvmfs/cms.cern.ch/cmsset_default.sh
eval `scramv1 runtime -sh`
cd /uscms/home/mbarrial/nobackup/fits-hgg/CMSSW_14_1_0_pre4/src/flashggFinalFit/Combine/runFits_tutorial_mu_inclusive

if [ $1 -eq 0 ]; then
  combine --snapshotName MultiDimFit --expectSignal 1 -t -1 --redefineSignalPOI r --saveWorkspace --freezeParameters MH --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -M AsymptoticLimits -m 125.38 -d /uscms_data/d3/mbarrial/fits-hgg/CMSSW_14_1_0_pre4/src/flashggFinalFit/Combine/runFits_tutorial_mu_inclusive/higgsCombine_bestfit_syst_r.MultiDimFit.mH125.38.root -n _AsymptoticLimit_syst_r
fi

