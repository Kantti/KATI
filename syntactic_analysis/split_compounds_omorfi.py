import sys, json
sys.path.append("/home/kanner/omorfi/src/python/")
from omorfi import omorfi
o = omorfi.Omorfi()
o.load_from_dir("/home/kanner/omorfi/src/generated/")

wordlist_filename = "all_context_words_with_freqs.json"
dirname = "vai_all/"

def analyse_lexc(lexc):
    line = lexc.output
    if "BOUNDARY=COMPOUND" in line:
        res = []
        lines = line.split("[BOUNDARY=COMPOUND]")
        for l in lines:
            res.append({ x.split("=")[0] : x.split("=")[1] for x in l[1:-1].split("][")})
#        print(res)
        return res
    else:
        return [{ x.split("=")[0] : x.split("=")[1] for x in line[1:-1].split("][")}]

def guess_compound(word):
    
    anal = o.analyse(word)
    anal = [analyse_lexc(a) for a in anal]
    compounds = []
    non_match = False
    for a in anal:
        
        if "ABBR" not in a and "PROPER" not in a:
            if len(a) > 1:
                            
                compounds.append("|".join([x["WORD_ID"] for x in a]))

            else:
                if a[0]["WORD_ID"].replace("-", "") != word: non_match = True
        
    count = 0
    s = None
    if non_match == True:
        return None
    
    for c in compounds:
#        print(c)
        if c.count("|") > count and c.replace("|", "") == word:
            count = c.count("|")
            s = c



    return s



    
    
def get_compound_dict():


    with open(dirname+wordlist_filename, "r", encoding="utf-8") as f:
        wordlist = json.load(f)

    wordlist_zeros = [x for x in wordlist if wordlist[x] == 0]
    wordlist_zeros = [x for x in wordlist if " " not in x]
    wordlist_rep = { x : guess_compound(x) for x in wordlist_zeros if guess_compound(x) != None}

    return wordlist_rep
