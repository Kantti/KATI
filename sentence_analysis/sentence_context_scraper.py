import json, sys, os, re
sys.path.append("../")
from constants import *
import korpreader as korp
from project_resources import *



def scrape(regex, cqp_query):

    output_cats = ("lemma", "word", "pos", "msd", "lemmacomp")
    filename = "vai_all/context_word_corpus/"+regex

    return korp.query(regex, ["klk_fi_"+str(i) for i in range(1980, 2000)], cqp_query, output_cats, sample_size=10000)

with open(config_data[PROJECT_PATH]+"filtered_sentence_context_words_with_freqs.json", "r", encoding="utf-8") as f:

    words = json.load(f)


for word in words:
    filelist = os.listdir(config_data[PROJECT_PATH]+"sentence_corpus/")
    print(len(filelist), "/", len(words))
    if word == "säilyä":
        query = scrape(word, "lemma")
        with open(config_data[PROJECT_PATH]+"sentence_corpus/"+word+".json", "w", encoding="utf-8") as f:
            json.dump(query, f)

    

