#!/bin/bash

cd /uscms/home/mbarrial/nobackup/fits-hgg/CMSSW_14_1_0_pre4/src/flashggFinalFit/Combine

eval `scramv1 runtime -sh`

text2workspace.py Datacard_tutorial_cat0.txt -o Datacard_tutorial_cat0_mu_inclusive.root -m 125 higgsMassRange=122,128 