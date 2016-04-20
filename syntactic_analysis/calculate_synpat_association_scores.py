import re, os, sys, json
sys.path.append("../")

from constants import *
from project_resources import *
import computation_resources as comp

tf = sum(config_data[CORPUS_FREQUENCIES])
f1 = 1200

syn_list = {}

with open(config_data[PROJECT_PATH]+"word_frequencies_by_synpattern.json", "r", encoding="utf-8") as f:
    data = json.load(f)

    for d in data:
        for g in data[d]:
            if g != "word" and g != "total":
                syn_list.update({d+"_"+g : {"f12" : data[d][g], "word" : data[d]["word"]}})

f2_freqs = {}

with open(config_data[PROJECT_PATH]+"syntactic_full_syntype_context_word_matrix.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    for tag in data:
        word = re.split("_", tag)[0]
        if "full_count" in data[tag] and data[tag]["full_count"] > 0:
            f2_freqs.update( { word : data[tag]["full_count"] })

LLR = {}
PMI = {}
locMI = {}

print(f2_freqs)


for synpat in syn_list:
    
    if syn_list[synpat]["word"] in f2_freqs:
        f2 = f2_freqs[syn_list[synpat]["word"]]
        f12 = syn_list[synpat]["f12"]
        args = (f1, f2, f12, tf)
        LLR.update( { synpat : comp.LLR(*args) } )
        PMI.update( { synpat : comp.PMI(*args) } )
        locMI.update( { synpat : comp.localMI(*args) } )

with open(config_data[PROJECT_PATH]+"syntactic_synpat_associations_LLR.tsv", "w", encoding="utf-8") as f:
    for line in LLR:
        f.write(line +"\t"+str(LLR[line]) + "\n")

with open(config_data[PROJECT_PATH]+"syntactic_synpat_associations_PMI.tsv", "w", encoding="utf-8") as f:
    for line in PMI:
        f.write(line +"\t"+str(PMI[line]) + "\n")

with open(config_data[PROJECT_PATH]+"syntactic_synpat_associations_locMI.tsv", "w", encoding="utf-8") as f:
    for line in locMI:
        f.write(line +"\t"+str(locMI[line]) + "\n")


with open(config_data[PROJECT_PATH]+"syntactic_synpat_associations_LLR.json", "w", encoding="utf-8") as f:
    json.dump(LLR, f)
with open(config_data[PROJECT_PATH]+"syntactic_synpat_associations_PMI.tsv", "w", encoding="utf-8") as f:
    json.dump(PMI, f)
with open(config_data[PROJECT_PATH]+"syntactic_synpat_associations_locMI.tsv", "w", encoding="utf-8") as f:
    json.dump(locMI, f)
