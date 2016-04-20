import re, sys, os, json
sys.path.append("../")

from constants import *
from project_resources import *
import computation_resources as comp

F_THRESHOLD = 50

word_filename_list = os.listdir(config_data[PROJECT_PATH]+"sentence_corpus/")
wordlist = [word.replace(".json", "") for word in word_filename_list ]

tf = sum(config_data[CORPUS_FREQUENCIES])

print("directory listed")
print("wordlist generated")
print("full corpus size determined")

f_matrix = {}
full_counts = {}
print("calculating full word frequencies")
try:
    with open(config_data[PROJECT_PATH]+"sentence_full_wordcounts_"+str(F_THRESHOLD)+".json", "r", encoding="utf-8") as f:
        full_counts = json.load(f)

except:
    IOError
    for filename in word_filename_list:
        with open(config_data[PROJECT_PATH]+"sentence_corpus/"+filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            full_counts.update( {filename.replace(".json", "") : data["full_count"] })

    print("filtering words under f_threshold")
    full_counts = { f : full_counts[f] for f in full_counts if full_counts[f] > F_THRESHOLD }
    with open(config_data[PROJECT_PATH]+"sentence_full_wordcounts_"+str(F_THRESHOLD)+".json", "w", encoding="utf-8") as f:
        json.dump(full_counts, f)



try:
    with open(config_data[PROJECT_PATH]+"sentence_collocation_frequency_matrix_"+str(F_THRESHOLD)+".json", "r", encoding="utf-8") as f:
        f_matrix = json.load(f)
    print("loading frequency matrix")
except:
    IOError

    print("building frequency matrix")
    for filename in full_counts:
        filename += ".json"
        with open(config_data[PROJECT_PATH]+"sentence_corpus/"+filename, "r", encoding="utf-8") as f:
            data = json.load(f)
    
        matrix_row = { x : 0 for x in full_counts }    

        hit_data = data["data"]

        for hit in hit_data:
            for word in hit:
                if word[LEMMA] in matrix_row:
                    matrix_row[word[LEMMA]] += 1

        f_matrix.update( { filename.replace(".json", "") : matrix_row } )

    with open(config_data[PROJECT_PATH]+"sentence_collocation_frequency_matrix_"+str(F_THRESHOLD)+".json", "w", encoding="utf-8") as f:
        json.dump(f_matrix, f)

           
LLR_matrix = {}
PMI_matrix = {}
locMI_matrix = {}
LPPMI_matrix = {}
LPlocMI_matrix = {}

print("bulding AM matrices")

for i in f_matrix:

    LLR_matrix.update( { i : {} } )
    PMI_matrix.update( { i : {} } )
    locMI_matrix.update( { i : {} } )
    LPPMI_matrix.update( { i : {} } )
    LPlocMI_matrix.update( { i : {} } )
    
    for j in f_matrix[i]:
        f1 = full_counts[i]
        f2 = full_counts[j]
        f12 = f_matrix[i][j]
        if f12 > 0:
            LLR_matrix[i].update( { j : comp.LLR(f1, f2, f12, tf) } )
            PMI_matrix[i].update( { j : comp.PMI(f1, f2, f12, tf) } )
            locMI_matrix[i].update( { j : comp.localMI(f1, f2, f12, tf) } )
            LPPMI_matrix[i].update( { j : comp.PMI(f1+1, f2+1, f12+1, tf+len(wordlist)) } )
            LPlocMI_matrix[i].update( { j : comp.localMI(f1+1, f2+1, f12+1, tf+len(wordlist)) } )
        else:

            LLR_matrix[i].update( { j : 0 } )
            PMI_matrix[i].update( { j : 0 } )
            locMI_matrix[i].update( { j : 0 } )
            
            LPPMI_matrix[i].update( { j : comp.PMI(f1+1, f2+1, 1, tf+len(wordlist)) } )
            LPlocMI_matrix[i].update( { j : comp.localMI(f1+1, f2+1, 1, tf+len(wordlist)) } )

print("writing output files")

with open(config_data[PROJECT_PATH]+"sentence_token_LLR_"+str(F_THRESHOLD)+".json", "w", encoding="utf-8" ) as f:
    json.dump(LLR_matrix, f)

with open(config_data[PROJECT_PATH]+"sentence_token_PMI_"+str(F_THRESHOLD)+".json", "w", encoding="utf-8" ) as f:
    json.dump(PMI_matrix, f)

with open(config_data[PROJECT_PATH]+"sentence_token_locMI_"+str(F_THRESHOLD)+".json", "w", encoding="utf-8" ) as f:
    json.dump(locMI_matrix, f)

with open(config_data[PROJECT_PATH]+"sentence_token_LPPMI_"+str(F_THRESHOLD)+".json", "w", encoding="utf-8" ) as f:
    json.dump(LPPMI_matrix, f)

with open(config_data[PROJECT_PATH]+"sentence_token_LPlocMI_"+str(F_THRESHOLD)+".json", "w", encoding="utf-8" ) as f:
    json.dump(LPlocMI_matrix, f)
