#!/usr/bin/python
# -*- coding: utf-8 -*-
import ssl
import random
from itertools import islice
from threading import Thread
import re
import json
import html
import ijson.backends.yajl2 as ijson
import urllib.request
import certifi
import time

BATCH_SIZE = 5000
dummy_cp = ["KLK_FI_"+str(i) for i in range(1890, 1900)]
ca_certs = "/etc/ssl/certs/ca_certificates.crt"
ca_path = "/home/kanner/anaconda3/ssl/cacert.pem"

def compose_url_string(regex, start, corpus_list, cqp_query, output_cats, context, sort="random", sample_size="all"):
    res = "https://korp.csc.fi/cgi-bin/korp.cgi?command=query"
    cqp = 'cqp=['+cqp_query+'="'+regex+'"]'
    cqp = regex_decode(cqp)

    if context == "sentence":
        res += "&"+cqp+"&defaultcontext=1+sentence&defaultwithin=sentence&show="
    else:
        res += "&"+cqp+"&defaultcontext=0&show="
    
    ###METADATA CATEGORIES

    res += "%2C".join(output_cats)
    res += "&start="+str(start)

    ###SAMPLE SIZE
    if type(sample_size) == int:
        res += "&end="+str(sample_size-1)
    else:
        res += "&end="+str(int(start+BATCH_SIZE-1))
    
    ###RANDOMIZE SAMPLE
    if sort == "random":
        res += "&sort=random"
        res += "&random_seed="+str(random.randint(1000000, 9999999))
    
    ###CHOOSE CORPORA
    res += "&corpus="
    for corpus in corpus_list:
        res += corpus+"%2C"
    res = re.sub("%2C$", "", res)
    res += "&incremental=true"
    return res

def regex_decode(string):

    string = re.sub(",", "%2C", string)
    string = re.sub("\[", "%5B", string)
    string = re.sub("\]", "%5D", string)
    string = re.sub("\*", "%2A", string)
    string = re.sub("\.", "%2E", string)
    string = re.sub("\|", "%7C", string)
    string = re.sub("\(", "%28", string)
    string = re.sub("\)", "%29", string)        
    string = re.sub("ä", "%C3%A4", string)
    string = re.sub("ö", "%C3%B6", string)
    string = re.sub("å", "%C3%A5", string)
    string = re.sub("Ä", "%C3%84", string)
    string = re.sub("Ö", "%C3%96", string)
    string = re.sub("ü", "%C3%BC", string)
    string = re.sub(" ", "%20", string)
    string = re.sub("§", "%A7", string)

    return string

def query(regex, corpus_list, cqp_query, output_cats, sample_size="all", context="sentence" ):
    if sample_size != "all": BATCH_SIZE = sample_size
    start = 0
    data = 0
    hits = -1
    lap = 0
    while data != hits:
        url_string = compose_url_string(regex, start, corpus_list, cqp_query, output_cats, context, sort="random", sample_size=sample_size)
        print(url_string)
        qround = get_query_round(url_string, regex, data, output_cats)
        if type(sample_size) != int or qround[0] < sample_size:
            hits = qround[0]
        else:
            hits = sample_size

        print("batching", start, "of", hits, "from", regex)
        
        return {"sample_size" : hits, "full_count" : qround[0], "data" : qround[1] }
            
        data += len(qround[1])
        start += BATCH_SIZE

            
        

    




def get_query_round(url_string, regex, index_starter, output_cats):       
    t = time.time()
    f = urllib.request.urlopen(url_string)
    response_as_string = f.read().decode("utf-8")
    items = json.loads(response_as_string)
    if "hits" in items:
        hits = int(items["hits"])
    else:
        print("error in query", url_string)
    res = []
    if "sentence" in output_cats:
        for item in items["kwic"]:
            keyword = item["tokens"][item["match"]["start"]]
            line = [[word[cat] if cat in word else "?" for cat in output_cats] for word in item["tokens"] if item["tokens"].index(word) != item["match"]["start"]]
            res.append({"id" : index_starter, "keyword" : [keyword[cat] if cat in keyword else "?" for cat in output_cats] , "words" : line, "key_loc" : item["match"]["start"]})
            index_starter += 1
    else:
        for item in items["kwic"]:
            res.append(item["tokens"])
            



   
                
    return [hits, res]




