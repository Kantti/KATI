from korpreader import *
import json



def scrape(regex, cqp_query):

    output_cats = ("lemma", "word", "pos", "msd", "lemmacomp")
    filename = "vai_all/context_word_corpus/"+regex

    initiate_korp_query(regex, ["klk_fi_"+str(i) for i in range(1980, 2000)], filename, cqp_query, output_cats, sample_size=10000, rewrite=True)

with open("vai_all/word_frequencies_by_synpattern.json", "r", encoding="utf-8") as f:
    data = json.load(f)


skips = ("nurmi", "mato", "ilma", "lampi", "jajalka", "kär", "selkää", "vatsaä", "sydänä", "niveli", "olvi")
start_replacements = ("hoito", "huolto", "pöllö", "koti", "poika", "akka")
lemma_comps = ("pikku", "käsi", "selkä", "jalka", "vatsa", "tyrä", "silmä", "munuainen", "nivunen", "kone")

for word in data:
    cqp_query = "lemma"
    if word not in skips:
        
        if "COMPOUND_ATTRIBUTE" in data[word]:
            cqp_query = "lemmacomp"
            regex = "ATT_"+word
            scrape(regex, cqp_query)

        if  "_POST_COMP_ATTRIBUTE" in data[word]:
            if word in lemma_comps: cqp_query = "lemmacomp"
            regex = "HEAD_"+word
            scrape(regex, cqp_query)
