from constants import *
import re
import json
from project_resources import *
from syntax_resources import *
from correction_data import *

class Context():

    def __init__(self, hit, debug=False, corrections=None, direction="straight", role=None):


        self.id_tag = hit["id"]
        self.config_data = config_data
        self.hit = hit
        self.disregard = False
        self.role = role
        self.corrections = corrections
        self.debug = debug
        
        self.keyword  = [x for x in hit["keyword"]]
        self.key_loc = 0+hit["key_loc"]
        self.words = [x for x in hit["words"]]
        self.words.insert(self.key_loc, self.keyword)
        self.all_words = [x for x in self.words if x[LEMMA] != '"']
        self.coordinations = []
        self.compress_props()
        self.compress_verbal_compounds()
        self.text = ' '.join([x[WORD] for x in self.all_words])

        if direction == "straight":
            self.key_loc = self.all_words.index(self.keyword)
#            self.analyse_hit_keyword(key_loc)

        if direction == "reversed":
            self.analyse_related_words(self.keyword, role)


    def slice_ngram(self, length):

        res = []
        if len(self.all_words) <= length: return self.all_words
        i = 0
        while len(res) < length:
            i += 1
            if self.key_loc-i >= 0: 
                res.insert(0, self.all_words[self.key_loc-i])
            if self.key_loc+i < len(self.all_words): res.append(self.all_words[self.key_loc+i])

        return res



    def analyse_hit_keyword(self, key_loc):

        self.key_loc = key_loc
        self.keyword = self.all_words[self.key_loc]
        self.clean_keyword()
        self.wordtype = analyse_wordtype(self.config_data, self.keyword)
        self.comp_attr = None
        
#        self.keyword[POS] = "N/A"


        self.coords=[]

        if self.wordtype != PRE_ATTR:
            self.categorise_morphological_forms()
            self.choose_role()
            self.disambiguate()
            self.coords = analyse_coordination(self.all_words, self.keyword)
            self.coordinations = [self.all_words[i] for i in range(0, len(self.all_words)) if i in self.coords]
            if self.wordtype == POST_HEAD and self.config_data != None:
                lemma = self.keyword[LEMMA]
                for c in self.config_data[PRE_ATTR_CONTEXT_WORD]:
                    lemma = re.sub(c[0], self.config_data[COMPOUND_BASE], lemma)
                self.comp_attr = re.sub(self.config_data[COMPOUND_BASE], "", lemma)

        else:
            self.possible_roles=[COMPOUND_ATTRIBUTE]

        self.role = self.possible_roles[0]
        self.context_word = self.get_context_word()
        if self.corrections != None: self.apply_correction_data(self.corrections)

        return (self.role, self.context_word)


    def analyse_related_words(self, word, role):

        self.res_words = []

        for i in range(0, len(self.all_words)):
            if role != COORDINATION:
                test = self.analyse_hit_keyword(i)
                if test[1] == word and test[0] == role: self.res_words.append(self.all_words[i])

            



 ### COMPRESSION

 # Compress elements comprising of more than one words to single items
 # Move key_loc accordingly
 # Word order might be changed when constructions are merged
 # Proper names:
 ## ['Janne', 'Ahonen'] -> ['Janne Ahonen']
 # Negated verbal constructs:
 # ['Eivät','ehkä,'tule'] -> ['Eivät tule', 'ehkä']
 # Temporal verbal constructs:
 # ['Olivat', sieltä', 'tulleet'] -> ['sieltä', 'Olivat tulleet']

    def clean_keyword(self):
    
        self.keyword[LEMMA] = self.keyword[LEMMA].lower()
        if self.config_data != None:
            for change in self.config_data[KEYWORD_CLEAN]:
                if change["test"] in self.keyword[LEMMA]:
                    for c in change["change"]:
                        self.keyword[c] = re.sub(change["change"][c][0], change["change"][c][1], self.keyword[c])


    def compress_props(self):
        removed = []

        

        for i in range(0, len(self.all_words)-1):
            if test_proper_name(i, self.all_words[i]) == True: self.all_words[i][MSD] += "|SUBCAT_Prop"
            if test_proper_name(i, self.all_words[i]) == True and test_proper_name(i+1, self.all_words[i+1]):
                if self.all_words[i+1][POS] != "N" and "OTHER" not in analyse_msd(self.all_words[i+1]):
                    self.all_words[i+1][POS] = "N"
                    self.all_words[i+1][MSD] = "SUBCAT_Prop|CASECHANGE_Up|NUM_sg"
                    if self.all_words[i+1][WORD].endswith("n"): self.all_words[i+1][MSD] += "|CASE_Gen"
                    else: 
                        self.all_words[i+1][MSD] += "|CASE_Nom"
                        self.all_words[i+1][LEMMA] = self.all_words[i+1][WORD]

                    
                if "CASE" in analyse_msd(self.all_words[i]) and analyse_msd(self.all_words[i])["CASE"] == "Nom":
                    self.all_words[i+1][WORD] = self.all_words[i][WORD]+" "+self.all_words[i+1][WORD]
                    self.all_words[i+1][LEMMA] = self.all_words[i][LEMMA]+" "+self.all_words[i+1][LEMMA]
                    if msd_key(self.all_words[i+1], "SUBCAT") != "Prop": self.all_words[i+1][MSD] += "|SUBCAT_Prop"
                    removed.append(i)                   

                elif msd_key(self.all_words[i], "OTHER") == "UNK":
                    if "CASE" in analyse_msd(self.all_words[i]) and "CASE" != "Nom":
                        notnom = True
                    else:
                        self.all_words[i+1][WORD] = self.all_words[i][WORD]+" "+self.all_words[i+1][WORD]
                        self.all_words[i+1][LEMMA] = self.all_words[i][LEMMA]+" "+self.all_words[i+1][LEMMA]
                        self.all_words[i+1][MSD] += "|SUBCAT_Prop"
                        removed.append(i)


        for i in reversed(removed):
            self.all_words.remove(self.all_words[i])


    def compress_verbal_compounds(self):

        self.compress_negation_compounds()
        self.compress_tempus_compounds()

    def compress_negation_compounds(self):
        neg_open = False
        removed = []
        for i in range(0, len(self.all_words)):
            if len(self.all_words[i]) < POS: print(self.all_words)
            if self.all_words[i][POS] == "V" and "SUBCAT" in analyse_msd(self.all_words[i]) and analyse_msd(self.all_words[i])["SUBCAT"] == "Neg":
                neg = self.all_words[i]
                neg_i = i
                neg_open = True
            elif neg_open == True and self.all_words[i][POS] == "V" and "NEG" in analyse_msd(self.all_words[i]) and analyse_msd(self.all_words[i])["NEG"] == "ConNeg":
                self.all_words[i][MSD] += "|"+neg[MSD]
                self.all_words[i][WORD] = neg[WORD]+" "+self.all_words[i][WORD]
