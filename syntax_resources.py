from constants import *
import re
import json
from project_resources import *
#from Context import *


### COMPRESS VERBAL CONSTRUCTIONS

def compress_props(words):
    removed = []

    for i in range(0, len(words)-1):
        if test_proper_name(i, words[i]) == True: words[i][MSD] += "|SUBCAT_Prop"
        if test_proper_name(i, words[i]) == True and test_proper_name(i+1, words[i+1]):
            if words[i+1][POS] != "N" and "OTHER" not in analyse_msd(words[i+1]):
                words[i+1][POS] = "N"
                words[i+1][MSD] = "SUBCAT_Prop|CASECHANGE_Up|NUM_sg"
                if words[i+1][WORD].endswith("n"): words[i+1][MSD] += "|CASE_Gen"
                else: 
                    words[i+1][MSD] += "|CASE_Nom"
                    words[i+1][LEMMA] = words[i+1][WORD]

                    
            if "CASE" in analyse_msd(words[i]) and analyse_msd(words[i])["CASE"] == "Nom":
                words[i+1][WORD] = words[i][WORD]+" "+words[i+1][WORD]
                words[i+1][LEMMA] = words[i][LEMMA]+" "+words[i+1][LEMMA]
                if msd_key(words[i+1], "SUBCAT") != "Prop": words[i+1][MSD] += "|SUBCAT_Prop"
                removed.append(i)                   

            elif msd_key(words[i], "OTHER") == "UNK":
                if "CASE" in analyse_msd(words[i]) and "CASE" != "Nom":
                    notnom = True
                else:
                    words[i+1][WORD] = words[i][WORD]+" "+words[i+1][WORD]
                    words[i+1][LEMMA] = words[i][LEMMA]+" "+words[i+1][LEMMA]
                    words[i+1][MSD] += "|SUBCAT_Prop"
                    removed.append(i)


    for i in reversed(removed):
        words.remove(words[i])

    return words

def compress_verbal_compounds(words):

    words = compress_negation_compounds(words)
    words = compress_tempus_compounds(words)
    return words

def compress_negation_compounds(words):
    neg_open = False
    removed = []
    for i in range(0, len(words)):
        if len(words[i]) < POS: print(words)
        if words[i][POS] == "V" and "SUBCAT" in analyse_msd(words[i]) and analyse_msd(words[i])["SUBCAT"] == "Neg":
            neg = words[i]
            neg_i = i
            neg_open = True
        elif neg_open == True and words[i][POS] == "V" and "NEG" in analyse_msd(words[i]) and analyse_msd(words[i])["NEG"] == "ConNeg":
            words[i][MSD] += "|"+neg[MSD]
            words[i][WORD] = neg[WORD]+" "+words[i][WORD]
#                print(words[i][WORD])
            neg_open = False
            removed.append(neg_i)
        elif neg_open == True and words[i][POS] == "V" and all(s in analyse_msd(words[i]) for s in ("CASE", "PCP")):
            if analyse_msd(words[i])["CASE"] == "Nom" and analyse_msd(words[i])["PCP"] == "PrfPrc":
                words[i][MSD] = re.sub("PCP_PrfPrc", "TENSE_Pst|MOOD_Ind", words[i][MSD])
                words[i][MSD] += "|"+neg[MSD]
                words[i][WORD] = neg[WORD]+" "+words[i][WORD]
                neg_open = False
 
                removed.append(neg_i)
    for r in reversed(removed):
        words.remove(words[r])

    return words

def compress_tempus_compounds(words):
    temp_open = False
    removed = []
    participles = ["PrfPrc", "PrsPrc"]
    for i in range(0, len(words)):
        if words[i][LEMMA] == "olla" and "PRS" in analyse_msd(words[i]):
            copula = words[i]
            copula_i = i
            temp_open = True
            if "PRS" not in analyse_msd(copula): print(copula[MSD])
            copula_num = re.sub("[0-9]", "", analyse_msd(copula)["PRS"])
        elif temp_open == True and words[i][POS] == "V" and "CASE" in analyse_msd(words[i]) and analyse_msd(words[i])["CASE"] == "Nom" and analyse_msd(words[i])["NUM"] == copula_num and "PCP" in analyse_msd(words[i]) and analyse_msd(words[i])["PCP"] in participles and words[i][LEMMA] != words[i][WORD]:
            temp_open = False
            removed.append(i)
            if "MOOD" not in analyse_msd(copula): print("No mood:", copula)
            if analyse_msd(copula)["MOOD"] == "Cond" or analyse_msd(copula)["MOOD"] == "Pot": words[copula_i][MSD] += "|TENSE_Pst"
            words[copula_i][MSD] = re.sub("TENSE_Prs", "TENSE_Prf", words[copula_i][MSD])
            words[copula_i][MSD] = re.sub("TENSE_Pst", "TENSE_PlPrf", words[copula_i][MSD])
            words[copula_i][LEMMA] = words[i][LEMMA]
            words[copula_i][WORD] += " "+words[i][WORD]
        
    for r in reversed(removed):
        words.remove(words[r])
        
    return words


