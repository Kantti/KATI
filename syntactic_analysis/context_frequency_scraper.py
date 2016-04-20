from korpreader import *
import json
from split_compounds_omorfi import *


def scrape(regex, cqp_query):

    output_cats = ("lemma", "word", "pos", "msd", "lemmacomp")
    filename = "vai_all/context_word_corpus/"+regex

    return initiate_korp_query(regex, ["klk_fi_"+str(i) for i in range(1980, 2000)], filename, cqp_query, output_cats, sample_size=10000, rewrite=True, write=False)

with open("vai_all/all_context_words_extend_test.json", "r", encoding="utf-8") as f:
    wordlist = json.load(f)


def count_real_lemmas(data, searchword, comped=None):
    
    total = data["full_count"]
    sample = data["sample_size"]
    data = data["data"]
    oks = 0
    for hit in data:
        hit = hit[0]
        if hit["lemmacomp"] == searchword: oks+=1
        else:
            if searchword in re.split("\|", hit["lemmacomp"]): oks+=1
            elif comped in hit["lemmacomp"]: oks += 1
                    

    if total > sample:
        return (oks/sample)*total
    else:
        return oks

try:
    with open("vai_all/all_context_words_with_freqs.json", "r", encoding="utf-8") as f:
        print("wordlist opened")
        wordlist_with_freqs = json.load(f)
except:
    IOError
    wordlist_with_freqs = {}


try: 
    with open("vai_all/miss_chars.json", "r", encoding="utf-8" ) as f:
        miss_chars = json.load(f)

except:
    IOError
    miss_chars = []

compound_dict = get_compound_dict()

for word in wordlist:
    cqp_query = "lemma"
    regex = ".*"+word+".*"
    comped = None
    if word not in wordlist_with_freqs or word in compound_dict:
        if word in compound_dict: comped = compound_dict[word]
        try:
            data = scrape(regex, cqp_query)
            print("counting:  ", word)
            x = count_real_lemmas(data, word, comped)
            print("counted ",word, ":   ", x)
        
            wordlist_with_freqs.update( { word : x } )
            print(len(wordlist_with_freqs))
            with open("vai_all/all_context_words_with_freqs.json", "w", encoding="utf-8") as f:
                print("printing")
                json.dump(wordlist_with_freqs, f)
        except:
            UnicodeEncodeError
            miss_chars.append(word)
            with open("vai_all/miss_chars.json", "w", encoding="utf-8") as f:
                json.dump(miss_chars, f)



    else:
        print("already scraped")
