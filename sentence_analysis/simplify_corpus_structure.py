import re, sys, os, json
sys.path.append("../")

from constants import *
from project_resources import *

corpus_dir = config_data[PROJECT_PATH]+"sentence_corpus_3/"

corpus_dir_2 = config_data[PROJECT_PATH]+"sentence_corpus/"

files = os.listdir(corpus_dir)

for fil in files:
    print(fil)
    with open(corpus_dir+fil, "r", encoding="utf-8") as f:
        data = json.load(f)

    for i in range(0, len(data["data"])):
        for j in range(0, len(data["data"][i])):
            row = [data["data"][i][j]["lemma"], data["data"][i][j]["word"], data["data"][i][j]["pos"], data["data"][i][j]["msd"], data["data"][i][j]["lemmacomp"]]
            data["data"][i][j] = row

    with open(corpus_dir_2+fil, "w", encoding="utf-8") as f:
        json.dump(data, f)
