SKIP_BLOCK=false
# ========== Tree2WS ==========
if ! $SKIP_BLOCK; then
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
fi