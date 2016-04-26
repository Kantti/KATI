import json, os, sys, re, math, operator, random, numpy, pandas, time
sys.path.append("../")

from constants import *
from project_resources import *
from syntax_resources import *
import computation_resources as comp

def get_first_order_freqs():

    filenames = os.listdir(config_data[PROJECT_PATH]+"sentence_corpus")

    full_count = 0
    first_order_freqs = {}
    for fn in filenames:
        print("first_order_freqs", fn)
        with open(config_data[PROJECT_PATH]+"sentence_corpus/"+fn, "r", encoding="utf-8") as f:
            data = json.load(f)

        full_count += sum([len(hit) for hit in data["data"]])
        try:
            first_order_freqs.update( { fn.replace(".json", "") : [data["full_count"], data["full_count"]/data["sample_size"]] })
        except:
            ZeroDivisionError
            print(fn)
        

    return first_order_freqs

            



def build_frequency_list(size):

    filenames = os.listdir(config_data[PROJECT_PATH]+"sentence_corpus")

    freq_list = {}
    ok_pos = ("A", "N", "V")

    for fn in filenames:
        with open(config_data[PROJECT_PATH]+"sentence_corpus/"+fn, "r", encoding="utf-8") as f:
            data = json.load(f)

        for hit in data["data"]:
        
            words = compress_props(hit)
            words = compress_verbal_compounds(words)
            for word in words:
                if word[POS] in ok_pos:
                    item = word[LEMMA]
                    if test_proper_name(words.index(word), word): item = "PROP"
                    if item in freq_list: freq_list[item] += 1
                    else: freq_list.update({item : 1})

    freq_size = { f : freq_list[f] for f in freq_list if freq_list[f] > size }


    with open(config_data[PROJECT_PATH]+"sentence_collocation_words_by_freq_"+str(size)+".json", "w", encoding="utf-8" ) as f:
        json.dump(freq_size, f)

    return freq_size



def build_collocation_matrix(first_order_freqs, rank_map):

    filenames = os.listdir(config_data[PROJECT_PATH]+"sentence_corpus")
    rl = []
    for r in rank_map:
        if r not in rl: rl.append(r)

    rank_map = rl
    collocation_matrix = pandas.DataFrame()
    ok_pos = ("A", "N", "V")
    
    t_0 = time.time()
    for fn in first_order_freqs:
        print(fn)
        try:
            pandas.Series.from_csv(config_data[PROJECT_PATH]+"sentence_collocations/"+fn+".tsv", sep="\t")
        except:
            IOError
            t_start = time.time()
            with open(config_data[PROJECT_PATH]+"sentence_corpus/"+fn+".json", "r", encoding="utf-8") as f:
                data = json.load(f)
        
            row = pandas.Series(index=rank_map, name=fn)
            row = row.fillna(0)
            t_1 = time.time()
#        print("source file opened: ", t_1 - t_start)
            for hit in data["data"]:
        
                words = compress_props(hit)
                words = compress_verbal_compounds(words)
                for word in words:
                    if word[POS] in ok_pos:
                        item = word[LEMMA]
                        if item in rank_map: row[item] += 1
            t_2 = time.time()
            print(len(row))
            row.to_csv(config_data[PROJECT_PATH]+"sentence_collocations/"+fn+".tsv", sep="\t", encoding="utf-8")

            with open("time_debug_"+str(int(t_0))+".tsv", "a", encoding="utf-8") as f:
                f.write(str(t_1-t_start) +"\t"+ str((t_2-t_1)/len(data["data"])) +"\t"+str(time.time()-t_2)+"\n")

    return True


SIZE = 100

print("opening freq list")

try:
    with open(config_data[PROJECT_PATH]+"sentence_collocation_words_by_freq_"+str(SIZE)+".json", "r", encoding="utf-8" ) as f:
        freq_list = json.load(f)
    print("freq list opened")

except:
    IOError
    print("open failed, building new freq list")
    freq_list = build_frequency_list(SIZE)

print("getting first order freqs")

try:
    with open(config_data[PROJECT_PATH]+"sentence_first_order_freqs.json", "r", encoding="utf-8") as f:
        first_order_freqs = json.load(f)
except:
    IOError
    first_order_freqs = get_first_order_freqs()
    with open(config_data[PROJECT_PATH]+"sentence_first_order_freqs.json", "w", encoding="utf-8") as f:
        json.dump(first_order_freqs, f)


tf = sum(config_data[CORPUS_FREQUENCIES])
wordcount_ratio = tf/config_data[SENTENCE_CORPUS_WORDCOUNT]

freq_sorted = sorted(freq_list.items(), key=operator.itemgetter(1), reverse = True)
freq_list_with_ranks = {}
rank_map = []

print("sorting freq lists")

for i in range(0, len(freq_sorted)):
    freq_list_with_ranks.update( { freq_sorted[i][0] : [ i, freq_sorted[i][1]] })
    rank_map.append( freq_sorted[i][0] )

print("building raw count collocation matrices")

# MATRIX A: equal distribution based on random indices
# MATRIX B: gaussian distribution based on variance of V and mean at mean_B
# MATRIX C: gaussian distribution based on variance of V and mean at mean_C
# MATRIX D: gaussian distribution based on variance of V and mean at mean_D
print(len(rank_map))
collocation_matrix = build_collocation_matrix(first_order_freqs, rank_map)

print("calculating association measures")

def calculate_AMs(collocation_matrix):
    LLR = {}
    locMI = {}
    for row in collocation_matrix:

        c1 = first_order_freqs[row][0]
        LLR.update( { row : [] } )
        locMI.update( { row : [] } )
    
        for col in collocation_matrix[row]:

            c2 = freq_list[rank_map[col]]*wordcount_ratio
            c12 = collocation_matrix[row][col]*first_order_freqs[row][1]
            tf = sum(config_data[CORPUS_FREQUENCIES])

            if c12 > 0:
                LLR[row].append(comp.LLR(c1, c2, c12, tf))
                locMI[row].append(comp.localMI(c1, c2, c12, tf))
            else:
                LLR[row].append(0)
                locMI[row].append(0)

    print("printing output files")

    with open(config_data[PROJECT_PATH]+"sentence_collocation_matrix_with_freqs_LLR.json", "w", encoding="utf-8") as f:
        json.dump(LLR, f)

    with open(config_data[PROJECT_PATH]+"sentence_collocation_matrix_with_freqs_locMI.json", "w", encoding="utf-8") as f:
        json.dump(locMI, f)