### TESTS

def test_NP_head(words, word, debug=False):


    if test_proper_name(words.index(word), word) == True: return True
#    if debug==True:print("here")
    if words[words.index(word)-1][LEMMA] in coordination_elements: return False
    if words[0] == word: return False
    for i in range(words.index(word)-1, -1, -1):

        if msd_key(words[i], "SUBCAT") == "Prop": return False
        if msd_key(word, "CASE") == msd_key(words[i], "CASE") and msd_key(word, "NUM") == msd_key(words[i], "NUM") and words[i-1][WORD] not in coordination_elements:
            if words[i][POS] == "N": return False
            else:
                return True

        if "PRS" in analyse_msd(words[i]):
            return False

        if "N" in words[i][POS] and msd_key(words[i], "CASE") in ("Nom", "Gen") : return True
        
        
    return False
        


def test_NP_attribute(words, word, debug=False):
    if word[POS] not in np_attribute_pos: return False
    if word[POS] == "V" and "PCP" not in analyse_msd(word): return False
#    print(words[0])
    if test_proper_name(words.index(word), word) == True: return False
    if words[-1] == word: return False
    for i in range(words.index(word)+1, len(words)):
        if msd_key(words[i], "SUBCAT") == "Prop": return True
        if msd_key(word, "CASE") == msd_key(words[i], "CASE") and msd_key(word, "NUM") == msd_key(words[i], "NUM") and words[i-1][WORD] not in coordination_elements: 
            return True

        if "PRS" in analyse_msd(words[i]):
            return False

        if words[i][POS] == "N" and msd_key(words[i], "CASE") not in ("Nom", "Gen") : return False
        
        
    return False

def test_Pron_attribute(words, word, debug=False):

    if words.index(word) == 0: return False

    if words[words.index(word)-1][POS] == "Pron" and msd_key(words[words.index(word)-1], "SUBCAT") == "Pers": return True

    return False





def test_NUM_attribute(words, word, debug=False):
    if word[POS] not in num_attribute_pos: return False
    if test_proper_name(words.index(word), word): return False
    
    loc = words.index(word)

    num_words = []
    if loc > 0 : num_words.append(words[loc-1])
    if loc < len(words)-1: num_words.append(words[loc+1])

    for n in num_words:
        if n[LEMMA] != "toinen":
            if n[POS] == "Num": return True
            if re.match(num_pattern, n[WORD]): return True
            if n[WORD].startswith(semi_numerals): return True

    return False

def test_Ess_adverbial(words, word, debug=False):
    return msd_key(word, "CASE") == "Ess"

def test_finite_subject(words, word, debug=False):

    verb = locate_closest_verb(words, words.index(word), FINITE)
    if verb != None: verb = words[verb]
    else: return False

    if "PRS" not in analyse_msd(verb): return False

    return test_finite_subject_agreement(verb, word)
    
def test_finite_subject_agreement(verb, noun):

    if "PRS" not in analyse_msd(verb) or "NUM" not in analyse_msd(noun): return False
    if re.sub("3", "", msd_key(verb, "PRS")) == msd_key(noun, "NUM") and msd_key(noun, "CASE") == "Nom": return True
    if verb[LEMMA] in modal_verbs and msd_key(noun, "CASE") == "Gen": return True
    return False

def test_object(words, word, debug=False):

    verb = locate_closest_verb(words, words.index(word), FINITE)
    if verb != None: verb = words[verb]
    else: return False

    if verb[LEMMA] == "olla": return False
    if verb[LEMMA] in intransitives: return False

    if msd_key(verb, "PRS") == "Pe4":
        if msd_key(word, "CASE") == "Gen": return False

    else:
        if msd_key(word, "CASE") == "Nom" and msd_key(word, "NUM") == "Sg" : return False

    
    
    if verb[LEMMA] in modal_verbs and msd_key(word, "CASE") == "Gen":
        return False
    return True

