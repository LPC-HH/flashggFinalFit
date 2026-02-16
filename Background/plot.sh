export LD_LIBRARY_PATH=$PWD/lib:$LD_LIBRARY_PATH
pushd ../Plots
  for cat in NOTAG; do python3 makeMultipdfPlot.py --inputWSFile ../Background/outdir_tutorial/CMS-HGG_multipdf_${cat}.root --cat ${cat} --ext tutorial --mass 125.38 --inputSignalWSFile ../Signal/outdir_packaged/CMS-HGG_sigfit_packaged_${cat}.root; done
popd
