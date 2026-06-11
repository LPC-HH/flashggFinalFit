#!/bin/bash
#set -euo pipefail
echo "running hello!"
voms-proxy-info --all
ls -l

echo "running hi!"
pwd

source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /uscms/home/esledge/nobackup/fits-hmm/CMSSW_14_1_0_pre4/src/flashggFinalFit/Combine/Checks/Bias_nominal/condor/BiasCondor_ggHcat5/
eval `scram runtime -sh`
ls -lh

CAT=$1
OUTDIR="condor/BiasCondor_${CAT}"
CSVFILE="bias_results_${CAT}_$(date +%Y%m%d_%H%M%S).csv"

mkdir -p ${OUTDIR}
cd ${OUTDIR}
echo ${CAT}

#cp ../../../../Datacard_tutorial_${CAT}_mu_inclusive.root .

python3 ../../RunBiasStudy.py \
  -d Datacard_tutorial_${CAT}_mu_inclusive.root -t \
  --generateCSV \
  -b ${CAT} \
  --selectFunction dytbern2 \
  -f -c "--setParameterRanges r=-5,5 --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints" \
  -p --gaussianFit \
  -n 10 \
  --outCSV ${CSVFILE}