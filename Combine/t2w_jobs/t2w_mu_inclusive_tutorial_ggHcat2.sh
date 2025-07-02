#!/bin/bash

cd /uscms/home/mbarrial/fits/Combine

eval `scramv1 runtime -sh`

text2workspace.py Datacard_tutorial_ggHcat2.txt -o Datacard_tutorial_ggHcat2_mu_inclusive.root -m 125 higgsMassRange=122,128 