def test_predicative(words, word, debug=False):
#    if debug == True: print("start")
    verb = locate_closest_verb(words, words.index(word), FINITE)
#    if debug == True: print(verb)
    if verb != None: verb = words[verb]
    else: return False
#    if debug == True: print(verb)
    if verb[LEMMA] != "olla" or msd_key(word, "CASE") not in predicative_cases or msd_key(verb, "PRS") == "Pe4": return False
#    print("here")
    if re.search("[12]", msd_key(verb, "PRS")) != None: return True
    has_subject = False
    for i in expanding_iteration(words, verb):
        if test_finite_subject_agreement(verb, words[i]) == True and i != words.index(word):
            has_subject = True
#    print(has_subject)
    if has_subject == False: return False

    return True

def test_e_subject(words, word, debug=False):

    verb_loc = locate_closest_verb(words, words.index(word), FINITE)
    if verb_loc == None: return verb_loc
    
    if msd_key(word, "CASE") not in ("Part", "Par") or msd_key(words[verb_loc], "PRS") == "Pe4": return False

    for i in range(verb_loc+1, len(words)):
        if "PRS" in analyse_msd(words[i]):break
        elif msd_key(words[i], "CASE") == "Nom": return False

    for i in range(verb_loc-1, -1, -1): 
        if "PRS" in analyse_msd(words[i]): return True
        elif msd_key(words[i], "CASE") == "Nom": return False
    return True
    
def test_POS_subject(words, word, debug=False):

    verb = locate_closest_verb(words, words.index(word), FINITE)
    if verb != None: verb=words[verb]
    else: return False
    if verb[LEMMA] != "olla": return False
    if msd_key(word, "CASE") != "Ade": return False
    return True

def test_N_subject(words, word, debug=False):
    
    if locate_closest_verb(words, words.index(word), INF_DRV) != None and msd_key(word, "CASE") == "Gen": return True
    else: return False
    
    
def test_P_subject(words, word, debug=False):
    
    verb = locate_closest_verb(words, words.index(word), FINITE)
    if verb != None: verb=words[verb]
    else: return False
    if verb[LEMMA] != "olla" and "PRS" in analyse_msd(verb): return False
    return test_finite_subject(words,word)

def test_POS_object(words, word, debug=False):

    verb = words[locate_closest_verb(words, words.index(word), FINITE)]
    if verb[LEMMA] != "olla": return False
    for i in range(0, len(words)):
        if test_finite_subject_agreement(verb, words[i]): return False
    return True

def test_Gen_attribute(words, word, debug=False):

    if msd_key(word, "CASE") != "Gen":return False
    for i in range(words.index(word), len(words)):
        if words[i][LEMMA] in coordination_elements: return False
        if "PRS" in analyse_msd(words[i]): return False
        if words[i][POS] == "N": return True

def test_adverbial(words, word, debug=False):

    if msd_key(word, "CASE") in adverbial_cases and msd_key(word, "CASE") != "Ess": return True 



def test_proper_name(i, word):
    if "OTHER" not in analyse_msd(word) and word[LEMMA].islower() == True: return False
    if "SUBCAT" in analyse_msd(word) and analyse_msd(word)["SUBCAT"] == "Prop": return True
    elif i > 0 and "CASECHANGE" in analyse_msd(word) and analyse_msd(word)["CASECHANGE"] == "Up" and word[WORD].isupper() == False: return True
    else: return False



def test_verb_agreement_match(verb, noun, cases, agreement):
    if "NUM" in analyse_msd(noun) and "CASE" in analyse_msd(noun) and analyse_msd(noun)["CASE"] in cases:
        if agreement == True and "VOICE" in analyse_msd(verb) and analyse_msd(verb)["VOICE"] == "Act":
            num_noun = analyse_msd(noun)["NUM"]
            if "PRS" in analyse_msd(verb) and "3" in analyse_msd(verb)["PRS"]:
                num_verb = re.sub("3", "", analyse_msd(verb)["PRS"])
                if num_verb == num_noun:
                    return True
        else:
            return True

    return False

