# ========== Background ==========

cd Background

echo "[INFO] Running fTest for background"
#python3 RunBackgroundScripts.py --inputConfig config_tutorial.py --mode fTestParallel
#python3 RunBackgroundScripts.py --inputConfig config_tutorial_VBF.py --mode fTestParallel

pushd ../Plots
CSVFILE="out_yields_$(date +%Y%m%d_%H%M%S).csv"
for cat in VBFcat1 VBFcat2 VBFcat3 VBFcat4 VBFcat5 ggHcat1 ggHcat2 ggHcat3 ggHcat4 ggHcat5; do
  python3 makeMultipdfPlot.py \
    --inputWSFile ../Background/outdir_tutorial/CMS-HGG_multipdf_${cat}.root \
    --cat ${cat} \
    --ext tutorial \
    --mass 125.38 \
    --inputSignalWSFile ../Signal/outdir_packaged/CMS-HGG_sigfit_packaged_${cat}.root \
    --outCSV ${CSVFILE}
  
done
popd

cd ..