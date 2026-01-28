#!/bin/bash
set -e

# ========== Tree2WS ==========

cd Trees2WS

echo "[INFO] Running trees2ws_data for ggH"
python3 trees2ws_data.py \
  --inputConfig config_tutorial.py \
  --inputTreeFile ${ROOT_IO}/tuples/split_tuples/ggH/allData_combined.root \
  --applyMassCut --massCutRange 100,180

echo "[INFO] Running trees2ws_data for VBF"
python3 trees2ws_data.py \
  --inputConfig config_tutorial.py \
  --inputTreeFile ${ROOT_IO}/tuples/split_tuples/VBF/allData_combined.root \
  --applyMassCut --massCutRange 100,180

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
  --cats VBFcat1,VBFcat2,VBFcat3,VBFcat4,ggHcat1,ggHcat2,ggHcat3 \
  --exts tutorial_combined --batch local --massPoints 125 --year combined --mergeYears

echo "[INFO] Running signal plotter"
for cat in VBFcat1 VBFcat2 VBFcat3 VBFcat4 ggHcat1 ggHcat2 ggHcat3; do
  python3 RunPlotter.py --procs all --years combined --cats $cat --ext packaged
done

cd ..

# ========== Background ==========

cd Background

echo "[INFO] Running fTest for background"
python3 RunBackgroundScripts.py --inputConfig config_tutorial.py --mode fTestParallel
python3 RunBackgroundScripts.py --inputConfig config_tutorial_VBF.py --mode fTestParallel

pushd ../Plots
for cat in VBFcat1 VBFcat2 VBFcat3 VBFcat4 ggHcat1 ggHcat2 ggHcat3; do
  python3 makeMultipdfPlot.py \
    --inputWSFile ../Background/outdir_tutorial/CMS-HGG_multipdf_${cat}.root \
    --cat ${cat} \
    --ext tutorial \
    --mass 125.38 \
    --inputSignalWSFile ../Signal/outdir_packaged/CMS-HGG_sigfit_packaged_${cat}.root
  
done
popd

cd ../Datacard
python3 generate_datacards.py

cd ../
cd Combine
bash copy.sh
bash run_workspace.sh
bash run_asym.sh  
bash run_sig.sh  
