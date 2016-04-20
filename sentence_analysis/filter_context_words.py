import json, os, sys, re
sys.path.append("../")

from constants import *
from project_resources import *


def test_word(word):

    if word.endswith("-"): return False
    if len(word) < 3: return False
    if re.match("^[a-zäö]*$", word) == None: return False

    return True


with open(config_data[PROJECT_PATH]+"all_sentence_context_words_with_freqs.json", "r", encoding="utf-8") as f:

    data = json.load(f)

print(len(data))

data_filtered = { d : data[d] for d in data if test_word(d) == True }

with open(config_data[PROJECT_PATH]+"filtered_sentence_context_words_with_freqs.json", "w", encoding="utf-8") as f:
    json.dump(data_filtered, f)


