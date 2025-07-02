echo "----------------------------ggH -----------------------------------"
python3 RunYields.py --inputWSDirMap combined=/uscms_data/d3/mbarrial/higgsAnalysis/CMSSW_14_0_14/src/HToMuMu/root_io/tuples/split_tuples/ggH/ws_GG2H  --cats ggHcat1 --procs auto --ext tutorial --mergeYears --skipCOWCorr --batch local --queue espresso
python3 makeDatacard.py --ext tutorial --years combined --prune --doTrueYield --skipCOWCorr --doMCStatUncertainty --saveDataFrame --output Datacard_tutorial

cp Datacard_tutorial.txt Datacard_tutorial_ggHcat1.txt
cp Datacard_tutorial.pkl Datacard_tutorial_ggHcat1.pkl
rm yields_tutorial/ggHcat1.pkl



python3 RunYields.py --inputWSDirMap combined=/uscms_data/d3/mbarrial/higgsAnalysis/CMSSW_14_0_14/src/HToMuMu/root_io/tuples/split_tuples/ggH/ws_GG2H  --cats ggHcat2 --procs auto --ext tutorial --mergeYears --skipCOWCorr --batch local --queue espresso
python3 makeDatacard.py --ext tutorial --years combined --prune --doTrueYield --skipCOWCorr --doMCStatUncertainty --saveDataFrame --output Datacard_tutorial

cp Datacard_tutorial.txt Datacard_tutorial_ggHcat2.txt
cp Datacard_tutorial.pkl Datacard_tutorial_ggHcat2.pkl
rm yields_tutorial/ggHcat2.pkl



python3 RunYields.py --inputWSDirMap combined=/uscms_data/d3/mbarrial/higgsAnalysis/CMSSW_14_0_14/src/HToMuMu/root_io/tuples/split_tuples/ggH/ws_GG2H  --cats ggHcat3 --procs auto --ext tutorial --mergeYears --skipCOWCorr --batch local --queue espresso
python3 makeDatacard.py --ext tutorial --years combined --prune --doTrueYield --skipCOWCorr --doMCStatUncertainty --saveDataFrame --output Datacard_tutorial

cp Datacard_tutorial.txt Datacard_tutorial_ggHcat3.txt
cp Datacard_tutorial.pkl Datacard_tutorial_ggHcat3.pkl
rm yields_tutorial/ggHCat2.pkl



python3 RunYields.py --inputWSDirMap combined=/uscms_data/d3/mbarrial/higgsAnalysis/CMSSW_14_0_14/src/HToMuMu/root_io/tuples/split_tuples/ggH/ws_GG2H  --cats ggHcat1,ggHcat2,ggHcat3 --procs auto --ext tutorial --mergeYears --skipCOWCorr --batch local --queue espresso
python3 makeDatacard.py --ext tutorial --years combined --prune --doTrueYield --skipCOWCorr --doMCStatUncertainty --saveDataFrame --output Datacard_tutorial

cp Datacard_tutorial.txt Datacard_tutorial_ggH.txt
cp Datacard_tutorial.pkl Datacard_tutorial_ggH.pkl

mkdir -p yields_tutorial/ggH

mv -v yields_tutorial/ggHcat1.pkl yields_tutorial/ggH/ggHcat1.pkl
mv -v yields_tutorial/ggHcat2.pkl yields_tutorial/ggH/ggHcat2.pkl
mv -v yields_tutorial/ggHcat3.pkl yields_tutorial/ggH/ggHcat3.pkl
 
echo "----------------------------VBF -----------------------------------"

python3 RunYields.py --inputWSDirMap combined=/uscms_data/d3/mbarrial/higgsAnalysis/CMSSW_14_0_14/src/HToMuMu/root_io/tuples/split_tuples/VBF/ws_VBF --cats VBFcat1 --procs auto --ext tutorial --mergeYears --skipCOWCorr --batch local --queue espresso
python3 makeDatacard.py --ext tutorial --years combined --prune --doTrueYield --skipCOWCorr --doMCStatUncertainty --saveDataFrame --output Datacard_tutorial

