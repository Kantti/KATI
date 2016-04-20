import os, sys, json, re
sys.path.append("../")
from constants import *
from project_resources import *
import computation_resources as comp

F_THRESHOLD = 100

with open(config_data[PROJECT_PATH]+"syntactic_full_syntype_context_word_matrix.json", "r", encoding="utf-8") as f:
        data = json.load(f)

with open(config_data[PROJECT_PATH]+"syntactic_context_words_with_freqs.json", "r", encoding="utf-8" ) as f:
    word_frequencies = json.load(f)

LLR_vectors = {}
LPPMI_vectors = {}
locMI_vectors = {}
LPlocMI_vectors = {}
PMI_vectors = {}
locMI_vectors = {}

tf = sum(config_data[CORPUS_FREQUENCIES])

for row in data:
    LLR_vectors.update( { row : {} } )
    PMI_vectors.update( { row : {} } )
    locMI_vectors.update( { row : {} } )
    LPPMI_vectors.update( { row : {} } )
    LPlocMI_vectors.update( { row : {} } )
    if "full_count" in data[row]:
        f1 = data[row]["full_count"]

        for col in word_frequencies:
       
            if word_frequencies[col] > F_THRESHOLD:
                f2 = word_frequencies[col]
                if col in data[row]:
                    f12 = data[row][col]
                    LLR_vectors[row].update({ col : comp.LLR(f1, f2, f12, tf) } )
                    LPlocMI_vectors[row].update({ col : comp.localMI(f1+1, f2+1, f12+1, tf+len(word_frequencies)) } )
                    LPPMI_vectors[row].update({ col : comp.PMI(f1+1, f2+1, f12+1, tf+len(word_frequencies)) } )
                    locMI_vectors[row].update({ col : comp.localMI(f1, f2, f12, tf) } )
                    PMI_vectors[row].update({ col : comp.PMI(f1, f2, f12, tf) } )
                else:
                    LPPMI_vectors[row].update({ col : comp.PMI(f1+1, f2+1, 1, tf+len(word_frequencies)) })
                    LPlocMI_vectors[row].update({ col : comp.localMI(f1+1, f2+1, 1, tf+len(word_frequencies)) } )
                    LLR_vectors[row].update( { col : 0 } )
                    PMI_vectors[row].update( { col : 0 } )
                    locMI_vectors[row].update( { col : 0 } )

    else:
        print("no count", row)

with open(config_data[PROJECT_PATH]+"syntactic_LLR_vectors_"+str(F_THRESHOLD)+".json", "w", encoding="utf-8") as f:
    json.dump(LLR_vectors, f)
            
with open(config_data[PROJECT_PATH]+"syntactic_PMI_vectors_"+str(F_THRESHOLD)+".json", "w", encoding="utf-8") as f:
    json.dump(PMI_vectors, f)

with open(config_data[PROJECT_PATH]+"syntactic_locMI_vectors_"+str(F_THRESHOLD)+".json", "w", encoding="utf-8") as f:
    json.dump(locMI_vectors, f)

with open(config_data[PROJECT_PATH]+"syntactic_LPPMI_vectors_"+str(F_THRESHOLD)+".json", "w", encoding="utf-8") as f:
    json.dump(LPPMI_vectors, f)

with open(config_data[PROJECT_PATH]+"syntactic_LPlocMI_vectors_"+str(F_THRESHOLD)+".json", "w", encoding="utf-8") as f:
    json.dump(LPlocMI_vectors, f)

