import json, re, os, sys, math
sys.path.append("../")

from constants import *
from project_resources import *
from Context import *

print("opening hit data")
with open(config_data[DATA_FILENAME], "r", encoding="utf-8") as f:
    data = json.load(f)

print("opening first order type collocations")
with open(config_data[PROJECT_PATH]+"sentence_token_LLR_"+str(config_data[F_THRESHOLD])+".json", "r", encoding="utf-8" ) as f:
    LLR_types= json.load(f)
with open(config_data[PROJECT_PATH]+"sentence_token_LPlocMI_"+str(config_data[F_THRESHOLD])+".json", "r", encoding="utf-8" ) as f:
    locMI_types = json.load(f)
with open(config_data[PROJECT_PATH]+"sentence_token_LPPMI_"+str(config_data[F_THRESHOLD])+".json", "r", encoding="utf-8" ) as f:
    PMI_types = json.load(f)


LLR_tokens = {}
locMI_tokens = {}
PMI_tokens = {}

wordlist = [x for x in LLR_types]

print("building matrices")

for hit in data["data"]:
    
    context = Context(hit)
    type_words = context.slice_ngram(10)
    if len(type_words) == 10:
        type_words = [w[LEMMA] for w in type_words if w[LEMMA] in wordlist]
    else: type_words = []

    if len(type_words) > 1:
        LLR_tokens.update({hit["id"] : {} } )
        locMI_tokens.update({hit["id"] : {} } )
        PMI_tokens.update({hit["id"] : {} } )
        print(type_words)
        for word in wordlist:

            mean_LLR = sum([LLR_types[word][x] for x in type_words])/len(type_words)
            if math.isnan(mean_LLR): mean_LLR = 0
    
            mean_PMI = sum([PMI_types[word][x] for x in type_words])/len(type_words)
            if math.isnan(mean_PMI): mean_PMI = 0

            mean_locMI = sum([locMI_types[word][x] for x in type_words])/len(type_words)
            if math.isnan(mean_locMI): mean_locMI = 0


            LLR_tokens[hit["id"]].update( { word : mean_LLR } )
            PMI_tokens[hit["id"]].update( { word : mean_PMI } )
            locMI_tokens[hit["id"]].update( { word : mean_locMI } )


print("printing output files")
    
with open(config_data[PROJECT_PATH]+"sentence_LLR_vectors_"+str(config_data[F_THRESHOLD])+".json", "w", encoding="utf-8" ) as f:
    json.dump(LLR_tokens, f)
with open(config_data[PROJECT_PATH]+"sentence_locMI_vectors_"+str(config_data[F_THRESHOLD])+".json", "w", encoding="utf-8" ) as f:
    json.dump(locMI_tokens, f)
with open(config_data[PROJECT_PATH]+"sentence_PMI_vectors_"+str(config_data[F_THRESHOLD])+".json", "w", encoding="utf-8" ) as f:
    json.dump(PMI_tokens, f)


