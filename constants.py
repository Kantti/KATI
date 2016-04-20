import re
LEMMA = 0 
WORD = 1
POS = 2
MSD = 3
LEMMACOMP = 4
#from compose_full_wordtype_list import *

SOLO = 0        #vaivainen
PRE_ATTR = 1    #VAIVAIStalo
POST_HEAD = 2   #selkäVAIVAINEN
ADVERB = 3      #vaivaisesti

LEFT = 0
RIGHT = 1

FINITE = 0
INFINITE = 1
DERIVATE = 3
INF_DRV = 4
ALL = 5

AGREEING = 0

ADVERBIAL = 0
F_SUBJECT = 1
OBJECT = 2
NP_ATTRIBUTE = 3
PREDICATIVE = 10
P_SUBJECT = 5
E_SUBJECT = 6
POS_SUBJECT = 7
POS_OBJECT = 8
NUM_ATTRIBUTE = 9
N_SUBJECT = 4
ESS_ADVERBIAL = 11
GEN_ATTRIBUTE = 12
COMPOUND_ATTRIBUTE = 13
PRON_ATTRIBUTE = 14
NONE = 15
COORDINATION = 16
POST_COMP_ATTRIBUTE = 17

CAT_NAMES = ["ADVERBIAL",
             "F_SUBJECT",
             "OBJECT",
             "NP_ATTRIBUTE",
             "N_SUBJECT",
             "P_SUBJECT",
             "E_SUBJECT",
             "POS_SUBJECT",
             "POS_OBJECT",
             "NUM_ATTRIBUTE",
             "PREDICATIVE",
             "ESS_ADVERBIAL",
             "GEN_ATTRIBUTE",
             "COMPOUND_ATTRIBUTE",
             "PRON_ATTRIBUTE",
             "NONE",
             "COORDINATION",
             "POST_COMP_ATTRIBUTE"]


FIRST_PERSON_SINGULAR = 101
SECOND_PERSON_SINGULAR = 102
FIRST_PERSON_PLURAL = 201
SECOND_PERSON_PLURAL = 202

coordination_elements = [",", "tai", "vai", "ynnä", "sekä", "ja"]

semi_numerals = ("puol", "sada", "tuhanne", "kahde",
                "kaks", "kolm", "neli", "neljä",
                "viisi", "viis", "kuus", "kuutis",
                "seitsem", "kahdeks", "yhdeks", "kymmen",
                "muutam")

adverbial_cases = ("Ess", "Tra", "Ela", "Ine", "Ill", "All", "Abl", "Ade")
finite_subject_cases = ("Nom", "Gen")
other_subject_cases = ("Nom", "Gen")
object_cases = ("Nom", "Gen", "Part", "Par")
predicative_cases = ("Nom", "Part", "Par")
modal_verbs = ("pitää", "täytyy", "tarvitsee")
intransitives = ("jäädä", "herätä")
num_attribute_pos = ("A", "Adv")
np_attribute_pos= ("A", "V")

num_pattern = re.compile("[£0-9\$]")

ID_TAG = 0
PRE_CONTEXT = 1
KEYWORD = 2
OPERATION = 3
NEW_ROLE = 4
NEW_CONTEXT_WORD = 5
POST_CONTEXT = 6

#Config stuff
PROJECT_NAME = 0
GARBAGE_LIST = 1
DATA_FILENAME = 2
PRE_ATTR_CONTEXT_WORD = 3
CORRECTION_FILENAME = 4
CHECKLIST = 5
KEYWORD_CLEAN = 6
COMPOUND_BASE = 7 
CONTEXT_CORPUS_DIR = 8 
COMP_REPLACEMENTS = 9
ROOT_PATH = 10
PROJECT_PATH = 11
CORPUS_FREQUENCIES = 12
F_THRESHOLD = 13
SENTENCE_CORPUS_WORDCOUNT = 14

xls_headers = ["id_tag", 
               "pre_context", 
               "keyword", 
               "operation",
               "new_role",
               "new_context_word",
               "post_context"]