def test_verb_to_type(verb, verb_type):

    if verb_type == FINITE:
        if "PRS" in analyse_msd(verb): return True
    elif verb_type == INFINITE: 
        if verb[POS] == "V" and "PRS" not in analyse_msd(verb): return True
    elif verb_type == DERIVATE:
        if msd_key(verb, "DRV") == "Der+minen": return True
    elif verb_type == INF_DRV:
        if msd_key(verb, "DRV") == "Der+minen": return True
        if verb[POS] == "V" and "PRS" not in analyse_msd(verb): return True
    else:
        if msd_key(verb, "DRV") == "Der+minen": return True
        if verb[POS] == "V" and "PRS" not in analyse_msd(verb): return True
        if "PRS" in analyse_msd(verb): return True
 
    return False



### LOCATING FUNCTIONS

def locate_closest_verb(words, key_loc, verb_type):

    sen_len = len(words)

        #look for verb left
    closest_left = None
    closest_right = None
    for i in range(key_loc-1, -1, -1):
        if test_verb_to_type(words[i], verb_type) == True:
            closest_left = i
            break

    for i in range(key_loc+1, sen_len):
        if test_verb_to_type(words[i], verb_type) == True:
            closest_right = i
            break

    return select_closer(closest_right, closest_left, key_loc, "l")




                
def locate_subject(words, word, debug=False, verb_loc=None):
    if verb_loc == None:
        verb_loc = locate_closest_verb(words, words.index(word), FINITE)
    if verb_loc == None: return None
    if "Sg1" in msd_key(words[verb_loc], "PRS"): return FIRST_PERSON_SINGULAR
    if "Sg2" in msd_key(words[verb_loc], "PRS"): return SECOND_PERSON_SINGULAR
    if "Pl1" in msd_key(words[verb_loc], "PRS"): return FIRST_PERSON_PLURAL
    if "Pl2" in msd_key(words[verb_loc], "PRS"): return SECOND_PERSON_PLURAL
    closest_right = None
    closest_left = None
    for i in range(verb_loc+1, len(words)):
        if "PRS" in analyse_msd(words[i]): break
        if test_verb_agreement_match(words[verb_loc], words[i], ("Nom"), True):
            closest_right = i
        if words[verb_loc][LEMMA] in modal_verbs and test_verb_agreement_match(words[verb_loc], words[i], "Gen", False):
            closest_right = i

    for i in range(verb_loc-1, -1, -1):
        if "PRS" in analyse_msd(words[i]): break
        if test_verb_agreement_match(words[verb_loc], words[i], ("Nom"), True):
            closest_left = i
            break
        if words[verb_loc][LEMMA] in modal_verbs and test_verb_agreement_match(words[verb_loc], words[i], "Gen", False):
            closest_left = i
            break

    return select_closer(closest_right, closest_left, verb_loc, "l")


def locate_object(words, word, debug=False):

    verb_loc = locate_closest_verb(words, words.index(word), FINITE)
    if verb_loc == None: return None
    closest_right = None
    closest_left = None
    for i in range(verb_loc+1, len(words)):
        if "PRS" in analyse_msd(words[i]): break
        if test_verb_agreement_match(words[verb_loc], words[i], ("Nom", "Gen", "Par"), False):
            closest_right = i

    for i in range(verb_loc-1, -1, -1):
        if "PRS" in analyse_msd(words[i]): break
        if test_verb_agreement_match(words[verb_loc], words[i], ("Nom", "Gen", "Par"), False):
            closest_left = i

    return select_closer(closest_right, closest_left, verb_loc, "r")


def locate_gen_head(words, word, debug=False):

    for i in range(words.index(word)+1, len(words)):

        if words[i][POS] == "N": return i

    return None


def locate_agreeing_head(words, word, debug=False):

    if words[-1] == word: return None
    res = None
    for i in range(words.index(word)+1, len(words)):
        if msd_key(words[i], "SUBCAT") == "Prop": return i
        if msd_key(word, "CASE") == msd_key(words[i], "CASE") and msd_key(word, "NUM") == msd_key(words[i], "NUM") and words[i-1][WORD] not in coordination_elements: res = i
        else: 
            if res != None: return res

    return res