#                print(self.all_words[i][WORD])
                neg_open = False
                if i < self.key_loc: self.key_loc -= 1    
                removed.append(neg_i)
            elif neg_open == True and self.all_words[i][POS] == "V" and all(s in analyse_msd(self.all_words[i]) for s in ("CASE", "PCP")):
                if analyse_msd(self.all_words[i])["CASE"] == "Nom" and analyse_msd(self.all_words[i])["PCP"] == "PrfPrc":
                    self.all_words[i][MSD] = re.sub("PCP_PrfPrc", "TENSE_Pst|MOOD_Ind", self.all_words[i][MSD])
                    self.all_words[i][MSD] += "|"+neg[MSD]
                    self.all_words[i][WORD] = neg[WORD]+" "+self.all_words[i][WORD]
                    neg_open = False
                    if i < self.key_loc: self.key_loc -= 1    
                    removed.append(neg_i)
        for r in reversed(removed):
            self.all_words.remove(self.all_words[r])

    def compress_tempus_compounds(self):
        temp_open = False
        removed = []
        participles = ["PrfPrc", "PrsPrc"]
        for i in range(0, len(self.all_words)):
            if self.all_words[i][LEMMA] == "olla" and "PRS" in analyse_msd(self.all_words[i]):
                copula = self.all_words[i]
                copula_i = i
                temp_open = True
                if "PRS" not in analyse_msd(copula): print(copula[MSD])
                copula_num = re.sub("[0-9]", "", analyse_msd(copula)["PRS"])
            elif temp_open == True and self.all_words[i][POS] == "V" and "CASE" in analyse_msd(self.all_words[i]) and analyse_msd(self.all_words[i])["CASE"] == "Nom" and analyse_msd(self.all_words[i])["NUM"] == copula_num and "PCP" in analyse_msd(self.all_words[i]) and analyse_msd(self.all_words[i])["PCP"] in participles and self.all_words[i][LEMMA] != self.all_words[i][WORD]:
                temp_open = False
                removed.append(i)
                if i < self.key_loc: self.key_loc -= 1
                if "MOOD" not in analyse_msd(copula): print("No mood:", copula)
                if analyse_msd(copula)["MOOD"] == "Cond" or analyse_msd(copula)["MOOD"] == "Pot": self.all_words[copula_i][MSD] += "|TENSE_Pst"
                self.all_words[copula_i][MSD] = re.sub("TENSE_Prs", "TENSE_Prf", self.all_words[copula_i][MSD])
                self.all_words[copula_i][MSD] = re.sub("TENSE_Pst", "TENSE_PlPrf", self.all_words[copula_i][MSD])
                self.all_words[copula_i][LEMMA] = self.all_words[i][LEMMA]
                self.all_words[copula_i][WORD] += " "+self.all_words[i][WORD]
        
        for r in reversed(removed):
            self.all_words.remove(self.all_words[r])
        
        return True

