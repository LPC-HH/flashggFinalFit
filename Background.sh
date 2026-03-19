# ========== Background ==========

cd Background

echo "[INFO] Running fTest for background"
python3 RunBackgroundScripts.py --inputConfig config_tutorial.py --mode fTestParallel

pushd ../Plots
for cat in ggHcat1 ggHcat2 ggHcat3 ggHcat4 ggHcat5 ggHcat6; do
  python3 makeMultipdfPlot.py \
    --inputWSFile ../Background/outdir_tutorial/CMS-HGG_multipdf_${cat}.root \
    --cat ${cat} \
    --ext tutorial \
    --mass 125.38 \
    --inputSignalWSFile ../Signal/outdir_packaged/CMS-HGG_sigfit_packaged_${cat}.root
  
done
popd

cd ..