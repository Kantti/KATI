import re, sys, os, json
sys.path.append("../")
from Context import *
from syntax_resources import *
from project_resources import *
project_name = config_data[PROJECT_NAME]

dirname = config_data[PROJECT_PATH]+"/"+config_data[CONTEXT_CORPUS_DIR]+"/"
filelist = os.listdir(dirname)

collocation_word_list = {}
skips = ("iva")
misses = ("ukko", "akka")
lemma_comps = ("akilles\|jänne", "olka\|pää", "kinner\|jänne",  "lisä\|luu", "ylävatsa","umpi\|asuoli", "maito\|happo") 

def collect_HEAD_words(filename):
    attribute = re.sub("HEAD_", "", filename)
    attribute = re.sub("-0.json", "", attribute)
    with open(dirname+filename, "r", encoding="utf-8" ) as f:
        word_data = json.load(f)
    total = word_data["full_count"]
    sample = word_data["sample_size"]
    oks = 0
    res = {"full_count" : total, "sample_size" : sample} 
    number_of_others = 0
    number_of_solos = 0
    for hit in word_data["data"]:
        hit = hit[0]
        if hit["lemmacomp"] == attribute: number_of_solos += 1
        else:
            if attribute in re.split("\|", hit["lemmacomp"]):
                comps = re.split("\|", hit["lemmacomp"])
                if comps.index(attribute) < len(comps) -1:
                    oks += 1
                    col_word = comps[comps.index(attribute)+1]
                    if col_word in res: res[col_word] += 1
                    else: res.update( { col_word : 1 } )
                else: number_of_others += 1
#                    print(comps)


    res = { x : res[x] for x in res if res[x] > 0 }
    
    if total == 0: 
        print(attribute)
    else:
        rel = total
        if total > sample: rel=sample
        print(attribute, (oks+number_of_solos+number_of_others)/rel)
    return res

def collect_ATT_words(filename):

    base = re.sub("ATT_", "", filename)
    base = re.sub("-0.json", "", base)
    with open(dirname+filename, "r", encoding="utf-8") as f:
        word_data = json.load(f)
    total = word_data["full_count"]
    sample = word_data["sample_size"]

    res = {"full_count" : total, "sample_size" : sample}
    oks = 0
    number_of_others = 0
    number_of_solos = 0
    for hit in word_data["data"]:
        hit = hit[0]
        if base in skips: break
        if hit["lemmacomp"] == base: number_of_solos += 1
        else:
            if base in re.split("\|", hit["lemmacomp"]):
                comps = re.split("\|", hit["lemmacomp"])
                if comps.index(base) > 0:
                    oks += 1
                    col_word = comps[comps.index(base)-1]
                    if col_word in res:
                        res[col_word] += 1
                    else:
                        res.update( { col_word : 1 } )
            else:
                number_of_others += 1
#                

    if total == 0:
        print(base)
    else:
        rel = total
        if total > sample: rel=sample
        print(base, (oks+number_of_others+number_of_solos)/rel)
    return res

def collect_context_words(filename, cat):

    word = re.sub("-0.json", "", filename)
    with open(dirname+filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    res = {"full_count" : data["full_count"], "sample_size" : data["sample_size"]}
    for row in data["data"]:
        context = Context(row, direction="reversed", role=cat)
        if len(context.res_words) > 0:
            for r in context.res_words:
                if test_proper_name(context.all_words.index(r), r) == True or " " in r[LEMMA]:
                    r_word = "PROP"
                elif r[POS] == "Num": r_word = "NUM"
                else:
                    r_word = r[LEMMA]
                if r_word in res:
                    res[r_word] += 1
                else:
                    res.update( { r_word : 1 } )

    return res

with open(config_data[PROJECT_PATH]+"word_frequencies_by_synpattern.json", "r", encoding="utf-8") as f:
    synpat = json.load(f)

skip_cats = ("word", "total", "COORDINATION", "COMPOUND_ATTRIBUTE", "POST_COMP_ATTRIBUTE")

runner = 0
for filename in filelist:
    word = re.sub("-0.json", "", filename)
    if "HEAD_" in filename:
        collocation_word_list.update({ word.replace("HEAD_", "")+"_HEAD" :collect_HEAD_words(filename)})
    if "ATT_" in filename:
        collocation_word_list.update({ word.replace("ATT_", "")+"_ATT" : collect_ATT_words(filename)})
    if word in synpat:
        runner += 1
        print(runner, len(synpat))
        for cat in synpat[word]:
            print(cat)
            if cat not in skip_cats:
                matrix_key = word+"_"+cat
                print(CAT_NAMES.index(cat))
                collocation_word_list.update( { matrix_key : collect_context_words(filename, CAT_NAMES.index(cat))})

        print("printing file")
        with open(config_data[PROJECT_PATH]+"syntactic_full_syntype_context_word_matrix.json", "w", encoding="utf-8") as f:
            json.dump(collocation_word_list, f)










word_list = []
for x in collocation_word_list:
    for t in collocation_word_list[x]:
        if t == "nuj": print(x)
        if t not in word_list: word_list.append(t)
print(len(word_list))

with open(config_data[PROJECT_PATH]+"all_context_words_extend_test.json", "w", encoding="utf-8") as f:
    json.dump(word_list, f)


