CSVFILE="bias_results_$(date +%Y%m%d_%H%M%S).csv"
for cat in VBFcat1 VBFcat2 VBFcat3 VBFcat4 VBFcat5 ggHcat1 ggHcat2 ggHcat3 ggHcat4 ggHcat5; do
  cp ../../Datacard_tutorial_${cat}_mu_inclusive.root .
  python3 RunBiasStudy.py \
  -d Datacard_tutorial_${cat}_mu_inclusive.root -t \
  --generateCSV \
  -b ${cat} \
  -f -c "--setParameterRanges r=-5,5 --cminDefaultMinimizerStrategy 1 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2" \
  -p --gaussianFit \
  -n 500 \
  --outCSV ${CSVFILE}

done