### ANALYSIS

## Analyse syntactic role of keyword by eliminating impossible choices


    def categorise_morphological_forms(self):
        self.possible_roles = [NP_ATTRIBUTE, NUM_ATTRIBUTE, PRON_ATTRIBUTE, NONE]
        case = msd_key(self.keyword, "CASE")

        if case in adverbial_cases:
            self.possible_roles.append(ADVERBIAL)
            self.possible_roles.append(ESS_ADVERBIAL)
            self.possible_roles.append(POS_SUBJECT)

        if case in finite_subject_cases:
            self.possible_roles.append(F_SUBJECT)
            self.possible_roles.append(P_SUBJECT)

        if case in other_subject_cases:
            self.possible_roles.append(N_SUBJECT)

        if case in object_cases:
            self.possible_roles.append(OBJECT)
            self.possible_roles.append(E_SUBJECT)

        if case in predicative_cases:
            self.possible_roles.append(PREDICATIVE)

        if case == "Gen": self.possible_roles.append(GEN_ATTRIBUTE)

#        print("1st step", self.possible_roles)


    def choose_role(self):


        self.possible_roles = [x for x in self.possible_roles if self.test_possibility(x) == True]
        if NUM_ATTRIBUTE in self.possible_roles: self.possible_roles = [NUM_ATTRIBUTE]  
        elif PRON_ATTRIBUTE in self.possible_roles: self.possible_roles = [PRON_ATTRIBUTE]
        elif NP_ATTRIBUTE in self.possible_roles: self.possible_roles = [NP_ATTRIBUTE]
        elif GEN_ATTRIBUTE in self.possible_roles: self.possible_roles = [GEN_ATTRIBUTE]
        elif P_SUBJECT in self.possible_roles: self.possible_roles.remove(F_SUBJECT)
        if len(self.possible_roles) > 1: self.possible_roles.remove(NONE)
       


    def test_possibility(self, pos):
        args = (self.all_words, self.keyword)
        if pos == NP_ATTRIBUTE: return test_NP_attribute(*args)
        if pos == NUM_ATTRIBUTE: return test_NUM_attribute(*args)
        if pos == F_SUBJECT: return test_finite_subject(*args)
        if pos == OBJECT: return test_object(*args)
        if pos == PREDICATIVE: return test_predicative(*args)
        if pos == E_SUBJECT: return test_e_subject(*args)
        if pos == ESS_ADVERBIAL: return test_Ess_adverbial(*args)
        if pos == POS_SUBJECT: return test_POS_subject(*args)
        if pos == N_SUBJECT: return test_N_subject(*args)
        if pos == P_SUBJECT: return test_P_subject(*args)
        if pos == POS_OBJECT: return test_POS_object(*args)
        if pos == GEN_ATTRIBUTE: return test_Gen_attribute(*args)
        if pos == ADVERBIAL: return test_adverbial(*args)
        if pos == PRON_ATTRIBUTE: return test_Pron_attribute(*args)
        if pos == NONE: return True