cp Datacard_tutorial.txt Datacard_tutorial_VBFcat1.txt
cp Datacard_tutorial.pkl Datacard_tutorial_VBFcat1.pkl
rm yields_tutorial/VBFcat1.pkl



python3 RunYields.py --inputWSDirMap combined=/uscms_data/d3/mbarrial/higgsAnalysis/CMSSW_14_0_14/src/HToMuMu/root_io/tuples/split_tuples/VBF/ws_VBF  --cats VBFcat2 --procs auto --ext tutorial --mergeYears --skipCOWCorr --batch local --queue espresso
python3 makeDatacard.py --ext tutorial --years combined --prune --doTrueYield --skipCOWCorr --doMCStatUncertainty --saveDataFrame --output Datacard_tutorial

cp Datacard_tutorial.txt Datacard_tutorial_VBFcat2.txt
cp Datacard_tutorial.pkl Datacard_tutorial_VBFcat2.pkl
rm yields_tutorial/VBFcat2.pkl

python3 RunYields.py --inputWSDirMap combined=/uscms_data/d3/mbarrial/higgsAnalysis/CMSSW_14_0_14/src/HToMuMu/root_io/tuples/split_tuples/VBF/ws_VBF  --cats VBFcat3 --procs auto --ext tutorial --mergeYears --skipCOWCorr --batch local --queue espresso
python3 makeDatacard.py --ext tutorial --years combined --prune --doTrueYield --skipCOWCorr --doMCStatUncertainty --saveDataFrame --output Datacard_tutorial

cp Datacard_tutorial.txt Datacard_tutorial_VBFcat3.txt
cp Datacard_tutorial.pkl Datacard_tutorial_VBFcat3.pkl
rm yields_tutorial/VBFcat3.pkl

python3 RunYields.py --inputWSDirMap combined=/uscms_data/d3/mbarrial/higgsAnalysis/CMSSW_14_0_14/src/HToMuMu/root_io/tuples/split_tuples/VBF/ws_VBF  --cats VBFcat4 --procs auto --ext tutorial --mergeYears --skipCOWCorr --batch local --queue espresso
python3 makeDatacard.py --ext tutorial --years combined --prune --doTrueYield --skipCOWCorr --doMCStatUncertainty --saveDataFrame --output Datacard_tutorial

cp Datacard_tutorial.txt Datacard_tutorial_VBFcat4.txt
cp Datacard_tutorial.pkl Datacard_tutorial_VBFcat4.pkl
rm yields_tutorial/VBFcat4.pkl

python3 RunYields.py --inputWSDirMap combined=/uscms_data/d3/mbarrial/higgsAnalysis/CMSSW_14_0_14/src/HToMuMu/root_io/tuples/split_tuples/VBF/ws_VBF --cats VBFcat1,VBFcat2,VBFcat3,VBFcat4 --procs auto --ext tutorial --mergeYears --skipCOWCorr --batch local --queue espresso
python3 makeDatacard.py --ext tutorial --years combined --prune --doTrueYield --skipCOWCorr --saveDataFrame --output Datacard_tutorial

cp Datacard_tutorial.txt Datacard_tutorial_VBF.txt
cp Datacard_tutorial.pkl Datacard_tutorial_VBF.pkl

echo "----------------------------Combined -----------------------------------"
mv -v  yields_tutorial/ggH/ggHcat1.pkl yields_tutorial/ggHcat1.pkl
mv -v  yields_tutorial/ggH/ggHcat2.pkl yields_tutorial/ggHcat2.pkl
mv -v  yields_tutorial/ggH/ggHcat3.pkl yields_tutorial/ggHcat3.pkl

python3 makeDatacard.py --ext tutorial --years combined --prune --doTrueYield --skipCOWCorr --doMCStatUncertainty --saveDataFrame --output Datacard_tutorial

rm yields_tutorial/*.pkl
