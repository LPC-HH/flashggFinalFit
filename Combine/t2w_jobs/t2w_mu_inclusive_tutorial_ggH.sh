#!/bin/bash

cd /afs/cern.ch/user/y/yulou/CMSSW_14_1_0_pre4/src/flashggFinalFit/Combine

eval `scramv1 runtime -sh`

text2workspace.py Datacard_tutorial_ggH.txt -o Datacard_tutorial_ggH_mu_inclusive.root -m 125 higgsMassRange=122,128 