#!/bin/bash
set -e

REMOVE_PREVIOUS=false

while getopts "r" opt; do
    case $opt in
        r) REMOVE_PREVIOUS=true ;;
    esac
done

if $REMOVE_PREVIOUS; then
    echo "Removing previous results..."
    echo "Removing previous workspaces"
    rm -rf ${ROOT_IO}/tuples/split_tuples/ggH/ws/*.root
    rm -rf ${ROOT_IO}/tuples/split_tuples/ggH/ws_GG2H/*.root
    rm -rf ${ROOT_IO}/tuples/split_tuples/VBF/ws/*.root
    rm -rf ${ROOT_IO}/tuples/split_tuples/VBF/ws_VBF/*.root

    echo "Removing background fits"
    rm -rf Background/outdir_tutorial/*.root
    rm -rf Background/outdir_tutorial/bkgfTest-Data/*.pdf
    rm -rf Background/outdir_tutorial/bkgfTest-Data/*.png
    rm -rf Background/outdir_tutorial/bkgfTest-Data/*.txt

    echo "Removing datacards"
    rm -rf Combine/Datacard*
    rm -rf Datacard/Datacard*
    
    echo "Removing signal fits"
    rm -rf Signal/outdir_tutorial_combined/signalFit/Plots/*.p*
    rm -rf Signal/outdir_tutorial_combined/signalFit/output/*.root
    rm -rf Signal/outdir_packaged/*.root
    rm -rf Signal/outdir_packaged/Plots/*.p*

    echo "Removing output plots"
    rm -rf Plots/plots_tutorial/*.p*
    exit 1
fi


SKIP_BLOCK=false
# ========== Tree2WS ==========
if ! $SKIP_BLOCK; then
  cd Trees2WS

  echo "[INFO] Running trees2ws_data for ggH"
  python3 trees2ws_data.py \
    --inputConfig config_tutorial.py \
    --inputTreeFile ${ROOT_IO}/tuples/split_tuples/allData_combined.root \
    --applyMassCut --massCutRange 100,180

  #echo "[INFO] Running trees2ws_data for VBF"
  #python3 trees2ws_data.py \
  #  --inputConfig config_tutorial.py \
  #  --inputTreeFile ${ROOT_IO}/tuples/split_tuples/VBF/allData_combined.root \
  #  --applyMassCut --massCutRange 100,180

  echo "[INFO] Running trees2ws for ggH signal"
  python3 trees2ws.py \
    --inputConfig config_tutorial.py \
    --inputTreeFile ${ROOT_IO}/tuples/split_tuples/ggH/output_signal_M125_13TeV_cats_pythia8.root \
    --inputMass 125 --productionMode ggh --year combined

  echo "[INFO] Running trees2ws for VBF signal"
  python3 trees2ws.py \
    --inputConfig config_tutorial.py \
    --inputTreeFile ${ROOT_IO}/tuples/split_tuples/VBF/output_signal_M125_13TeV_cats_pythia8.root \
    --inputMass 125 --productionMode vbf --year combined
  
  cd ..
  python3 cp_workspaces.py

  # ========== Signal ==========

  cd Signal

  #echo "[INFO] Running fTest for signal"
  #python3 RunSignalScripts.py --inputConfig config_tutorial_combined.py --mode fTest --modeOpts "--doPlots"

  echo "[INFO] Running signalFit for ggH"
  python3 RunSignalScripts.py --inputConfig config_tutorial_combined.py --mode signalFit --modeOpts "--doPlots --useDCB --skipVertexScenarioSplit --skipSystematics --massPoints 125 --skipBeamspotReweigh" --groupSignalFitJobsByCat

  echo "[INFO] Running signalFit for VBF"
  python3 RunSignalScripts.py --inputConfig config_tutorial_combined_VBF.py --mode signalFit --modeOpts "--doPlots --useDCB --skipVertexScenarioSplit --skipSystematics --massPoints 125 --skipBeamspotReweigh" --groupSignalFitJobsByCat

  echo "[INFO] Packaging signal fits"
  python3 RunPackager.py \
    --cats VBFcat1,VBFcat2,VBFcat3,VBFcat4,VBFcat5,ggHcat1,ggHcat2,ggHcat3,ggHcat4,ggHcat5 \
    --exts tutorial_combined --batch local --massPoints 125 --year combined --mergeYears

  echo "[INFO] Running signal plotter"
  for cat in VBFcat1 VBFcat2 VBFcat3 VBFcat4 VBFcat5 ggHcat1 ggHcat2 ggHcat3 ggHcat4 ggHcat5; do
    python3 RunPlotter.py --procs all --years combined --cats $cat --ext packaged --doFWHM 
  done

  cd ..

  # ========== Background ==========

  cd Background

  echo "[INFO] Running fTest for background"
  python3 RunBackgroundScripts.py --inputConfig config_tutorial.py --mode fTestParallel
  #python3 RunBackgroundScripts.py --inputConfig config_tutorial_VBF.py --mode fTestParallel
else
  cd Background
fi

pushd ../Plots
CSVFILE="out_yields_$(date +%Y%m%d_%H%M%S).csv"
for cat in ggHcat1 ggHcat2 ggHcat3 ggHcat4 ggHcat5; do
  python3 makeMultipdfPlot.py \
   --inputWSFile ../Background/outdir_tutorial/CMS-HGG_multipdf_${cat}.root \
    --cat ${cat} \
    --ext tutorial \
    --nBins 160 \
    --mass 125.38 \
    --inputSignalWSFile ../Signal/outdir_packaged/CMS-HGG_sigfit_packaged_${cat}.root \
    --outCSV ${CSVFILE}
  
done

for cat in VBFcat1 VBFcat2 VBFcat3 VBFcat4 VBFcat5; do
  python3 makeMultipdfPlot.py \
    --inputWSFile ../Background/outdir_tutorial/CMS-HGG_multipdf_${cat}.root \
    --cat ${cat} \
    --ext tutorial \
    --mass 125.38 \
    --nBins 80 \
    --inputSignalWSFile ../Signal/outdir_packaged/CMS-HGG_sigfit_packaged_${cat}.root \
    --outCSV ${CSVFILE}
  
done
popd

cd ../Datacard
echo "[INFO] Generating Datacards"
python3 generate_datacards.py

cd ../
cd Combine

echo "[INFO] Copying Signal, Data, and Datacards into combine folder"
bash copy.sh

echo "[INFO] Creating workspaces for Combine"
bash run_workspace.sh

echo "[INFO] Running asymptotic limits"
bash run_asym.sh  

echo "[INFO] Running significance"
bash run_sig.sh  