## Analyse relevant words in relation to keyword's syntactic role

    def locate_context_word(self, r):
        args = (self.all_words, self.keyword)
        if r == None or locate_closest_verb(self.all_words, self.key_loc, FINITE) == None: return None
        if r == ADVERBIAL: return locate_subject(*args)         #tehty
        if r == GEN_ATTRIBUTE: return locate_gen_head(*args)    #tehty
        if r == ESS_ADVERBIAL: return locate_subject(*args) #tehty
        if r == F_SUBJECT: return locate_closest_verb(self.all_words, self.key_loc, FINITE) #tehty
        if r == OBJECT: return locate_closest_verb(self.all_words, self.key_loc, FINITE) # tehty
        if r == NP_ATTRIBUTE: return locate_agreeing_head(*args)    #tehty
        if r == PREDICATIVE: return locate_subject(*args)   #tehty
        if r == P_SUBJECT: return locate_object(*args)      #tehty
        if r == E_SUBJECT: return locate_adverbial(*args)   #tehty
        if r == POS_SUBJECT: return locate_adverbial(*args) #tehty
        if r == POS_OBJECT: return locate_object(*args)     #tehty
        if r == NUM_ATTRIBUTE: return locate_num_head(*args)    #tehty
        if r == N_SUBJECT: return locate_closest_verb(self.all_words, self.key_loc, INF_DRV)   #tehty
    
    def get_context_word(self):
        if self.wordtype == PRE_ATTR:
            word = [x for x in self.keyword]
            if self.config_data == None:
                word = self.keyword
                word[WORD] = re.sub("[vV]aivai(s(en|ten)*|nen)", "", word[WORD])
                word[LEMMA] = re.sub("[vV]aivai(s(en|ten)*|nen)", "", word[LEMMA])
            else:
                for p in self.config_data[PRE_ATTR_CONTEXT_WORD]:
                    word[WORD] = re.sub(p[0], p[1], word[WORD])
                    word[LEMMA] = re.sub(p[0], p[1], word[LEMMA])

            return word

        else:
            c = self.locate_context_word(self.possible_roles[0])
            if c != None: 
                if c >= len(self.all_words): return [""]
                else: return self.all_words[c]

            else: return [""]


    def disambiguate(self):

        if len(self.possible_roles) > 1:

            if P_SUBJECT in self.possible_roles and PREDICATIVE in self.possible_roles:
                if self.key_loc > locate_closest_verb(self.all_words, self.key_loc, FINITE):
                    self.possible_roles.remove(P_SUBJECT)
                else:
                    self.possible_roles.remove(PREDICATIVE)

### TAKING ACCOUNT OF MANUAL RE-PROCESSING CHANGES

    def apply_correction_data(self, corrections):
        if corrections["operation"] == "out" : self.disregard = True
        else:
            if corrections["new_context_word"] != "":
                nw = None
                if type(corrections["new_context_word"]) != str:
                    corrections["new_context_word"] = re.sub("\..*", "", str(corrections["new_context_word"]))
                for x in self.all_words:
                    if x[WORD] == str(corrections["new_context_word"]): 
                        nw = x
                        break

                if nw == None:
                    for x in self.all_words:
                        if corrections["new_context_word"] in x[WORD]:
                            nw = x
                            break

                if nw == None:
                    for x in self.all_words:
                        if x[WORD] in re.split(" ", str(corrections["new_context_word"])):
                            nw = x
                            break

                if nw == None:
                    mark = True
#                    print(CAT_NAMES[self.role], self.id_tag, corrections["new_context_word"], self.all_words)
                else:
                    self.context_word = nw

            if corrections["new_role"] != "":
                self.role = CAT_NAMES.index(corrections["new_role"])
                self.possible_roles[0] = CAT_NAMES.index(corrections["new_role"])

### OUTPUT STUFF

    def get_concordance_line(self, line_type):
        line = []
        for i in range(0, len(self.all_words)):
            
            word = self.all_words[i][WORD]
            if i == self.key_loc: word = "\t"+word+"\t\t\t\t"
            if line_type == "cat" and i == self.locate_context_word(self.possible_roles[0]): word = "_"+word+"_"
            if line_type == "coord" and i in self.coords: word = "_"+word+"_"
                    
            line.append(word)
#        if line_type == "coord": print(str(self.id_tag)+"\t"+" ".join(line))

        return str(self.id_tag)+"\t"+" ".join(line)


    def get_concordance_dict(self, line_type="cat"):


        line = re.split("\t", self.get_concordance_line(line_type))

        return { xls_headers[i] : line[i] for i in range(0, len(xls_headers)) }



