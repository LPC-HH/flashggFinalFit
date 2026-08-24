import pickle
import re

df = pickle.load(open("Datacard_tutorial_ggHcat1.pkl", "rb"))

print(df[["proc", "procOriginal", "proc_s0", "cat", "type", "pdf_Higgs_ggH"]].drop_duplicates().to_string())
