#!/bin/bash
#set -euo pipefail
echo "running hello!"
voms-proxy-info --all
ls -l

echo "running hi!"
cat=$1
cmssw_version=$2

echo "Categroy: $cat"
echo "CMSSW version: $cmssw_version"


workDir=`pwd`
echo "Getting CMSSW"
source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=el9_amd64_gcc12
#tar -zxvf cms_setup.tar.gz
scramv1 project CMSSW $cmssw_version

mkdir -p BiasResults/
DATA_FOLDER="$cmssw_version/src/data/"


###########################################
# Copy input list and exec to cmssw folder
###########################################
echo "Copying inputs to CMSSW/src"
cp Datacard_${cat}.root $cmssw_version/src/.
cp RunBiasStudy.py $cmssw_version/src/.
cp biasUtils.py $cmssw_version/src/.
cp combine ${cmssw_version}/src/

echo "Making output directories"
mkdir -p ${cmssw_version}/src/BiasToys/
mkdir -p ${cmssw_version}/src/BiasFits/
mkdir -p ${cmssw_version}/src/BiasPlots/

###########################
# Get cmssw environment
###########################
echo "Seting up CMSSW"
cd $cmssw_version/src/
eval `scram runtime -sh`


###########################
# Get fitting environment
###########################
#echo "getting flashgg and combine"
#COMBINE_TAG=07b56c67ba6e4304b42c3a6cdba710d59c719192
#COMBINEHARVESTER_TAG=94017ba5a3a657f7b88669b1a525b19d34ea41a2
#FINALFIT_TAG=higgsdnafinalfit

#git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
#cd HiggsAnalysis/CombinedLimit && git fetch origin ${COMBINE_TAG} && git checkout ${COMBINE_TAG}
#cd ${cmssw_version}/src
#bash <(curl -s https://raw.githubusercontent.com/cms-analysis/CombineHarvester/${COMBINEHARVESTER_TAG}/CombineTools/scripts/sparse-checkout-https.sh)
#cd CombineHarvester && git fetch origin ${COMBINEHARVESTER_TAG} && git checkout ${COMBINEHARVESTER_TAG}

#cd ${cmssw_version}/src
#cmsenv
#scram b clean
#scram b -j 8

#git clone git@github.com:LPC-HH/flashggFinalFit.git
#cd flashggFinalFit/
#cd Background
#make clean
#make
#cd ..
#source setup.sh


CSVFILE="bias_results_${cat}_$(date +%Y%m%d_%H%M%S).csv"

cd ${cmssw_version}/src

echo "running bias study"
python3 RunBiasStudy.py \
  -d Datacard_${cat}.root -t \
  --generateCSV \
  -b ${cat} \
  --selectFunction dytbern2 \
  -f -c "--setParameterRanges r=-5,5 --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints" \
  -p --gaussianFit \
  -n 10 \
  --outCSV ${CSVFILE}

################################################################
# Copy output files 
################################################################
cp -r BiasFits/ ${workDir}/BiasResults/
cp -r BiasToys/ ${workDir}/BiasResults/
cp -r BiasPlots/ ${workDir}/BiasResults/