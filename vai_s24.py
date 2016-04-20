from project_resources import *
config_data = {
PROJECT_NAME : "vai_s24",
DATA_FILENAME : "../data/vai_s24_datawl_msd_id-0.json",
GARBAGE_LIST : ["c3sn"],
PRE_ATTR_CONTEXT_WORD :  (("[vV]aivaisten", ""), 
                          ("[Vv]aivainen",  ""),
                          ("[Vv]aivaisen",  ""),
                          ("[Vv]aivais",    "")),
CORRECTION_FILENAME : "Concordance_checkup_s24.xls",
CHECKLIST : (":", "ja", "-ja", ".", "i")
}
