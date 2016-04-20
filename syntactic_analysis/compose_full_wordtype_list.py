import re
import json
from syntax_resources import *


def get_wordlist():
    with open("../data/vai_all_1980-2000_datawl-0.json", "r", encoding="utf-8" ) as f:
        data = json.load(f)

    wordlist = []

    for hit in data["data"]:
        wl_here = []
        wl_here = [x[LEMMA] for x in hit["words"] if x[LEMMA] not in wl_here and x[LEMMA] not in wordlist]
        wordlist.extend(wl_here)
        if hit["keyword"][LEMMA] not in wordlist: wordlist.append(hit["keyword"][LEMMA])

    return wordlist

