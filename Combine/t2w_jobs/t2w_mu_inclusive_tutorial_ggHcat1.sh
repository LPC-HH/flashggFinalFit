#!/bin/bash

cd /uscms/home/mbarrial/fits/Combine

eval `scramv1 runtime -sh`

text2workspace.py Datacard_tutorial_ggHcat1.txt -o Datacard_tutorial_ggHcat1_mu_inclusive.root -m 125 higgsMassRange=122,128 