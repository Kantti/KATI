import json, os, sys, csv, re, xlwt
from Context import *
from syntax_resources import *
from project_resources import *



def build_concordances(config_data, corrected = "auto"):
    data = open_data(config_data)
    dirname = config_data[PROJECT_NAME]+"/concordances_"+corrected+"/"
    test_dir(dirname)
    csv_dicts = { x : [] for x in range(0, len(CAT_NAMES)) }
    correction_data = open_correction_data(config_data, rewrite=True)

    for row in data:
        
        if row["id"] in correction_data and corrected != "auto": 
            cor = correction_data[row["id"]]
        else: cor = None
        context = Context(row, corrections=cor, config_data=config_data)
        if context.disregard == False:
            csv_dicts[context.role].append(context.get_concordance_dict())
            if len(context.coords) > 0:
                csv_dicts[COORDINATION].append(context.get_concordance_dict("coord"))


    for x in CAT_NAMES:
        with open(dirname+x+".tsv", "w", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=xls_headers, delimiter="\t")
            writer.writeheader()
            for row in csv_dicts[CAT_NAMES.index(x)]:
                writer.writerow(row)

    workbook = xlwt.Workbook()
    sheets = {CAT_NAMES.index(x) :  workbook.add_sheet(x) for x in CAT_NAMES}
    for cat in range(0, len(CAT_NAMES)):
        for j in range(0, len(xls_headers)):
            sheets[cat].write(0, j, xls_headers[j])

    for cat in range(0, len(csv_dicts)):
        for i in range(0, len(csv_dicts[cat])):
#            if cat ==COORDINATION: print(csv_dicts[cat][i])
#            print(len(csv_dicts[cat][i]))
            for j in range(0, len(csv_dicts[cat][i])):
                sheets[cat].write(i+1, j, csv_dicts[cat][i][xls_headers[j]])

    workbook.save(config_data[PROJECT_NAME]+"/concordances_"+corrected+".xls")


def get_context_word_types(config_data, corrected = "auto"):
    data = open_data(config_data)
    correction_data = open_correction_data(config_data, rewrite=True)
    res = {}
    bases = []
    for row in data:
        if row["id"] in correction_data and corrected != "auto": 
            cor = correction_data[row["id"]]
        else: cor = None
        context = Context(row, corrections=cor, config_data=config_data)
        if context.disregard == False:

            if context.comp_attr != None:
                if context.comp_attr in res:
                    res[context.comp_attr]["POST_COMP_ATTRIBUTE"] += 1
                    res[context.comp_attr]["total"] += 1
                else:
                    res.update( { context.comp_attr : { "POST_COMP_ATTRIBUTE" :  1, "total" : 1, "word" : context.comp_attr } })
            words = [context.context_word]
            if len(context.coordinations) > 0:
                words.extend(context.coordinations)
            for word_f in words:
                word = word_f[LEMMA]
                if context.context_word == [""]: word = "NONE"
                elif context.wordtype != PRE_ATTR and test_proper_name(context.all_words.index(context.context_word),  context.context_word) == True: word = "PROP"
                elif word == "%": word = "prosentti"
                elif context.context_word[POS] == "Num": word = "NUM"
                word = re.sub("-", "", word)
                if word in config_data[COMP_REPLACEMENTS]: word = config_data[COMP_REPLACEMENTS][word]
                if word in config_data[CHECKLIST]: print(CAT_NAMES[context.role], context.id_tag)
                else:
                    if word_f == context.context_word: cat = context.role
                    else: cat = COORDINATION
                    if word in res:
                        res[word]["total"] += 1
                        if CAT_NAMES[cat] in res[word]: res[word][CAT_NAMES[cat]] += 1
                        else:
                            res[word].update( { CAT_NAMES[cat] : 1 } )

                        
                    else:
                        res.update( { word : { "total" : 1, CAT_NAMES[cat] : 1, "word" : word } } )


        

    return res

def write_word_frequency_table(data):
    data = [data[x] for x in data]
    with open(config_data[PROJECT_NAME]+"/word_type_frequencies.tsv", "w", encoding="utf-8") as f:
        header = ["word", "total"]
        header.extend(CAT_NAMES)

        writer = csv.DictWriter(f, fieldnames = header, delimiter = "\t")
        writer.writeheader()
        for row in data:
            
            writer.writerow(row)


project_name = "vai_all"

try:
    config = __import__(project_name)
except:
    ImportError
    sys.exit("No config file found")
    

config_data = config.config_data

build_concordances(config_data, corrected="manual")

data = get_context_word_types(config_data, corrected="manual")

x = 0
for row in data:
    if "COMPOUND_ATTRIBUTE" in data[row]:
        x+=1
        print(data[row])

print(x)

#write_word_frequency_table(data)




with open("vai_all/word_frequencies_by_synpattern.json", "w", encoding="utf-8") as f:
    json.dump(data, f)


   
                    



