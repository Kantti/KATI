import re, json, os, sys, csv
sys.path.append("../")
from constants import *
from project_resources import *
from syntax_resources import *
from Context import *

good_pos = ("V", "N", "A")

with open(config_data[DATA_FILENAME], "r", encoding="utf-8") as f:
    original_data = json.load(f)

all_context_words = {}

for hit in original_data["data"]:
    context = Context(hit)
    for word in context.all_words:
        
        if test_proper_name(context.all_words.index(word), word) != True and word[POS] in good_pos:
            if word[LEMMA] not in all_context_words: 
                all_context_words.update({ word[LEMMA] : 1 })
            else: all_context_words[word[LEMMA]] += 1
print(PROJECT_NAME)
with open(config_data[PROJECT_PATH]+"all_sentence_context_words_with_freqs.tsv", "w", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter='\t')
    [writer.writerow([w, all_context_words[w]]) for w in all_context_words]

with open(config_data[PROJECT_PATH]+"all_sentence_context_words_with_freqs.json", "w", encoding="utf-8") as f:
        json.dump(all_context_words, f)
