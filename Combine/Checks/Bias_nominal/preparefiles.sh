#!/bin/bash
set -e

cmsenv
source ../../../setup.sh

rm -f Datacard_tutorial*.root

echo "===== Create toy background ====="
cd ../../..
bash Background_toy.sh
bash Datacard.sh
cd Combine
bash copy.sh
bash run_workspace.sh
cd Checks/Bias_nominal/

for cat in ggHcat1 ggHcat2 ggHcat3 ggHcat4 ggHcat5 ggHcat6; do
  cp ../../Datacard_tutorial_${cat}_mu_inclusive.root ./Datacard_tutorial_${cat}_mu_inclusive_toy.root
done

echo "===== Create nominal background ====="
cd ../../..
bash Background.sh
bash Datacard.sh
cd Combine
bash copy.sh
bash run_workspace.sh
cd Checks/Bias_nominal/

for cat in ggHcat1 ggHcat2 ggHcat3 ggHcat4 ggHcat5 ggHcat6; do
  cp ../../Datacard_tutorial_${cat}_mu_inclusive.root ./Datacard_tutorial_${cat}_mu_inclusive.root
done