def locate_adverbial(words, word, debug=False):

    res_r = None
    res_l = None
    adv_open = False
    verb_loc = locate_closest_verb(words, words.index(word), FINITE)
    for i in range(verb_loc+1, len(words)):

        if msd_key(words[i], "CASE") in adverbial_cases: 
            adv_open = True
            res_r = i
        else:
            if adv_open == True: break

    for i in range(verb_loc-1, -1, -1):
        if msd_key(words[i], "CASE") in adverbial_cases:
            res_r = i
            break
    
    return select_closer(res_r, res_l, verb_loc, "r")




def locate_num_head(words, word, debug=False):

    if words[words.index(word)-1][POS] == "Num" or words[words.index(word)-1][WORD].startswith(semi_numerals) or re.match(num_pattern, words[words.index(word)][WORD]) != None: return words.index(word)+1
    else:
        return words.index(word)+2


### ANALYSE STUFF

def analyse_coordination(words, word):
    
    coords = []
    co_open = False
    att_open = False

    if words.index(word) < len(words)-1 and words[words.index(word)+1][LEMMA] in coordination_elements:
        for i in range(words.index(word)+1, len(words)-1):
        
            if words[i][LEMMA] in coordination_elements:
#                if co_open == True: 
#                    break
#                else:
#                    if att_open == True:
#                        coords.append(i-1)
#                        att_open = False
#                    co_open = True
#            elif words[i][POS] == "Pron": break
#            elif msd_key(words[i], "CASE") == msd_key(word, "CASE") or msd_key(words[i], "CASE") == "Gen":
#                att_open = True
#            else:
#                if att_open == True and co_open == True: 
#                    coords.append(i-1)
#                break

                if (msd_key(words[i+1], "CASE") == msd_key(word, "CASE") or msd_key(words[i+1], "CASE") == "Gen") and words[i+1][POS] != "Pron":
                    coords.append(i+1)
                else:
                    break

    
    co_open = False
#    print(test_NP_head(words, word) , test_NP_head(words, words[words.index(word)-2]))
#    print(test_NP_attribute(words, word) , test_NP_attribute(words, words[words.index(word)-2]))
    if words.index(word) > 2 and test_NP_attribute(words, word) == test_NP_attribute(words, words[words.index(word)-2]) and test_NP_head(words, word) == test_NP_head(words, words[words.index(word)-2]):
        for i in range(words.index(word)-1, -1, -1):

            if words[i][LEMMA] in coordination_elements:
                co_open = True

            elif msd_key(words[i], "CASE") == msd_key(word, "CASE") and co_open == True:
                coords.append(i)
                co_open = False

            elif msd_key(words[i], "CASE") != "Gen": break
        
    return coords




### GENERAL TOOLS

def msd_key(word, key):

    if analyse_msd(word) != None and key in analyse_msd(word): return analyse_msd(word)[key]
    else: return "no have!!!"

        
def analyse_msd(hit):
    if len(hit) < MSD: return None
    text = re.sub("DRV_Der_", "DRV_Der+", hit[MSD])
    if len(text) > 2 and text[-2] == "|": text = text[:-1]+"MISC_"+text[-1]
    try: 
        return { re.split("_", x)[0] : re.split("_", x)[1] for x in re.split("\|", text) if len(re.split("\|", text)) > 1 }
    except:
        IndexError
        print(hit)
        return None

def expanding_iteration(words, word, debug=False):
    res = []
    stop_left = False
    stop_right = False
    start = words.index(word)
    for i in range(1, 100):
        if start-i >= 0: res.append(start-i)
        else: stop_left = True

        if start+i <= len(words)-1: res.append(start+i)
        else: stop_right = True

        if stop_right == True and stop_left == True: break

    return res
        

def select_closer(right, left, center, pref):

    if right == None and left == None: return None
    if right == None: return left
    if left == None: return right

    if pref == "r":
        if right-center <= center-left: return right
        else: return left

    else:
        if center-left <= right-center: return left
        else: return right


def analyse_wordtype(config_data, word_list):

    lemma = word_list[LEMMA]
    if lemma == "vaivaisesti" : return ADVERB
    if config_data != None:
        for c in config_data[PRE_ATTR_CONTEXT_WORD]:
            lemma = re.sub(c[0], config_data[COMPOUND_BASE], lemma)
        if re.sub(config_data[COMPOUND_BASE]+".*", "", lemma) == "":
            if re.sub(config_data[COMPOUND_BASE], "", lemma) == "": return SOLO
            else: return PRE_ATTR
        else:
            return POST_HEAD
